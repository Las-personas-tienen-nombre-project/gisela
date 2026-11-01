"""PA-001 PT-02R: entradas inválidas y continuación válida tras restauración."""

import copy
import unittest

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session
from gisela.engine.tests.test_e2_evaluations import fixture, send, simple_node
from gisela.engine.tests.test_e3_visible import from_choice, v15
from gisela.engine.tests.test_h2_closure import PACKAGE, SEED, reach_choice, with_roll
from gisela.engine.tests.test_pa001_differential_restore import roundtrip


class InvalidPendingRecovery(unittest.TestCase):
    def assert_identical(self, a, b):
        self.assertEqual(a.export(), b.export())
        self.assertEqual(a.observe(), b.observe())

    def test_invalid_visible_continue_then_valid_after_restore(self):
        admitted = admit_package(v15(simple_node(fixture())))
        continuous = new_session(admitted, seed="d" * 64)
        restored = roundtrip(admitted, continuous)
        baseline = copy.deepcopy(continuous.export())
        for session in (continuous, restored):
            for invalid in ("advance", "cancel_pending", "continue_evaluation_fake"):
                result = send(session, invalid)
                self.assertEqual(result["status"], "error")
                self.assertEqual(result["error"]["code"], "INVALID_ACTION")
                self.assertEqual(session.export(), baseline)
        restored = roundtrip(admitted, restored)
        for session in (continuous, restored):
            self.assertEqual(send(session, "continue_evaluation")["status"], "ok")
        self.assert_identical(continuous, restored)

    def test_invalid_visible_choice_response_then_valid(self):
        admitted = admit_package(from_choice())
        continuous = new_session(admitted, seed="e" * 64)
        restored = roundtrip(admitted, continuous)
        for session in (continuous, restored):
            self.assertEqual(send(session, "choose_intentar")["status"], "ok")
        pending = copy.deepcopy(continuous.export())
        for session in (continuous, restored):
            self.assertEqual(
                send(session, "choose_intentar")["error"]["code"], "INVALID_ACTION"
            )
            self.assertEqual(
                send(session, "cancel_pending")["error"]["code"], "INVALID_ACTION"
            )
            self.assertEqual(session.export(), pending)
        restored = roundtrip(admitted, restored)
        for session in (continuous, restored):
            self.assertEqual(send(session, "continue_evaluation")["status"], "ok")
        self.assert_identical(continuous, restored)
        self.assertEqual(
            len(continuous.export()["history"]["executions"][0]["selected_options"]), 1
        )

    def test_invalid_pending_resolution_does_not_change_rng_then_valid(self):
        admitted = admit_package(with_roll(admit_package_file(PACKAGE).materialize()))
        continuous = new_session(admitted, seed=SEED)
        reach_choice(continuous)
        restored = roundtrip(admitted, continuous)
        for session in (continuous, restored):
            self.assertEqual(send(session, "choose_prestar")["status"], "ok")
        pending = copy.deepcopy(continuous.export())
        for session in (continuous, restored):
            for invalid in ("resolve_hab_999", "advance", "choose_guardar"):
                result = send(session, invalid)
                self.assertEqual(result["error"]["code"], "INVALID_ACTION")
                self.assertEqual(session.export(), pending)
        restored = roundtrip(admitted, restored)
        for session in (continuous, restored):
            self.assertEqual(send(session, "resolve_hab_01")["status"], "ok")
        self.assert_identical(continuous, restored)
        self.assertEqual(continuous.export()["rng"]["counter"], 1)
