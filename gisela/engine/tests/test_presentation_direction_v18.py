"""M2: closed step direction, public projection, and narrative noninterference."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from unittest import TestCase

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import new_session, restore_session

BASE = (
    Path(__file__).resolve().parents[2]
    / "packages/h46b_central_clasificadora.package.json"
)


def story(version="1.8"):
    package = json.loads(BASE.read_text(encoding="utf-8"))
    package["manifest"]["format_version"] = version
    return package


def direction():
    return {
        "box": "narration",
        "portrait": "alberto_stickman",
        "expression": "concerned",
        "background": "porteria_evening",
        "reveal": {"mode": "typewriter", "characters_per_second": 32},
        "transition": {"kind": "fade", "duration_ms": 350},
        "advance": {"mode": "confirm"},
        "sound": {"cue": "clock_click", "channel": "sfx"},
        "color": "default",
    }


def reach_node(session):
    view = session.observe()
    offer = next(a for a in view["actions"] if a["id"] == "tomar_turno")
    result = session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": offer["action_id"],
        }
    )
    if result["status"] != "ok":
        raise AssertionError(result)
    return session.observe()


def advance(session):
    view = session.observe()
    offer = next(a for a in view["actions"] if a["kind"] == "advance")
    result = session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": offer["action_id"],
        }
    )
    if result["status"] != "ok":
        raise AssertionError(result)
    return session.observe()


class PresentationDirectionV18(TestCase):
    def test_public_projection_is_active_step_only_and_defensive(self):
        package = story()
        first, second, hidden = package["nodes"][0]["steps"]
        first["presentation"] = direction()
        second["presentation"] = {
            "box": "dialogue",
            "expression": "smile",
            "reveal": {"mode": "instant"},
            "advance": {"mode": "auto", "delay_ms": 1000},
        }
        hidden["annotations"] = [{"audience": "info", "text": "Private future choice"}]
        first["annotations"] = [{"audience": "info", "text": "private author comment"}]
        package["author_annotations"] = [
            {
                "target": "/nodes/0/steps/1/text/text",
                "annotations": [{"audience": "info", "text": "hidden target"}],
            }
        ]
        admitted = admit_package(package)
        session = new_session(admitted, session_id="m2", seed="1" * 64)
        self.assertNotIn("presentation", session.observe()["content"])
        initial_state = session.export()
        first_view = reach_node(session)
        self.assertEqual(first_view["content"]["presentation"], direction())
        self.assertNotIn("smile", json.dumps(first_view))
        self.assertNotIn("private", json.dumps(first_view).lower())
        self.assertNotIn("author_annotations", json.dumps(first_view))
        self.assertNotIn("presentation", session.read_history()[-1])
        current_snapshot = session.export()
        for _ in range(20):
            self.assertEqual(session.observe(), first_view)
        self.assertEqual(session.export(), current_snapshot)
        first_view["content"]["presentation"]["portrait"] = "mutated"
        self.assertEqual(
            session.observe()["content"]["presentation"]["portrait"],
            "alberto_stickman",
        )
        second_view = advance(session)
        self.assertEqual(second_view["content"]["kind"], "dialogue")
        self.assertEqual(second_view["content"]["presentation"], second["presentation"])
        self.assertNotIn("alberto_stickman", json.dumps(second_view))
        self.assertNotEqual(initial_state["revision"], session.export()["revision"])
        self.assertEqual(
            restore_session(admitted, session.export()).observe(), session.observe()
        )

    def test_presentational_hints_do_not_change_rng_state_or_choices(self):
        base = story()
        annotated = copy.deepcopy(base)
        annotated["nodes"][0]["steps"][0]["presentation"] = direction()
        annotated["nodes"][0]["steps"][1]["presentation"] = {
            "background": "main_floor",
            "advance": {"mode": "auto", "delay_ms": 500},
        }
        left, right = [
            new_session(admit_package(p), session_id="m2", seed="c" * 64)
            for p in (base, annotated)
        ]
        for index in range(3):
            if index == 0:
                vleft, vright = reach_node(left), reach_node(right)
            else:
                vleft, vright = advance(left), advance(right)
            cleaned = copy.deepcopy(vright)
            cleaned["content"].pop("presentation", None)
            self.assertEqual(vleft, cleaned)
            a, b = left.export(), right.export()
            a.pop("package_digest")
            b.pop("package_digest")
            self.assertEqual(a, b)
            self.assertEqual(left.read_history(), right.read_history())

    def test_closed_vocabulary_rejects_scripts_paths_ranges_and_unknown_fields(self):
        invalid = [
            {"python": "print(1)"},
            {"portrait": "../private/file.png"},
            {"expression": "foo bar"},
            {"background": "C:\\private\\file"},
            {"box": "script"},
            {"reveal": {"mode": "typewriter", "characters_per_second": 0}},
            {"reveal": {"mode": "typewriter", "characters_per_second": True}},
            {"reveal": {"mode": "instant", "characters_per_second": 20}},
            {"transition": {"kind": "python", "duration_ms": 100}},
            {"transition": {"kind": "fade", "duration_ms": 3001}},
            {"advance": {"mode": "auto", "delay_ms": 249}},
            {"advance": {"mode": "auto", "delay_ms": 10001}},
            {"advance": {"mode": "confirm", "delay_ms": 500}},
            {"sound": {"cue": "/absolute/audio.ogg"}},
            {"sound": {"cue": "clock_click", "channel": "python"}},
            {"color": "absolute"},
            {},
        ]
        for specimen in invalid:
            with self.subTest(specimen=specimen):
                package = story()
                package["nodes"][0]["steps"][0]["presentation"] = specimen
                with self.assertRaises(PackageRejected) as ctx:
                    admit_package(package)
                self.assertTrue(
                    any(d.code == "SCHEMA_INVALID" for d in ctx.exception.diagnostics)
                )

    def test_legacy_v16_v17_hints_remain_accepted_but_are_not_forwarded(self):
        for version in ("1.6", "1.7"):
            with self.subTest(version=version):
                package = story(version)
                package["nodes"][0]["steps"][0]["presentation"] = {
                    "color": "green",
                    "legacy_custom": "accepted old hint",
                }
                session = new_session(
                    admit_package(package), session_id="legacy", seed="2" * 64
                )
                view = reach_node(session)
                self.assertNotIn("presentation", view["content"])
                self.assertNotIn("legacy_custom", json.dumps(view))
                self.assertEqual(session.observe(), view)

    def test_auto_policy_is_only_hint_not_an_engine_trigger(self):
        package = story()
        package["nodes"][0]["steps"][0]["presentation"] = {
            "advance": {"mode": "auto", "delay_ms": 400},
            "reveal": {"mode": "instant"},
        }
        session = new_session(admit_package(package), session_id="auto", seed="9" * 64)
        view = reach_node(session)
        snapshot = session.export()
        self.assertEqual(view["content"]["presentation"]["advance"]["mode"], "auto")
        self.assertEqual(view["actions"][0]["kind"], "advance")
        for _ in range(30):
            self.assertEqual(session.observe(), view)
        self.assertEqual(session.export(), snapshot)

    def test_public_contract_and_canonical_distribution(self):
        package = story()
        package["nodes"][0]["steps"][0]["presentation"] = direction()
        admitted = admit_package(package)
        self.assertEqual(
            admitted.materialize()["nodes"][0]["steps"][0]["presentation"],
            direction(),
        )
        session = new_session(admitted, session_id="m2", seed="1" * 64)
        view = reach_node(session)
        validator = Validator()
        self.assertTrue(validator.use_version("1.8"))
        self.assertTrue(validator.check_schema("observe", view), validator.issues)
        self.assertTrue(
            validator.check_schema("session", session.export()), validator.issues
        )
        self.assertEqual(admit_package(admitted.materialize()).digest, admitted.digest)
