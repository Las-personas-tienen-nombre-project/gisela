"""Planifica escrituras declarativas de una ronda sobre un estado común.

Las operaciones no conmutativas se rechazan, nunca se ordenan por prioridad.
"""

from __future__ import annotations

import json
from math import fsum, isfinite

from .conditions import value
from .world_base import WorldError
from .world_values import read


def key(target: dict) -> str:
    """Identifica semánticamente un destino sin depender del orden de claves."""
    return json.dumps(target, ensure_ascii=False, sort_keys=True)


def _number(value) -> bool:
    """No confunde booleanos con enteros de Python."""
    return type(value) is int or (type(value) is float and isfinite(value))


def _aggregate(state: dict, group: list[tuple], definitions):
    """Combina sumas, consolida set iguales o comunica incompatibilidad."""
    kinds = {effect["op"] for _, _, effect in group}
    if len(kinds) != 1:
        raise WorldError("REACTION_CONFLICT", "set y add compiten por el mismo destino")
    vals = [value(state, effect["value"], definitions) for _, _, effect in group]
    if kinds == {"set"}:
        if any(
            (type(x) is not type(vals[0]) and not (_number(x) and _number(vals[0])))
            or x != vals[0]
            for x in vals[1:]
        ):
            raise WorldError("REACTION_CONFLICT", "Valores set diferentes en una ronda")
        return vals[0]
    previous = read(state, group[0][2]["target"], definitions)
    if not _number(previous) or not all(_number(x) for x in vals):
        raise WorldError("TYPE_MISMATCH", "add requiere valores numéricos")
    try:
        total = sum(vals) if all(type(x) is int for x in vals) else fsum(vals)
    except (OverflowError, ValueError) as exc:
        raise WorldError("PROPERTY_RANGE", "Suma no representable") from exc
    result = previous + total
    if not _number(result):
        raise WorldError("PROPERTY_RANGE", "Suma no finita")
    return result


def prepare(state: dict, enabled: list[dict], definitions) -> dict:
    """Precalcula las escrituras de toda la ronda desde su mismo estado base."""
    groups = {}
    for rule in enabled:
        for index, effect in enumerate(rule["effects"]):
            if effect["op"] in ("set", "add"):
                groups.setdefault(key(effect["target"]), []).append(
                    (rule["id"], index, effect)
                )
    plan = {}
    for group in groups.values():
        computed = _aggregate(state, group, definitions)
        for offset, (rule_id, index, effect) in enumerate(group):
            plan[(rule_id, index)] = (
                (effect["target"], computed) if offset == 0 else None
            )
    return plan
