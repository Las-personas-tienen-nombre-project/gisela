"""E1: comprueba cada invariante y la cobertura de todas sus pruebas nuevas."""

from __future__ import annotations

import json
from pathlib import Path

from verify_e0_invariants import methods

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/operatives/E1_INVARIANTES_TRAZABILIDAD.json"
TEST_FILE = "gisela/contracts/test_e1_evaluations_v14.py"


def verify() -> list[str]:
    """Anclajes ejecutables, invariantes no duplicadas y cobertura completa."""
    data = json.loads(REGISTRY.read_text())
    issues = []
    if data.get("schema_version") != "gisela.e1.invariants.v1":
        issues.append("Versión E1 incorrecta")
    ids, covered = set(), set()
    for entry in data["invariants"]:
        key = entry["id"]
        if key in ids or not entry.get("statement") or not entry.get("tests"):
            issues.append("Invariante repetida o incompleta: " + key)
        ids.add(key)
        if entry.get("stage") != "E1" or entry.get("status") != "enforced":
            issues.append("Etapa o estado inválido: " + key)
        for anchor in entry["tests"]:
            parts = anchor.split("::")
            if len(parts) != 2 or parts[0] != TEST_FILE:
                issues.append("Anclaje inesperado: " + anchor)
            elif parts[1] not in methods(ROOT / TEST_FILE):
                issues.append("Test inexistente: " + anchor)
            covered.add(anchor)
    expected = {TEST_FILE + "::" + name for name in methods(ROOT / TEST_FILE)}
    issues += [
        "Prueba E1 sin invariante: " + name for name in sorted(expected - covered)
    ]
    return issues


def main() -> int:
    """Regresa 1 ante drift de trazabilidad; sin alterar el repositorio."""
    issues = verify()
    for issue in issues:
        print("ERROR:", issue)
    if not issues:
        print("OK: invariantes E1 ancladas en pruebas reales")
    return int(bool(issues))


if __name__ == "__main__":
    raise SystemExit(main())
