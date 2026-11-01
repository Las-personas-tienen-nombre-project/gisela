"""Consultas diagnósticas de mundo confirmado, exclusivas para autores.

No forman parte de Observe del jugador. Su resultado puede contener datos
narrativos ocultos, por lo que el anfitrión debe exigir modo de desarrollo.
"""

from __future__ import annotations

import copy

from .world_base import WorldError, find, instance
from .world_values import read


def _character(session, request: dict) -> dict:
    """Entrega conocimiento, posesiones y habilidades de un personaje."""
    state = session._state
    actor = copy.deepcopy(find(state, "characters", request["character"]))
    identifier = actor["id"]
    actor["objects"] = [
        o["id"] for o in state["world"]["objects"] if o.get("owner") == identifier
    ]
    actor["skills"] = [
        {"id": s["id"], "card": s["card"], "zone": s["zone"]}
        for s in state["world"]["skills"]
        if s["character"] == identifier
    ]
    return actor


def _typed(session, request: dict) -> dict:
    """Resuelve propiedades y relaciones sin crear entradas nuevas."""
    name = request["kind"]
    if name == "property":
        ref = {"property": {"entity": request["entity"], "key": request["key"]}}
    else:
        ref = {
            "relationship": {
                "from": request["from"],
                "to": request["to"],
                "key": request["key"],
            }
        }
    value = read(session._state, ref, session._definitions)
    return {"query": copy.deepcopy(ref), "value": copy.deepcopy(value)}


def query(session, request: dict) -> dict:
    """Devuelve una copia diagnóstica del estado confirmado, nunca su borrador."""
    if not isinstance(request, dict) or not isinstance(request.get("kind"), str):
        raise WorldError("INVALID_QUERY", "Consulta diagnóstica inválida")
    kind = request["kind"]
    required = {
        "character": {"character"},
        "entity": {"entity"},
        "property": {"entity", "key"},
        "relationship": {"from", "to", "key"},
        "scoresheet": {"character"},
        "facts": set(),
    }
    if kind not in required or set(request) != required[kind] | {"kind"}:
        raise WorldError(
            "INVALID_QUERY", "Campos de consulta desconocidos o incompletos"
        )
    if kind == "character":
        return _character(session, request)
    if kind == "entity":
        return copy.deepcopy(instance(session._state, request["entity"])[1])
    if kind in ("property", "relationship"):
        return _typed(session, request)
    if kind == "scoresheet":
        return session.scoresheet(request["character"])
    return {"facts": copy.deepcopy(session._state["history"]["facts"])}
