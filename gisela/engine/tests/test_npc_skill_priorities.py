"""GISELA: prioridades autorales, alternativas y rollback atómico de habilidades NPC."""

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
    / "tegularis_npc_prioridades_v03.package.json"
)
SEED = "b" * 64


def fixture():
    return json.loads(SOURCE.read_text())


def session(pkg=None):
    admitted = admit_package(pkg) if pkg is not None else admit_package_file(SOURCE)
    return GiselaSession.new_session(admitted, seed=SEED), admitted


def run_to(s, marker):
    play_until(s, marker)
    return s.export()


def step_after(s, marker):
    run_to(s, marker)
    response = advance(s)
    assert response["status"] == "ok", response
    return s.export()


def test_priorities_choose_heal_then_mana_on_next_action():
    s, _ = session()
    before = step_after(s, "Clarisa examina")
    assert character(s, "parnecio")["properties"]["heridas"] == 19
    assert before["narrative"]["session_variables"]["mana_clarisa"] == 15
    assert len(owned("curacion_01", before)) == 1
    assert not owned("concentracion_clarisa_01", before)
    after = step_after(s, "Clarisa reevalúa")
    assert after["narrative"]["session_variables"]["mana_clarisa"] == 45
    assert character(s, "parnecio")["properties"]["heridas"] == 19
    assert len(owned("curacion_01", after)) == 1
    assert len(owned("concentracion_clarisa_01", after)) == 1
    assert owned("concentracion_clarisa_01", after)[0]["detail"]["origin"] == "script"


def test_low_mana_skips_heal_and_uses_concentration():
    pkg = fixture()
    pkg["initial_state"]["session_variables"]["mana_clarisa"] = 5
    s, _ = session(pkg)
    after = step_after(s, "Clarisa examina")
    assert after["narrative"]["session_variables"]["mana_clarisa"] == 35
    assert character(s, "parnecio")["properties"]["heridas"] == 39
    assert not owned("curacion_01", after)
    assert len(owned("concentracion_clarisa_01", after)) == 1


def test_guard_can_skip_first_candidate():
    pkg = fixture()
    node = next(n for n in pkg["nodes"] if n["id"] == "respuesta_npc")
    priority = next(
        step["effects"][0]
        for step in node["steps"]
        if step["op"] == "effect"
        and step.get("effects", [{}])[0].get("op") == "play_first_skill"
    )
    priority["candidates"][0]["when"] = {"constant": False}
    pkg["initial_state"]["session_variables"]["mana_clarisa"] = 25
    s, _ = session(pkg)
    after = step_after(s, "Clarisa examina")
    assert len(owned("concentracion_clarisa_01", after)) == 1
    assert not owned("curacion_01", after)


def test_when_no_option_plays_otherwise_operations():
    pkg = fixture()
    pkg["initial_state"]["session_variables"]["mana_clarisa"] = 60
    node = next(n for n in pkg["nodes"] if n["id"] == "respuesta_npc")
    priority = next(
        step["effects"][0]
        for step in node["steps"]
        if step["op"] == "effect"
        and step.get("effects", [{}])[0].get("op") == "play_first_skill"
    )
    priority["candidates"][0]["when"] = {"constant": False}
    s, _ = session(pkg)
    after = step_after(s, "Clarisa examina")
    assert "clarisa_sin_opcion" in [e["fact"] for e in after["history"]["facts"]]
    assert after["narrative"]["session_variables"]["mana_clarisa"] == 60
    assert not owned("curacion_01", after)
    assert not owned("concentracion_clarisa_01", after)


def test_unsupported_player_skill_is_not_a_fallback():
    pkg = fixture()
    node = next(n for n in pkg["nodes"] if n["id"] == "respuesta_npc")
    priority = next(
        step["effects"][0]
        for step in node["steps"]
        if step["op"] == "effect"
        and step.get("effects", [{}])[0].get("op") == "play_first_skill"
    )
    priority["candidates"] = [
        {"skill_instance": "slash_01"},
        {"skill_instance": "concentracion_clarisa_01"},
    ]
    s, _ = session(pkg)
    run_to(s, "Firebreath deja")
    before = s.export()
    r = advance(s)
    assert r["status"] == "error" and r["error"]["code"] == "INVALID_ACTION"
    assert s.export() == before


