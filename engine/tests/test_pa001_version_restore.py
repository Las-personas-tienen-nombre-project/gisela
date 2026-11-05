"""PA-001: restauración exacta por contrato; sin migración implícita."""

import copy
import unittest
from pathlib import Path

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.errors import EngineFailure
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.tests.test_e2_evaluations import fixture as hidden_v14
from gisela.engine.tests.test_e2_evaluations import simple_node
from gisela.engine.tests.test_traits_alberto_v13 import fixture as traits_v13

ROOT = Path(__file__).resolve().parents[2] / "packages"
CASES = (
    ("1.2", "h4_exploracion.package.json"),
    ("1.5", "h46b_central_clasificadora.package.json"),
)


class TestVersionedRestore(unittest.TestCase):
    def test_roundtrip_preserves_observation_and_state(self):
        for version, filename in CASES:
            with self.subTest(version=version):
                admitted = admit_package_file(ROOT / filename)
                original = new_session(admitted, seed="0" * 64)
                snapshot = original.export()
                self.assertEqual(snapshot["schema_version"], version)
                restored = restore_session(admitted, snapshot)
                self.assertEqual(restored.export(), snapshot)
                self.assertEqual(restored.observe(), original.observe())

    def test_rejects_foreign_package_digest(self):
        for version, filename in CASES:
            with self.subTest(version=version):
                admitted = admit_package_file(ROOT / filename)
                snapshot = new_session(admitted).export()
                tampered = copy.deepcopy(snapshot)
                tampered["package_digest"] = "f" * 64
                with self.assertRaises(EngineFailure):
                    restore_session(admitted, tampered)

    def test_rejects_foreign_schema_version(self):
        for version, filename in CASES:
            with self.subTest(version=version):
                admitted = admit_package_file(ROOT / filename)
                snapshot = new_session(admitted).export()
                tampered = copy.deepcopy(snapshot)
                tampered["schema_version"] = "1.5" if version != "1.5" else "1.4"
                with self.assertRaises(EngineFailure):
                    restore_session(admitted, tampered)

    def test_v13_traits_roundtrip_and_observation(self):
        """ADR-020: v1.3 conserva sus rasgos y proyección tras restaurar."""
        admitted = admit_package(traits_v13())
        original = new_session(admitted)
        snapshot = original.export()
        self.assertEqual(snapshot["schema_version"], "1.3")
        restored = restore_session(admitted, snapshot)
        self.assertEqual(restored.export(), snapshot)
        self.assertEqual(restored.observe(), original.observe())

    def test_v14_hidden_roundtrip_and_observation(self):
        """ADR-022: evaluación oculta v1.4 es ejecutable y restaurable."""
        admitted = admit_package(simple_node(hidden_v14(mode="deterministic")))
        original = new_session(admitted)
        snapshot = original.export()
        self.assertEqual(snapshot["schema_version"], "1.4")
        restored = restore_session(admitted, snapshot)
        self.assertEqual(restored.export(), snapshot)
        self.assertEqual(restored.observe(), original.observe())

    def test_v13_v14_restore_rejects_foreign_digest_and_version(self):
        """Identidad exacta de paquete y versión también para v1.3/v1.4."""
        for pkg in (traits_v13(), simple_node(hidden_v14(mode="deterministic"))):
            admitted = admit_package(pkg)
            original = new_session(admitted)
            snap = original.export()
            for field, invalid in (
                ("package_digest", "f" * 64),
                ("schema_version", "1.5"),
            ):
                with self.subTest(version=snap["schema_version"], field=field):
                    modified = copy.deepcopy(snap)
                    modified[field] = invalid
                    with self.assertRaises(EngineFailure):
                        restore_session(admitted, modified)

    def test_snapshots_cannot_cross_supported_versions(self):
        """PT-05: no se admite restauración cruzada entre 1.2 a 1.5."""
        admitted = [
            admit_package_file(ROOT / CASES[0][1]),
            admit_package(traits_v13()),
            admit_package(simple_node(hidden_v14(mode="deterministic"))),
            admit_package_file(ROOT / CASES[1][1]),
        ]
        snapshots = [new_session(package).export() for package in admitted]
        for index, package in enumerate(admitted):
            for other, snapshot in enumerate(snapshots):
                if index == other:
                    continue
                with self.subTest(target=index, origin=other):
                    with self.assertRaises(EngineFailure) as raised:
                        restore_session(package, snapshot)
                    self.assertEqual(raised.exception.code, "RESTORE_MISMATCH")

    def test_v14_exhausted_node_without_scene_has_engine_error(self):
        """ADR-001 a 017: fin sin escena debe fallar con error técnico tipado."""
        admitted = admit_package(hidden_v14(mode="deterministic"))
        with self.assertRaises(EngineFailure) as raised:
            new_session(admitted)
        self.assertEqual(raised.exception.code, "INVALID_STATE")

    def test_noninitial_exhausted_node_without_scene_is_typed_and_atomic(self):
        """H9: agotar un nodo observable tampoco depende de un KeyError de proyección."""
        admitted = admit_package(simple_node(hidden_v14(mode="deterministic")))
        session = new_session(admitted)
        before = session.export()
        view = session.observe()
        response = session.act(
            {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": "advance",
            }
        )
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "INVALID_STATE")
        self.assertEqual(
            response["error"]["message"], "Nodo agotado sin escena, transición ni final"
        )
        self.assertEqual(session.export(), before)

    def test_admitted_v14_e3_example_remains_not_executable(self):
        """Admisión estática no promete capacidad de ejecución."""
        admitted = admit_package_file(ROOT / "e1_reparacion_sin_jugador.package.json")
        self.assertEqual(admitted.materialize()["manifest"]["format_version"], "1.4")
        with self.assertRaises(EngineFailure) as raised:
            new_session(admitted)
        self.assertEqual(raised.exception.code, "UNSUPPORTED_FORMAT")
