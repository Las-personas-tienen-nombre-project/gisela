"""V0.5: evaluated contests are generic, transactional and reproducible."""

import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import (
    PackageRejected,
    admit_package,
    admit_package_file,
)
from gisela.engine.runtime import GiselaSession, restore_session
from gisela.engine.tests.test_scripted_npc_skills import advance, play_until

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "tegularis_npc_evaluaciones_v05.package.json"
)


def package():
    return json.loads(SOURCE.read_text())


def run(seed="c" * 64, pkg=None):
    adm = admit_package(pkg) if pkg is not None else admit_package_file(SOURCE)
    session = GiselaSession.new_session(adm, seed=seed)
    play_until(session, "Consulte los eventos contest_resolved")
    state = session.export()
    return session, adm, state


def contests(state):
    return [
        event["detail"]
        for event in state["history"]["trace"]
        if event["kind"] == "contest_resolved"
    ]


def test_admission_and_two_real_contests():
    _, _, state = run()
    entries = contests(state)
    assert len(entries) == 2
    assert state["rng"]["counter"] >= 4
    assert all(
        1 <= x <= 10 for c in entries for x in c["left"]["rolls"] + c["right"]["rolls"]
    )
    assert entries[0]["right"]["bonus"] == -5, "enorme should modify Evasion"
    assert entries[1]["right"]["bonus"] == -5
    assert entries[1]["left"]["base"] == 10, (
        "INT 9 is for damage; Hit uses AWA 8 + floor(X/10)"
    )
    assert entries[1]["left"]["total"] == entries[1]["left"]["die_value"] + 10


def test_both_hit_and_miss_are_observable_and_costs_paid():
    seen = set()
    for i in range(30):
        _, _, state = run(f"{i:064x}")
        entries = contests(state)
        assert len(entries) == 2
        magic = entries[-1]["winner"]
        seen.add(magic)
        facts = {f["fact"] for f in state["history"]["facts"]}
        assert ("magic_blast_impacto" in facts) == (magic == "left")
        assert ("magic_blast_fallo" in facts) == (magic == "right")
        assert state["narrative"]["session_variables"]["mana_iosepus"] == 39
        if len(seen) == 2:
            break
    assert seen == {"left", "right"}


def test_replay_and_restore():
    first, adm, state = run()
    _second, _, other = run()
    assert state == other
    restored = restore_session(adm, state)
    assert restored.export() == first.export()
    assert restored.observe() == first.observe()


def test_wrong_profile_rejected_at_admission():
    pkg = package()
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    card["play"]["effects"][1]["profile"] = "unknown_profile"
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_non_numeric_base_rejected_at_admission():
    pkg = package()
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    card["play"]["effects"][1]["left"]["base"] = {"literal": "wrong"}
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_rollback_on_runtime_division_by_zero():
    pkg = package()
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    contest = card["play"]["effects"][1]
    contest["left"]["base"] = {
        "math": {"op": "floor_divide", "left": {"literal": 8}, "right": {"literal": 0}}
    }
    admitted = admit_package(pkg)
    session = GiselaSession.new_session(admitted, seed="c" * 64)
    play_until(session, "Iosepus ejecuta Magic Blast")
    previous = session.export()
    result = advance(session)
    assert result["status"] == "error"
    assert result["error"]["code"] == "PROPERTY_RANGE"
    assert session.export() == previous


def test_player_cannot_execute_dragon_skill():
    admitted = admit_package_file(SOURCE)
    session = GiselaSession.new_session(admitted, seed="c" * 64)
    state = session.export()
    view = session.observe()
    r = session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": "play_zarpa_01",
        }
    )
    assert r["status"] == "error" and r["error"]["code"] == "INVALID_ACTION"
    assert state == session.export()


def test_dodge_contributes_to_contest_when_context_matches():
    pkg = package()
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    contest = card["play"]["effects"][1]
    contest["right"]["context"]["participants"] = [
        {"entity": "parnecio", "role": "defender"}
    ]
    _, _, state = run(pkg=pkg)
    assert contests(state)[-1]["right"]["bonus"] == 2  # Dodge via TRAITS


def test_unknown_fact_in_nested_outcome_rejected():
    pkg = package()
    card = next(c for c in pkg["cards"] if c["id"] == "magic_blast")
    contest = card["play"]["effects"][1]
    contest["on_win"].append({"op": "record_fact", "fact": "unregistered_fact"})
    with pytest.raises(PackageRejected):
        admit_package(pkg)


def test_parameter_can_be_used_in_contested_base_and_is_bound_per_cast():
    p = package()
    all_actions = [
        e for n in p["nodes"] for s in n["steps"] for e in s.get("effects", [])
    ]
    action = next(e for e in all_actions if e.get("skill_instance") == "magic_blast_01")
    action["arguments"]["x"] = {"literal": 0}
    _, _, state = run(pkg=p)
    assert contests(state)[-1]["left"]["base"] == 8
    assert state["narrative"]["session_variables"]["mana_iosepus"] == 59
