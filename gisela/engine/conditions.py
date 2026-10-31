"""Evaluación de expresiones y condiciones declaradas por el autor."""
from __future__ import annotations
from .world_base import find, var_access, WorldError


def value(state: dict, expression: dict, definitions=None):
    """Lee literales, variables, turno o reloj sin mutar el mundo."""
    if 'literal' in expression:
        return expression['literal']
    if 'var' in expression:
        owner, key = var_access(state, expression['var'])
        return owner[key]
    if 'property' in expression or 'relationship' in expression or 'stat' in expression:
        from .world_values import read
        return read(state, expression, definitions)
    if 'turn' in expression:
        return state['turn']
    if 'clock' in expression:
        return state['world_time']
    raise WorldError('UNSUPPORTED_FORMAT', 'Expresión todavía no disponible')


def _knowledge(state: dict, condition: dict) -> bool:
    """Consulta conocimientos y creencias sin inferir hechos históricos."""
    if 'knows' in condition:
        query = condition['knows']
        return query['fact'] in find(state, 'characters', query['character']).get('knowledge', [])
    query = condition['believes']
    return (find(state, 'characters', query['character']).get('beliefs', {})
            .get(query['claim']) is query['value'])


def _skill(state: dict, condition: dict) -> bool:
    """Comprueba una carta de habilidad y la zona autorizada."""
    query = condition['has_skill']
    find(state, 'characters', query['character'])
    return any(item['character'] == query['character'] and item['card'] == query['skill']
               and (query['zone'] == 'either' or item['zone'] == query['zone'])
               for item in state['world']['skills'])


def _compare(state: dict, query: dict, definitions=None) -> bool:
    """Compara usando el lenguaje común y traduce errores del dominio."""
    from narrative_conditions import compare
    try:
        return compare(value(state, query['left'], definitions),
                       value(state, query['right'], definitions), query['op'])
    except ValueError as exc:
        raise WorldError('INVALID_STATE', str(exc)) from exc



def _leaf(state: dict, cond: dict, definitions=None) -> bool:
    """Resuelve solo predicados del mundo de GISELA/ALBERTO."""
    if 'has_trait' in cond:
        from .world_traits import query
        return query(state, cond['has_trait'], definitions.traits)
    if 'has_fact' in cond:
        return any(item['fact'] == cond['has_fact'] for item in state['history']['facts'])
    if 'knows' in cond or 'believes' in cond:
        return _knowledge(state, cond)
    if 'has_skill' in cond:
        return _skill(state, cond)
    if 'has_effect' in cond:
        query = cond['has_effect']
        return any(item['target'] == query['target'] and item['card'] == query['effect']
                   for item in state['world']['effects'])
    if 'owns' in cond:
        return find(state, 'objects', cond['owns']['object']).get('owner') == cond['owns']['owner']
    if 'at_location' in cond:
        return find(state, 'characters', cond['at_location']['character'])['location'] == cond['at_location']['location']
    if 'compare' in cond:
        return _compare(state, cond['compare'], definitions)
    raise WorldError('UNSUPPORTED_FORMAT', 'Condición todavía no implementada')


def predicate(state: dict, cond: dict, definitions=None) -> bool:
    """Comparte la lógica booleana; ALBERTO interpreta sus propias consultas."""
    from narrative_conditions import evaluate
    return evaluate(cond, lambda item: _leaf(state, item, definitions))
