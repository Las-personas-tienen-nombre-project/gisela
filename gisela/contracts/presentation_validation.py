"""Static checks for safe authorial presentation paths and complexity."""

from __future__ import annotations

import re

from gisela.engine.author_presentation import COMPONENTS, CONTAINERS, ROOTS

_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,95}$")
_SEGMENT = re.compile(r"^[a-z][a-z0-9_]*$")


def errors(definition: dict) -> list[str]:
    """Return deterministic diagnostics, never executing author expressions."""
    problems = []
    count = 0
    seen = set()

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
        kind = node["component"]
        if kind not in COMPONENTS:
            problems.append("Componente desconocido: " + kind)
        for field in ("source", "maximum"):
            path = node.get(field)
            if path is None:
                continue
            segments = path.split(".")
            if (
                segments[0] not in ROOTS
                or any(not _SEGMENT.fullmatch(part) for part in segments)
                or len(segments) > 8
            ):
                problems.append("Ruta pública no autorizada: " + path)
        if kind == "meter" and "maximum" not in node:
            problems.append("meter requiere maximum")
        if kind == "conditional" and "source" not in node:
            problems.append("conditional requiere source")
        if kind not in CONTAINERS and "children" in node:
            problems.append("Hijos en componente no contenedor")
        if kind not in CONTAINERS and kind != "text" and "source" not in node:
            problems.append("Falta source en " + identifier)
        if kind == "text" and ("text" in node) == ("source" in node):
            problems.append("text requiere exactamente text o source")
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
