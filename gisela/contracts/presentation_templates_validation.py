"""Closed, statically checked authorial templates over public causal fields."""

from __future__ import annotations

import string

FIELDS = {
    "initiative": frozenset({"order"}),
    "event_triggered": frozenset({"event"}),
    "encounter_completed": frozenset({"outcome"}),
    "dice_roll": frozenset({"sides", "result", "store"}),
    "contest_resolved": frozenset({"profile", "winner", "left_total", "right_total"}),
    "variable_changed": frozenset({"variable", "before", "after"}),
    "skill_started": frozenset({"card", "actor", "origin"}),
    "skill_played": frozenset({"card", "actor", "origin"}),
    "author_message": frozenset({"text"}),
}
ROLES = frozenset({"damage", "healing", "buff", "debuff", "neutral"})


def errors(view: dict, location: str) -> list[str]:
    """Validate templates without evaluating author-provided expressions."""
    problems = []
    seen = set()
    for index, item in enumerate(view.get("event_formats", [])):
        where = f"{location}/event_formats/{index}"
        key = (item["kind"], item.get("variable"))
        if key in seen:
            problems.append(f"{where}: formato duplicado")
        seen.add(key)
        if item["kind"] not in FIELDS:
            problems.append(f"{where}: clase no pública")
            continue
        if item.get("role", "neutral") not in ROLES:
            problems.append(f"{where}: rol inválido")
        if "variable" in item and item["kind"] != "variable_changed":
            problems.append(f"{where}: variable solo admite variable_changed")
        if "template" in item:
            problems.extend(
                _template_errors(item["template"], FIELDS[item["kind"]], where)
            )
    return problems


def _template_errors(template: str, fields: frozenset, where: str) -> list[str]:
    problems = []
    try:
        parts = list(string.Formatter().parse(template))
    except ValueError:
        return [f"{where}: plantilla malformada"]
    if sum(field is not None for _, field, _, _ in parts) > 16:
        problems.append(f"{where}: demasiadas sustituciones")
    for _, field, spec, conversion in parts:
        if field is not None and (field not in fields or spec or conversion):
            problems.append(f"{where}: campo o formato no permitido: {field}")
    return problems
