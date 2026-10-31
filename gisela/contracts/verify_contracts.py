#!/usr/bin/env python3
"""GISELA v1.2 schema smoke checker (offline). Requires jsonschema, referencing.

Usage: python verify_contracts.py [path/to/package.json]
This checks JSON Schema syntax + shape, NOT the full semantic validator.
"""
import json
import pathlib
import sys

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = pathlib.Path(__file__).resolve().parent
schemas = {
    p.name.removesuffix('.schema.json'): json.loads(p.read_text(encoding='utf-8'))
    for p in ROOT.glob('*.schema.json')
}
for spec in schemas.values():
    Draft202012Validator.check_schema(spec)
registry = Registry().with_resources((spec['$id'], Resource.from_contents(spec)) for spec in schemas.values())


def validate(name, data):
    """Valida un ejemplo contra su schema registrado y comunica fallos."""
    validator = Draft202012Validator(schemas[name], registry=registry, format_checker=FormatChecker())
    errors = list(validator.iter_errors(data))
    if errors:
        for e in errors[:15]:
            print(f'{name}: {"/".join(str(x) for x in e.absolute_path) or "<root>"}: {e.message}', file=sys.stderr)
        raise SystemExit(1)


package_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'example.package.json'
from admit_package import admit_package_file, PackageRejected
try:
    admitted = admit_package_file(package_path)  # JSON estricto + estructura + semántica obligatorias
except PackageRejected as ex:
    for d in ex.diagnostics:
        print(f'{d.severity.upper()} {d.code} {d.path}: {d.message}', file=sys.stderr)
    raise SystemExit(1)
except (OSError, UnicodeError, ValueError) as ex:
    print(f'Paquete no legible: {ex}', file=sys.stderr)
    raise SystemExit(2)
package = admitted.materialize()
validate('package', package)

# Independent contract smoke tests with consistent, schematic values.
world_snapshot = {
    'revision': 1, 'world_time': '1998-08-13T19:00:00-04:00',
    'characters': [{'id': 'alberto', 'location': 'porteria', 'status': {'alert': True}}],
}
validate('world_snapshot', world_snapshot)
observe = {
    'session_id': 'fixture_01', 'revision': 2, 'world_revision': 1,
    'world_time': '1998-08-13T19:00:00-04:00', 'turn': 1,
    'scene': 'porteria_noche', 'status': 'node',
    'content': {'kind': 'choice', 'prompt': '¿Qué hace Alberto?'},
    'actions': [{'kind':'choose','action_id': 'choose_prestar', 'id': 'prestar', 'label': 'Prestar casete', 'enabled': True}],
    'actors': [{'id': 'gisela', 'name': 'Gisela'}],
}
validate('observe', observe)
assert 'world_snapshot' not in schemas['observe']['properties'], 'Snapshot privileged leaked through Observe'
validate('act', {'session_id': 'fixture_01', 'revision': 2, 'action_id': 'choose_prestar'})
validate('scoresheet', {
    'session_id': 'fixture_01', 'revision': 2, 'character': 'alberto',
    'stats': [{'name': k, 'base': 6, 'current': 6, 'modifier': 2, 'effective': 8} for k in
              ('strength', 'openness', 'fortune', 'intelligence', 'awareness')],
    'active_effects': [], 'hand': [], 'reserve': [],
})
validate('result', {'status': 'ok', 'revision': 2, 'view': observe})
validate('result', {'status': 'error', 'revision': 2, 'error':
                    {'code': 'STALE_PROJECTION', 'message': 'Old revision'}})

# Confirm unknown executable operations are forbidden.
import copy
bad = copy.deepcopy(package)
bad['nodes'][0]['steps'][0]['op'] = 'python'
validator = Draft202012Validator(schemas['package'], registry=registry)
assert not validator.is_valid(bad), 'Unknown operation accidentally accepted'
for path in (ROOT / 'examples').glob('*.json'):
    family = path.name.split('_')[0]
    assert family in ('session', 'observe'), f'Unknown fixture family: {path.name}'
    validate(family, json.loads(path.read_text(encoding='utf8')))
print(f'PASS: {len(schemas)} schema definitions; package + API contracts; {len(list((ROOT / "examples").glob("*.json")))} example snapshots; unknown operation rejected.')
print('NOTE: Paquete admitido estructural y semánticamente; sesiones y ejecución necesitan verificaciones adicionales.')
