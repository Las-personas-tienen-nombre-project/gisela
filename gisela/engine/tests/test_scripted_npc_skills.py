"""Extensión general: una habilidad de NPC se ejecuta desde el guion."""

import json
from pathlib import Path

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import GiselaSession, restore_session

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "tegularis_npc_ronda_1.package.json"
)
SEED = "a" * 64


def session(pkg=None):
    admitted = admit_package_file(SOURCE) if pkg is None else admit_package(pkg)
    return GiselaSession.new_session(admitted, seed=SEED), admitted


def advance(s, skill="slash_01"):
    """Elige la habilidad del jugador solo cuando aparece; avanza narraciones."""
    view = s.observe()
    enabled = [a for a in view["actions"] if a["enabled"]]
    candidate = next((a for a in enabled if a.get("id") == skill), enabled[0])
    response = s.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": candidate["action_id"],
        }
    )
    return response


def play_until(s, marker):
    for _ in range(40):
        v = s.observe()
        if v["content"].get("text", "").startswith(marker):
            return
        result = advance(s)
        assert result["status"] == "ok", result
    raise AssertionError("no se alcanzó " + marker)


def owned(source, state):
    return [
        e
        for e in state["history"]["trace"]
        if e["kind"] == "skill_played" and e["source"] == source
    ]


def character(s, name):
    return next(c for c in s.export()["world"]["characters"] if c["id"] == name)


def test_npc_plays_real_cards_and_updates_shared_world():
    s, _ = session()
    play_until(s, "Iosepus utiliza Concentración")
    state = s.export()
    assert character(s, "parnecio")["properties"]["heridas"] == 19
    assert character(s, "gillius")["properties"]["heridas"] == 39
    assert character(s, "tegularis")["properties"]["heridas"] >= 30
    assert state["narrative"]["session_variables"]["mana_tegularis"] == 40
    assert state["narrative"]["session_variables"]["mana_iosepus"] == 60
    assert state["narrative"]["session_variables"]["mana_clarisa"] == 40
    assert state["narrative"]["session_variables"]["tp_gillius"] == 10
    for id in (
        "firebreath_01",
        "curacion_01",
        "hachazo_01",
        "concentracion_iosepus_01",
    ):
        logs = owned(id, state)
        assert len(logs) == 1
        assert logs[0]["detail"]["origin"] == "script"
    assert owned("slash_01", state)[0]["detail"]["origin"] == "player"
    assert not any(a.get("id") == "hachazo_01" for a in s.observe()["actions"])


def test_player_cannot_invoke_npc_card_even_when_npc_uses_it():
    s, _ = session()
    view = s.observe()
    before = s.export()
    response = s.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": "play_hachazo_01",
        }
    )
    assert response["status"] == "error"
    assert response["error"]["code"] == "INVALID_ACTION"
    assert s.export() == before


def test_failed_npc_requirement_does_not_commit_partial_effects():
    pkg = json.loads(SOURCE.read_text())
    pkg["initial_state"]["session_variables"]["mana_tegularis"] = 0
    s, _ = session(pkg)
    play_until(s, "Tegularis abre sus fauces")
    before = s.export()
    result = advance(s)
    assert result["status"] == "error"
    assert result["error"]["code"] == "INVALID_ACTION"
    assert s.export() == before


def test_script_cannot_force_play_players_card():
    pkg = json.loads(SOURCE.read_text())
    for node in pkg["nodes"]:
        if node["id"] == "respuesta_npc":
            node["steps"][1]["effects"][0]["skill_instance"] = "slash_01"
    s, _ = session(pkg)
    play_until(s, "Tegularis abre sus fauces")
    before = s.export()
    result = advance(s)
    assert result["status"] == "error"
    assert result["error"]["code"] == "INVALID_ACTION"
    assert s.export() == before


def test_scripted_npc_actions_are_replayable_and_restoreable():
    a, admitted = session()
    b, _ = session()
    play_until(a, "Iosepus utiliza Concentración")
    play_until(b, "Iosepus utiliza Concentración")
    assert a.export() == b.export()
    restored = restore_session(admitted, a.export())
    assert restored.export() == a.export()
    assert restored.observe() == a.observe()


def test_node_completed_rule_can_trigger_npc_skill():
    pkg = json.loads(SOURCE.read_text())
    pkg["rules"].append(
        {
            "id": "respuesta_del_dragon",
            "trigger": {"on": "node_completed", "node": "inicio"},
            "effects": [{"op": "play_skill", "skill_instance": "firebreath_01"}],
        }
    )
    for node in pkg["nodes"]:
        if node["id"] == "respuesta_npc":
            node["steps"][1]["effects"] = [
                {"op": "record_fact", "fact": "firebreath_resuelto"}
            ]
    s, _ = session(pkg)
    play_until(s, "Tegularis abre sus fauces")
    assert len(owned("firebreath_01", s.export())) == 1
    assert character(s, "parnecio")["properties"]["heridas"] == 39


def test_npc_skill_cannot_open_player_auxiliary_choice():
    pkg = json.loads(SOURCE.read_text())
    spell = next(c for c in pkg["cards"] if c["id"] == "firebreath")
    # The ability consumes its own slot, then grants another skill to fill that
    # slot. Returning the original to a full hand would prompt for a discard;
    # NPC execution must fail closed instead of asking the player.
    spell["play"]["effects"] = [
        {"op": "grant_skill", "character": "tegularis", "skill": "zarpa"}
    ]
    next(
        cap
        for cap in pkg["initial_state"]["capacities"]
        if cap["character"] == "tegularis"
    )["hand"] = 6
    s, _ = session(pkg)
    play_until(s, "Tegularis abre sus fauces")
    before = s.export()
    response = advance(s)
    assert response["status"] == "error"
    assert response["error"]["code"] in ("SCRIPT_CHOICE_REQUIRED", "CAPACITY_EXCEEDED")
    assert s.export() == before
