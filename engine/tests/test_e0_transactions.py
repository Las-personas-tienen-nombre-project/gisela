"""E0-T: las proyecciones deben construirse ANTES del commit."""

import copy
from unittest import TestCase, mock

from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import EngineFailure, new_session, restore_session
from gisela.engine.tests.test_h34a_values import ready, send
from gisela.engine.tests.test_pending import (
    PACKAGE,
    before_choice,
)
from gisela.engine.tests.test_pending import (
    send as pending_send,
)
from gisela.engine.tests.test_traits_alberto_v13 import fixture
from gisela.engine.world_base import WorldError


class CommitBoundary(TestCase):
    def test_e0_t01_rejected_projection_preserves_state(self):
        _, session = ready()
        initial = session.export()
        with mock.patch.object(
            session,
            "_project_state",
            side_effect=WorldError("INVALID_STATE", "proyección falla"),
        ):
            response = send(session, "guardar")
        self.assertEqual(response["error"]["code"], "INVALID_STATE")
        self.assertEqual(session.export(), initial)

    def test_e0_t02_pending_projection_failure_is_atomic(self):
        session = new_session(admit_package_file(PACKAGE))
        before_choice(session)
        initial = session.export()
        with mock.patch.object(
            session,
            "_project_state",
            side_effect=WorldError("INVALID_STATE", "proyección falla"),
        ):
            result = pending_send(session, "choose_prestar")
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.export(), initial)

    def test_e0_t03_cancel_projection_failure_is_atomic(self):
        session = new_session(admit_package_file(PACKAGE))
        before_choice(session)
        pending_send(session, "choose_prestar")
        initial = session.export()
        with mock.patch.object(
            session,
            "_project_state",
            side_effect=WorldError("INVALID_STATE", "proyección falla"),
        ):
            result = pending_send(session, "cancel_pending")
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.export(), initial)

    def test_e0_t04_invalid_projection_schema_prevents_commit(self):
        _, session = ready()
        initial = session.export()
        view = session.observe()
        chosen = next(a for a in view["actions"] if a["id"] == "guardar")
        request = {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": chosen["action_id"],
        }
        with (
            mock.patch.object(session, "observe", return_value=view),
            mock.patch(
                "gisela.engine.runtime.project_observe",
                return_value={"status": "node", "actions": []},
            ),
        ):
            result = session.act(request)
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.export(), initial)

    def test_e0_t06_restore_uses_frozen_snapshot_copy(self):
        admitted, session = ready()
        original = session.export()
        expected = copy.deepcopy(original)
        inherited = Validator.validate_session

        def mutate(*args, **kwargs):
            result = inherited(*args, **kwargs)
            original["revision"] += 77
            return result

        with mock.patch.object(Validator, "validate_session", new=mutate):
            restored = restore_session(admitted, original)
        self.assertEqual(restored.export(), expected)

    def test_e0_t07_restore_rejects_unprojectable_snapshot(self):
        admitted, session = ready()
        with (
            mock.patch(
                "gisela.engine.runtime.project_observe",
                return_value={"content": "invalid"},
            ),
            self.assertRaises(EngineFailure) as failure,
        ):
            restore_session(admitted, session.export())
        self.assertEqual(failure.exception.code, "RESTORE_MISMATCH")

    def test_e0_t08_act_chooses_session_schema_version(self):
        _, session = ready(fixture())
        calls = []
        inherited = Validator.use_version

        def capture(obj, version):
            calls.append(version)
            return inherited(obj, version)

        with mock.patch.object(Validator, "use_version", new=capture):
            self.assertEqual(send(session, "guardar")["status"], "ok")
        self.assertIn("1.3", calls)

    def test_e0_t05_read_only_projection_is_pure(self):
        admitted, session = ready()
        initial = session.export()
        self.assertEqual(session.observe(), session.observe())
        self.assertEqual(
            restore_session(admitted, initial).observe(), session.observe()
        )
        self.assertEqual(session.export(), initial)
