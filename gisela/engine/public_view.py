"""Proyecciones para jugadores. La CLI no examina el mundo directamente.

Solo publica lo que pertenece al personaje o aparece en la escena visible.
Las definiciones ocultas, las creencias y los datos de otros personajes quedan
fuera de estas consultas. La autoridad de lectura es GISELA.
"""

from __future__ import annotations

from .projection import text
from .world_base import WorldError


def card_view(session, item: dict) -> dict:
    """Extrae los textos autorizados de una carta conocida."""
    card = session._cards[item["card"]]
    result = {
        "id": item["id"],
        "card": card["id"],
        "kind": card["kind"],
        "title": text(card["title"]),
    }
    if "description" in card:
        result["description"] = text(card["description"])
    return result


def owned(session) -> dict:
    """Proyecta las posesiones del jugador, sin consultar otros inventarios."""
    player = session._state.get("player_character")
    world = session._state["world"]
    inventory = [
        card_view(session, o) for o in world["objects"] if o.get("owner") == player
    ]
    skills = [
        dict(card_view(session, s), zone=s["zone"])
        for s in world["skills"]
        if s["character"] == player and s["zone"] != "discard"
    ]
    effects = [card_view(session, e) for e in world["effects"] if e["target"] == player]
    return {"inventory": inventory, "skills": skills, "effects": effects}


def _references(session, view: dict) -> tuple[dict, dict]:
    scene = session._scenes.get(session._state.get("current_scene"), {})
    actors = {
        a.get("public_id", a["character"]): a["character"]
        for a in scene.get("actors", [])
    }
    elements = {
        e.get("public_entity", e.get("entity")): e.get("entity")
        for e in scene.get("elements", [])
        if "entity" in e
    }
    return actors, elements


def _visible_ids(session, view: dict, references: tuple[dict, dict]) -> set[str]:
    actors, elements = references
    ids = {
        item["id"]
        for group in ("inventory", "skills", "effects")
        for item in view.get(group, [])
    }
    ids.update(actors.get(actor["id"], actor["id"]) for actor in view.get("actors", []))
    ids.update(
        elements.get(e["entity"], e["entity"])
        for e in view.get("elements", [])
        if "entity" in e
    )
    if session._state.get("player_character"):
        ids.add(session._state["player_character"])
    return ids


def _visible_card(session, item: dict, view: dict) -> dict:
    card = card_view(session, item)
    actors, elements = _references(session, view)
    actor = next(
        (
            a
            for a in view.get("actors", [])
            if actors.get(a["id"], a["id"]) == item["id"]
        ),
        None,
    )
    if actor:
        if actor.get("identity_hidden"):
            card["title"] = actor["name"]
            card.pop("description", None)
        card["id"] = card["card"] = actor["id"]
    visible = {e["entity"] for e in view.get("elements", []) if "entity" in e}
    for public, private in elements.items():
        if private == item["id"] and public in visible:
            card["id"] = card["card"] = public
    return card


def known(session, view: dict) -> list[dict]:
    """Enumera fichas autorizadas y aplica sus referencias públicas."""
    references = _references(session, view)
    ids = _visible_ids(session, view, references)
    return [
        _visible_card(session, item, view)
        for group in ("characters", "objects", "locations", "skills", "effects")
        for item in session._state["world"][group]
        if item["id"] in ids
    ]


def augment(session, view: dict) -> None:
    """Agrega información pública incluso durante una transacción pendiente."""
    view.update(owned(session))
    view["cards"] = known(session, view)


def inspect(session, identifier: str) -> dict:
    """Lee una ficha pública por ID sin acudir al API de depuración."""
    cards = known(session, session.observe())
    matches = [item for item in cards if item["id"] == identifier]
    if len(matches) != 1:
        raise WorldError("NOT_VISIBLE", "La carta no es conocida por el jugador")
    return matches[0].copy()


def status(session) -> dict:
    """Proyecta únicamente el Scoresheet del protagonista declarado."""
    player = session._state.get("player_character")
    if not player:
        return {"character": None, "stats": []}
    card = next(
        (c for c in session._state["world"]["characters"] if c["id"] == player), None
    )
    if card is None or "sofia" not in session._cards[card["card"]]:
        return {"character": player, "stats": []}
    from .sofia import scoresheet

    return scoresheet(session._state, player, session._definitions)
