"""Resuelve presentación pública y disposición privada sin mutar la sesión."""

from __future__ import annotations

from math import isfinite

from .world_values import read

COLORS = frozenset(
    {"default", "red", "yellow", "green", "cyan", "blue", "magenta", "white"}
)
CATEGORIES = ("hostile", "unfriendly", "neutral", "friendly", "very_friendly")
DEFAULT_CUTS = (-60, -20, 20, 60)


def explicit_color(
    instance: dict, card: dict, scene_item: dict
) -> tuple[str | None, str]:
    """Devuelve rol y procedencia según la precedencia declarada."""
    dynamic = instance.get("properties", {}).get("presentation_color", "inherit")
    if dynamic != "inherit":
        return dynamic, "instance"
    for source, item in (("scene", scene_item), ("card", card)):
        value = item.get("presentation", {}).get("color")
        if value is not None:
            return value, source
    return None, "theme"


def disposition(session, actor_id: str) -> dict:
    """Calcula afinidad dirigida efectiva para diagnóstico privilegiado."""
    config = session._package["manifest"].get("disposition_display")
    result = {"category": "unknown", "normalized": None, "value": None, "scale": config}
    player = session._state.get("player_character")
    if not config or not player:
        return result
    field = config["field"]
    spec = session._definitions.relations.get(field)
    if spec is None or spec["type"] not in ("integer", "number"):
        return result
    value = read(
        session._state,
        {"relationship": {"from": actor_id, "to": player, "key": field}},
        session._definitions,
    )
    if type(value) not in (int, float) or not isfinite(value):
        return result
    low, mid, high = (config[key] for key in ("minimum", "neutral", "maximum"))
    normalized = (
        -100 * (mid - max(low, min(value, mid))) / (mid - low)
        if value <= mid
        else 100 * (min(high, max(value, mid)) - mid) / (high - mid)
    )
    cuts = config.get("thresholds", DEFAULT_CUTS)
    if normalized < cuts[0]:
        category = "hostile"
    elif normalized < cuts[1]:
        category = "unfriendly"
    elif normalized <= cuts[2]:
        category = "neutral"
    elif normalized <= cuts[3]:
        category = "friendly"
    else:
        category = "very_friendly"
    result.update(value=value, normalized=normalized, category=category)
    return result
