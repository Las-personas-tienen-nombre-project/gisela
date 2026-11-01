"""Creación y retiro controlados de instancias de ALBERTO."""

from __future__ import annotations

from .world_base import WorldError, allocate_id, find, instance


def _card(catalog: dict, identifier: str) -> dict:
    """Requiere una carta de entidad cuya clase pueda instanciarse."""
    card = catalog.get(identifier)
    if card is None or card["kind"] not in ("character", "location", "object"):
        raise WorldError(
            "INVALID_REFERENCE", f"Carta de entidad no disponible: {identifier}"
        )
    return card


def _new_fields(state: dict, card: dict, effect: dict) -> dict:
    """Valida las relaciones necesarias para construir la entidad."""
    kind = card["kind"]
    if kind == "character":
        if "location" not in effect:
            raise WorldError("INVALID_STATE", "Crear personaje requiere lugar")
        find(state, "locations", effect["location"])
        return {"location": effect["location"]}
    if kind == "object":
        if ("owner" in effect) == ("location" in effect):
            raise WorldError("INVALID_STATE", "Crear objeto requiere un solo origen")
        key = "owner" if "owner" in effect else "location"
        target = "characters" if key == "owner" else "locations"
        find(state, target, effect[key])
        return {key: effect[key]}
    return {}


def create_instance(state: dict, effect: dict, definitions) -> list[dict]:
    """Crea una entidad desde una carta y reserva su identidad en el borrador."""
    card = _card(definitions.cards, effect["card"])
    fields = _new_fields(state, card, effect)
    prefix = card["kind"]
    identifier = allocate_id(state, prefix, effect.get("instance_id"))
    item = {"id": identifier, "card": card["id"], **fields}
    if "traits" in card:
        from .world_traits import defaults

        item["traits"] = defaults(card, definitions.traits)
    elif state["schema_version"] == "1.3" and card["kind"] in (
        "character",
        "object",
        "location",
    ):
        item["traits"] = []
    if card["kind"] == "character":
        item["knowledge"] = []
        item["beliefs"] = {}
    state["world"][prefix + "s"].append(item)
    return []


def _referenced(state: dict, identifier: str) -> bool:
    """Impide retirar entidades referidas por otras instancias o relaciones."""
    world = state["world"]
    references = [
        ("characters", "location"),
        ("objects", "owner"),
        ("objects", "location"),
        ("skills", "character"),
        ("effects", "target"),
    ]
    if any(
        item.get(field) == identifier
        for group, field in references
        for item in world[group]
    ):
        return True
    if any(
        r["from"] == identifier or r["to"] == identifier for r in world["relationships"]
    ):
        return True
    if any(c["character"] == identifier for c in world["capacities"]):
        return True
    return state.get("player_character") == identifier


def remove_instance(state: dict, effect: dict) -> list[dict]:
    """Retira una instancia libre de referencias sin reutilizar su ID."""
    collection, item = instance(state, effect["instance"])
    if _referenced(state, item["id"]):
        raise WorldError("ENTITY_IN_USE", f"Instancia todavía referida: {item['id']}")
    state["world"][collection].remove(item)
    return []
