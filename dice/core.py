"""Evaluaciones reproducibles con RNG inyectado y perfiles de juego."""
from __future__ import annotations
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA = json.loads((Path(__file__).parent / 'schemas/profile.schema.json').read_text())


class DiceError(ValueError):
    """Solicitud o perfil de evaluación inválido."""


def compile_profile(document: dict) -> dict:
    """Compila un perfil neutral y verifica los umbrales."""
    issues = list(Draft202012Validator(SCHEMA).iter_errors(document))
    if issues:
        raise DiceError(sorted(issues, key=lambda x: str(x.path))[0].message)
    bounds = [band['min'] for band in document['bands']]
    if bounds != sorted(set(bounds)):
        raise DiceError('Los umbrales deben estar ordenados y ser únicos')
    ids = [band['id'] for band in document['bands']]
    if len(ids) != len(set(ids)):
        raise DiceError('Los identificadores de resultado deben ser únicos')
    return copy.deepcopy(document)


def evaluate(profile: dict, request: dict, draw=None) -> dict:
    """Resuelve una solicitud neutral; nunca administra ni persiste el RNG."""
    if (not isinstance(request, dict) or set(request) != {'base', 'bonus', 'difficulty'}
            or any(type(v) is not int or abs(v) > 1000000 for v in request.values())):
        raise DiceError('Solicitud numérica inválida')
    profile = compile_profile(profile)
    mode = profile['mode']
    count = profile.get('count', 0)
    sides = profile.get('sides', 0)
    if mode != 'deterministic' and draw is None:
        raise DiceError('Falta fuente de aleatoriedad')
    rolls = []
    for _ in range(count if mode != 'deterministic' else 0):
        result = draw(sides)
        if type(result) is not int or not 1 <= result <= sides:
            raise DiceError('La fuente devolvió un dado fuera de rango')
        rolls.append(result)
    value = max(rolls) if mode == 'dice_pool' else sum(rolls)
    total = request['base'] + request['bonus'] + value - request['difficulty']
    # El primer intervalo también es la reserva inferior: cubre toda entrada
    # numérica admitida y no exige umbrales artificiales como -3000000.
    band = next((x['id'] for x in reversed(profile['bands']) if total >= x['min']),
                profile['bands'][0]['id'])
    return {'schema_version': 'dice.result.v1', 'profile': profile['id'],
            'rolls': rolls, 'die_value': value, 'base': request['base'],
            'bonus': request['bonus'], 'difficulty': request['difficulty'],
            'total': total, 'outcome': band}
