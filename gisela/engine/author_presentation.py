"""Pure declarative projection over a *public* Observe document.

Never reads a session or an author-defined executable expression.
"""

from __future__ import annotations

import copy

ROOTS = frozenset(
    {
        "content",
        "actions",
        "actuation",
        "actors",
        "elements",
        "inventory",
        "skills",
        "effects",
        "cards",
        "quests",
        "annotations",
        "status",
        "scene",
        "scene_title",
        "scene_description",
        "world_time",
        "turn",
    }
)
COLLECTIONS = frozenset(
    {"entity_collection", "choice_list", "event_log", "initiative_order"}
)
CONTAINERS = frozenset({"section", "conditional"})
SCALARS = frozenset({"text", "stat", "meter", "entity_status"})
COMPONENTS = COLLECTIONS | CONTAINERS | SCALARS
MAX_DEPTH = 8
MAX_NODES = 64
MAX_ITEMS = 64
MISSING = object()


def read_public(view: dict, path: str):
    """Read a fixed, validated dot-path from a public observation only."""
    value = view
    for segment in path.split("."):
        if not isinstance(value, dict) or segment not in value:
            return MISSING
        value = value[segment]
    return value


def _project_item(node: dict, view: dict, depth: int) -> dict:
    kind = node["component"]
    if kind in CONTAINERS:
        return _project_container(node, view, depth)
    result = _region(node)
    value = read_public(view, node["source"]) if "source" in node else MISSING
    if kind == "text" and "text" in node:
        value = node["text"]
    if value is MISSING or value is None:
        return dict(result, missing=True, text="No disponible")
    if kind in COLLECTIONS:
        return _project_collection(result, value)
    if kind == "meter":
        return _project_meter(result, value, read_public(view, node["maximum"]))
    return _project_scalar(result, value)


def _region(node: dict) -> dict:
    return {
        "id": node["id"],
        "component": node["component"],
        "label": node.get("label", ""),
    }


def _project_container(node: dict, view: dict, depth: int) -> dict:
    result = _region(node)
    if node["component"] == "conditional":
        value = read_public(view, node["source"])
        if value is MISSING or not isinstance(value, bool) or not value:
            return dict(result, visible=False, children=[])
    result["children"] = [
        _project_item(child, view, depth + 1) for child in node.get("children", [])
    ]
    return result


def _project_collection(result: dict, value) -> dict:
    if not isinstance(value, list):
        return dict(result, missing=True, text="Tipo incompatible")
    items = value[:MAX_ITEMS]
    if result["component"] == "choice_list":
        items = [
            item for item in items if isinstance(item, dict) and item.get("enabled")
        ]
    result["items"] = copy.deepcopy(items)
    return result


def _project_meter(result: dict, value, maximum) -> dict:
    if not _number(value) or not _number(maximum) or maximum <= 0:
        return dict(result, missing=True, text="Magnitud no disponible")
    result.update(value=value, maximum=maximum, text=f"{value}/{maximum}")
    return result


def _project_scalar(result: dict, value) -> dict:
    kind = result["component"]
    if kind == "entity_status":
        if not isinstance(value, dict):
            return dict(result, missing=True, text="Tipo incompatible")
        result["value"] = copy.deepcopy(value)
    elif kind == "stat" and not _number(value) and not isinstance(value, str):
        return dict(result, missing=True, text="Tipo incompatible")
    else:
        result["text"] = str(value)[:1000]
    return result


def _number(value):
    return type(value) in (int, float)


def project(definition: dict, observation: dict) -> dict:
    """Deterministic, size-bounded, session-independent public projection."""
    return {
        "id": definition["id"],
        "regions": [
            _project_item(node, observation, 1) for node in definition["regions"]
        ],
    }
