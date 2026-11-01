"""Frontera de ALBERTO: operaciones puras sobre el borrador de GISELA.

Las entidades no poseen sesión, contador de turnos ni autoridad de commit.
"""

from __future__ import annotations

import json

from . import world_base
from .effect_context import EffectContext
from .world_base import WorldError
from .world_entities import learn_fact, move_character, set_belief, transfer
from .world_lifecycle import create_instance, remove_instance
from .world_skills import discard_skill, grant_skill, move_skill

var_access = world_base.var_access


def writable_key(effect: dict) -> str | None:
    """Identifica destinos para detectar conflictos entre reglas de una ronda."""
    op = effect["op"]
    if op in ("set", "add", "roll"):
        return json.dumps(
            effect["store"] if op == "roll" else effect["target"], sort_keys=True
        )
    if op == "create_instance":
        return "identity:" + str(effect.get("instance_id", "auto"))
    if op == "remove_instance":
        return "remove:" + str(effect["instance"])
    if op == "transfer":
        return "object_owner:" + str(effect["object"])
    if op == "move_character":
        return "character_location:" + str(effect["character"])
    if op == "learn_fact":
        return "knowledge:" + str(effect["character"]) + ":" + effect["fact"]
    if op == "set_belief":
        return "belief:" + str(effect["character"]) + ":" + effect["claim"]
    if op in ("assign_trait", "remove_trait"):
        return "traits:" + str(effect["entity"])
    if op in ("grant_skill", "move_skill", "discard_skill"):
        return "skill_capacity:" + str(effect["character"])
    if op == "set_scene":
        return "scene"
    return None


def _set_value(state: dict, effect: dict, definitions) -> list[dict]:
    """Resuelve `set` o `add` sobre un destino declarado y tipado."""
    from .conditions import value
    from .world_values import read, write

    target = effect["target"]
    result = value(state, effect["value"], definitions)
    if effect["op"] == "add":
        previous = read(state, target, definitions)
        if type(previous) not in (int, float) or type(result) not in (int, float):
            raise WorldError("TYPE_MISMATCH", "add exige operandos numéricos")
        result = previous + result
    return write(state, {"target": target, "value": result}, definitions)


def apply_operation(state: dict, effect: dict, context: EffectContext) -> list[dict]:
    """Despacha operaciones de mundo ya admitidas, sin confirmar el borrador."""
    op = effect["op"]
    if op in ("set", "add"):
        return _set_value(state, effect, context.definitions)
    if op == "grant_skill":
        return grant_skill(state, effect, context.decisions)
    operations = {
        "transfer": transfer,
        "move_character": move_character,
        "learn_fact": learn_fact,
        "set_belief": set_belief,
        "move_skill": move_skill,
        "discard_skill": discard_skill,
    }
    if op in operations:
        return operations[op](state, effect)
    if op == "create_instance":
        if context.definitions is None:
            raise WorldError("INVALID_STATE", "Falta catálogo de cartas admitidas")
        return create_instance(state, effect, context.definitions)
    if op == "remove_instance":
        return remove_instance(state, effect)
    if op in ("assign_trait", "remove_trait"):
        from .world_traits import change

        return change(state, effect, context.definitions.traits)
    if op == "set_scene":
        state["current_scene"] = effect["scene"]
        return []
    raise WorldError("UNSUPPORTED_FORMAT", f"Operación no disponible: {op}")
