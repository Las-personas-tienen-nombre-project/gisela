"""Reloj de oportunidades autorales, independiente del turno narrativo.

No contiene ataques, daño, HP, ni nombres del mundo. El autor suministra el
orden, las puntuaciones, las prioridades y las señales de duración.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass

from gisela.contracts.rng import RNGState, draw

from .conditions import predicate
from .sofia import read as read_stat
from .world_base import WorldError, find

MAX_PARTICIPANTS = 32
MAX_ACTIONS = 16
MAX_ROUNDS = 1000


@dataclass(frozen=True)
class ActuationDuration:
    """Duración explícita de un efecto en turnos de su beneficiario."""

    identifier: str
    beneficiary: str
    turns: int


@dataclass(frozen=True)
class _ActorContext:
    definitions: object
    actor: str
    spec: dict
    config: dict


def _stat(state, context, name):
    return read_stat(
        state,
        {"character": context.actor, "name": name, "component": "effective"},
        context.definitions,
    )


def _total(state, context):
    definitions, actor, spec = context.definitions, context.actor, context.spec
    # TRAITS are evaluated by the general-purpose bridge.
    from .traits_dice_bridge import contribution_total

    value = _stat(state, context, spec["main_stat"])
    if "action_traits" in spec:
        query = copy.deepcopy(spec["action_traits"])
        query["participants"] = [{"entity": actor, "role": "actor"}]
        value += contribution_total(state, query, definitions)
    return value


def _budget(state, context):
    config = context.config
    total = _total(state, context)
    budget = config["base_actions"]
    for threshold in config.get("thresholds", []):
        if total >= threshold["at"]:
            budget = threshold["actions"]
    if not 0 <= budget <= MAX_ACTIONS:
        raise WorldError("BUDGET_EXCEEDED", "Presupuesto de acciones inválido")
    return budget


def _record(clock, kind, **detail):
    if len(clock["events"]) >= 16000:
        raise WorldError("BUDGET_EXCEEDED", "Historial de actuación agotado")
    clock["events"].append(
        {"sequence": len(clock["events"]) + 1, "kind": kind, "detail": detail}
    )


def initialize(session, state):
    config = session._package.get("actuation")
    if config is None:
        return
    if "actuation" in state:
        raise WorldError("INVALID_STATE", "Actuación ya iniciada")
    people = config["participants"]
    if not 1 <= len(people) <= MAX_PARTICIPANTS:
        raise WorldError("BUDGET_EXCEEDED", "Cantidad de participantes fuera de rango")
    _setup(session, state, config)
    rng = RNGState(**state["rng"])
    queue = []
    seen = set()
    for person in people:
        actor = person["character"]
        if actor in seen:
            raise WorldError("INVALID_STATE", "Actor duplicado")
        seen.add(actor)
        find(state, "characters", actor)
        values = [
            _stat(
                state, _ActorContext(session._definitions, actor, person, config), name
            )
            for name in ("strength", "awareness", "fortune")
        ]
        die, rng = draw(rng, config["initiative_die"])
        queue.append(
            {
                "actor": actor,
                "score": sum(values) + die,
                "die": die,
                "strength": values[0],
                "awareness": values[1],
                "fortune": values[2],
            }
        )
    queue.sort(
        key=lambda a: (
            -a["score"],
            -a["awareness"],
            -a["strength"],
            -a["fortune"],
            a["actor"],
        )
    )
    state["rng"] = rng.as_json()
    _initialize_clock(session, state, queue)


def _initialize_clock(session, state, queue):
    config = session._package["actuation"]
    clock = {
        "round": 1,
        "order": [item["actor"] for item in queue],
        "initiative": queue,
        "index": 0,
        "remaining": 0,
        "turn_serial": 0,
        "effects": [],
        "events": [],
        "complete": False,
        "fired": [],
        "outcome": None,
        "event_policies": copy.deepcopy(config.get("event_policies", [])),
        "outcome_policies": copy.deepcopy(config.get("outcome_policies", [])),
        "public_trace_variables": list(config.get("public_trace_variables", [])),
    }
    state["actuation"] = clock
    _record(clock, "initiative", order=copy.deepcopy(queue))
    from .causal_trace import record_actuation

    record_actuation(state, "initiative", {"order": clock["order"]})
    _begin_actor(session, state)


def _begin_actor(session, state):
    clock = state["actuation"]
    config = session._package["actuation"]
    if clock["complete"]:
        return
    if clock["index"] == len(clock["order"]):
        if clock["round"] >= MAX_ROUNDS:
            raise WorldError("BUDGET_EXCEEDED", "Límite de rondas alcanzado")
        clock["round"] += 1
        clock["index"] = 0
        _record(clock, "round_started", round=clock["round"])
    actor = clock["order"][clock["index"]]
    person = next(p for p in config["participants"] if p["character"] == actor)
    # Contrato genérico: vencimiento en el comienzo del siguiente turno
    # autoral. No adelanta el reloj narrativo ni deja el bonus activo en
    # las primeras decisiones de ese turno.
    _expire_at_start(session, state, actor)
    clock["turn_serial"] += 1
    clock["remaining"] = _budget(
        state, _ActorContext(session._definitions, actor, person, config)
    )
    _block_actions(session, state, actor)
    _record(
        clock,
        "actor_turn_started",
        actor=actor,
        round=clock["round"],
        actions=clock["remaining"],
        serial=clock["turn_serial"],
    )
    # Start-of-turn effects never use narrative state["turn"].
    # Run author-supplied periodic effects once per actor turn, never per action.
    _pulse_effects(session, state, actor)
    resolve_policies(state, session._definitions, "after_action")
    if clock["remaining"] == 0 and not clock["complete"]:
        _end_actor(session, state)


def _end_actor(session, state):
    clock = state["actuation"]
    actor = clock["order"][clock["index"]]
    _record(clock, "actor_turn_ended", actor=actor, round=clock["round"])
    retained = []
    expired_linked = []
    for effect in clock["effects"]:
        if effect["beneficiary"] == actor:
            effect["remaining"] -= 1
            if effect["remaining"] == 0:
                _record(clock, "effect_expired", effect=effect["id"], actor=actor)
                if effect.get("linked"):
                    expired_linked.append(effect["id"])
                continue
        retained.append(effect)
    clock["effects"] = retained
    if expired_linked:
        from .effect_context import EffectContext
        from .pending import DecisionReplay

        for identifier in expired_linked:
            session._operations(
                state,
                [{"op": "end_effect", "effect_instance": identifier}],
                EffectContext(identifier, DecisionReplay(), session._definitions),
            )
    clock["index"] += 1
    _begin_actor(session, state)


def add_duration(draft, duration: ActuationDuration, linked=False):
    """Add or refresh an explicitly declared authorial duration in draft."""
    if not isinstance(duration, ActuationDuration):
        raise WorldError("INVALID_ACTION", "Duración inválida")
    identifier, beneficiary, turns = (
        duration.identifier,
        duration.beneficiary,
        duration.turns,
    )
    clock = draft.get("actuation")
    if clock is None:
        raise WorldError("INVALID_STATE", "No hay reloj autoral")
    if (
        not isinstance(identifier, str)
        or type(turns) is not int
        or not 1 <= turns <= 1000
    ):
        raise WorldError("INVALID_ACTION", "Duración inválida")
    if beneficiary not in clock["order"]:
        raise WorldError("INVALID_REFERENCE", "Beneficiario desconocido")
    for effect in clock["effects"]:
        if effect["id"] == identifier:
            if effect["beneficiary"] != beneficiary:
                raise WorldError("INVALID_STATE", "Identidad de efecto reutilizada")
            effect["remaining"] = turns
            effect["linked"] = linked or effect.get("linked", False)
            _record(clock, "effect_refreshed", effect=identifier, turns=turns)
            return
    clock["effects"].append(
        {
            "id": identifier,
            "beneficiary": beneficiary,
            "remaining": turns,
            "linked": linked,
        }
    )
    _record(clock, "effect_started", effect=identifier, actor=beneficiary, turns=turns)


def resolve_policies(state, definitions, phase):
    """Resuelve disparadores autorales sobre el mismo borrador, exact-once.

    La fase immediate se aplica tras una mutación individual; after_action
    después de completar todas las consecuencias de una oportunidad.
    """
    clock = state.get("actuation")
    if not clock or clock.get("_resolving_policies") or clock["complete"]:
        return
    policies = clock.get("event_policies", [])
    if not policies:
        return
    from .consequences import apply_operation
    from .effect_context import EffectContext
    from .pending import DecisionReplay

    clock["_resolving_policies"] = True
    try:
        for policy in policies:
            if policy["phase"] != phase or policy["id"] in clock["fired"]:
                continue
            if not predicate(state, policy["when"], definitions):
                continue
            # Antes de ejecutar efectos, marca el disparador. Al fallar cualquier
            # operación se descartará el borrador completo con la marca incluida.
            clock["fired"].append(policy["id"])
            _record(clock, "event_triggered", event=policy["id"], phase=phase)
            from .causal_trace import record_actuation

            record_actuation(state, "event_triggered", {"event": policy["id"]})
            context = EffectContext(
                "actuation_event_" + policy["id"], DecisionReplay(), definitions
            )
            for operation in policy["effects"]:
                apply_operation(state, operation, context)
            for branch in policy.get("outcomes", []):
                if predicate(state, branch["when"], definitions):
                    for operation in branch["effects"]:
                        apply_operation(state, operation, context)
        # Un autor puede definir una condición de cierre distinta al nombre
        # o la semántica de un combate. Se evalúa DESPUÉS de los disparadores.
        if phase == "after_action":
            for outcome in state.get("actuation", {}).get("outcome_policies", []):
                if predicate(state, outcome["when"], definitions):
                    clock["outcome"] = outcome["id"]
                    clock["complete"] = True
                    clock["remaining"] = 0
                    _record(clock, "encounter_completed", outcome=outcome["id"])
                    from .causal_trace import record_actuation

                    record_actuation(
                        state, "encounter_completed", {"outcome": outcome["id"]}
                    )
                    break
    finally:
        clock.pop("_resolving_policies", None)


def current(state):
    clock = state.get("actuation")
    if not clock or clock["complete"]:
        return None
    return clock["order"][clock["index"]]


def _execute_skill(session, draft, skill_id):
    actor = current(draft)
    from .effect_context import EffectContext
    from .skill_execution import SkillExecution, _NoScriptChoices, _run

    skill = find(draft, "skills", skill_id)
    if skill["character"] != actor or skill["zone"] != "hand":
        raise WorldError("INVALID_ACTION", "Habilidad ajena o fuera de mano")
    card = session._cards[skill["card"]]
    if card["kind"] != "skill" or card.get("passive_traits"):
        raise WorldError("INVALID_ACTION", "Habilidad no ejecutable")
    if card["play"].get("parameters"):
        raise WorldError("INVALID_ACTION", "El reloj requiere parámetros resueltos")
    if not predicate(
        draft, card["play"].get("requires", {"constant": True}), session._definitions
    ):
        raise WorldError("INVALID_ACTION", "No cumple requisitos")

    def operations(state, ops, context):
        return session._operations(state, ops, context)

    return _run(
        draft,
        SkillExecution(
            skill,
            card,
            EffectContext(skill["id"], _NoScriptChoices(), session._definitions),
            operations,
            "player" if actor == draft.get("player_character") else "script",
        ),
    )


def step(session, draft, skill_id=None):
    clock = draft.get("actuation")
    if clock is None or clock["complete"]:
        raise WorldError("INVALID_ACTION", "Reloj inactivo")
    actor = current(draft)
    config = session._package["actuation"]
    person = next(p for p in config["participants"] if p["character"] == actor)
    if clock["remaining"] <= 0:
        raise WorldError("INVALID_STATE", "Actor sin acciones")
    if actor == draft.get("player_character"):
        if skill_id is None and not person.get("allow_pass", False):
            raise WorldError("INVALID_ACTION", "El jugador debe elegir carta")
        if skill_id is not None:
            _execute_skill(session, draft, skill_id)
    else:
        if skill_id is not None:
            raise WorldError("INVALID_ACTION", "El jugador no controla NPC")
        from .effect_context import EffectContext
        from .pending import DecisionReplay
        from .skill_execution import execute_first_available

        candidates = person.get("candidates", [])
        if candidates:
            decisions = DecisionReplay()
            events = execute_first_available(
                draft,
                {"candidates": candidates, "otherwise": []},
                EffectContext("actuation_" + actor, decisions, session._definitions),
            )
            if events:
                from .reactions import ReactionContext, settle

                settle(
                    draft,
                    events,
                    ReactionContext(
                        session._rules, decisions, session._definitions, session._mary
                    ),
                )
        elif not person.get("allow_pass", False):
            raise WorldError("INVALID_STATE", "Política sin cartas ni pase")
    resolve_policies(draft, session._definitions, "after_action")
    if clock["complete"]:
        return
    _record(
        clock,
        "action_consumed",
        actor=actor,
        round=clock["round"],
        skill=skill_id if skill_id is not None else "automatic",
    )
    clock["remaining"] -= 1
    if clock["remaining"] == 0:
        _end_actor(session, draft)


def _setup(session, state, config):
    if config.get("setup"):
        from .effect_context import EffectContext
        from .pending import DecisionReplay
        from .reactions import ReactionContext, settle

        decisions = DecisionReplay()
        events = session._operations(
            state,
            config["setup"],
            EffectContext("actuation_setup", decisions, session._definitions),
        )
        if events:
            settle(
                state,
                events,
                ReactionContext(
                    session._rules, decisions, session._definitions, session._mary
                ),
            )


def _expire_at_start(session, state, actor):
    clock = state["actuation"]
    from .effect_context import EffectContext
    from .pending import DecisionReplay

    for timed in list(clock["effects"]):
        if timed["beneficiary"] != actor or not timed.get("linked"):
            continue
        instance = next(
            (e for e in state["world"]["effects"] if e["id"] == timed["id"]), None
        )
        if instance is None or not session._cards[instance["card"]].get(
            "expire_on_actor_turn_start"
        ):
            continue
        clock["effects"].remove(timed)
        _record(clock, "effect_expired", effect=timed["id"], actor=actor)
        session._operations(
            state,
            [{"op": "end_effect", "effect_instance": timed["id"]}],
            EffectContext(timed["id"], DecisionReplay(), session._definitions),
        )


def _block_actions(session, state, actor):
    clock = state["actuation"]
    for effect in clock["effects"]:
        if effect["beneficiary"] != actor or not effect.get("linked"):
            continue
        instance = next(
            (x for x in state["world"]["effects"] if x["id"] == effect["id"]), None
        )
        if instance and session._cards[instance["card"]].get(
            "actuation_blocks_actions", False
        ):
            clock["remaining"] = 0
            break


def _pulse_effects(session, state, actor):
    clock = state["actuation"]
    from .effect_context import EffectContext
    from .pending import DecisionReplay

    for effect in list(clock["effects"]):
        if effect["beneficiary"] != actor:
            continue
        _record(
            clock,
            "effect_pulse",
            effect=effect["id"],
            actor=actor,
            remaining=effect["remaining"],
        )
        if not effect.get("linked"):
            continue
        instance = next(
            (x for x in state["world"]["effects"] if x["id"] == effect["id"]), None
        )
        if instance is not None:
            card = session._cards[instance["card"]]
            if card.get("on_actor_turn_start"):
                session._operations(
                    state,
                    card["on_actor_turn_start"],
                    EffectContext(effect["id"], DecisionReplay(), session._definitions),
                )
