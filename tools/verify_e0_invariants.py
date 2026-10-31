#!/usr/bin/env python3
"""Verifica que las invariantes E0 están declaradas y ancladas en tests reales."""
from __future__ import annotations
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'docs/operatives/E0_INVARIANTES_TRAZABILIDAD.json'
NEW_TESTS = ('dice/tests/test_dice_hardening.py',
             'gisela/engine/tests/test_e0_transactions.py',
             'gisela/engine/tests/test_e0_gateway.py',
             'gisela/engine/tests/test_e0_error_contracts.py')


def methods(path: Path) -> set[str]:
    """Obtiene Class.method declarados directamente en la fuente de test."""
    tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
    return {cls.name + '.' + item.name for cls in tree.body
            if isinstance(cls, ast.ClassDef) for item in cls.body
            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_')}


def verify() -> list[str]:
    """Comprueba IDs, etapas, anclajes y cobertura de todos los tests E0."""
    data = json.loads(REGISTRY.read_text(encoding='utf-8'))
    issues = []
    if data.get('schema_version') != 'gisela.e0.invariants.v1':
        issues.append('Versión de matriz desconocida')
    ids, covered = set(), set()
    for item in data['invariants']:
        key = item['id']
        if key in ids or not item.get('statement') or not item.get('tests'):
            issues.append('Invariante incompleta o duplicada: ' + key)
        ids.add(key)
        if item.get('status') != 'enforced' or item.get('stage') not in ('E0.1','E0.2','E0.3','E0.4'):
            issues.append('Estado o etapa inválido: ' + key)
        for anchor in item['tests']:
            parts = anchor.split('::')
            if len(parts) != 2:
                issues.append('Anclaje inválido: ' + anchor)
                continue
            path, name = parts
            full = (ROOT / path).resolve()
            if not full.is_relative_to(ROOT) or not full.is_file() or name not in methods(full):
                issues.append('Test inexistente: ' + anchor)
            covered.add(anchor)
    for path in NEW_TESTS:
        missing = {path + '::' + name for name in methods(ROOT/path)} - covered
        issues.extend('Test E0 sin invariante: ' + name for name in sorted(missing))
    return issues


def main() -> int:
    """Herramienta de integración que devuelve código de salida verificable."""
    issues = verify()
    for issue in issues:
        print('ERROR:', issue)
    if not issues:
        print('OK: invariantes E0, anclajes existentes y tests nuevos registrados')
    return int(bool(issues))


if __name__ == '__main__':
    raise SystemExit(main())
