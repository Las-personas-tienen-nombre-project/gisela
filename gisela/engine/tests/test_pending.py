"""Pruebas de H2. Ningún estado provisional es autoritativo."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import EngineFailure, new_session, restore_session

PACKAGE = Path(__file__).resolve().parents[2] / "packages" / "h2_descarte.package.json"


def send(session, action_id):
    view = session.observe()
    return session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": action_id,
        }
    )


def before_choice(session):
    for _ in range(2):
        result = send(session, "advance")
        if result["status"] != "ok":
            raise AssertionError(result)
    if session.observe()["content"]["kind"] != "choice":
        raise AssertionError("No se alcanzó la elección")


class PendingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admitted = admit_package_file(PACKAGE)

    def setUp(self):
        self.session = new_session(self.admitted)
        before_choice(self.session)

    def test_reaction_suspends_without_publishing_changes(self):
        base = self.session.export()
        result = send(self.session, "choose_prestar")
        self.assertEqual(result["status"], "ok")
        snapshot = self.session.export()
        self.assertEqual(snapshot["world"], base["world"])
        self.assertEqual(snapshot["narrative"], base["narrative"])
        self.assertEqual(snapshot["history"], base["history"])
        self.assertEqual(snapshot["rng"], base["rng"])
        self.assertEqual(snapshot["identity"], base["identity"])
        self.assertEqual(snapshot["world_revision"], base["world_revision"])
        self.assertEqual(snapshot["revision"], base["revision"] + 1)
        self.assertEqual(
            snapshot["pending_transaction"]["source"]["kind"], "choice_option"
        )
        view = self.session.observe()
        self.assertEqual(view["content"]["kind"], "pending_transaction")
        self.assertEqual(
            {x["kind"] for x in view["actions"]}, {"resolve_pending", "cancel_pending"}
        )
        self.assertFalse(list(Validator().schemas["session"].iter_errors(snapshot)))
        self.assertFalse(list(Validator().schemas["observe"].iter_errors(view)))

    def test_confirmed_only_after_answer(self):
        send(self.session, "choose_prestar")
        result = send(self.session, "resolve_hab_01")
        self.assertEqual(result["status"], "ok")
        final = self.session.export()
        self.assertNotIn("pending_transaction", final)
        self.assertTrue(final["narrative"]["session_variables"]["gisela_reacciono"])
        self.assertEqual(final["world"]["objects"][0]["owner"], "gisela")
        self.assertEqual(len(final["history"]["facts"]), 1)
        self.assertEqual(len(final["history"]["trace"]), 2)
        self.assertEqual(final["identity"]["next_sequence"], 2)
        self.assertIn("skill_000001", final["identity"]["used_instance_ids"])
        self.assertEqual(
            {s["card"] for s in final["world"]["skills"]},
            {"habilidad_b", "habilidad_c"},
        )
        self.assertEqual(final["world_revision"], 1)
        self.assertFalse(
            [
                i
                for i in Validator().validate_session(
                    final, self.admitted.materialize()
                )
                if i.severity == "error"
            ]
        )

    def test_cancel_does_not_change_confirmed_state(self):
        base = self.session.export()
        send(self.session, "choose_prestar")
        result = send(self.session, "cancel_pending")
        self.assertEqual(result["status"], "ok")
        final = self.session.export()
        self.assertNotIn("pending_transaction", final)
        self.assertEqual(final["world"], base["world"])
        self.assertEqual(final["narrative"], base["narrative"])
        self.assertEqual(final["history"], base["history"])
        self.assertEqual(final["rng"], base["rng"])
        self.assertEqual(final["identity"], base["identity"])
        self.assertEqual(final["world_revision"], base["world_revision"])
        self.assertEqual(final["cursor"], base["cursor"])
        self.assertEqual(final["revision"], base["revision"] + 2)
        self.assertEqual(self.session.observe()["content"]["kind"], "choice")
        self.assertEqual(send(self.session, "choose_guardar")["status"], "ok")

    def test_resolving_unoffered_action_cannot_change_state(self):
        send(self.session, "choose_prestar")
        snapshot = self.session.export()
        for action in (
            "advance",
            "choose_guardar",
            "resolve_skill_fake",
            "resolve_hab_999",
        ):
            failure = send(self.session, action)
            self.assertEqual(failure["error"]["code"], "INVALID_ACTION")
            self.assertEqual(self.session.export(), snapshot)
        old = {
            "session_id": snapshot["session_id"],
            "revision": snapshot["revision"] - 1,
            "action_id": "resolve_hab_01",
        }
        self.assertEqual(self.session.act(old)["error"]["code"], "STALE_PROJECTION")
        self.assertEqual(self.session.export(), snapshot)

    def test_restore_pending_and_continue_matches_uninterrupted(self):
        send(self.session, "choose_prestar")
        snapshot = json.loads(json.dumps(self.session.export(), ensure_ascii=False))
        restored = restore_session(self.admitted, snapshot)
        self.assertEqual(restored.observe(), self.session.observe())
        self.assertEqual(send(restored, "resolve_hab_02")["status"], "ok")
        self.assertEqual(send(self.session, "resolve_hab_02")["status"], "ok")
        self.assertEqual(restored.export(), self.session.export())

    def test_tampered_request_is_not_restorable(self):
        send(self.session, "choose_prestar")
        saved = self.session.export()
        saved["pending_transaction"]["request"]["options"] = ["hab_02"]
        with self.assertRaises(EngineFailure) as failure:
            restore_session(self.admitted, saved)
        self.assertEqual(failure.exception.code, "RESTORE_MISMATCH")

    def test_tampered_origin_is_not_restorable(self):
        send(self.session, "choose_prestar")
        saved = self.session.export()
        saved["pending_transaction"]["origin"] = "mandatory"
        with self.assertRaises(EngineFailure) as failure:
            restore_session(self.admitted, saved)
        self.assertEqual(failure.exception.code, "RESTORE_MISMATCH")

    def test_two_consecutive_auxiliary_decisions_replay(self):
        pkg = self.admitted.materialize()
        pkg["rules"][-1]["effects"].append(
            {
                "op": "grant_skill",
                "character": "gisela",
                "skill": "habilidad_d",
                "overflow": "require_choice",
            }
        )
        admitted = admit_package(pkg)
        s = new_session(admitted)
        before_choice(s)
        self.assertEqual(send(s, "choose_prestar")["status"], "ok")
        self.assertEqual(send(s, "resolve_hab_01")["status"], "ok")
        intermediate = s.export()
        self.assertEqual(
            intermediate["pending_transaction"]["request"]["request_id"],
            "auxiliar_0002",
        )
        self.assertEqual(
            intermediate["pending_transaction"]["answers"],
            [{"request_id": "auxiliar_0001", "option_id": "hab_01"}],
        )
        self.assertFalse(
            intermediate["narrative"]["session_variables"]["gisela_reacciono"]
        )
        self.assertEqual(intermediate["identity"]["next_sequence"], 1)
        restored = restore_session(admitted, json.loads(json.dumps(intermediate)))
        self.assertEqual(restored.observe(), s.observe())
        for target in (s, restored):
            self.assertEqual(send(target, "resolve_hab_02")["status"], "ok")
        self.assertEqual(restored.export(), s.export())
        self.assertEqual(
            {item["card"] for item in s.export()["world"]["skills"]},
            {"habilidad_c", "habilidad_d"},
        )
        self.assertEqual(s.export()["identity"]["next_sequence"], 3)

    def test_forged_old_answer_rejected(self):
        pkg = self.admitted.materialize()
        pkg["rules"][-1]["effects"].append(
            {
                "op": "grant_skill",
                "character": "gisela",
                "skill": "habilidad_d",
                "overflow": "require_choice",
            }
        )
        admitted = admit_package(pkg)
        s = new_session(admitted)
        before_choice(s)
        send(s, "choose_prestar")
        send(s, "resolve_hab_01")
        snapshot = s.export()
        snapshot["pending_transaction"]["answers"][0]["option_id"] = "fantasma"
        with self.assertRaises(EngineFailure):
            restore_session(admitted, snapshot)

    def test_automatic_step_is_mandatory(self):
        pkg = self.admitted.materialize()
        pkg["nodes"][0]["steps"].insert(
            1,
            {
                "id": "concesion_obligatoria",
                "op": "effect",
                "effects": [
                    {
                        "op": "grant_skill",
                        "character": "gisela",
                        "skill": "habilidad_c",
                        "overflow": "require_choice",
                    }
                ],
            },
        )
        admitted = admit_package(pkg)
        s = new_session(admitted)
        original = s.export()
        self.assertEqual(send(s, "advance")["status"], "ok")
        pending = s.export()
        self.assertEqual(pending["pending_transaction"]["origin"], "mandatory")
        self.assertEqual(pending["world"], original["world"])
        self.assertEqual(
            {a["kind"] for a in s.observe()["actions"]}, {"resolve_pending"}
        )
        self.assertEqual(send(s, "cancel_pending")["error"]["code"], "INVALID_ACTION")
        restored = restore_session(admitted, s.export())
        self.assertEqual(send(restored, "resolve_hab_01")["status"], "ok")
        self.assertEqual(send(s, "resolve_hab_01")["status"], "ok")
        self.assertEqual(restored.export(), s.export())

    def test_conflict_after_answer_keeps_pending_for_cancel(self):
        pkg = self.admitted.materialize()
        pkg["manifest"]["facts"].append("segundo_hecho")
        pkg["manifest"]["variables"].append(
            {
                "scope": "session",
                "id": "revision_aux",
                "type": "boolean",
                "initial": False,
            }
        )
        pkg["initial_state"]["session_variables"]["revision_aux"] = False
        pkg["rules"][-1]["effects"].append(
            {"op": "record_fact", "fact": "segundo_hecho"}
        )
        for i, value in enumerate((True, False)):
            pkg["rules"].append(
                {
                    "id": f"conflicto_{i}",
                    "trigger": {"on": "fact_recorded", "fact": "segundo_hecho"},
                    "effects": [
                        {
                            "op": "set",
                            "target": {
                                "var": {"scope": "session", "key": "revision_aux"}
                            },
                            "value": {"literal": value},
                        }
                    ],
                }
            )
        admitted = admit_package(pkg)
        s = new_session(admitted)
        before_choice(s)
        send(s, "choose_prestar")
        saved = s.export()
        failure = send(s, "resolve_hab_01")
        self.assertEqual(failure["error"]["code"], "REACTION_CONFLICT")
        self.assertEqual(s.export(), saved)
        self.assertEqual(send(s, "cancel_pending")["status"], "ok")

    def test_two_rules_granting_to_same_character_conflict_before_wait(self):
        pkg = self.admitted.materialize()
        pkg["rules"].append(
            {
                "id": "aprendizaje_concurrente",
                "trigger": {"on": "fact_recorded", "fact": "alberto_presto_casete"},
                "effects": [
                    {
                        "op": "grant_skill",
                        "character": "gisela",
                        "skill": "habilidad_d",
                        "overflow": "require_choice",
                    }
                ],
            }
        )
        admitted = admit_package(pkg)
        s = new_session(admitted)
        before_choice(s)
        saved = s.export()
        failure = send(s, "choose_prestar")
        self.assertEqual(failure["error"]["code"], "REACTION_CONFLICT")
        self.assertEqual(s.export(), saved)

    def test_no_legal_discard_rolls_back_without_pending(self):
        pkg = self.admitted.materialize()
        pkg["initial_state"]["capacities"] = [
            {"character": "gisela", "hand": 0, "reserve": 0}
        ]
        pkg["initial_state"]["skills"] = []
        admitted = admit_package(pkg)
        s = new_session(admitted)
        before_choice(s)
        saved = s.export()
        response = send(s, "choose_prestar")
        self.assertEqual(response["error"]["code"], "NO_LEGAL_CHOICE")
        self.assertEqual(s.export(), saved)

    def test_without_overflow_policy_rejects_atomic_grant(self):
        pkg = self.admitted.materialize()
        pkg["rules"][-1]["effects"][0].pop("overflow")
        admitted = admit_package(pkg)
        s = new_session(admitted)
        before_choice(s)
        saved = s.export()
        response = send(s, "choose_prestar")
        self.assertEqual(response["error"]["code"], "CAPACITY_EXCEEDED")
        self.assertEqual(s.export(), saved)

    def test_discarded_ids_are_not_reused(self):
        send(self.session, "choose_prestar")
        send(self.session, "resolve_hab_01")
        ids = self.session.export()["identity"]["used_instance_ids"]
        self.assertIn("hab_01", ids)
        self.assertIn("skill_000001", ids)


if __name__ == "__main__":
    unittest.main()
