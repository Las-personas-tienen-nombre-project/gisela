"""Protección contra escrituras ocultas en callbacks de efectos reactivos."""
from __future__ import annotations
from .world import writable_key
from .world_base import WorldError


def _children(state: dict, operation: dict, definitions) -> list[dict]:
    """Localiza las consecuencias anidadas sin ejecutar ninguna de ellas."""
    if operation['op'] == 'apply_effect':
        return definitions.cards[operation['effect']].get('on_apply', [])
    if operation['op'] == 'end_effect':
        item = next((item for item in state['world']['effects']
                     if item['id'] == operation['effect_instance']), None)
        if item is not None:
            return definitions.cards[item['card']].get('on_expire', [])
    return []


def _walk(state: dict, operation: dict, definitions):
    """Recorre callbacks con un límite explícito de profundidad de trabajo."""
    yield operation, False
    pending = list(reversed(_children(state, operation, definitions)))
    count = 0
    while pending:
        count += 1
        if count > 32:
            raise WorldError('BUDGET_EXCEEDED', 'Demasiadas operaciones anidadas')
        child = pending.pop()
        yield child, True
        pending.extend(reversed(_children(state, child, definitions)))


def check(state: dict, rules: list[dict], definitions) -> None:
    """Rechaza dependencias ocultas de prioridad entre reglas distintas."""
    owners = {}
    for rule in rules:
        for operation in rule['effects']:
            for nested, indirect in _walk(state, operation, definitions):
                target = writable_key(nested)
                if target is None:
                    continue
                previous = owners.get(target)
                if previous and previous[0] != rule['id'] and (indirect or previous[1]):
                    raise WorldError('REACTION_CONFLICT',
                                     'Escrituras anidadas incompatibles entre reglas')
                owners[target] = (rule['id'], indirect)
