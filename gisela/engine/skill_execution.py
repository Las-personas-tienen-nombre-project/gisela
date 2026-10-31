"""Ejecución declarativa de habilidades por GISELA, sin autoridad adicional."""
from __future__ import annotations
from dataclasses import dataclass
from .conditions import predicate
from .effect_context import EffectContext
from .world_base import WorldError, find
from .world_skills import take_for_play, return_from_play, SkillReturn


@dataclass(frozen=True)
class SkillRequest:
    """Agrupa el identificador original y las respuestas de la transacción."""
    identifier: str
    decisions: object


def _matched(state: dict, clauses: list[dict], definitions) -> list[dict]:
    """Filtra condiciones sobre el borrador después de ejecutar los efectos base."""
    return [item for item in clauses if predicate(state, item['when'], definitions)]


def _destination(state: dict, card: dict, definitions) -> str:
    """Rechaza retornos contradictorios en lugar de usar prioridades implícitas."""
    policy = card.get('return_policy', {'default': 'discard'})
    options = {item['to'] for item in policy.get('when', [])
               if predicate(state, item['if'], definitions)}
    if len(options) > 1:
        raise WorldError('RETURN_POLICY_CONFLICT', 'Políticas de retorno incompatibles')
    return next(iter(options)) if options else policy['default']


def _trace(state: dict, skill: dict) -> None:
    """Registra el intento confirmado en la misma transacción del nodo."""
    seq = len(state['history']['facts']) + len(state['history']['trace']) + 1
    detail = {'card':skill['card']}
    if state['status'] == 'node':
        cursor = state['cursor']
        detail.update({'execution_id':cursor['execution_id'], 'step_id':cursor['step']})
    else:
        detail['scene'] = state['current_scene']
    state['history']['trace'].append({
        'sequence': seq, 'kind': 'skill_played', 'source': skill['id'],
        'detail': detail})


def execute(session, state: dict, request: SkillRequest) -> None:
    """Consume el intento, ejecuta consecuencias y resuelve el retorno."""
    from .skill_window import allowed
    skill = find(state, 'skills', request.identifier)
    if not allowed(state, skill, session):
        raise WorldError('INVALID_ACTION', 'La habilidad no está habilitada')
    card = session._cards[skill['card']]
    take_for_play(state, skill)
    context = EffectContext(request.identifier, request.decisions, session._definitions)
    session._operations(state, card['play']['effects'], context)
    for outcome in _matched(state, card['play'].get('outcomes', []), session._definitions):
        session._operations(state, outcome['effects'], context)
    destination = _destination(state, card, session._definitions)
    return_from_play(state, skill, SkillReturn(destination, request.decisions))
    _trace(state, skill)
