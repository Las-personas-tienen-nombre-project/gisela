"""Comprobación de capacidades dinámicas de las cartas de habilidad."""

from __future__ import annotations

from .errors import EngineFailure


def check_cards(package: dict) -> None:
    """Valida requisitos, resultados y políticas antes de iniciar sesión."""
    from .support import check_condition, check_effect

    windows = any(
        step["op"] == "skill_window"
        for node in package["nodes"]
        for step in node["steps"]
    )
    if windows and not package["initial_state"].get("player_character"):
        raise EngineFailure(
            "UNSUPPORTED_FORMAT",
            "Una ventana de habilidad requiere player_character explícito",
        )
    for card in package["cards"]:
        if card["kind"] != "skill":
            continue
        play = card["play"]
        if "requires" in play:
            check_condition(play["requires"])
        for effect in play["effects"]:
            check_effect(effect)
        for outcome in play.get("outcomes", []):
            check_condition(outcome["when"])
            for effect in outcome["effects"]:
                check_effect(effect)
        for entry in card.get("return_policy", {}).get("when", []):
            check_condition(entry["if"])
