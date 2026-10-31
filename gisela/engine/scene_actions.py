"""Acciones exploratorias. La misma resolución sirve a Observe y Act.

Los identificadores de acción duran una revisión. La procedencia persistente
es escena, elemento opcional e identificador de la acción del autor.
"""
from __future__ import annotations
from .conditions import predicate
from .world_base import WorldError
from .scene_presence import present


def _shown(state: dict, item: dict, definitions) -> bool:
    """Decide visibilidad sin materializar estado."""
    return predicate(state, item.get('visible_if', {'constant': True}), definitions)


def _element_shown(session, state: dict, element: dict) -> bool:
    """Requiere visibilidad declarada y presencia de la entidad vinculada."""
    if not _shown(state, element, session._definitions):
        return False
    scene = session._scenes[state['current_scene']]
    return 'entity' not in element or present(state, scene, element['entity'])


def sources(session, state: dict) -> list[tuple[dict, dict]]:
    """Construye acciones y procedencias inequívocas de la escena actual."""
    scene = session._scenes[state['current_scene']]
    from .projection import text
    result = []
    groups = [(None, scene.get('actions', []))]
    groups.extend((element, element.get('actions', [])) for element in scene.get('elements', []))
    for group_index, (element, actions) in enumerate(groups):
        if element is not None and not _element_shown(session, state, element):
            continue
        for action_index, action in enumerate(actions):
            if not _shown(state, action, session._definitions):
                continue
            source = {'kind': 'scene_action', 'scene':scene['id'], 'action':action['id']}
            if element is not None:
                source['element'] = element['id']
            entry = {'kind':'interact', 'action_id':f'interact_{group_index}_{action_index}',
                     'id':action['id'], 'label':text(action['label']),
                     'enabled':predicate(state, action.get('enabled_if', {'constant':True}),
                                         session._definitions)}
            result.append((source, entry))
    return result


def definition(session, source: dict) -> dict:
    """Resuelve la acción declarada sin inferir propietarios."""
    scene = session._scenes.get(source['scene'])
    if scene is None:
        raise WorldError('INVALID_REFERENCE', 'Escena de origen inexistente')
    if 'element' in source:
        element = next((e for e in scene.get('elements', [])
                        if e['id'] == source['element']), None)
        if element is None:
            raise WorldError('INVALID_REFERENCE', 'Elemento de origen inexistente')
        actions = element.get('actions', [])
    else:
        actions = scene.get('actions', [])
    action = next((a for a in actions if a['id'] == source['action']), None)
    if action is None:
        raise WorldError('INVALID_REFERENCE', 'Acción de origen inexistente')
    return action


def _actors(session, scene: dict) -> list[dict]:
    """Lista personajes presentes que cumplen las condiciones de visibilidad."""
    from .projection import text
    result = []
    for actor in scene.get('actors', []):
        if (not _shown(session._state, actor, session._definitions)
                or not present(session._state, scene, actor['character'])):
            continue
        identifier = actor['character']
        instance = next((c for c in session._state['world']['characters']
                         if c['id'] == identifier), None)
        if instance is None:
            continue
        card = session._cards[instance['card']]
        display = {'id':identifier, 'name':text(card['title']) if 'title' in card else identifier}
        if 'presentation' in actor:
            display['presentation'] = actor['presentation']
        result.append(display)
    return result


def project(session, view: dict) -> None:
    """Expone únicamente actores y elementos visibles y sus acciones."""
    scene = session._scenes[session._state['current_scene']]
    from .projection import text
    view['scene_title'] = text(scene.get('title', scene['id']))
    if 'description' in scene:
        view['scene_description'] = text(scene['description'])
    offers = sources(session, session._state)
    view['content'] = {'kind':'exploring'}
    view['actions'] = [entry for _, entry in offers]
    if scene.get('allow_skill_play', False):
        from .skill_window import offered
        view['actions'].extend(offered(session))
    view['elements'] = []
    for element in scene.get('elements', []):
        if _element_shown(session, session._state, element):
            actions = [entry for source, entry in offers
                       if source.get('element') == element['id']]
            item = {'id':element['id'], 'label':text(element['label']), 'actions':actions}
            if 'description' in element:
                item['description'] = text(element['description'])
            if isinstance(element.get('entity'), str) and not element['entity'].startswith('$'):
                item['entity'] = element['entity']
            view['elements'].append(item)
    view['actors'] = _actors(session, scene)
    if 'presentation' in scene:
        view['presentation'] = scene['presentation']


def trace(state: dict, source: dict) -> None:
    """Conserva la procedencia de una interacción confirmada."""
    history = state['history']
    sequence = len(history['facts']) + len(history['trace']) + 1
    detail = {'scene':source['scene'], 'action':source['action']}
    if 'element' in source:
        detail['element'] = source['element']
    history['trace'].append({'sequence':sequence, 'kind':'scene_action',
                             'source':source['scene'], 'detail':detail})
