"""Proyección causal ordenada de acontecimientos CONFIRMADOS del encuentro.

No ejecuta tiradas, no interpreta texto narrativo y no toca el RNG.
"""

from __future__ import annotations

VISIBLE = {
    "initiative",
    "event_triggered",
    "encounter_completed",
    "skill_started",
    "skill_played",
    "dice_roll",
    "contest_resolved",
    "author_message",
    "variable_changed",
}


def correlate(event: dict, context) -> None:
    """Etiqueta solo un registro producido por un contexto explícito de habilidad."""
    if context.causal_execution_id is not None:
        event["causal_execution_id"] = context.causal_execution_id


def record_actuation(state, kind, detail):
    """Registra el hito autoral en la misma cronología transaccional."""
    trace = state["history"]["trace"]
    trace.append(
        {
            "sequence": len(state["history"]["facts"]) + len(trace) + 1,
            "kind": kind,
            "source": "actuation",
            "detail": detail,
        }
    )


def variable_snapshot(state, effect):
    """Captura una variable numérica declarada antes de la mutación."""
    from .world import var_access

    target = effect.get("target", {})
    if not isinstance(target, dict) or "var" not in target:
        return None
    reference = target["var"]
    if reference.get("scope") != "session":
        return None
    owner, key = var_access(state, reference)
    previous = owner[key]
    if type(previous) not in (int, float):
        return None
    return key, previous


def record_variable(state, snapshot, context):
    """Registra diferencias después de una operación ALBERTO ya aceptada."""
    if snapshot is None:
        return
    from .world import var_access

    key, before = snapshot
    owner, _ = var_access(state, {"scope": "session", "key": key})
    after = owner[key]
    if before == after:
        return
    history = state["history"]
    history["trace"].append(
        {
            "sequence": len(history["facts"]) + len(history["trace"]) + 1,
            "kind": "variable_changed",
            "source": context.source,
            "detail": {"variable": key, "before": before, "after": after},
        }
    )
    correlate(history["trace"][-1], context)


def project(state, limit=40):
    """Orden y procedencia de hechos sin datos de RNG ni TRAITS privados."""
    entries = []
    allowed = set(state.get("actuation", {}).get("public_trace_variables", []))
    for event in state["history"]["trace"]:
        kind = event.get("kind")
        if kind not in VISIBLE:
            continue
        detail = event.get("detail", {})
        if kind == "variable_changed" and detail.get("variable") not in allowed:
            continue
        public = _detail(kind, detail)
        entries.append(
            {
                "sequence": event.get("sequence", 0),
                "kind": kind,
                "source": str(event.get("source", "")),
                "detail": public,
            }
        )
        if "causal_execution_id" in event:
            entries[-1]["causal_execution_id"] = event["causal_execution_id"]
    return entries[-limit:]


def _detail(kind, detail):
    if kind == "initiative":
        return {"order": ", ".join(detail["order"])}
    if kind == "event_triggered":
        return {"event": detail["event"]}
    if kind == "encounter_completed":
        return {"outcome": detail["outcome"]}
    if kind == "dice_roll":
        fields = ("sides", "result", "store")
    elif kind == "variable_changed":
        fields = ("variable", "before", "after")
    elif kind == "contest_resolved":
        return {
            "profile": detail["profile"],
            "winner": detail["winner"],
            "left_total": detail["left"]["total"],
            "right_total": detail["right"]["total"],
        }
    elif kind in ("skill_started", "skill_played"):
        fields = ("card", "actor", "origin")
    else:
        fields = ("text",)
    return {key: detail[key] for key in fields if key in detail}
