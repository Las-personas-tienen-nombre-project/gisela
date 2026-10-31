"""Integrador optativo: TRAITS + DICE + S.O.F.I.A. + RNG de GISELA."""
from __future__ import annotations
from gisela.contracts.rng import RNGState, draw as rng_draw
from traits import evaluate as traits_evaluate
from dice import evaluate as dice_evaluate, DiceError
from .world_base import WorldError, instance
from .sofia import read as read_stat


def _contributions(state: dict, spec: dict, definitions) -> dict:
    """Reúne participantes y computa contribuciones sin leer reglas de DICE."""
    participants = []
    for item in spec['participants']:
        group, entity = instance(state, item['entity'])
        if group not in ('characters', 'objects', 'locations'):
            raise WorldError('INVALID_REFERENCE', 'Entidad sin rasgos')
        participants.append({'entity': item['entity'], 'kind': group[:-1],
                             'role': item['role'], 'traits': entity.get('traits', [])})
    request = {'schema_version': 'traits.evaluation.v1', 'participants': participants,
               'tags': spec['tags'], 'slots': ['bonus','difficulty']}
    if definitions.traits is None:
        if any(item['traits'] for item in participants):
            raise WorldError('INVALID_STATE', 'Rasgos sin catálogo')
        contributions = {'schema_version':'traits.result.v1',
                         'contributions':[], 'totals':{}}
    else:
        contributions = traits_evaluate(definitions.traits, request)
    return contributions


def resolve(state: dict, spec: dict, definitions) -> dict:
    """Entrega resultado y siguiente RNG *propuestos*; no muta la sesión."""
    contributions = _contributions(state, spec, definitions)
    bonus = contributions['totals'].get('bonus', 0)
    difficulty = spec.get('difficulty', 0) + contributions['totals'].get('difficulty', 0)
    base = spec.get('base', 0)
    if 'stat' in spec:
        base += read_stat(state, spec['stat'], definitions)
    if any(type(v) is not int or abs(v) > 1000000 for v in (base, bonus, difficulty)):
        raise DiceError('La solicitud efectiva supera el límite numérico antes de tirar')
    profile = spec['profile']  # EvaluationRoutes ya compiló el perfil al crear la sesión.
    rng = RNGState(**state['rng'])
    if rng.counter + profile.get('count', 0) > 9007199254740991:
        raise DiceError('Presupuesto del RNG insuficiente para la evaluación')

    def take(sides):
        nonlocal rng
        result, rng = rng_draw(rng, sides)
        return result

    result = dice_evaluate(profile,
                           {'base':base, 'bonus':bonus, 'difficulty':difficulty}, take)
    return {'dice': result, 'traits': contributions, 'rng_after': rng.as_json()}
