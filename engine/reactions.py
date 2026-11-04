"""Rondas reactivas deterministas de una sola transacción GISELA."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass

from .conditions import predicate
from .consequences import apply_operation
from .effect_context import EffectContext
from .expiration import due
from .reaction_nested import check as check_nested
from .reaction_writes import prepare
from .world import writable_key
from .world_base import WorldError

MAX_ROUNDS = 32


@dataclass(frozen=True)
class ReactionContext:
    """Definiciones y respuestas comunes a las rondas de una cadena."""

    rules: list[dict]
    decisions: object
    definitions: object
    progression: object = None


def _matches(trigger: dict, event: dict) -> bool:
    """Comprueba el evento causal sin ejecutar ninguna regla."""
    if trigger["on"] != event["on"]:
        return False
    if trigger["on"] in ("fact_recorded", "node_completed"):
        key = "fact" if trigger["on"] == "fact_recorded" else "node"
        return trigger[key] == event[key]
    if trigger["on"] == "effect_expired":
        return trigger["effect"] == event["effect"]
    if trigger["on"] == "state_changed":
        return trigger["target"] == event["target"]
    return trigger["on"] in ("turn_started", "turn_ended")


def _enabled(state: dict, events: list[dict], context: ReactionContext) -> list[dict]:
    """Selecciona reglas contra una misma instantánea de la ronda."""
    base = copy.deepcopy(state)
    result = [
        r
        for r in context.rules
        if r.get("enabled", True)
        and any(_matches(r["trigger"], event) for event in events)
        and predicate(base, r.get("when", {"constant": True}), context.definitions)
    ]
    return sorted(result, key=lambda rule: rule["id"])


def _removed_targets(enabled: list[dict]) -> None:
    """Rechaza retiro y utilización de una misma instancia entre reglas."""
    removals = [
        (rule["id"], effect["instance"])
        for rule in enabled
        for effect in rule["effects"]
        if effect["op"] == "remove_instance"
    ]
    fields = (
        "character",
        "location",
        "object",
        "from",
        "to",
        "owner",
        "instance",
        "skill_instance",
        "target",
    )
    for owner, identifier in removals:
        for rule in enabled:
            if rule["id"] == owner:
                continue
            if any(
                effect.get(field) == identifier
                for effect in rule["effects"]
                for field in fields
                if isinstance(effect.get(field), str)
            ):
                raise WorldError(
                    "REACTION_CONFLICT",
                    f"Las reglas {owner} y {rule['id']} utilizan {identifier}",
                )


def _conflicts(state: dict, enabled: list[dict], definitions) -> None:
    """Rechaza destinos no combinables y referencias retiradas en una ronda."""
    _removed_targets(enabled)
    check_nested(state, enabled, definitions)
    owners = {}
    for rule in enabled:
        for effect in rule["effects"]:
            target = writable_key(effect)
            if target is None:
                continue
            previous = owners.get(target)
            if (
                previous
                and previous[0] != rule["id"]
                and (
                    effect["op"] not in ("set", "add")
                    or previous[1] not in ("set", "add")
                )
            ):
                raise WorldError(
                    "REACTION_CONFLICT",
                    f"Las reglas {previous[0]} y {rule['id']} escriben {target}",
                )
            owners[target] = (rule["id"], effect["op"])


def _apply(state: dict, enabled: list[dict], context: ReactionContext) -> list[dict]:
    """Aplica un único cambio por destino y conserva la traza causal."""
    plan = prepare(state, enabled, context.definitions)
    events = []
    for rule in enabled:
        sequence = len(state["history"]["facts"]) + len(state["history"]["trace"]) + 1
        state["history"]["trace"].append(
            {"sequence": sequence, "kind": "rule_fired", "source": rule["id"]}
        )
        for index, effect in enumerate(rule["effects"]):
            if effect["op"] in ("set", "add"):
                entry = plan[(rule["id"], index)]
                if entry is None:
                    continue
                target, result = entry
                effect = {"op": "set", "target": target, "value": {"literal": result}}
            events.extend(
                apply_operation(
                    state,
                    effect,
                    EffectContext(rule["id"], context.decisions, context.definitions),
                )
            )
    return events


def _fingerprint(state: dict, events: list[dict]) -> str:
    """Detecta rondas repetidas por estado y sucesos, no por tiempo real."""
    return json.dumps(
        {
            "events": events,
            "world": state["world"],
            "variables": state["narrative"]["session_variables"],
            "time": state["world_time"],
            "rng": state["rng"],
        },
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )


def settle(state: dict, events: list[dict], context: ReactionContext) -> None:
    """Resuelve la cadena, o rechaza todo el borrador si no converge."""
    seen = set()
    events = [{"on": "causal_boundary"}, *events]
    for _ in range(MAX_ROUNDS):
        if not events:
            return
        fingerprint = _fingerprint(state, events)
        if fingerprint in seen:
            raise WorldError("REACTION_CYCLE", "La cadena reactiva repite un estado")
        seen.add(fingerprint)
        enabled = _enabled(state, events, context)
        if enabled:
            _conflicts(state, enabled, context.definitions)
            produced = _apply(state, enabled, context)
        else:
            produced = []
        from .mary_bridge import advance

        produced.extend(advance(state, context.progression, context))
        expired = due(state, events + produced, context.definitions)
        for identifier in expired:
            produced.extend(
                apply_operation(
                    state,
                    {"op": "end_effect", "effect_instance": identifier},
                    EffectContext("expiration", context.decisions, context.definitions),
                )
            )
        if not produced:
            return
        events = produced
    raise WorldError("BUDGET_EXCEEDED", "Se superó el límite de rondas reactivas")
