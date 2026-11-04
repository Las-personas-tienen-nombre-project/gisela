"""Presencia pública de entidades en escenas físicas de GISELA.

Las escenas sin location son contextos narrativos: la autoría gobierna su
visibilidad. Las escenas físicas no revelan inventarios ajenos por defecto.
"""

from __future__ import annotations

from .world_base import WorldError, instance


def present(state: dict, scene: dict, identifier: str) -> bool:
    """Comprueba una entidad referenciada, sin alterar el mundo confirmado."""
    place = scene.get("location")
    if not place:
        return True
    if not isinstance(identifier, str) or identifier.startswith("$"):
        return False
    try:
        kind, entity = instance(state, identifier)
    except WorldError:
        return False
    if kind == "characters":
        return entity["location"] == place
    if kind == "locations":
        return entity["id"] == place
    if kind == "objects":
        if entity.get("location") == place:
            return True
        owner = entity.get("owner")
        player = state.get("player_character")
        if owner != player or not player:
            return False
        actor = next(
            (c for c in state["world"]["characters"] if c["id"] == player), None
        )
        return actor is not None and actor["location"] == place
    return False
