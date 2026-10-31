"""Habilidades como instancias de ALBERTO, sin ejecución de cartas."""
from __future__ import annotations
from dataclasses import dataclass
from .world_base import find, allocate_id, WorldError


def _capacity(state: dict, character: str) -> dict:
    """Resuelve la capacidad declarada de un personaje."""
    find(state, 'characters', character)
    capacity = next((item for item in state['world']['capacities']
                     if item['character'] == character), None)
    if capacity is None:
        raise WorldError('MISSING_CAPACITY', f'No hay capacidad para {character}')
    return capacity


def _skills(state: dict, character: str) -> list[dict]:
    """Devuelve habilidades del personaje sin moverlas todavía."""
    return [item for item in state['world']['skills'] if item['character'] == character]


def _available_zone(capacity: dict, skills: list[dict]) -> str | None:
    """Prefiere mano y luego reserva, sin sobrepasar el límite."""
    for zone in ('hand', 'reserve'):
        if sum(item['zone'] == zone for item in skills) < capacity[zone]:
            return zone
    return None


def grant_skill(state: dict, effect: dict, decisions=None) -> list[dict]:
    """Concede una habilidad o solicita el descarte en la transacción actual."""
    if decisions is None:
        raise WorldError('INVALID_STATE', 'Falta contexto de decisiones para grant_skill')
    character = effect['character']
    capacity = _capacity(state, character)
    skills = _skills(state, character)
    zone = _available_zone(capacity, skills)
    if zone is None:
        zone = _discard_overflow(state, effect, decisions)
    candidate = allocate_id(state, 'skill')
    state['world']['skills'].append({
        'id':candidate, 'card':effect['skill'], 'character':character, 'zone':zone})
    return []


def _discard_overflow(state: dict, effect: dict, decisions) -> str:
    """Resuelve un desbordamiento o rechaza una concesión sin espacio."""
    skills = _skills(state, effect['character'])
    if effect.get('overflow') != 'require_choice':
        raise WorldError('CAPACITY_EXCEEDED', 'No hay espacio para recibir la habilidad')
    if not skills:
        raise WorldError('NO_LEGAL_CHOICE', 'No hay habilidades que puedan descartarse')
    selected = decisions.select('discard_skill', [s['id'] for s in skills],
                                'La mano y la reserva están llenas. Elija una habilidad que descartar.')
    old = next(item for item in skills if item['id'] == selected)
    state['world']['skills'].remove(old)
    return old['zone']


def move_skill(state: dict, effect: dict) -> list[dict]:
    """Mueve una habilidad propia a una zona con cupo disponible."""
    character = effect['character']
    capacity = _capacity(state, character)
    skill = find(state, 'skills', effect['skill_instance'])
    if skill['character'] != character:
        raise WorldError('INVALID_STATE', 'La habilidad no pertenece al personaje')
    zone = effect['to']
    if skill['zone'] == zone:
        return []
    if sum(s['zone'] == zone for s in _skills(state, character)) >= capacity[zone]:
        raise WorldError('CAPACITY_EXCEEDED', f'No hay cupo en {zone}')
    skill['zone'] = zone
    return []


def discard_skill(state: dict, effect: dict) -> list[dict]:
    """Retira una habilidad propia conservando el registro de su identidad."""
    _capacity(state, effect['character'])
    skill = find(state, 'skills', effect['skill_instance'])
    if skill['character'] != effect['character']:
        raise WorldError('INVALID_STATE', 'La habilidad no pertenece al personaje')
    state['world']['skills'].remove(skill)
    return []


def take_for_play(state: dict, skill: dict) -> None:
    """Separa temporalmente la instancia de su mano dentro del borrador."""
    if skill['zone'] != 'hand':
        raise WorldError('INVALID_ACTION', 'Solo se juegan habilidades de la mano')
    state['world']['skills'].remove(skill)


@dataclass(frozen=True)
class SkillReturn:
    """Destino y respuestas auxiliares disponibles para el retorno."""
    zone: str
    decisions: object


def return_from_play(state: dict, skill: dict, request: SkillReturn) -> None:
    """Devuelve la misma instancia o la descarta, sin reutilizar su identidad."""
    zone = request.zone
    if zone == 'discard':
        return
    capacity = _capacity(state, skill['character'])
    others = [s for s in _skills(state, skill['character']) if s['zone'] == zone]
    if len(others) >= capacity[zone]:
        if not others:
            raise WorldError('CAPACITY_EXCEEDED', 'La zona no admite retorno')
        picked = request.decisions.select('return_skill', [s['id'] for s in others],
                                  'Elija una habilidad que descartar para permitir el retorno.')
        state['world']['skills'].remove(next(s for s in others if s['id'] == picked))
    skill['zone'] = zone
    state['world']['skills'].append(skill)
