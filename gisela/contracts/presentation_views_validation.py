"""Admission rules for named, typed and bounded public presentation views."""

from __future__ import annotations

from gisela.engine.causal_trace import VISIBLE

SOURCES = {
    "actuation.resources",
    "actuation.participants",
    "actuation.effects",
    "actors",
}
EVENT_SOURCE = "actuation.causal"


def errors(definition: dict) -> list[str]:
    problems = []
    seen = set()
    for index, view in enumerate(definition.get("views", [])):
        location = f"views/{index}"
        identifier = view["id"]
        if identifier in seen:
            problems.append(f"{location}: vista duplicada")
        seen.add(identifier)
        component = view["component"]
        source = view["source"]
        allowed = SOURCES if component == "table" else {EVENT_SOURCE}
        if source not in allowed:
            problems.append(f"{location}: fuente pública no permitida: {source}")
        if component == "table":
            problems.extend(_table_errors(view, location))
        elif component == "event_log":
            from .presentation_templates_validation import errors as template_errors

            problems.extend(template_errors(view, location))
            if view.get("group_by") not in (None, "action"):
                problems.append(f"{location}: agrupación inválida")
            if any(kind not in VISIBLE for kind in view.get("kinds", [])):
                problems.append(f"{location}: clase de acontecimiento inválida")
            if view.get("filter_field") not in (None, "kind", "source"):
                problems.append(f"{location}: filtro no autorizado")
            if ("filter_field" in view) != ("filter_value" in view):
                problems.append(f"{location}: filtro incompleto")
        else:
            problems.append(f"{location}: componente de vista desconocido")
    return problems


def _table_errors(view: dict, location: str) -> list[str]:
    problems = []
    if "group_by" in view:
        problems.append(f"{location}: agrupación causal solo admite eventos")
    columns = view["columns"]
    identifiers = [col["id"] for col in columns]
    if len(set(identifiers)) != len(identifiers):
        problems.append(f"{location}: columnas duplicadas")
    if view.get("transform") == "pivot_resources":
        if view["source"] != "actuation.resources":
            problems.append(f"{location}: pivot_resources requiere recursos públicos")
    elif "transform" in view:
        problems.append(f"{location}: transformación desconocida")
    elif view["source"] == "actuation.resources":
        if any(key not in {"entity", "id", "value", "maximum"} for key in identifiers):
            problems.append(f"{location}: campo no público de recursos")
    elif view["source"] == "actuation.participants":
        if any(key != "id" for key in identifiers):
            problems.append(f"{location}: campo no público de participantes")
    elif view["source"] == "actuation.effects":
        if any(key not in {"id", "beneficiary", "remaining"} for key in identifiers):
            problems.append(f"{location}: campo no público de efectos")
    elif view["source"] == "actors" and any(
        key not in {"id", "name", "color"} for key in identifiers
    ):
        problems.append(f"{location}: campo no público de actores")
    return problems
