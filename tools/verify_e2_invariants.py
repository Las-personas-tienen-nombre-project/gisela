"""Verifica existencia y cobertura completa de pruebas de invariantes E2."""

from __future__ import annotations

import json
from pathlib import Path

from verify_e0_invariants import methods

ROOT = Path(__file__).resolve().parents[1]
TEST = "gisela/engine/tests/test_e2_evaluations.py"
REGISTRY = ROOT / "docs/operatives/E2_INVARIANTES_TRAZABILIDAD.json"


def verify() -> list[str]:
    """Rechaza IDs duplicados, test ausente o test E2 sin invariante."""
    data = json.loads(REGISTRY.read_text())
    problems = []
    if data.get("schema_version") != "gisela.e2.invariants.v1":
        problems.append("Versión de matriz E2 incorrecta")
    seen, covered = set(), set()
    existing = methods(ROOT / TEST)
    for item in data["invariants"]:
        identifier = item["id"]
        if (
            identifier in seen
            or item.get("stage") != "E2"
            or item.get("status") != "enforced"
        ):
            problems.append("Invariante repetida o sin cumplimiento: " + identifier)
        seen.add(identifier)
        if (
            not item.get("statement")
            or not item.get("decision")
            or not item.get("subsystem")
        ):
            problems.append("Invariante sin metadatos: " + identifier)
        for anchor in item.get("tests", []):
            name = anchor.split("::")[-1]
            if anchor != f"{TEST}::{name}" or name not in existing:
                problems.append("Prueba ausente o mal vinculada: " + anchor)
            covered.add(anchor)
    expected = {f"{TEST}::{name}" for name in existing if name.startswith("test_e2_")}
    problems.extend("Prueba sin invariante: " + x for x in sorted(expected - covered))
    return problems


def main() -> int:
    """Comprueba la trazabilidad y retorna error si es incompleta."""
    issues = verify()
    for item in issues:
        print("ERROR:", item)
    if not issues:
        print("OK: invariantes E2 ancladas en pruebas existentes")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
