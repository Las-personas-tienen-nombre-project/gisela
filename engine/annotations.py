"""Información editorial visible en GLAUQUIR, independiente de estado y Act."""

from __future__ import annotations

from .projection import text
from .scene_actions import definition


def visible_annotations(session, view: dict, language: str) -> list[dict]:
    """Lee únicamente fuentes alcanzadas, acciones ofertadas y escena activa."""
    state = session._state
    result: list[dict] = []

    def add(owner: dict, source: tuple[str, str, str | None]):
        scope, identifier, action_id = source
        for annotation in owner.get("annotations", []):
            if annotation["audience"] != "glauquir":
                continue
            item = {
                "scope": scope,
                "source": identifier,
                "text": text(annotation["text"], session, language),
            }
            if action_id is not None:
                item["action_id"] = action_id
            result.append(item)

    # Pendientes son un estado transaccional; no mostrar anotaciones sobre
    # contenidos que todavía no se han confirmado.
    if state.get("pending_transaction") or state.get("pending_evaluation"):
        return result
    if state["status"] == "exploring":
        scene = session._scenes[state["current_scene"]]
        add(scene, ("scene", scene["id"], None))
        # Resolver desde las ofertas visibles, nunca desde las definiciones
        # completas de la escena (pueden contener acciones ocultas).
        from .scene_actions import sources

        visible = {
            entry["action_id"]: source for source, entry in sources(session, state)
        }
        for offer in view["actions"]:
            if offer["action_id"] in visible:
                source = visible[offer["action_id"]]
                add(
                    definition(session, source),
                    ("action", offer["id"], offer["action_id"]),
                )
    elif state["status"] == "node":
        node = session._nodes[state["cursor"]["node"]]
        step = session._current_step(state)
        current = node["id"] + "." + step["id"]
        # history.reading permite distinguir la primera vista del nodo sin
        # añadir contadores de "anotaciones leídas" al estado narrativo.
        recent = []
        for record in reversed(state["history"].get("reading", [])):
            if record["kind"] in ("narrate", "dialogue") and record[
                "source"
            ].startswith(node["id"] + "."):
                recent.append(record)
            else:
                break
        if not recent or (len(recent) == 1 and recent[0]["source"] == current):
            add(node, ("node", node["id"], None))
        add(step, ("step", current, None))
    return result
