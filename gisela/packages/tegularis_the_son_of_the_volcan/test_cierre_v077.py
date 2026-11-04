"""Regresión focalizada: decisiones autorales, causalidad y restauración."""

import copy
from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.conditions import predicate
from gisela.engine.consequences import apply_operation
from gisela.engine.effect_context import EffectContext
from gisela.engine.pending import DecisionReplay
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.sofia import read

PACKAGE = Path(__file__).with_name("09_cierre_autoral_v077.package.json")


def fresh():
    admitted = admit_package_file(PACKAGE)
    return admitted, new_session(admitted, seed="a" * 64)


def context(session):
    return EffectContext("test_cierre", DecisionReplay(), session._definitions)


def operation(session, state, item):
    return apply_operation(state, item, context(session))


def var(state, key):
    return state["narrative"]["session_variables"][key]


def test_bless_cost_effective_attribute_and_refresh():
    _, session = fresh()
    state = copy.deepcopy(session._state)
    old_mp = var(state, "mp_clarisa")
    before = read(
        state,
        {"character": "gillius", "name": "strength", "component": "effective"},
        session._definitions,
    )
    operation(
        session, state, {"op": "play_skill", "skill_instance": "bless_gillius_01"}
    )
    assert var(state, "mp_clarisa") == old_mp - 10
    assert (
        read(
            state,
            {"character": "gillius", "name": "strength", "component": "effective"},
            session._definitions,
        )
        == before + 2
    )
    effects = [x for x in state["world"]["effects"] if x["card"] == "ef_bless_gillius"]
    assert len(effects) == 1
    assert (
        next(x for x in state["actuation"]["effects"] if x["id"] == effects[0]["id"])[
            "remaining"
        ]
        == 3
    )
    operation(
        session, state, {"op": "play_skill", "skill_instance": "bless_gillius_01"}
    )
    assert var(state, "mp_clarisa") == old_mp - 20
    assert (
        len([x for x in state["world"]["effects"] if x["card"] == "ef_bless_gillius"])
        == 1
    )
    session._validate_state(state)


def test_group_protection_applies_defense_then_half_only_once():
    _, session = fresh()
    state = copy.deepcopy(session._state)
    operation(
        session,
        state,
        {"op": "apply_effect", "effect": "ef_proteccion_gillius", "target": "parnecio"},
    )
    figures = {
        who: var(state, "hp_" + who)
        for who in ("parnecio", "gillius", "clarisa", "iosepus")
    }
    state["narrative"]["session_variables"]["defense_parnecio"] = 10
    for who in figures:
        state["narrative"]["session_variables"]["tail_hit_" + who] = 100
        state["narrative"]["session_variables"]["tail_eva_" + who] = 0
        state["narrative"]["session_variables"]["tail_dmg_" + who] = 30
    for branch in session._cards["coletazo"]["play"]["outcomes"]:
        if predicate(state, branch["when"], session._definitions):
            for item in branch["effects"]:
                operation(session, state, item)
    assert var(state, "hp_gillius") == figures["gillius"]
    assert var(state, "hp_parnecio") == figures["parnecio"] - 10
    assert var(state, "hp_clarisa") == figures["clarisa"] - 30
    assert var(state, "hp_iosepus") == figures["iosepus"] - 30


def test_burst_redirects_one_glancing_hit():
    _, session = fresh()
    state = copy.deepcopy(session._state)
    operation(
        session,
        state,
        {"op": "apply_effect", "effect": "ef_proteccion_gillius", "target": "parnecio"},
    )
    figures = {
        who: var(state, "hp_" + who)
        for who in ("parnecio", "gillius", "clarisa", "iosepus")
    }
    operation(
        session,
        state,
        {
            "op": "set",
            "target": {"var": {"scope": "session", "key": "hp_tegularis"}},
            "value": {"literal": 0},
        },
    )
    from gisela.engine.actuation import resolve_policies

    resolve_policies(state, session._definitions, "after_action")
    assert var(state, "hp_gillius") == figures["gillius"]
    assert figures["parnecio"] - var(state, "hp_parnecio") < var(state, "burst_raw")
    assert var(state, "hp_clarisa") < figures["clarisa"]
    assert state["actuation"]["complete"]


def test_public_causality_and_restore():
    admitted, session = fresh()
    v = session.observe()
    validator = Validator()
    validator.use_version("1.5")
    assert validator.check_schema("observe", v)
    snapshot = session.export()
    assert session.observe() == v and session.export() == snapshot
    for _ in range(6):
        v = session.observe()
        action = next(a for a in v["actions"] if a["enabled"])
        result = session.act(
            {
                "session_id": v["session_id"],
                "revision": v["revision"],
                "action_id": action["action_id"],
            }
        )
        assert result["status"] == "ok"
    causal = session.observe()["actuation"]["causal"]
    assert any(x["kind"] == "dice_roll" for x in causal)
    assert any(x["kind"] == "variable_changed" for x in causal)
    assert [x["sequence"] for x in causal] == sorted(x["sequence"] for x in causal)
    restored = restore_session(admitted, session.export())
    assert restored.observe() == session.observe()
    assert validator.check_schema("observe", restored.observe())


def test_protection_blocks_paralysis_of_covered_ally():
    _, session = fresh()
    state = copy.deepcopy(session._state)
    operation(
        session,
        state,
        {"op": "apply_effect", "effect": "ef_proteccion_gillius", "target": "parnecio"},
    )
    values = state["narrative"]["session_variables"]
    for who in ("parnecio", "gillius", "clarisa", "iosepus"):
        values["wing_hit_" + who] = 100
        values["wing_eva_" + who] = 0
        values["wing_res_" + who] = 1
    values["wing_common"] = 30
    for branch in session._cards["wingblast"]["play"]["outcomes"]:
        if predicate(state, branch["when"], session._definitions):
            for item in branch["effects"]:
                operation(session, state, item)
    assert not any(
        x["card"] == "ef_paralizado_gillius" for x in state["world"]["effects"]
    )
    assert any(x["card"] == "ef_paralizado_clarisa" for x in state["world"]["effects"])


def test_group_shield_precedes_protection():
    _, session = fresh()
    state = copy.deepcopy(session._state)
    operation(
        session,
        state,
        {"op": "apply_effect", "effect": "ef_proteccion_gillius", "target": "parnecio"},
    )
    operation(
        session,
        state,
        {
            "op": "set",
            "target": {"var": {"scope": "session", "key": "group_shield"}},
            "value": {"literal": 1},
        },
    )
    old_hp = var(state, "hp_parnecio")
    old_gillius = var(state, "hp_gillius")
    operation(
        session,
        state,
        {
            "op": "set",
            "target": {"var": {"scope": "session", "key": "hp_tegularis"}},
            "value": {"literal": 0},
        },
    )
    from gisela.engine.actuation import resolve_policies

    resolve_policies(state, session._definitions, "after_action")
    assert var(state, "group_shield") == 0
    assert var(state, "hp_parnecio") == old_hp
    assert var(state, "hp_gillius") == old_gillius


def test_initiative_event_and_rollback_in_causal_projection():
    _, session = fresh()
    view = session.observe()
    assert any(x["kind"] == "initiative" for x in view["actuation"]["causal"])
    snapshot = session.export()
    wrong = {
        "session_id": view["session_id"],
        "revision": view["revision"],
        "action_id": "actturn_unoffered",
    }
    assert session.act(wrong)["status"] == "error"
    assert session.export() == snapshot
    assert session.observe() == view
