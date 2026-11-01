"""Adaptación MARY a los borradores transaccionales. Solo GISELA confirma."""

from __future__ import annotations

from mary import evaluate as mary_evaluate

from .consequences import apply_operation
from .effect_context import EffectContext


def context(state: dict) -> dict:
    """Publica a MARY hechos y variables, sin referencias al mundo privado."""
    values = {
        "session." + key: value
        for key, value in state["narrative"]["session_variables"].items()
    }
    values.update(
        {
            "world." + key: value
            for key, value in state["world"]["world_variables"].items()
        }
    )
    return {
        "facts": [item["fact"] for item in state["history"]["facts"]],
        "values": values,
    }


def advance(state: dict, plan: dict | None, transaction) -> list[dict]:
    """Aplica yields autorizados al borrador; nunca confirma por cuenta propia."""
    if plan is None:
        return []
    result = mary_evaluate(plan, context(state), state.get("mary"))
    state["mary"] = result["progress"]
    events = []
    for item in result["yields"]:
        fact = item["effect"]["fact"]
        if fact in {row["fact"] for row in state["history"]["facts"]}:
            continue
        operation = {"op": "record_fact", "fact": fact}
        source = "mary." + item["source"].replace(":", ".")
        effect_context = EffectContext(
            source, transaction.decisions, transaction.definitions
        )
        events.extend(apply_operation(state, operation, effect_context))
    return events
