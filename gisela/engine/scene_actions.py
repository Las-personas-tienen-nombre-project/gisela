"""Acciones exploratorias. La misma resolución sirve a Observe y Act.

Los identificadores de acción duran una revisión. La procedencia persistente
es escena, elemento opcional e identificador de la acción del autor.
"""

from __future__ import annotations

from .conditions import predicate
from .effect_context import EffectContext
from .presentation import explicit_color
from .scene_presence import present
from .world_base import WorldError


def _shown(state: dict, item: dict, definitions) -> bool:
    """Decide visibilidad sin materializar estado."""
    return predicate(state, item.get("visible_if", {"constant": True}), definitions)


def _element_shown(session, state: dict, element: dict) -> bool:
    """Requiere visibilidad declarada y presencia de la entidad vinculada."""
    if not _shown(state, element, session._definitions):
        return False
    scene = session._scenes[state["current_scene"]]
    return "entity" not in element or present(state, scene, element["entity"])


def sources(
    session, state: dict, language: str | None = None
) -> list[tuple[dict, dict]]:
    """Construye acciones y procedencias inequívocas de la escena actual."""
    scene = session._scenes[state["current_scene"]]
    from .projection import text

    result = []
    groups = [(None, scene.get("actions", []))]
    groups.extend(
        (element, element.get("actions", [])) for element in scene.get("elements", [])
    )
    for group_index, (element, actions) in enumerate(groups):
        if element is not None and not _element_shown(session, state, element):
            continue
        for action_index, action in enumerate(actions):
            if not _shown(state, action, session._definitions):
                continue
            source = {
                "kind": "scene_action",
                "scene": scene["id"],
                "action": action["id"],
            }
            if element is not None:
                source["element"] = element["id"]
            entry = {
                "kind": "interact",
                "action_id": f"interact_{group_index}_{action_index}",
                "id": action.get("public_id", action["id"]),
                "label": text(action["label"], session, language),
                "enabled": predicate(
                    state,
                    action.get("enabled_if", {"constant": True}),
                    session._definitions,
                ),
            }
            if "role" in action:
                entry["role"] = action["role"]
            result.append((source, entry))
    return result


def definition(session, source: dict) -> dict:
    """Resuelve la acción declarada sin inferir propietarios."""
    scene = session._scenes.get(source["scene"])
    if scene is None:
        raise WorldError("INVALID_REFERENCE", "Escena de origen inexistente")
    if "element" in source:
        element = next(
            (e for e in scene.get("elements", []) if e["id"] == source["element"]), None
        )
        if element is None:
            raise WorldError("INVALID_REFERENCE", "Elemento de origen inexistente")
        actions = element.get("actions", [])
    else:
        actions = scene.get("actions", [])
    action = next((a for a in actions if a["id"] == source["action"]), None)
    if action is None:
        raise WorldError("INVALID_REFERENCE", "Acción de origen inexistente")
    return action


def execute_source(session, draft: dict, request: tuple) -> None:
    """Revalida la acción exploratoria y ejecuta sus efectos en el borrador."""
    source, decisions = request
    if draft["status"] != "exploring" or draft["current_scene"] != source["scene"]:
        raise WorldError("REPLAY_MISMATCH", "La escena de origen ya no es actual")
    offered = [entry for item, entry in sources(session, draft) if item == source]
    if len(offered) != 1 or not offered[0]["enabled"]:
        raise WorldError("REPLAY_MISMATCH", "Acción exploratoria no autorizada")
    action = definition(session, source)
    if "evaluation" in action:
        key = ("scene", source["scene"], source.get("element"), source["action"])
        branch = session._evaluate(draft, key, decisions)
        destination = branch.get("next")
    else:
        session._operations(
            draft,
            action.get("effects", []),
            EffectContext(source["action"], decisions, session._definitions),
        )
        destination = action.get("next")
    trace(draft, source)
    if destination is not None:
        session._enter_node(draft, destination["node"], decisions)


def _actors(session, scene: dict, language: str | None = None) -> list[dict]:
    """Lista personajes presentes que cumplen las condiciones de visibilidad."""
    from .projection import text

    result = []
    for actor in scene.get("actors", []):
        if not _shown(session._state, actor, session._definitions) or not present(
            session._state, scene, actor["character"]
        ):
            continue
        identifier = actor["character"]
        instance = next(
            (c for c in session._state["world"]["characters"] if c["id"] == identifier),
            None,
        )
        if instance is None:
            continue
        card = session._cards[instance["card"]]
        display = {
            "id": actor.get("public_id", identifier),
            "name": text(card["title"], session, language)
            if "title" in card
            else identifier,
        }
        color, _ = explicit_color(instance, card, actor)
        if color is not None:
            display["color"] = color
        if "unknown_name" in actor and not _shown(
            session._state, {"visible_if": actor["known_if"]}, session._definitions
        ):
            display["name"] = text(actor["unknown_name"], session, language)
            display["identity_hidden"] = True
        if "presentation" in actor:
            display["presentation"] = actor["presentation"]
        result.append(display)
    return result


def project(session, view: dict, language: str | None = None) -> None:
    """Expone únicamente actores y elementos visibles y sus acciones."""
    scene = session._scenes[session._state["current_scene"]]
    from .projection import text

    view["scene_title"] = text(scene.get("title", scene["id"]), session, language)
    if "description" in scene:
        view["scene_description"] = text(scene["description"], session, language)
    offers = sources(session, session._state, language)
    view["content"] = {"kind": "exploring"}
    view["actions"] = [entry for _, entry in offers]
    if scene.get("allow_skill_play", False):
        from .skill_window import offered

        view["actions"].extend(offered(session, language))
    view["elements"] = []
    for element in scene.get("elements", []):
        if _element_shown(session, session._state, element):
            actions = [
                entry
                for source, entry in offers
                if source.get("element") == element["id"]
            ]
            item = {
                "id": element.get("public_id", element["id"]),
                "label": text(element["label"], session, language),
                "actions": actions,
            }
            if isinstance(element.get("entity"), str) and not element[
                "entity"
            ].startswith("$"):
                from .world_base import instance

                _, entity_instance = instance(session._state, element["entity"])
                color, _ = explicit_color(
                    entity_instance, session._cards[entity_instance["card"]], element
                )
                if color is not None:
                    item["color"] = color
            if "role" in element:
                item["role"] = element["role"]
            if "description" in element:
                item["description"] = text(element["description"], session, language)
            if isinstance(element.get("entity"), str) and not element[
                "entity"
            ].startswith("$"):
                item["entity"] = element.get("public_entity", element["entity"])
            view["elements"].append(item)
    view["actors"] = _actors(session, scene, language)
    if "presentation" in scene:
        view["presentation"] = scene["presentation"]


def trace(state: dict, source: dict) -> None:
    """Conserva la procedencia de una interacción confirmada."""
    history = state["history"]
    sequence = len(history["facts"]) + len(history["trace"]) + 1
    detail = {"scene": source["scene"], "action": source["action"]}
    if "element" in source:
        detail["element"] = source["element"]
    history["trace"].append(
        {
            "sequence": sequence,
            "kind": "scene_action",
            "source": source["scene"],
            "detail": detail,
        }
    )