def test_runtime_failure_does_not_silently_try_next_candidate():
    pkg = fixture()
    card = next(c for c in pkg["cards"] if c["id"] == "curacion")
    card["play"]["effects"].append(
        {
            "op": "add",
            "target": {"property": {"entity": "tegularis", "key": "heridas"}},
            "value": {"literal": 99999999},
        }
    )
    s, _ = session(pkg)
    run_to(s, "Firebreath deja")
    before = s.export()
    r = advance(s)
    assert r["status"] == "error", r
    assert s.export() == before
    assert not owned("concentracion_clarisa_01", s.export())


def test_removed_first_card_can_fallback():
    pkg = fixture()
    card = next(c for c in pkg["cards"] if c["id"] == "curacion")
    card["return_policy"] = {"default": "discard"}
    s, _ = session(pkg)
    run_to(s, "Clarisa reevalúa")
    after = advance(s)
    assert after["status"] == "ok", after
    assert len(owned("concentracion_clarisa_01", s.export())) == 1


def test_bad_candidate_reference_is_rejected_on_admission():
    pkg = fixture()
    node = next(n for n in pkg["nodes"] if n["id"] == "respuesta_npc")
    priority = next(
        step["effects"][0]
        for step in node["steps"]
        if step["op"] == "effect"
        and step.get("effects", [{}])[0].get("op") == "play_first_skill"
    )
    priority["candidates"][0]["skill_instance"] = "habilidad_inexistente"
    with pytest.raises(PackageRejected) as exc:
        admit_package(pkg)
    assert any("UNKNOWN" in d.code for d in exc.value.diagnostics)


def test_undeclared_fact_in_otherwise_is_rejected_on_admission():
    pkg = fixture()
    node = next(n for n in pkg["nodes"] if n["id"] == "respuesta_npc")
    priority = next(
        step["effects"][0]
        for step in node["steps"]
        if step["op"] == "effect"
        and step.get("effects", [{}])[0].get("op") == "play_first_skill"
    )
    priority["otherwise"][0]["fact"] = "hecho_inexistente"
    with pytest.raises(PackageRejected) as exc:
        admit_package(pkg)
    assert any(d.code == "UNKNOWN_FACT" for d in exc.value.diagnostics)


def test_repeatability_and_restore():
    a, adm = session()
    b, _ = session()
    run_to(a, "Compruebe mana_clarisa")
    run_to(b, "Compruebe mana_clarisa")
    assert a.export() == b.export()
    r = restore_session(adm, a.export())
    assert r.export() == a.export()
    assert r.observe() == a.observe()


def test_declared_rule_can_select_an_npc_skill():
    pkg = fixture()
    pkg["initial_state"]["session_variables"]["mana_clarisa"] = 5
    pkg["rules"].append(
        {
            "id": "clarisa_responde_al_inicio",
            "trigger": {"on": "node_completed", "node": "inicio"},
            "effects": [
                {
                    "op": "play_first_skill",
                    "candidates": [
                        {"skill_instance": "curacion_01"},
                        {"skill_instance": "concentracion_clarisa_01"},
                    ],
                }
            ],
        }
    )
    s, _ = session(pkg)
    run_to(s, "Tegularis abre sus fauces")
    assert len(owned("concentracion_clarisa_01", s.export())) == 1
    assert not owned("curacion_01", s.export())
    assert s.export()["narrative"]["session_variables"]["mana_clarisa"] == 35


def test_reserved_card_is_skipped_without_consuming_resources():
    pkg = fixture()
    next(s for s in pkg["initial_state"]["skills"] if s["id"] == "curacion_01")[
        "zone"
    ] = "reserve"
    pkg["initial_state"]["session_variables"]["mana_clarisa"] = 15
    s, _ = session(pkg)
    after = step_after(s, "Clarisa examina")
    assert len(owned("concentracion_clarisa_01", after)) == 1
    assert not owned("curacion_01", after)
