"""Habilidades NPC parametrizadas: objetivo, costos variables y atomicidad."""

import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import (
    PackageRejected,
    admit_package,
    admit_package_file,
)
from gisela.engine.runtime import GiselaSession, restore_session
from gisela.engine.tests.test_scripted_npc_skills import (
    advance,
    character,
    owned,
    play_until,
)

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "tegularis_npc_argumentos_v04.package.json"
)
SEED = "c" * 64


def package():
    return json.loads(SOURCE.read_text())


def session(pkg=None):
    adm = admit_package(pkg) if pkg is not None else admit_package_file(SOURCE)
    return GiselaSession.new_session(adm, seed=SEED), adm


def node(pkg):
    return next(n for n in pkg["nodes"] if n["id"] == "respuesta_npc")


def skill_action(pkg, skill):
    return next(
        s["effects"][0]
        for s in node(pkg)["steps"]
        if s["op"] == "effect" and s["effects"][0].get("skill_instance") == skill
    )


def run_to(s, marker):
    play_until(s, marker)
    return s.export()


def after(s, marker):
    run_to(s, marker)
    r = advance(s)
    assert r["status"] == "ok", r
    return s.export()


def test_admitted_and_concurrent_character_arguments():
    s, _ = session()
    st = after(s, "Compruebe las heridas de Parnecio")
    assert character(s, "parnecio")["properties"]["heridas"] == 19
    assert character(s, "gillius")["properties"]["heridas"] == 19
    assert st["narrative"]["session_variables"]["mana_clarisa"] == 20
    entries = owned("curacion_01", st)
    assert [e["detail"]["arguments"]["target"] for e in entries] == [
        "parnecio",
        "gillius",
    ]


def test_magic_blast_variable_cost_damage_and_rng():
    s, _ = session()
    state = after(s, "Compruebe blast_die")
    v = state["narrative"]["session_variables"]
    assert v["mana_iosepus"] == 39  # 30+30 por Concentración, luego -21
    assert 1 <= v["blast_die"] <= 10
    assert (
        character(s, "tegularis")["properties"]["heridas"]
        == 30 + 9 + 20 + v["blast_die"]
    )
    entry = owned("magic_blast_01", state)[0]
    assert entry["detail"]["origin"] == "script"
    assert entry["detail"]["arguments"] == {"x": 20}


@pytest.mark.parametrize("x", [0, 1, 20, 39])
def test_different_x_costs_and_damage(x):
    pkg = package()
    skill_action(pkg, "magic_blast_01")["arguments"]["x"] = {"literal": x}
    s, _ = session(pkg)
    state = after(s, "Compruebe blast_die")
    variables = state["narrative"]["session_variables"]
    assert variables["mana_iosepus"] == 60 - (1 + x)
    assert (
        character(s, "tegularis")["properties"]["heridas"]
        == 30 + 9 + x + variables["blast_die"]
    )


def test_runtime_insufficient_mana_rolls_back_exactly():
    pkg = package()
    skill_action(pkg, "magic_blast_01")["arguments"]["x"] = {"literal": 60}
    s, _ = session(pkg)
    run_to(s, "Iosepus ejecuta Magic Blast")
    before = s.export()
    r = advance(s)
    assert r["status"] == "error" and r["error"]["code"] == "INVALID_ACTION", r
    assert s.export() == before


def test_invalid_target_is_rejected_during_admission():
    pkg = package()
    action = next(s["effects"][0] for s in node(pkg)["steps"] if s["id"] == "sacer_on")
    action["candidates"][0]["arguments"]["target"] = {"literal": "nobody"}
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_wrong_argument_type_is_rejected_during_admission():
    pkg = package()
    skill_action(pkg, "magic_blast_01")["arguments"]["x"] = {"literal": "twenty"}
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_wrong_argument_name_is_rejected_during_admission():
    pkg = package()
    skill_action(pkg, "magic_blast_01")["arguments"] = {"z": {"literal": 10}}
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_outside_boundaries_rejected_on_admission():
    pkg = package()
    skill_action(pkg, "magic_blast_01")["arguments"]["x"] = {"literal": 61}
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_static_signature_does_not_mutate_card_catalog():
    pkg = package()
    s, _ = session(pkg)
    after(s, "Compruebe blast_die")
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    assert card["play"]["parameters"][0]["id"] == "x"
    assert card["play"]["requires"]["compare"]["right"]["math"]["right"] == {
        "parameter": "x"
    }


def test_repeatable_and_restoreable():
    a, admitted = session()
    b, _ = session()
    run_to(a, "Compruebe las heridas de Parnecio")
    run_to(b, "Compruebe las heridas de Parnecio")
    assert a.export() == b.export()
    r = restore_session(admitted, a.export())
    assert r.export() == a.export()
    assert r.observe() == a.observe()


def test_missing_parameter_reference_rejected_at_admission():
    pkg = package()
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    card["play"]["effects"][0]["value"]["math"]["right"]["math"]["right"] = {
        "parameter": "missing"
    }
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_skill_with_parameters_remains_unavailable_to_player():
    pkg = package()
    spell = next(c for c in pkg["cards"] if c["id"] == "slash")
    spell["play"]["parameters"] = [{"id": "x", "kind": "integer"}]
    s, _ = session(pkg)
    assert not any(
        a.get("id") == "slash_01" and a["enabled"] for a in s.observe()["actions"]
    )
