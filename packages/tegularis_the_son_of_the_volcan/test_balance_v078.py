"""Regresiones del balance autoral, sin excepciones de calidad ni motor especial."""

import copy
import json
from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.conditions import predicate
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.sofia import read

HERE = Path(__file__).resolve().parent
FILE = HERE / "10_balance_v078.package.json"
BASE = HERE / "09_cierre_autoral_v077.package.json"
PEOPLE = ("parnecio", "gillius", "clarisa", "iosepus")


def setup():
    package = admit_package_file(FILE)
    return package, new_session(package, seed="a" * 64)


def participants(package):
    return {x["character"]: x for x in package["actuation"]["participants"]}


def test_gillius_awareness_increase_is_effective():
    package, session = setup()
    gillius = next(c for c in session._package["cards"] if c["id"] == "gillius")
    assert gillius["sofia"]["awareness"] == 6
    assert read(session._state, {"character": "gillius", "name": "awareness", "component": "effective"}, session._definitions) == 6


def test_preponderancia_resources_and_nonstacking():
    _, session = setup()
    card = session._cards["preponderancia"]
    state = copy.deepcopy(session._state)
    state["narrative"]["session_variables"].update(tp_tegularis=0, mp_tegularis=0)
    from gisela.engine.consequences import apply_operation
    from gisela.engine.effect_context import EffectContext
    from gisela.engine.pending import DecisionReplay
    ctx = EffectContext("balance_test", DecisionReplay(), session._definitions)
    for op in card["play"]["effects"]:
        apply_operation(state, op, ctx)
    values = state["narrative"]["session_variables"]
    assert (values["tp_tegularis"], values["mp_tegularis"]) == (25, 15)
    assert len([e for e in state["world"]["effects"] if e["card"] == "ef_preponderancia"]) == 1


def test_no_regeneration_for_healthy_party():
    _, session = setup()
    state = session._state
    for who in PEOPLE:
        card = session._cards["regeneracion" + ("" if who == "parnecio" else "_" + who)]
        assert not predicate(state, card["play"]["requires"], session._definitions)


def test_clarisa_targets_lowest_health_fraction():
    _, session = setup()
    state = copy.deepcopy(session._state)
    values = state["narrative"]["session_variables"]
    for who in PEOPLE:
        values["hp_" + who] = values["max_hp_" + who] * 3 // 4
    values["hp_gillius"] = values["max_hp_gillius"] // 5
    for who in PEOPLE:
        card = session._cards["curacion" + ("" if who == "parnecio" else "_" + who)]
        eligible = predicate(state, card["play"]["requires"], session._definitions)
        assert eligible == (who == "gillius"), who


def test_iosepus_prioritizes_frontline_and_preserves_parameters():
    data = json.loads(FILE.read_text())
    actors = participants(data)
    spells = [x["skill_instance"] for x in actors["iosepus"]["candidates"]]
    assert spells.index("armadura_magica_gillius_01") < spells.index("armadura_magica_iosepus_01")
    assert spells.index("firesteel_gillius_01") < spells.index("firesteel_iosepus_01")
    blast = next(x for x in actors["iosepus"]["candidates"] if x["skill_instance"] == "magic_blast_01")
    assert blast["arguments"]["x"] == {"literal": 10}


def test_clarisa_has_no_fixed_preference_for_iosepus():
    data = json.loads(FILE.read_text())
    ids = [x["skill_instance"] for x in participants(data)["clarisa"]["candidates"]]
    assert ids.index("curacion_gillius_01") < ids.index("curacion_iosepus_01")
    assert ids.index("regeneracion_gillius_01") < ids.index("regeneracion_iosepus_01")
    assert len(ids) == len(set(ids))


def test_seed_and_restoration_are_identical():
    admitted, session = setup()
    for _ in range(12):
        view = session.observe()
        action = next(x for x in view["actions"] if x["enabled"])
        result = session.act({"session_id": view["session_id"], "revision": view["revision"], "action_id": action["action_id"]})
        assert result["status"] == "ok", result
    restored = restore_session(admitted, session.export())
    assert restored.export() == session.export()
    assert restored.observe() == session.observe()
