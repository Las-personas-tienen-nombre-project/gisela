"""PA-001 PT-02R: atomicidad y recuperación tras fallo causal anidado."""

import copy
import unittest

from gisela.engine.tests.test_h34a_values import ready, send
from gisela.engine.tests.test_h34c_effects import chosen, grant, package
from gisela.engine.tests.test_pa001_differential_restore import roundtrip


class ErrorRecovery(unittest.TestCase):
    def assert_same(self, a, b):
        self.assertEqual(a.export(), b.export())
        self.assertEqual(a.observe(), b.observe())

    def test_nested_effect_error_is_atomic_across_restore_and_retry(self):
        pkg = package(
            stacking="unique_per_target",
            behavior={"apply": [{"op": "record_fact", "fact": "aplicado"}]},
        )
        pkg = chosen(pkg, [grant("valor_01"), grant("valor_02")])
        admitted, a = ready(pkg)
        b = roundtrip(admitted, a)
        baseline = copy.deepcopy(a.export())
        for _ in range(2):
            for session in (a, b):
                result = send(session, "prestar")
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["error"]["code"], "EFFECT_ALREADY_ACTIVE")
                self.assertEqual(session.export(), baseline)
            b = roundtrip(admitted, b)
            self.assert_same(a, b)
        for session in (a, b):
            self.assertEqual(send(session, "guardar")["status"], "ok")
        self.assert_same(a, b)
        self.assertEqual(a.export()["world"]["effects"], [])
        self.assertFalse(
            any(f["fact"] == "aplicado" for f in a.export()["history"]["facts"])
        )

    def test_reaction_conflict_is_atomic_and_other_choice_recovers(self):
        pkg = package()
        pkg["rules"] = [
            {
                "id": "reacciona_a",
                "trigger": {"on": "fact_recorded", "fact": "despedida"},
                "effects": [
                    {
                        "op": "set",
                        "target": {"var": {"scope": "session", "key": "choque"}},
                        "value": {"literal": True},
                    }
                ],
            },
            {
                "id": "reacciona_b",
                "trigger": {"on": "fact_recorded", "fact": "despedida"},
                "effects": [
                    {
                        "op": "set",
                        "target": {"var": {"scope": "session", "key": "choque"}},
                        "value": {"literal": False},
                    }
                ],
            },
        ]
        pkg["manifest"]["variables"].append(
            {"scope": "session", "id": "choque", "type": "boolean", "initial": False}
        )
        pkg["initial_state"]["session_variables"]["choque"] = False
        pkg = chosen(pkg, [{"op": "record_fact", "fact": "despedida"}])
        admitted, a = ready(pkg)
        b = roundtrip(admitted, a)
        before = copy.deepcopy(a.export())
        for session in (a, b):
            result = send(session, "prestar")
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error"]["code"], "REACTION_CONFLICT")
            self.assertEqual(session.export(), before)
        b = roundtrip(admitted, b)
        for session in (a, b):
            self.assertEqual(send(session, "guardar")["status"], "ok")
        self.assert_same(a, b)
