"""Mutaciones de entidades de ALBERTO sin autoridad de confirmación.

Las funciones solo trabajan sobre el borrador entregado por GISELA.
"""
from __future__ import annotations
from .world_base import find, instance, WorldError


def move_character(state: dict, effect: dict) -> list[dict]:
    """Cambia un personaje de lugar, sin alterar la escena presentada."""
    character = find(state, 'characters', effect['character'])
    find(state, 'locations', effect['location'])
    character['location'] = effect['location']
    return []


def learn_fact(state: dict, effect: dict) -> list[dict]:
    """Agrega conocimiento individual sin registrar una ocurrencia histórica."""
    character = find(state, 'characters', effect['character'])
    knowledge = character.setdefault('knowledge', [])
    if effect['fact'] not in knowledge:
        knowledge.append(effect['fact'])
    return []


def set_belief(state: dict, effect: dict) -> list[dict]:
    """Actualiza una creencia declarada sin confundirla con un hecho."""
    character = find(state, 'characters', effect['character'])
    character.setdefault('beliefs', {})[effect['claim']] = effect['value']
    return []


def _holder(state: dict, identifier: str) -> str:
    """Admite una persona o un lugar como destino de un objeto."""
    kind, _ = instance(state, identifier)
    if kind not in ('characters', 'locations'):
        raise WorldError('INVALID_REFERENCE', 'Un objeto requiere personaje o lugar')
    return 'owner' if kind == 'characters' else 'location'


def transfer(state: dict, effect: dict) -> list[dict]:
    """Traslada un objeto entre personas y lugares, con ubicación exclusiva."""
    obj = find(state, 'objects', effect['object'])
    old_field = _holder(state, effect['from'])
    new_field = _holder(state, effect['to'])
    if obj.get(old_field) != effect['from']:
        raise WorldError('INVALID_STATE', 'El origen ya no contiene el objeto')
    if old_field == new_field and effect['from'] == effect['to']:
        return []
    obj.pop('owner', None)
    obj.pop('location', None)
    obj[new_field] = effect['to']
    return []
