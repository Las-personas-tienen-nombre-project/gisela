"""Atributos opcionales de S.O.F.I.A. y modificadores calculados.

ALBERTO resuelve datos declarados. No guarda valores derivados ni confirma
transacciones; esa responsabilidad pertenece a GISELA.
"""

from __future__ import annotations

from .world_base import WorldError, find

NAMES = ("strength", "openness", "fortune", "intelligence", "awareness")


def _character(state: dict, identifier: str, definitions):
    """Resuelve un personaje con una carta S.O.F.I.A. declarada."""
    actor = find(state, "characters", identifier)
    card = definitions.cards[actor["card"]]
    if "sofia" not in card:
        raise WorldError("INVALID_REFERENCE", "El personaje no tiene S.O.F.I.A.")
    return actor, card


def _modifier(state: dict, ref: dict, definitions) -> int:
    """Suma modificadores declarados de efectos activos, sin aplicarlos."""
    total = 0
    for effect in state["world"]["effects"]:
        if effect["target"] != ref["character"]:
            continue
        card = definitions.cards[effect["card"]]
        for mod in card.get("modifiers", []):
            if mod["stat"] == ref["name"]:
                total += mod["amount"]
    return total


def components(state: dict, ref: dict, definitions) -> dict:
    """Devuelve base, actual y efectivo, sin modificar el estado confirmado."""
    actor, card = _character(state, ref["character"], definitions)
    name = ref["name"]
    if name not in NAMES:
        raise WorldError("INVALID_REFERENCE", "Atributo S.O.F.I.A. desconocido")
    base = card["sofia"][name]
    current = actor.get("stats", {}).get(name, base)
    modifier = _modifier(state, {"character": actor["id"], "name": name}, definitions)
    return {
        "name": name,
        "base": base,
        "current": current,
        "modifier": modifier,
        "effective": current + modifier,
    }


def read(state: dict, ref: dict, definitions) -> int:
    """Resuelve el componente solicitado sin aceptar componentes arbitrarios."""
    row = components(state, ref, definitions)
    component = ref["component"]
    if component not in ("base", "current", "effective"):
        raise WorldError("INVALID_REFERENCE", "Componente S.O.F.I.A. desconocido")
    return row[component]


def write(state: dict, assignment: dict, definitions) -> list[dict]:
    """Modifica únicamente current dentro del borrador transaccional."""
    ref, value = assignment["ref"], assignment["value"]
    if ref["component"] != "current":
        raise WorldError("INVALID_STATE", "Solo current admite escrituras")
    actor, card = _character(state, ref["character"], definitions)
    if type(value) is not int:
        raise WorldError("TYPE_MISMATCH", "S.O.F.I.A. exige enteros")
    scale = definitions.scale
    if not scale["min"] <= value <= scale["max"]:
        raise WorldError("STAT_RANGE", "Atributo actual fuera de escala")
    name = ref["name"]
    previous = actor.get("stats", {}).get(name, card["sofia"][name])
    if previous == value:
        return []
    if value == card["sofia"][name]:
        actor.get("stats", {}).pop(name, None)
        if not actor.get("stats"):
            actor.pop("stats", None)
    else:
        actor.setdefault("stats", {})[name] = value
    return [{"on": "state_changed", "target": {"stat": ref}}]


def scoresheet(state: dict, identifier: str, definitions) -> dict:
    """Proyecta el Scoresheet desde el estado confirmado."""
    _character(state, identifier, definitions)
    stats = [
        components(state, {"character": identifier, "name": name}, definitions)
        for name in NAMES
    ]
    skills = [s for s in state["world"]["skills"] if s["character"] == identifier]
    effects = [e for e in state["world"]["effects"] if e["target"] == identifier]
    active = [{"instance_id": e["id"], "card": e["card"]} for e in effects]
    return {
        "session_id": state["session_id"],
        "revision": state["revision"],
        "character": identifier,
        "stats": stats,
        "active_effects": active,
        "hand": [s["id"] for s in skills if s["zone"] == "hand"],
        "reserve": [s["id"] for s in skills if s["zone"] == "reserve"],
    }
