"""Interprete de consecuencias. Responsable único del historial de hechos.

Dirige cambios del mundo hacia ALBERTO y registra hechos en GISELA.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from gisela.contracts.rng import RNGState, draw

from .effect_context import EffectContext
from .world import WorldError, var_access
from .world import apply_operation as apply_world_operation
from .world_effects import create as create_effect
from .world_effects import remove as remove_effect


def apply_operation(state: dict, effect: dict, context: EffectContext) -> list[dict]:
    """Registra hechos en GISELA o delega mutaciones de mundo a ALBERTO.

    Opera sobre el borrador causal y devuelve sucesos para las reacciones.
    La confirmación y el descarte del borrador pertenecen al runtime.
    """
    if effect["op"] == "emit_message":
        return _emit_message(state, effect, context)
    if effect["op"] == "contest":
        from .contest_execution import execute

        return execute(state, effect, context)
    if effect["op"] == "play_skill":
        from .skill_execution import execute_scripted

        return execute_scripted(state, effect, context)
    if effect["op"] == "play_first_skill":
        from .skill_execution import execute_first_available

        return execute_first_available(state, effect, context)
    if effect["op"] == "apply_effect":
        return _apply_effect(state, effect, context)
    if effect["op"] == "end_effect":
        return _end_effect(state, effect["effect_instance"], context)
    if effect["op"] == "roll":
        return _roll(state, effect, context)
    if effect["op"] == "advance_time":
        try:
            current = datetime.fromisoformat(state["world_time"].replace("Z", "+00:00"))
            updated = current + timedelta(minutes=effect["minutes"])
        except (ValueError, OverflowError) as exc:
            raise WorldError(
                "INVALID_TIME", "El reloj excede el intervalo admisible"
            ) from exc
        state["world_time"] = updated.isoformat()
        return [{"on": "clock_advanced"}]
    if effect["op"] == "record_fact":
        sequence = len(state["history"]["facts"]) + len(state["history"]["trace"]) + 1
        fact = {"sequence": sequence, "fact": effect["fact"], "source": context.source}
        if "payload" in effect:
            fact["payload"] = effect["payload"]
        state["history"]["facts"].append(fact)
        return [{"on": "fact_recorded", "fact": effect["fact"]}]
    from .causal_trace import record_variable, variable_snapshot

    snapshot = (
        variable_snapshot(state, effect)
        if effect["op"] in ("set", "add") and "actuation" in state
        else None
    )
    events = apply_world_operation(state, effect, context)
    if snapshot is not None:
        record_variable(state, snapshot, context)
    if effect["op"] in ("set", "add") and "actuation" in state:
        from .actuation import resolve_policies

        resolve_policies(state, context.definitions, "immediate")
    return events


def _roll(state: dict, effect: dict, context: EffectContext) -> list[dict]:
    """Consume una tirada exclusivamente en el borrador transaccional."""
    # El RNG es responsabilidad de GISELA. Se consume en el borrador,
    # nunca en la sesión confirmada mientras haya una espera o un error.
    target = effect["store"]
    if "var" not in target:
        raise WorldError("UNSUPPORTED_FORMAT", "roll solo escribe variables declaradas")
    owner, key = var_access(state, target["var"])
    if type(owner[key]) not in (int, float):
        raise WorldError("INVALID_STATE", "roll requiere variable numérica")
    try:
        result, new_rng = draw(RNGState(**state["rng"]), effect["sides"])
    except (ValueError, OverflowError) as exc:
        raise WorldError("INVALID_RNG", str(exc)) from exc
    previous = owner[key]
    owner[key] = result
    state["rng"] = new_rng.as_json()
    # El historial vive en el borrador: una transacción rechazada no publica
    # tiradas ni consume RNG. Solo se expone el resultado, no el estado RNG.
    sequence = len(state["history"]["facts"]) + len(state["history"]["trace"]) + 1
    state["history"]["trace"].append(
        {
            "sequence": sequence,
            "kind": "dice_roll",
            "source": context.source,
            "detail": {
                "sides": effect["sides"],
                "result": result,
                "store": target["var"]["scope"] + ":" + target["var"]["key"],
            },
        }
    )
    if previous != result:
        return [{"on": "state_changed", "target": target}]
    return []


def _children(
    state: dict, operations: list[dict], context: EffectContext
) -> list[dict]:
    """Ejecuta consecuencias declaradas dentro del mismo borrador causal."""
    events = []
    for operation in operations:
        events.extend(apply_operation(state, operation, context))
    return events


def _apply_effect(state: dict, effect: dict, context: EffectContext) -> list[dict]:
    """Instancia un efecto y ejecuta su on_apply una sola vez."""
    instance = create_effect(state, effect, context.definitions)
    card = context.definitions.cards[instance["card"]]
    if "actuation_turns" in card and "actuation" in state:
        from .actuation import ActuationDuration, add_duration

        add_duration(
            state,
            ActuationDuration(
                instance["id"], instance["target"], card["actuation_turns"]
            ),
            linked=True,
        )
    if instance.get("_refreshed"):
        return [{"on": "effect_refreshed"}]
    child = EffectContext(
        context.source,
        context.decisions,
        context.definitions,
        skill_depth=context.skill_depth,
    )
    return [{"on": "effect_applied"}] + _children(
        state, card.get("on_apply", []), child
    )


def _end_effect(state: dict, identifier: str, context: EffectContext) -> list[dict]:
    """Termina un efecto y produce sus consecuencias sin duplicarlas."""
    info = remove_effect(state, identifier, context.definitions)
    child = EffectContext(
        context.source,
        context.decisions,
        context.definitions,
        skill_depth=context.skill_depth,
    )
    return [{"on": "effect_expired", "effect": info["card"]["id"]}] + _children(
        state, info["card"].get("on_expire", []), child
    )


def _emit_message(state: dict, effect: dict, context: EffectContext) -> list[dict]:
    """Representa un aviso autoral usando solamente valores confirmables.

    No interpreta expresiones Python ni revela un borrador antes del commit.
    """
    import re

    from .conditions import value
    from .reading_log import append

    template = effect["template"]
    names = re.findall(r"\{([a-z][a-z0-9_]*)\}", template)
    if set(names) != set(effect["values"]):
        raise WorldError(
            "INVALID_ACTION", "Marcadores y valores del mensaje no coinciden"
        )
    remainder = re.sub(r"\{[a-z][a-z0-9_]*\}", "", template)
    if "{" in remainder or "}" in remainder:
        raise WorldError("INVALID_ACTION", "Formato de mensaje no permitido")
    values = {
        name: value(state, expression, context.definitions)
        for name, expression in effect["values"].items()
    }
    if any(type(x) not in (int, float, str, bool) for x in values.values()):
        raise WorldError("TYPE_MISMATCH", "El aviso requiere valores escalares")
    message = re.sub(
        r"\{([a-z][a-z0-9_]*)\}",
        lambda matched: str(values[matched.group(1)]),
        template,
    )
    if not message or len(message) > 1000:
        raise WorldError("PROPERTY_RANGE", "Longitud de mensaje inválida")
    append(state, ("action", context.source, message))
    sequence = len(state["history"]["facts"]) + len(state["history"]["trace"]) + 1
    state["history"]["trace"].append(
        {
            "sequence": sequence,
            "kind": "author_message",
            "source": context.source,
            "detail": {"text": message, "values": values},
        }
    )
    return []
