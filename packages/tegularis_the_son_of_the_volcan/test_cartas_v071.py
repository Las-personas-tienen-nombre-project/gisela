"""Pruebas integradas de las cartas implementadas: estado, trazas y RNG."""

import json
from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

PATH = Path(__file__).with_name("07_cartas_v071.package.json")
SEED = "a" * 64


def new():
    admitted = admit_package_file(PATH)
    return admitted, new_session(admitted, seed=SEED)


def advance(s):
    v = s.actuation_observe()
    card = None
    if v["actor"] == "parnecio":
        enabled = [x for x in v["offers"] if x["enabled"] and x["id"] != "pasar"]
        card = enabled[0]["id"] if enabled else None
    result = s.actuation_step(s.export()["revision"], card)
    assert result["status"] == "ok", result
    return result


def test_admission_and_32_design_cards():
    _admitted, session = new()
    definition = json.loads(PATH.read_text())
    assert len([x for x in definition["cards"] if x["kind"] == "skill"]) >= 32
    assert {
        x["id"]
        for x in json.loads(
            PATH.with_name("02_diseno_productivo_completo.json").read_text()
        )["skills"]
    } <= {x["id"] for x in definition["cards"] if x["kind"] == "skill"}
    assert session.actuation_observe()["active"]


def test_initiative_is_persistent_and_three_rounds_finish():
    _, s = new()
    initial = s.export()["actuation"]["initiative"]
    for _ in range(100):
        if s.actuation_observe()["round"] > 3:
            break
        advance(s)
    else:
        raise AssertionError("Tres rondas no terminaron")
    assert s.export()["actuation"]["initiative"] == initial


def test_restore_and_seed_reproducible_with_damage():
    a, s = new()
    for _ in range(16):
        advance(s)
    restored = restore_session(a, s.export())
    for _ in range(22):
        advance(s)
        advance(restored)
    assert s.export() == restored.export()
    assert any(t["kind"] == "author_message" for t in s.export()["history"]["trace"])


def test_failed_spend_is_atomic():
    _, s = new()
    while s.actuation_observe()["actor"] != "parnecio":
        advance(s)
    before = s.export()
    result = s.actuation_step(before["revision"], "blai_01")
    assert result["status"] == "error"
    assert s.export() == before


def test_card_costs_and_implementations_are_explicit():
    p = json.loads(PATH.read_text())
    cards = {c["id"]: c for c in p["cards"] if c["kind"] == "skill"}
    for name in (
        "slash",
        "double_slash",
        "blai",
        "hachazo",
        "eviscerate",
        "curacion",
        "concentracion_clarisa",
        "concentracion_iosepus",
        "magic_blast",
        "firebreath",
    ):
        assert cards[name]["play"]["effects"], name
    for name in ("proteccion", "bless"):
        assert cards[name]["play"]["requires"] == {"constant": False}
    assert (
        len([c for c in cards["double_slash"]["play"]["effects"] if c["op"] == "roll"])
        == 6
    )
    assert (
        len([c for c in cards["firebreath"]["play"]["effects"] if c["op"] == "roll"])
        == 9
    )


def test_initial_resource_dice_are_declared_and_in_bounds():
    _, s = new()
    values = s.export()["narrative"]["session_variables"]
    strengths = {"parnecio": 8, "gillius": 10, "clarisa": 4, "iosepus": 4}
    intelligence = {"parnecio": 4, "gillius": 4, "clarisa": 7, "iosepus": 9}
    for who, strength in strengths.items():
        assert 151 + strength <= values["hp_" + who] <= 170 + strength
        assert 51 + intelligence[who] <= values["mp_" + who] <= 60 + intelligence[who]
        assert values["max_hp_" + who] == values["hp_" + who]
        assert values["max_mp_" + who] == values["mp_" + who]
    assert 503 <= values["hp_tegularis"] <= 560
    assert 81 <= values["mp_tegularis"] <= 100
    assert values["tp_tegularis"] == 50


def test_repeated_seed_runs_have_valid_resources_and_restore():
    for seed_number in range(4):
        admitted = admit_package_file(PATH)
        s = new_session(admitted, seed=f"{seed_number + 1:064x}")
        for index in range(55):
            advance(s)
            state = s.export()
            vars = state["narrative"]["session_variables"]
            for who in ("parnecio", "gillius", "clarisa", "iosepus", "tegularis"):
                assert 0 <= vars["hp_" + who] <= vars["max_hp_" + who]
                assert 0 <= vars["mp_" + who] <= vars["max_mp_" + who]
                assert 0 <= vars["tp_" + who] <= (60 if who == "tegularis" else 50)
            if index == 22:
                restored = restore_session(admitted, state)
                assert restored.export() == state


def test_target_variants_are_real_cards_with_distinct_owners():
    p = json.loads(PATH.read_text())
    cards = {x["id"]: x for x in p["cards"]}
    skills = {x["id"]: x for x in p["initial_state"]["skills"]}
    for who in ("gillius", "clarisa", "iosepus"):
        for name in (
            "curacion",
            "fenix",
            "regeneracion",
            "armadura_magica",
            "firesteel",
        ):
            card = name + "_" + who
            assert cards[card]["play"]["effects"]
            assert skills[card + "_01"]["card"] == card
            owner = (
                "clarisa"
                if name in ("curacion", "fenix", "regeneracion")
                else "iosepus"
            )
            assert skills[card + "_01"]["character"] == owner
            operations = json.dumps(cards[card]["play"], ensure_ascii=False)
            assert "Parnecio" not in operations
