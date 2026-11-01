"""P0/A3: admission and transactional validation stay separated."""

from pathlib import Path
from unittest import TestCase, mock

from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import new_session

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "gisela" / "packages" / "mvp_casete.package.json"


class AdmissionBoundary(TestCase):
    def test_admitted_package_schema_is_not_revalidated_by_action(self):
        admitted = admit_package_file(PACKAGE)
        calls = []
        inherited = Validator.check_schema

        def capture(instance, kind, document):
            calls.append(kind)
            return inherited(instance, kind, document)

        with mock.patch.object(Validator, "check_schema", new=capture):
            session = new_session(admitted)
            view = session.observe()
            action = next(item for item in view["actions"] if item["enabled"])
            result = session.act(
                {
                    "session_id": view["session_id"],
                    "revision": view["revision"],
                    "action_id": action["action_id"],
                }
            )
        self.assertEqual(result["status"], "ok")
        self.assertNotIn("package", calls)
        self.assertIn("session", calls)

    def test_public_validator_still_validates_package_schema(self):
        admitted = admit_package_file(PACKAGE)
        package = admitted.materialize()
        snapshot = new_session(admitted).export()
        calls = []
        inherited = Validator.check_schema

        def capture(instance, kind, document):
            calls.append(kind)
            return inherited(instance, kind, document)

        with mock.patch.object(Validator, "check_schema", new=capture):
            Validator().validate_session(snapshot, package, admitted.digest)
        self.assertIn("package", calls)
        self.assertIn("session", calls)


class InternalFailureDiagnostic(TestCase):
    def test_structural_internal_failure_is_logged_and_atomic(self):
        admitted = admit_package_file(PACKAGE)
        session = new_session(admitted)
        before = session.export()
        view = session.observe()
        action = next(item for item in view["actions"] if item["enabled"])
        request = {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": action["action_id"],
        }
        with (
            mock.patch.object(
                session, "_execute_source", side_effect=KeyError("engine_bug")
            ),
            self.assertLogs("gisela.engine.action_handler", level="ERROR") as logs,
        ):
            result = session.act(request)
        self.assertEqual(result["error"]["code"], "INVALID_STATE")
        self.assertEqual(result["error"]["message"], "Error interno de ejecución")
        self.assertIn("engine_bug", "\n".join(logs.output))
        self.assertEqual(session.export(), before)


class DiceCompiledProfileBoundary(TestCase):
    def test_gisela_reuses_compiled_dice_profile_during_evaluation(self):
        from tools.h46b_walkthrough import admitted, take

        session = new_session(admitted(), seed="0" * 64)
        take(session, "tomar_turno")
        take(session, "saludar")
        take(session, "ir_puesto_b")
        with mock.patch(
            "dice.core.compile_profile",
            side_effect=AssertionError("perfil DICE revalidado"),
        ):
            take(session, "probar_radio")
        self.assertGreater(session.export()["revision"], 6)
