"""Validación de Act y coordinación del compromiso transaccional de GISELA."""
from __future__ import annotations
import copy
from gisela.contracts.semantic_validator import Validator
from .world_base import WorldError
from .pending import DecisionRequired, DecisionReplay, EvaluationPause, EvaluationReplay


def _authorize(session, request: dict) -> dict:
    """Rechaza acciones inexistentes, vencidas o ajenas a la proyección."""
    validator = Validator()
    validator.use_version(session._state['schema_version'])
    if not isinstance(request, dict) or not validator.check_schema('act', request):
        raise WorldError('INVALID_ACTION', 'Act no cumple el contrato JSON Schema de la sesión')
    state = session._state
    if request['session_id'] != state['session_id'] or request['revision'] != state['revision']:
        raise WorldError('STALE_PROJECTION', 'La acción pertenece a otra sesión o revisión')
    if request.get('parameters'):
        raise WorldError('INVALID_ACTION', 'El subconjunto H3 no acepta parámetros')
    matches = [a for a in session.observe()['actions'] if a['action_id'] == request['action_id']]
    if len(matches) != 1 or not matches[0]['enabled']:
        raise WorldError('INVALID_ACTION', 'La acción no está ofrecida o está inhabilitada')
    return matches[0]


def _cancel(session) -> dict:
    """Descarta la intención voluntaria sin alterar mundo, historial ni RNG."""
    current = session._state
    if current['pending_transaction']['origin'] != 'voluntary':
        raise WorldError('INVALID_ACTION', 'Una operación automática obligatoria no puede cancelarse')
    draft = copy.deepcopy(current)
    del draft['pending_transaction']
    draft['revision'] += 1
    session._validate_state(draft)
    view = session._project_state(draft)
    session._state = draft
    return {'status':'ok', 'revision':draft['revision'], 'view':view}


def _evaluation_intent(state: dict, action: dict) -> tuple:
    """Continúa una tirada fijada o responde a su solicitud auxiliar."""
    pending = state.get('pending_evaluation')
    if pending:
        auxiliary = pending.get('auxiliary_request')
        if auxiliary:
            if action['kind'] != 'resolve_evaluation_auxiliary':
                raise WorldError('INVALID_ACTION', 'Debe resolver la decisión auxiliar')
            answer = {'request_id':auxiliary['request_id'], 'option_id':action['id']}
            answers = pending['answers'] + [answer]
        else:
            if action['kind'] != 'continue_evaluation':
                raise WorldError('INVALID_ACTION', 'Debe continuar la evaluación fija')
            answers = pending['answers']
        return pending['source'], pending['origin'], answers, pending['initiated_revision']


def _intent(session, action: dict) -> tuple[dict, str, list, int]:
    """Recupera el origen de la transacción o de la acción del nodo actual."""
    state = session._state
    if state.get('pending_evaluation'):
        return _evaluation_intent(state, action)
    pending = state.get('pending_transaction')
    if pending:
        if action['kind'] != 'resolve_pending':
            raise WorldError('INVALID_ACTION', 'Debe resolverse la transacción pendiente')
        answer = {'request_id':pending['request']['request_id'], 'option_id':action['id']}
        return (pending['source'], pending['origin'],
                pending['answers'] + [answer], pending['initiated_revision'])
    if action['kind'] == 'interact' and state['status'] == 'exploring':
        from .scene_actions import sources
        found = [source for source, entry in sources(session, state)
                 if entry['action_id'] == action['action_id']]
        if len(found) != 1:
            raise WorldError('INVALID_ACTION', 'Acción de escena ambigua')
        return found[0], 'voluntary', [], state['revision']
    if action['kind'] == 'play_skill':
        return {'kind':'skill_play', 'skill_instance':action['id']}, 'voluntary', [], state['revision']
    cursor = state['cursor']
    if action['kind'] == 'advance':
        source = {'kind':'node_step', 'node':cursor['node'], 'step':cursor['step']}
        return source, 'mandatory', [], state['revision']
    if action['kind'] == 'choose':
        source = {'kind':'choice_option', 'node':cursor['node'],
                  'step':cursor['step'], 'option':action['id']}
        return source, 'voluntary', [], state['revision']
    raise WorldError('INVALID_ACTION', 'Acción aún no disponible')


def _pending_after_evaluation(session, current: dict, details: tuple) -> dict:
    """Continúa la espera de una evaluación sin alterar sus dados."""
    answers, required = details
    pending = copy.deepcopy(current)
    pending['pending_evaluation']['answers'] = copy.deepcopy(answers)
    pending['pending_evaluation']['auxiliary_request'] = copy.deepcopy(required.request)
    pending['revision'] += 1
    session._validate_state(pending)
    view = session._project_state(pending)
    session._state = pending
    return {'status':'ok','revision':pending['revision'],'view':view}


def _perform(session, current: dict, intent: tuple) -> dict:
    """Reconstruye la acción, publica una espera o confirma íntegramente."""
    source, origin, answers, initiated_revision = intent
    draft = copy.deepcopy(current)
    draft.pop('pending_transaction', None)
    old = current.get('pending_evaluation')
    draft.pop('pending_evaluation', None)
    if old:
        draft['rng'] = copy.deepcopy(old['rng_initial'])
    tape = EvaluationReplay(old['fixed'] if old else [])
    try:
        session._execute_source(draft, source, DecisionReplay(answers, tape))
    except EvaluationPause as paused:
        return session._publish_evaluation({'current':current, 'draft':draft,
                'intent':{'origin':origin, 'source':source, 'initiated_revision':initiated_revision,
                          'answers':answers}, 'paused':paused})
    except DecisionRequired as required:
        if old:
            return _pending_after_evaluation(session, current, (answers, required))
        return session._publish_pending(current, {'origin':origin, 'source':source,
                                 'initiated_revision':initiated_revision,
                                 'answers':answers, 'request':required.request})
    from .reading_log import action
    action(session, draft, source)
    return session._commit(current, draft)


def act(session, request: dict) -> dict:
    """Autoriza, ejecuta y responde sin propagar errores previsibles al anfitrión."""
    try:
        action = _authorize(session, request)
        if session._state.get('pending_transaction') and action['kind'] == 'cancel_pending':
            return _cancel(session)
        intent = _intent(session, action)
        return _perform(session, session._state, intent)
    except WorldError as exc:
        return session._fail(exc.code, str(exc))
    except (KeyError, TypeError, ValueError, StopIteration) as exc:
        return session._fail('INVALID_STATE', f'Error de ejecución: {exc}')
