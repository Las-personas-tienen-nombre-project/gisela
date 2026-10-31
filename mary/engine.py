"""Evaluador funcional de objetivos y misiones: solo propuestas, sin commit."""
from __future__ import annotations
import copy
from narrative_conditions import compare, evaluate as condition
from .contracts import MaryError


def initial_progress(plan: dict) -> dict:
    """Crea un progreso serializable sin hacer avanzar objetivos."""
    return {'objectives': {key: False for key in sorted(plan['objectives'])},
            'missions': {key: 'inactive' for key in sorted(plan['missions'])}}


def _resolve(query: dict, context: dict) -> bool:
    """Interpreta solamente hechos y valores declarados por el anfitrión."""
    if 'has_fact' in query:
        return query['has_fact'] in context['facts']
    if 'compare' in query:
        test = query['compare']
        return compare(_value(test['left'], context), _value(test['right'], context), test['op'])
    raise MaryError('Predicado externo desconocido')


def _value(expression: dict, context: dict):
    """Lee escalares explícitos; nunca explora objetos privados del anfitrión."""
    if 'literal' in expression:
        return expression['literal']
    key = expression['value']
    if key not in context['values']:
        raise MaryError(f'Valor no publicado por el anfitrión: {key}')
    return context['values'][key]


def _matches(spec: dict, context: dict) -> bool:
    """Evalúa criterios de estado, hechos distintos o pesos."""
    kind = spec['kind']
    if kind == 'condition':
        return condition(spec['when'], lambda item: _resolve(item, context))
    if kind == 'distinct':
        return len(set(spec['facts']) & context['facts']) >= spec['minimum']
    return sum(weight for fact, weight in spec['weights'].items()
               if fact in context['facts']) >= spec['minimum']


def _transition(source: str, effect: dict | None, outputs: list) -> None:
    """Entrega un resultado declarativo, sin ejecutarlo."""
    if effect:
        outputs.append({'source': source, 'effect': copy.deepcopy(effect)})


def _objectives(plan: dict, work: dict) -> list:
    """Actualiza hitos persistentes y condiciones reversibles."""
    context, progress, outputs = work['context'], work['progress'], work['outputs']
    changed = []
    for key, spec in sorted(plan['objectives'].items()):
        old = progress['objectives'][key]
        satisfied = _matches(spec['criterion'], context)
        new = old or satisfied if spec['mode'] == 'milestone' else satisfied
        progress['objectives'][key] = new
        if new != old:
            changed.append({'type': 'objective', 'id': key, 'from': old, 'to': new})
            if new and spec['mode'] == 'milestone':
                _transition('objective:' + key, spec.get('yield'), outputs)
    return changed


def _mission_state(spec: dict, work: dict, old: str) -> str:
    """Prioriza fracaso sobre cumplimiento y conserva terminales."""
    context, progress = work['context'], work['progress']
    if old in ('completed', 'failed', 'abandoned'):
        return old
    active = condition(spec.get('activate_when', {'constant': True}),
                       lambda item: _resolve(item, context))
    if not active:
        return 'inactive'
    failure = condition(spec.get('fail_when', {'constant': False}),
                        lambda item: _resolve(item, context))
    if failure:
        return 'failed'
    values = [progress['objectives'][key] for key in spec['objectives']]
    complete = all(values) if spec['completion'] == 'all' else any(values)
    return 'completed' if complete else 'active'


def _missions(plan: dict, work: dict) -> list:
    """Resuelve misiones según objetivos y condiciones de vigencia."""
    context, progress, outputs = work['context'], work['progress'], work['outputs']
    changed = []
    for key, spec in sorted(plan['missions'].items()):
        old = progress['missions'][key]
        new = _mission_state(spec, work, old)
        progress['missions'][key] = new
        if old != new:
            changed.append({'type': 'mission', 'id': key, 'from': old, 'to': new})
            if new == 'completed':
                _transition('mission:' + key, spec.get('yield'), outputs)
    return changed


def validate_progress(plan: dict, progress: dict) -> None:
    """Rechaza progreso adulterado sin evaluar condiciones del mundo."""
    if set(progress) != {'objectives', 'missions'}:
        raise MaryError('Estructura de progreso incompatible')
    if set(progress.get('objectives', {})) != set(plan['objectives']):
        raise MaryError('Progreso de objetivos incompatible con el plan')
    if set(progress.get('missions', {})) != set(plan['missions']):
        raise MaryError('Progreso de misiones incompatible con el plan')
    if any(type(v) is not bool for v in progress['objectives'].values()):
        raise MaryError('Progreso de objetivo inválido')
    if any(v not in ('inactive', 'active', 'completed', 'failed', 'abandoned')
           for v in progress['missions'].values()):
        raise MaryError('Estado de misión inválido')


def evaluate(plan: dict, context: dict, progress: dict | None = None) -> dict:
    """Propone progreso y yields; toda confirmación corresponde al anfitrión."""
    if not isinstance(context.get('facts'), (set, list, tuple)) or not isinstance(context.get('values'), dict):
        raise MaryError('Contexto requiere facts y values')
    if any(not isinstance(name, str) for name in context['facts']):
        raise MaryError('Los hechos deben identificarse por cadenas')
    ctx = {'facts': set(context['facts']), 'values': context['values']}
    current = initial_progress(plan) if progress is None else copy.deepcopy(progress)
    validate_progress(plan, current)
    outputs = []
    work = {'context':ctx, 'progress':current, 'outputs':outputs}
    transitions = _objectives(plan, work)
    transitions.extend(_missions(plan, work))
    return {'progress': current, 'transitions': transitions, 'yields': outputs}
