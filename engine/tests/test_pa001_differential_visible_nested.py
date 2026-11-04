"""PA-001 PT-02R: comparación de evaluaciones visibles y efectos causales anidados."""

import copy
import unittest

from gisela.contracts.admit_package import admit_package
from gisela.engine.runtime import new_session
from gisela.engine.tests.test_e2_evaluations import fixture, send, simple_node
from gisela.engine.tests.test_e3_visible import from_choice, v15
from gisela.engine.tests.test_h34a_values import ready
from gisela.engine.tests.test_h34a_values import send as send_effect
from gisela.engine.tests.test_h34c_effects import chosen, grant, package
from gisela.engine.tests.test_pa001_differential_restore import roundtrip


class DifferentialVisibleNested(unittest.TestCase):
    def verify(self, original, resumed):
        self.assertEqual(original.export(), resumed.export())
        self.assertEqual(original.observe(), resumed.observe())

    def test_visible_evaluation_chain_each_suspension(self):
        pkg = v15(simple_node(fixture()))
        second = copy.deepcopy(pkg["nodes"][0]["steps"][0])
        second["id"] = "second"
        pkg["nodes"][0]["steps"].insert(1, second)
        admitted = admit_package(pkg)
        original = new_session(admitted, seed="b" * 64)
        resumed = roundtrip(admitted, original)
        self.verify(original, resumed)
        for _ in range(2):
            self.assertEqual(send(original, "continue_evaluation")["status"], "ok")
            self.assertEqual(send(resumed, "continue_evaluation")["status"], "ok")
            resumed = roundtrip(admitted, resumed)
            self.verify(original, resumed)
        self.assertNotIn("pending_evaluation", original.export())

    def test_visible_choice_commit_once_after_restore(self):
        admitted = admit_package(from_choice())
        original = new_session(admitted, seed="c" * 64)
        resumed = roundtrip(admitted, original)
        for action in ("choose_intentar", "continue_evaluation"):
            self.assertEqual(send(original, action)["status"], "ok")
            self.assertEqual(send(resumed, action)["status"], "ok")
            resumed = roundtrip(admitted, resumed)
            self.verify(original, resumed)
        self.assertEqual(
            len(original.export()["history"]["executions"][0]["selected_options"]), 1
        )

    def test_nested_effect_and_reaction_equivalence(self):
        pkg = package(behavior={"apply": [{"op": "record_fact", "fact": "aplicado"}]})
        pkg["rules"] = [
            {
                "id": "reacciona",
                "trigger": {"on": "fact_recorded", "fact": "despedida"},
                "effects": [grant("valor_01")],
            }
        ]
        pkg = chosen(pkg, [{"op": "record_fact", "fact": "despedida"}])
        admitted, original = ready(pkg)
        resumed = roundtrip(admitted, original)
        self.verify(original, resumed)
        self.assertEqual(send_effect(original, "prestar")["status"], "ok")
        self.assertEqual(send_effect(resumed, "prestar")["status"], "ok")
        resumed = roundtrip(admitted, resumed)
        self.verify(original, resumed)
        facts = [f["fact"] for f in original.export()["history"]["facts"]]
        self.assertEqual(facts.count("despedida"), 1)
        self.assertEqual(facts.count("aplicado"), 1)
        self.assertEqual(len(original.export()["world"]["effects"]), 1)
