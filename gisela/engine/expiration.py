"""Selección pura de efectos vencidos, sin reloj ni confirmación propios."""
from __future__ import annotations
from datetime import datetime, timedelta
from .conditions import predicate
from .world_base import WorldError


def _elapsed(state: dict, effect: dict, minutes: int) -> bool:
    """Compara instantes con zona horaria y detecta tiempos incompatibles."""
    try:
        start = datetime.fromisoformat(effect['started_at'].replace('Z', '+00:00'))
        now = datetime.fromisoformat(state['world_time'].replace('Z', '+00:00'))
        return now - start >= timedelta(minutes=minutes)
    except (ValueError, TypeError, OverflowError) as exc:
        raise WorldError('INVALID_TIME', 'Fecha de efecto incompatible') from exc


def _matches(state: dict, clause: dict, data: dict) -> bool:
    """Evalúa una cláusula sobre la frontera causal actual."""
    event, effect, definitions = data['event'], data['effect'], data['definitions']
    if 'after_turns' in clause:
        return event['on'] == 'turn_ended' and state['turn'] - effect['started_turn'] >= clause['after_turns']
    if 'after_minutes' in clause:
        return event['on'] == 'clock_advanced' and _elapsed(state, effect, clause['after_minutes'])
    if 'on_fact' in clause:
        return event['on'] == 'fact_recorded' and event['fact'] == clause['on_fact']
    return predicate(state, clause['when'], definitions)


def due(state: dict, events: list[dict], definitions) -> list[str]:
    """Calcula IDs vencidos sin modificar el mundo ni el orden de las cartas."""
    result = []
    for effect in sorted(state['world']['effects'], key=lambda item: item['id']):
        card = definitions.cards[effect['card']]
        clauses = card.get('expiration', {}).get('clauses', [])
        if clauses and any(_matches(state, clause, {'event':event, 'effect':effect,
                               'definitions':definitions}) for clause in clauses
                           for event in events):
            result.append(effect['id'])
    return result
