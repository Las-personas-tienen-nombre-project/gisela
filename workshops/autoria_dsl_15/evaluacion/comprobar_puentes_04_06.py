"""Comprobación docente de TRAITS sobre la referencia de Unidad 4; no evalúa NPC ni entregas."""
from __future__ import annotations
import json
from pathlib import Path
from gisela.contracts.admit_package import admit_package
from gisela.engine.runtime import new_session
from gisela.engine.traits_dice_bridge import contribution_total

ROOT = Path(__file__).resolve().parents[1]
pkg = json.loads((ROOT / 'paquetes/04_progresivo/04_laboratorio.package.json').read_text())
s = new_session(admit_package(pkg))
before = s.export()
checks = [("defender_evasion", 'defender', ['evasion'], 2),
          ("actor_evasion", 'actor', ['evasion'], 0),
          ("defender_no_evasion", 'defender', ['physical_damage_reduction'], 0),
          ("defender_multiple_tags", 'defender', ['evasion', 'other'], 2)]
for title, role, tags, expected in checks:
    actual = contribution_total(s.export(), {'participants': [{'entity': 'parnecio', 'role': role}], 'tags': tags, 'slot': 'bonus'}, s._definitions)
    assert actual == expected, (title, actual, expected)
    print('OK TRAITS', title, actual)
assert before == s.export(), 'La consulta modificó el estado'
print('OK TRAITS consulta pura')
