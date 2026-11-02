"""Consulta pura de ventanas de habilidades y sus usos confirmados."""

from __future__ import annotations

from .conditions import predicate
from .world_base import WorldError, find


def plays(state: dict) -> int:
    """Cuenta usos de la ventana actual sin un segundo contador persistente."""
    cursor = state["cursor"]
    return sum(
        item["kind"] == "skill_played"
        and item.get("detail", {}).get("execution_id") == cursor["execution_id"]
        and item.get("detail", {}).get("step_id") == cursor["step"]
        for item in state["history"]["trace"]
    )


def exhausted(state: dict, step: dict) -> bool:
    """Comprueba el límite declarado, si existe."""
    return "max_plays" in step and plays(state) >= step["max_plays"]


def allowed(state: dict, skill: dict, session) -> bool:
    """Autoriza solamente habilidades propias, en mano y con requisitos cumplidos."""
    if state["status"] == "exploring":
        if not session._scenes[state["current_scene"]].get("allow_skill_play", False):
            return False
    elif state["status"] != "node":
        return False
    if state.get("player_character") != skill["character"] or skill["zone"] != "hand":
        return False
    find(state, "characters", skill["character"])
    card = session._cards[skill["card"]]
    if card["kind"] != "skill":
        raise WorldError(
            "INVALID_STATE", "La carta de una habilidad no es de tipo skill"
        )
    return predicate(
        state, card["play"].get("requires", {"constant": True}), session._definitions
    )


def offered(session, language: str | None = None) -> list[dict]:
    """Construye acciones habilitadas sin publicar información provisional."""
    state = session._state
    from .projection import text

    actions = []
    for skill in state["world"]["skills"]:
        if (
            skill["character"] != state.get("player_character")
            or skill["zone"] != "hand"
        ):
            continue
        card = session._cards[skill["card"]]
        if card["kind"] != "skill":
            raise WorldError(
                "INVALID_STATE", "Instancia de habilidad con carta incorrecta"
            )
        actions.append(
            {
                "kind": "play_skill",
                "action_id": "play_" + skill["id"],
                "id": skill["id"],
                "label": text(
                    card["play"].get("label", card["title"]), session, language
                ),
                "enabled": allowed(state, skill, session),
            }
        )
    return actions
