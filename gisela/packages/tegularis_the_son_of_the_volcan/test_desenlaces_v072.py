"""Regresión dirigida de acontecimientos v0.7.2 en el DSL 1.5."""

import copy
from pathlib import Path

import pytest

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.actuation import resolve_policies
from gisela.engine.consequences import apply_operation
from gisela.engine.effect_context import EffectContext
from gisela.engine.pending import DecisionReplay
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.world_base import WorldError

PACKAGE = Path(__file__).with_name("08_desenlaces_v072.package.json")
HEROES = ("parnecio", "gillius", "clarisa", "iosepus")


def fresh(seed="a" * 64):
    a = admit_package_file(PACKAGE)
    return a, new_session(a, seed=seed)


def write(session, draft, assignment):
    key, value = assignment
    effect = {
        "op": "set",
        "target": {"var": {"scope": "session", "key": key}},
        "value": {"literal": value},
    }
    apply_operation(
        draft,
        effect,
        EffectContext("test_author", DecisionReplay(), session._definitions),
    )


def vars_(draft):
    return draft["narrative"]["session_variables"]


def pulse(session, draft):
    resolve_policies(draft, session._definitions, "after_action")


def test_pride_before_second_damage_and_only_once():
    _, s = fresh()
    d = copy.deepcopy(s._state)
    v = vars_(d)
    threshold = v["max_hp_tegularis"] * 3 // 10
    write(s, d, ("hp_tegularis", threshold))
    assert d["actuation"]["fired"] == ["pride_of_the_volcan_son"]
    assert s._definitions.cards["ef_pride_volcan"]["modifiers"][0]["amount"] == 1
    from gisela.engine.sofia import read

    assert (
        read(
            d,
            {"character": "tegularis", "name": "strength", "component": "effective"},
            s._definitions,
        )
        == 16
    )
    write(s, d, ("hp_tegularis", threshold - 1))
    assert d["actuation"]["fired"].count("pride_of_the_volcan_son") == 1
    assert d["actuation"]["outcome"] is None
    s._validate_state(d)


def test_burst_executed_before_victory_and_exact_once():
    _, s = fresh()
    d = copy.deepcopy(s._state)
    write(s, d, ("hp_tegularis", 0))
    assert not d["actuation"]["complete"]
    pulse(s, d)
    assert d["actuation"]["complete"] and d["actuation"]["outcome"] in (
        "victoria",
        "destruccion_mutua",
    )
    assert d["actuation"]["fired"].count("ultima_llama") == 1
    assert d["actuation"]["events"][-1]["kind"] == "encounter_completed"
    before = copy.deepcopy(d)
    pulse(s, d)
    assert before == d
    s._validate_state(d)


def test_groupal_shield_absorbs_one_burst():
    _, s = fresh()
    d = copy.deepcopy(s._state)
    initial = {w: vars_(d)["hp_" + w] for w in HEROES}
    write(s, d, ("group_shield", 1))
    write(s, d, ("hp_tegularis", 0))
    pulse(s, d)
    assert vars_(d)["group_shield"] == 0
    assert all(vars_(d)["hp_" + w] == initial[w] for w in HEROES)
    assert d["actuation"]["outcome"] == "victoria"
    assert d["actuation"]["fired"].count("ultima_llama") == 1


def test_mutual_destruction_after_burst():
    _, s = fresh()
    d = copy.deepcopy(s._state)
    for w in HEROES:
        write(s, d, ("hp_" + w, 1))
    write(s, d, ("hp_tegularis", 0))
    pulse(s, d)
    assert d["actuation"]["outcome"] == "destruccion_mutua"
    assert all(vars_(d)["hp_" + w] == 0 for w in HEROES)


def test_defeat_without_burst():
    _, s = fresh()
    d = copy.deepcopy(s._state)
    for w in HEROES:
        write(s, d, ("hp_" + w, 0))
    pulse(s, d)
    assert d["actuation"]["outcome"] == "derrota"
    assert "ultima_llama" not in d["actuation"]["fired"]


def test_restoration_and_same_rng_after_burst():
    a, s = fresh()
    d = copy.deepcopy(s._state)
    write(s, d, ("hp_tegularis", 0))
    d["revision"] += 1
    d["world_revision"] += 1
    s._validate_state(d)
    s._state = d
    restored = restore_session(a, s.export())
    d1 = copy.deepcopy(s._state)
    d2 = copy.deepcopy(restored._state)
    pulse(s, d1)
    pulse(restored, d2)
    assert d1 == d2
    assert d1["rng"] == d2["rng"]


def test_tampered_event_policy_rejected():
    _, s = fresh()
    d = copy.deepcopy(s._state)
    d["actuation"]["event_policies"].pop()
    with pytest.raises(WorldError, match="ACTUATION_POLICIES"):
        s._validate_state(d)
