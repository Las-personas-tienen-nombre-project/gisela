"""Verifica la matriz E3 contra pruebas ejecutables y metadatos obligatorios."""

from __future__ import annotations

import json
from pathlib import Path

from verify_e0_invariants import methods

ROOT = Path(__file__).resolve().parents[1]
TEST = "gisela/engine/tests/test_e3_visible.py"
REGISTRY = ROOT / "docs/operatives/E3_INVARIANTES_TRAZABILIDAD.json"


def verify() -> list[str]:
    data = json.loads(REGISTRY.read_text(encoding="utf8"))
    issues = []
    if data.get("schema_version") != "gisela.e3.invariants.v1":
        issues.append("Matriz con versión incorrecta")
    existing = {m for m in methods(ROOT / TEST) if m.startswith("E3Visible.test_")}
    seen, covered = set(), set()
    for item in data.get("invariants", []):
        identifier = item.get("id")
        if (
            identifier in seen
            or item.get("status") != "enforced"
            or item.get("stage") != "E3"
            or not all(
                item.get(k) for k in ("statement", "decision", "subsystem", "tests")
            )
        ):
            issues.append("Invariante inválida: " + str(identifier))
        seen.add(identifier)
        for anchor in item.get("tests", []):
            prefix, _, method = anchor.partition("::E3Visible.")
            if prefix != TEST or "E3Visible." + method not in existing:
                issues.append("Prueba ausente: " + anchor)
            covered.add("E3Visible." + method)
    issues.extend(
        "Prueba sin invariante: " + name for name in sorted(existing - covered)
    )
    return issues


if __name__ == "__main__":
    problems = verify()
    for item in problems:
        print("ERROR:", item)
    if not problems:
        print("OK: E3; invariantes y pruebas enlazadas")
    raise SystemExit(int(bool(problems)))
