"""M1: universal, inert, opt-in, versioned author annotations."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest import TestCase

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.contracts.author_annotations import (
    InvalidTarget,
    _resolve,
    inspect_author_annotations,
)
from gisela.engine.runtime import new_session, restore_session

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "packages/h46b_central_clasificadora.package.json"
)


def base():
    value = json.loads(SOURCE.read_text(encoding="utf8"))
    value["manifest"]["format_version"] = "1.7"
    return value


def add(package, target, text="test annotation"):
    package.setdefault("author_annotations", []).append(
        {
            "target": target,
            "annotations": [{"audience": "info", "text": text}],
        }
    )
    return package


def reject(package, diagnostic):
    try:
        admit_package(package)
    except PackageRejected as exc:
        if diagnostic not in [row.code for row in exc.diagnostics]:
            raise AssertionError(exc.diagnostics) from exc
    else:
        raise AssertionError("Package was unexpectedly admitted")


class UniversalAuthorAnnotationsV17(TestCase):
    def test_local_and_addressed_unified_inspector_and_canonical_roundtrip(self):
        story = base()
        story["nodes"][0]["annotations"] = [
            {"audience": "info", "text": {"text": "whole node"}}
        ]
        story["nodes"][0]["steps"][0]["annotations"] = [
            {"audience": "glauquir", "text": {"text": "public glauquir note"}},
            {"audience": "info", "text": "Private: source dialogue"},
        ]
        for target in [
            "",
            "/manifest/format_version",
            "/nodes/0/steps/0/text/text",
            "/rules/0/effects/0/op",
            "/dice_profiles/0/bands/0/min",
            "/initial_state/facts",
            "/scenes/0/actors/0/visible_if/constant",
            "/nodes/0/steps/2/options/0",
            "/endings/0/id",
        ]:
            add(story, target, target or "package")
        admitted = admit_package(story)
        notes = inspect_author_annotations(admitted)
        self.assertEqual(len(notes), 12)
        self.assertEqual([x["order"] for x in notes], list(range(12)))
        self.assertEqual([x["source"] for x in notes[:3]], ["local"] * 3)
        self.assertEqual(
            [x["target"] for x in notes[:3]],
            ["/nodes/0", "/nodes/0/steps/0", "/nodes/0/steps/0"],
        )
        self.assertEqual([x["source"] for x in notes[3:]], ["addressed"] * 9)
        self.assertEqual(notes[3]["target"], "")
        self.assertEqual(notes[4]["target"], "/manifest/format_version")
        self.assertEqual(
            inspect_author_annotations(admit_package(admitted.materialize())), notes
        )
        self.assertNotIn("author_annotations", new_session(admitted).export())

    def test_pointer_escaping_and_scalar_types_and_null(self):
        story = base()
        # `mary` is a pre-existing permissive object; no executable content added.
        story["mary"] = {
            "demo/key~": {"array": [True, False, None, 0, {"deep": [1, "hi"]}]}
        }
        for target in (
            "/mary/demo~1key~0/array/0",
            "/mary/demo~1key~0/array/1",
            "/mary/demo~1key~0/array/2",
            "/mary/demo~1key~0/array/3",
            "/mary/demo~1key~0/array/4/deep/1",
        ):
            add(story, target)
        # Admission of arbitrary MARY payload is not guaranteed; separately
        # verify RFC 6901 resolution without altering the story semantics.
        for entry in story["author_annotations"]:
            _resolve(story, entry["target"])
        self.assertIsNone(_resolve(story, "/mary/demo~1key~0/array/2"))
        self.assertIs(_resolve(story, "/mary/demo~1key~0/array/0"), True)

    def test_pointer_combined_escapes_and_invalid_escape_errors(self):
        package = {"~1/~": {"": "value"}}
        self.assertEqual(_resolve(package, "/~01~1~0/"), "value")
        for target in ("/~", "/~2", "/~01~1~0/~x"):
            with (
                self.subTest(target=target),
                self.assertRaisesRegex(InvalidTarget, "Malformed ~ escape"),
            ):
                _resolve(package, target)

    def test_pointer_array_indices_preserve_canonical_and_bounds_errors(self):
        package = {"items": [None, False], "keys": {"00": "member"}}
        self.assertIsNone(_resolve(package, "/items/0"))
        self.assertIs(_resolve(package, "/items/1"), False)
        self.assertEqual(_resolve(package, "/keys/00"), "member")
        for key in ("", "00", "01", "-", "-1", "+1", "١", "１", "1.0"):
            with (
                self.subTest(key=key),
                self.assertRaisesRegex(InvalidTarget, "not canonical decimal"),
            ):
                _resolve(package, "/items/" + key)
        for key in ("2", "9999999999999999", "1" * 17):
            with (
                self.subTest(key=key),
                self.assertRaisesRegex(InvalidTarget, "out of bounds"),
            ):
                _resolve(package, "/items/" + key)

    def test_pointer_length_and_depth_boundaries(self):
        key = "x" * 2047
        package = {key: "value"}
        self.assertIs(_resolve(package, ""), package)
        self.assertEqual(_resolve(package, "/" + key), "value")
        with self.assertRaisesRegex(InvalidTarget, "character budget"):
            _resolve(package, "/" + key + "x")
        nested = "leaf"
        for _ in range(64):
            nested = {"x": nested}
        self.assertEqual(_resolve(nested, "/x" * 64), "leaf")
        with self.assertRaisesRegex(InvalidTarget, "exceeds 64 segments"):
            _resolve(nested, "/x" * 65)

    def test_reject_invalid_missing_ambiguous_and_metadata_pointers(self):
        for path in (
            "a",
            "/",
            "/nodes/999",
            "/nodes/00",
            "/nodes/-",
            "/nodes/0/steps/0/unknown",
            "/nodes/0/steps/0/text/text/1",
            "/nodes/~2",
            "/nodes/~",
            "/author_annotations",
            "/author_annotations/0/target",
            "/nodes/0/annotations/0",
        ):
            with self.subTest(path=path):
                reject(add(base(), path), "AUTHOR_POINTER_INVALID")
        story = add(base(), "/nodes/0")
        add(story, "/nodes/0")
        reject(story, "AUTHOR_POINTER_DUPLICATE")
        reject(add(base(), "/nodes/" + "/0/" * 65 + "id"), "AUTHOR_POINTER_INVALID")
        reject(add(base(), "/" + "a" * 2049), "SCHEMA_INVALID")

    def test_drift_rejected_on_final_compiled_json(self):
        story = add(base(), "/nodes/16/id")
        admit_package(story)
        story["nodes"].pop()
        reject(story, "AUTHOR_POINTER_INVALID")

    def test_incompatible_formats_and_illegal_local_placement_rejected(self):
        p = add(base(), "/manifest/format_version")
        p["manifest"]["format_version"] = "1.6"
        reject(p, "SCHEMA_INVALID")
        p = base()
        p["rules"][0]["effects"][0]["annotations"] = [
            {"audience": "info", "text": "not permitted"}
        ]
        reject(p, "SCHEMA_INVALID")
        p = base()
        p["nodes"][0]["annotations"] = [{"audience": "secret", "text": {"text": "x"}}]
        reject(p, "SCHEMA_INVALID")
        p = base()
        p["nodes"][0]["annotations"] = [{"audience": "info", "text": ""}]
        reject(p, "SCHEMA_INVALID")
        p = base()
        p["nodes"][0]["annotations"] = [
            {"audience": "info", "text": {"text": "x", "eval": "bad"}}
        ]
        reject(p, "SCHEMA_INVALID")
        p = base()
        add(p, "/nodes/0")
        p["author_annotations"][0]["annotations"][0]["audience"] = "glauquir"
        reject(p, "SCHEMA_INVALID")

    def test_limits_and_localization(self):
        reject(add(base(), "/nodes/0", "x" * 8193), "SCHEMA_INVALID")
        p = base()
        p["nodes"][0]["annotations"] = [
            {"audience": "info", "text": {"text": "x" * 8193}}
        ]
        reject(p, "AUTHOR_TEXT_LIMIT")
        p = base()
        p["nodes"][0]["annotations"] = [
            {"audience": "info", "text": {"text_key": "absent"}}
        ]
        reject(p, "MISSING_AUTHOR_TEXT")
        p = base()
        p["strings"] = {"es_cl": {"note": "Texto de autor"}}
        p["nodes"][0]["annotations"] = [
            {"audience": "info", "text": {"text_key": "note"}}
        ]
        admitted = admit_package(p)
        self.assertEqual(
            inspect_author_annotations(admitted)[0]["text"], {"text_key": "note"}
        )
        p = base()
        p["nodes"][0]["annotations"] = [{"audience": "info", "text": "a"}] * 33
        reject(p, "SCHEMA_INVALID")
        p = base()
        for i in range(513):
            add(p, "/nodes/0/id" if i == 0 else f"/nodes/{i % 17}/id")
        reject(p, "SCHEMA_INVALID")
        p = base()
        for i in range(160):
            add(p, f"/nodes/{i % 17}/steps/0/id", "X" * 8192)
        reject(p, "AUTHOR_POINTER_DUPLICATE")
        self.assertEqual(len(inspect_author_annotations(admit_package(base()))), 0)

    def test_info_inert_for_rng_observe_state_history_and_restore(self):
        pure = base()
        noted = copy.deepcopy(pure)
        noted["nodes"][0]["steps"][0]["annotations"] = [
            {"audience": "info", "text": "hidden secret marker"}
        ]
        noted["scenes"][0]["annotations"] = [
            {"audience": "info", "text": "never displayed"}
        ]
        add(noted, "/nodes/15/steps/0", "unreachable branch hidden content")
        add(noted, "/dice_profiles/0/bands/0/min", "dice config")
        original = admit_package(pure)
        annotation = admit_package(noted)
        self.assertNotEqual(original.digest, annotation.digest)
        seed = "4" * 64
        left = new_session(original, session_id="m1", seed=seed)
        right = new_session(annotation, session_id="m1", seed=seed)
        for i in range(25):
            lo, ro = left.observe(), right.observe()
            self.assertEqual(lo, ro)
            self.assertNotIn("hidden secret marker", json.dumps(ro))
            self.assertNotIn("unreachable branch hidden content", json.dumps(ro))
            self.assertEqual(left.read_history(), right.read_history())
            self.assertEqual(left.export()["rng"], right.export()["rng"])
            # Ignore only package identity (full package digest includes metadata).
            ls, rs = left.export(), right.export()
            ls.pop("package_digest")
            rs.pop("package_digest")
            self.assertEqual(ls, rs)
            self.assertEqual(
                restore_session(annotation, right.export()).export(), right.export()
            )
            if lo["status"] == "ended":
                break
            if not lo["actions"]:
                break
            action = lo["actions"][0]["action_id"]
            request = {
                "session_id": "m1",
                "revision": lo["revision"],
                "action_id": action,
            }
            self.assertEqual(left.act(request), right.act(request))
        self.assertTrue(
            any(
                n["target"] == "/nodes/15/steps/0"
                for n in inspect_author_annotations(annotation)
            )
        )
        # The special Glauquir projection must not reclassify info as glauquir.
        self.assertNotIn("hidden secret marker", json.dumps(right.observe_glauquir()))

    def test_legacy_glauquir_and_v16_untouched(self):
        old = json.loads(SOURCE.read_text("utf8"))
        old["manifest"]["format_version"] = "1.6"
        old["nodes"][0]["annotations"] = [
            {"audience": "glauquir", "text": {"text": "Legacy"}}
        ]
        s = new_session(admit_package(old))
        self.assertIn("Legacy", json.dumps(s.observe_glauquir())) if s.observe()[
            "status"
        ] == "node" else None
        self.assertNotIn("annotations", s.observe())
        self.assertRaises(TypeError, inspect_author_annotations, old)

    def test_actual_roll_and_action_notes_cannot_change_rng_or_history(self):
        pure = base()
        pure["manifest"].setdefault("variables", []).append(
            {
                "scope": "session",
                "id": "m1_die",
                "type": "integer",
                "initial": 0,
            }
        )
        pure["initial_state"].setdefault("session_variables", {})["m1_die"] = 0
        action = {
            "id": "m1_roll",
            "label": {"text": "Roll"},
            "effects": [
                {
                    "op": "roll",
                    "sides": 20,
                    "store": {"var": {"scope": "session", "key": "m1_die"}},
                }
            ],
        }
        pure["scenes"][0]["actions"].insert(0, action)
        noted = copy.deepcopy(pure)
        noted["scenes"][0]["actions"][0]["annotations"] = [
            {"audience": "info", "text": "Action author notes are not observable"}
        ]
        add(noted, "/scenes/0/actions/0/effects/0/sides", "The actual die")
        add(
            noted,
            "/scenes/0/actions/0/effects/0/store/var/key",
            "The result destination",
        )
        left = new_session(admit_package(pure), session_id="die", seed="a" * 64)
        right = new_session(admit_package(noted), session_id="die", seed="a" * 64)
        for _ in range(3):
            self.assertEqual(left.observe(), right.observe())
            left_action = next(
                a for a in left.observe()["actions"] if a["id"] == "m1_roll"
            )
            right_action = next(
                a for a in right.observe()["actions"] if a["id"] == "m1_roll"
            )
            for session, chosen in ((left, left_action), (right, right_action)):
                response = session.act(
                    {
                        "session_id": "die",
                        "revision": session.observe()["revision"],
                        "action_id": chosen["action_id"],
                    }
                )
                self.assertEqual(response["status"], "ok")
            self.assertEqual(left.observe(), right.observe())
            a, b = left.export(), right.export()
            self.assertGreater(a["rng"]["counter"], 0)
            a.pop("package_digest")
            b.pop("package_digest")
            self.assertEqual(a, b)
            self.assertEqual(left.read_history(), right.read_history())

    def test_utf8_budget_and_null_target_in_admitted_package(self):
        story = base()
        story["scenes"][0]["presentation"] = {"example_null": None}
        add(story, "/scenes/0/presentation/example_null", "NULL scalar")
        admitted = admit_package(story)
        self.assertEqual(
            inspect_author_annotations(admitted)[0]["target"],
            "/scenes/0/presentation/example_null",
        )
        big = base()
        # 160 distinct local notes exceed the global byte budget without
        # exceeding the per-record and per-owner record limits.
        for node in big["nodes"][:10]:
            node["annotations"] = [
                {"audience": "info", "text": "á" * 8192} for _ in range(16)
            ]
        reject(big, "AUTHOR_TEXT_BUDGET")

    def test_dice_result_pending_and_continuation_are_unchanged(self):
        pure = base()
        pure["manifest"]["entry"] = {"scene": "puesto_b"}
        pure["initial_state"]["current_scene"] = "puesto_b"
        for character in pure["initial_state"]["characters"]:
            if character["id"] == "alberto":
                character["location"] = "puesto_b"
        # Isolate the existing DICE scenario from the productive time gate.
        pure["scenes"][3]["actions"][1].pop("enabled_if")
        noted = copy.deepcopy(pure)
        add(
            noted,
            "/scenes/3/actions/1/evaluation/branches/0/outcome",
            "Hidden DICE result provenance",
        )
        add(noted, "/dice_profiles/1/bands/0/min", "DICE profile boundary")
        left = new_session(admit_package(pure), session_id="dice", seed="e" * 64)
        right = new_session(admit_package(noted), session_id="dice", seed="e" * 64)
        for session in (left, right):
            before = session.observe()
            action = next(
                row for row in before["actions"] if row["id"] == "probar_radio"
            )
            result = session.act(
                {
                    "session_id": "dice",
                    "revision": before["revision"],
                    "action_id": action["action_id"],
                }
            )
            self.assertEqual(result["status"], "ok")
        self.assertEqual(left.observe(), right.observe())
        self.assertEqual(left.observe()["content"]["rolls"], [2])
        self.assertEqual(left.observe()["content"]["outcome"], "distorsion")
        self.assertEqual(left.export()["rng"]["counter"], 1)
        original_state = left.export()
        annotated_state = right.export()
        original_state.pop("package_digest")
        annotated_state.pop("package_digest")
        self.assertEqual(original_state, annotated_state)
        for session in (left, right):
            view = session.observe()
            self.assertEqual(
                session.act(
                    {
                        "session_id": "dice",
                        "revision": view["revision"],
                        "action_id": "continue_evaluation",
                    }
                )["status"],
                "ok",
            )
        self.assertEqual(left.observe(), right.observe())
        self.assertEqual(left.export()["rng"], right.export()["rng"])
        self.assertEqual(left.export()["history"], right.export()["history"])
        self.assertNotIn(
            "Hidden DICE result provenance", json.dumps(right.observe_glauquir())
        )
