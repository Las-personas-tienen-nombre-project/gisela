"""Evaluaciones enfrentadas declarativas con S.O.F.I.A., TRAITS y DICE.

Ningún concepto de ataque, turno o daño forma parte del resolvedor.
La ejecución y las consecuencias ocurren dentro del borrador causal exterior.
"""

from __future__ import annotations

from dice import DiceError
from traits import TraitsError

from .conditions import value
from .effect_context import EffectContext
from .traits_dice_bridge import resolve
from .world_base import WorldError


def execute(state: dict, operation: dict, context: EffectContext) -> list[dict]:
    from .consequences import apply_operation

    profile = context.definitions.dice_profiles.get(operation["profile"])
    if profile is None:
        raise WorldError("INVALID_STATE", "Perfil DICE inexistente")
    results = []
    for side in ("left", "right"):
        spec = operation[side]
        base = value(state, spec["base"], context.definitions)
        if type(base) is not int or abs(base) > 1000000:
            raise WorldError("TYPE_MISMATCH", "La evaluación requiere base entera")
        ctx = spec.get("context", {})
        request = {
            "profile": profile,
            "base": base,
            "difficulty": 0,
            "tags": ctx.get("tags", []),
            "participants": ctx.get("participants", []),
        }
        try:
            computed = resolve(state, request, context.definitions)
        except (DiceError, TraitsError, OverflowError) as exc:
            raise WorldError("INVALID_STATE", f"Evaluación inválida: {exc}") from exc
        state["rng"] = computed["rng_after"]
        results.append(computed)
    lhs, rhs = (r["dice"]["total"] for r in results)
    won = lhs > rhs or (lhs == rhs and operation.get("tie_favors", "right") == "left")
    sequence = len(state["history"]["facts"]) + len(state["history"]["trace"]) + 1
    state["history"]["trace"].append(
        {
            "sequence": sequence,
            "kind": "contest_resolved",
            "source": context.source,
            "detail": {
                "profile": operation["profile"],
                "winner": "left" if won else "right",
                "left": results[0]["dice"],
                "right": results[1]["dice"],
                "left_traits": results[0]["traits"]["contributions"],
                "right_traits": results[1]["traits"]["contributions"],
            },
        }
    )
    events = []
    for effect in operation["on_win" if won else "on_lose"]:
        events.extend(apply_operation(state, effect, context))
    return events
