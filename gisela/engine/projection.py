"""Proyección pública de GISELA basada exclusivamente en estado confirmado."""
from __future__ import annotations
from .conditions import predicate
from .world_base import WorldError


def text(value: object) -> str:
    """Presenta el texto en idioma principal de la vertical."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get('text'), str):
        return value['text']
    raise WorldError('INVALID_STATE', 'Texto localizado sin variante principal')


def _pending(session, view: dict) -> None:
    """Publica solo la solicitud, sin exponer consecuencias provisionales."""
    state = session._state
    pending = state['pending_transaction']
    req = pending['request']
    view['content'] = {'kind':'pending_transaction', 'request_id':req['request_id'],
                       'purpose':req['purpose'], 'prompt':req['description']}
    for candidate in req['options']:
        skill = next((s for s in state['world']['skills'] if s['id'] == candidate), None)
        card = session._cards.get(skill['card']) if skill else None
        view['actions'].append({'kind':'resolve_pending', 'action_id':'resolve_' + candidate,
                                'id':candidate, 'label':text(card['title']) if card else candidate,
                                'enabled':True})
    if pending['origin'] == 'voluntary':
        view['actions'].append({'kind':'cancel_pending', 'action_id':'cancel_pending',
                                'id':'cancelar', 'label':'Cancelar', 'enabled':True})


def _evaluation(session, view: dict) -> None:
    """Publica únicamente dados y banda; jamás la entrada efectiva privada."""
    pending = session._state['pending_evaluation']
    last = pending['fixed'][-1]
    result = last['result']
    view['content'] = {'kind':'pending_evaluation',
                       'evaluation_id':pending['evaluation_id'],
                       'presentation':last['presentation'],
                       'rolls':result['rolls'], 'outcome':result['outcome']}
    request = pending.get('auxiliary_request')
    if request:
        view['content']['auxiliary_request'] = {
            'request_id':request['request_id'], 'prompt':request['description']}
        for candidate in request['options']:
            skill = next((s for s in session._state['world']['skills'] if s['id'] == candidate), None)
            card = session._cards.get(skill['card']) if skill else None
            view['actions'].append({'kind':'resolve_evaluation_auxiliary',
                     'action_id':'resolve_' + candidate, 'id':candidate,
                     'label':text(card['title']) if card else candidate, 'enabled':True})
    else:
        view['actions'].append({'kind':'continue_evaluation',
                     'action_id':'continue_evaluation','id':'continue',
                     'label':'Continuar','enabled':True})


def _choice(session, step: dict, view: dict) -> None:
    """Presenta únicamente las opciones visibles y sus estados habilitados."""
    state, definitions = session._state, session._definitions
    view['content'] = {'kind':'choice'}
    if 'prompt' in step:
        view['content']['prompt'] = text(step['prompt'])
    for option in step['options']:
        if not predicate(state, option.get('visible_if', {'constant':True}), definitions):
            continue
        enabled = predicate(state, option.get('enabled_if', {'constant':True}), definitions)
        view['actions'].append({'kind':'choose', 'action_id':'choose_' + option['id'],
                                'id':option['id'], 'label':text(option['label']),
                                'enabled':enabled})


def _window(session, view: dict) -> None:
    """Ofrece habilidades de la mano y la opción explícita de continuar."""
    from .skill_window import offered
    view['content'] = {'kind':'skill_window'}
    view['actions'].extend(offered(session))
    view['actions'].append({'kind':'advance', 'action_id':'advance', 'id':'continue',
                            'label':'Continuar', 'enabled':True})


def _node(session, view: dict) -> None:
    """Construye el contenido observable del nodo activo."""
    step = session._current_step(session._state)
    if step['op'] == 'choice':
        _choice(session, step, view)
    elif step['op'] == 'skill_window':
        _window(session, view)
    elif step['op'] in ('narrate', 'dialogue'):
        view['content'] = {'kind':step['op'], 'text':text(step['text'])}
        if step['op'] == 'dialogue':
            view['content']['speaker'] = step['speaker']
        view['actions'].append({'kind':'advance', 'action_id':'advance', 'id':'continue',
                                'label':'Continuar', 'enabled':True})
    else:
        raise WorldError('INVALID_STATE', 'Cursor apunta a paso no observable')


def observe(session) -> dict:
    """Devuelve escena, contenido y acciones sin modificar estado ni revisiones."""
    state = session._state
    view = {'session_id':state['session_id'], 'revision':state['revision'],
            'world_revision':state['world_revision'], 'world_time':state['world_time'],
            'turn':state['turn'], 'status':state['status'], 'actions':[]}
    if 'current_scene' in state:
        view['scene'] = state['current_scene']
    if 'pending_evaluation' in state:
        _evaluation(session, view)
    elif 'pending_transaction' in state:
        _pending(session, view)
    elif state['status'] == 'ended':
        view['content'] = {'kind':'ending', 'ending':state['ending']}
    elif state['status'] == 'exploring':
        from .scene_actions import project
        project(session, view)
    elif state['status'] == 'node':
        _node(session, view)
    else:
        raise WorldError('INVALID_STATE', 'Estado sin contenido observable')
    from .public_view import augment
    augment(session, view)
    if session._mary is not None and 'pending_transaction' not in state and 'pending_evaluation' not in state:
        from mary import public_quests
        view['quests'] = public_quests(session._mary, state['mary'])
    return view
