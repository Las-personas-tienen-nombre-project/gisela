"""Static checks for safe authorial presentation paths and complexity."""

from __future__ import annotations

import re

from gisela.engine.author_presentation import COMPONENTS, CONTAINERS, ROOTS

from .presentation_views_validation import errors as view_errors

_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,95}$")
_SEGMENT = re.compile(r"^[a-z][a-z0-9_]*$")


def errors(definition: dict) -> list[str]:
    """Return deterministic diagnostics, never executing author expressions."""
    problems = view_errors(definition)
    count = 0
    seen = set()
    views = {view["id"]: view for view in definition.get("views", [])}

    def visit(node, depth):
        nonlocal count
        count += 1
        if count > 64 or depth > 8:
            problems.append("Límite de nodos o profundidad excedido")
            return
        identifier = node["id"]
        if identifier in seen:
            problems.append("Identificador de región duplicado: " + identifier)
        seen.add(identifier)
        problems.extend(_node_errors(node, views))
        for child in node.get("children", []):
            visit(child, depth + 1)

    target_skills = set()
    for item in definition.get("action_targets", []):
        if item["skill"] in target_skills:
            problems.append("Destino duplicado: " + item["skill"])
        target_skills.add(item["skill"])
    for region in definition["regions"]:
        visit(region, 1)
    return problems


def _node_errors(node: dict, views: dict) -> list[str]:
    problems = _path_errors(node)
    kind = node["component"]
    if kind not in COMPONENTS:
        problems.append("Componente desconocido: " + kind)
    if "view" in node:
        view = views.get(node["view"])
        if view is None or view["component"] != kind:
            problems.append("Vista ausente o incompatible: " + node["view"])
        if kind not in {"table", "event_log"} or "source" in node:
            problems.append("Referencia de vista no permitida en " + node["id"])
    elif kind == "table":
        problems.append("table requiere view")
    elif kind not in CONTAINERS and kind != "text" and "source" not in node:
        problems.append("Falta source en " + node["id"])
    if kind == "meter" and "maximum" not in node:
        problems.append("meter requiere maximum")
    if kind == "conditional" and "source" not in node:
        problems.append("conditional requiere source")
    if kind not in CONTAINERS and "children" in node:
        problems.append("Hijos en componente no contenedor")
    if kind == "text" and ("text" in node) == ("source" in node):
        problems.append("text requiere exactamente text o source")
    return problems


def _path_errors(node: dict) -> list[str]:
    problems = []
    for field in ("source", "maximum"):
        path = node.get(field)
        if path is None:
            continue
        segments = path.split(".")
        if (
            segments[0] not in ROOTS
            or len(segments) > 8
            or any(not _SEGMENT.fullmatch(part) for part in segments)
        ):
            problems.append("Ruta pública no autorizada: " + path)
    return problems
