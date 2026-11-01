"""Instancias de efectos de ALBERTO; sin decisiones ni confirmación de sesión."""

from __future__ import annotations

from .world_base import WorldError, allocate_id, find


def _definition(definitions, card_id: str) -> dict:
    """Comprueba la clase de carta sin inferir capacidades."""
    card = definitions.cards.get(card_id)
    if card is None or card["kind"] != "effect":
        raise WorldError(
            "INVALID_REFERENCE", "La carta no define un efecto: " + card_id
        )
    return card


def create(state: dict, effect: dict, definitions) -> dict:
    """Crea una instancia con identidad y fecha de comienzo transaccionales."""
    card = _definition(definitions, effect["effect"])
    find(state, "characters", effect["target"])
    if card.get("stacking") == "unique_per_target" and any(
        item["target"] == effect["target"] and item["card"] == card["id"]
        for item in state["world"]["effects"]
    ):
        raise WorldError("EFFECT_ALREADY_ACTIVE", "El efecto único ya está activo")
    identifier = allocate_id(state, "effect", effect.get("instance_id"))
    instance = {
        "id": identifier,
        "card": card["id"],
        "target": effect["target"],
        "started_turn": state["turn"],
        "started_at": state["world_time"],
    }
    state["world"]["effects"].append(instance)
    return instance


def remove(state: dict, identifier: str, definitions) -> dict:
    """Retira la instancia solicitada una sola vez y devuelve su definición."""
    instance = next(
        (item for item in state["world"]["effects"] if item["id"] == identifier), None
    )
    if instance is None:
        raise WorldError("INVALID_REFERENCE", "Efecto inexistente: " + identifier)
    card = _definition(definitions, instance["card"])
    state["world"]["effects"].remove(instance)
    return {"instance": instance, "card": card}
