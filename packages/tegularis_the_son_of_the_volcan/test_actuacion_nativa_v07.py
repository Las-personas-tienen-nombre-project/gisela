"""Pruebas del reloj GISELA v1.5. No certifican cartas sin efectos."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import (
    PackageRejected,
    admit_package,
    admit_package_file,
)
from gisela.engine.actuation import ActuationDuration
from gisela.engine.runtime import new_session, restore_session

PACKAGE_PATH = Path(__file__).with_name("05_actuacion_v07_laboratorio.package.json")
SEED = "a" * 64


def fresh(seed=SEED):
    admitted = admit_package_file(PACKAGE_PATH)
    return admitted, new_session(admitted, seed=seed)


def advance(session):
    view = session.actuation_observe()
    choice = None
    if view["actor"] == "parnecio":
        enabled = [x for x in view["offers"] if x["enabled"] and x["id"] != "pasar"]
        choice = enabled[0]["id"] if enabled else None
    return session.actuation_step(session.export()["revision"], choice)


def test_native_package_is_admitted():
    assert fresh()[1].actuation_observe()["active"]


def test_five_actors_once_in_initiative():
    _, session = fresh()
    view = session.actuation_observe()
    assert set(view["order"]) == {
        "parnecio",
        "gillius",
        "clarisa",
        "iosepus",
        "tegularis",
    }
    assert len(view["order"]) == len(set(view["order"])) == 5
    initiative = session.export()["actuation"]["initiative"]
    assert all(
        x["score"] == x["strength"] + x["awareness"] + x["fortune"] + x["die"]
        for x in initiative
    )


def test_one_initiative_for_three_rounds():
    _, session = fresh()
    original = copy.deepcopy(session.export()["actuation"]["initiative"])
    for _ in range(100):
        if session.actuation_observe()["round"] >= 4:
            break
        assert advance(session)["status"] == "ok"
    else:
        pytest.fail("No terminó tres rondas")
    assert session.export()["actuation"]["initiative"] == original
    assert (
        len(
            [
                e
                for e in session.export()["actuation"]["events"]
                if e["kind"] == "initiative"
            ]
        )
        == 1
    )


def test_action_thresholds_from_author():
    _, session = fresh()
    turns = {}
    for _ in range(14):
        view = session.actuation_observe()
        if view["round"] != 1:
            break
        turns.setdefault(view["actor"], view["remaining"])
        assert advance(session)["status"] == "ok"
    assert turns == {
        "tegularis": 3,
        "clarisa": 2,
        "gillius": 3,
        "parnecio": 2,
        "iosepus": 2,
    }


def test_narrative_turn_independent():
    _, session = fresh()
    original = session.export()["turn"]
    for _ in range(15):
        assert advance(session)["status"] == "ok"
    assert session.export()["turn"] == original


def test_duration_counts_beneficiary_turns_not_actions():
    _, session = fresh()
    assert (
        session.actuation_add_duration(
            session.export()["revision"],
            ActuationDuration("escudo_de_prueba", "gillius", 2),
        )["status"]
        == "ok"
    )

    def remaining():
        return next(
            (
                e["remaining"]
                for e in session.export()["actuation"]["effects"]
                if e["id"] == "escudo_de_prueba"
            ),
            None,
        )

    assert remaining() == 2
    for _ in range(100):
        if remaining() == 1:
            break
        assert advance(session)["status"] == "ok"
    assert remaining() == 1
    for _ in range(100):
        if remaining() is None:
            break
        assert advance(session)["status"] == "ok"
    assert remaining() is None
    assert (
        len(
            [
                x
                for x in session.export()["actuation"]["events"]
                if x["kind"] == "effect_expired"
                and x["detail"].get("effect") == "escudo_de_prueba"
            ]
        )
        == 1
    )


def test_stale_revision_cannot_mutate():
    _, session = fresh()
    old = session.export()
    result = session.actuation_step(old["revision"] + 1)
    assert result["status"] == "error"
    assert session.export() == old


def test_illegal_player_controls_npc_no_mutation():
    _, session = fresh()
    snapshot = session.export()
    result = session.actuation_step(snapshot["revision"], "firebreath_01")
    assert result["status"] == "error"
    assert session.export() == snapshot


def test_player_cannot_skip_without_author_permission():
    p = json.loads(PACKAGE_PATH.read_text())
    for person in p["actuation"]["participants"]:
        if person["character"] == "parnecio":
            person["allow_pass"] = False
    admitted = admit_package(p)
    session = new_session(admitted, seed=SEED)
    for _ in range(50):
        if session.actuation_observe()["actor"] == "parnecio":
            break
        assert advance(session)["status"] == "ok"
    saved = session.export()
    assert session.actuation_step(saved["revision"])["status"] == "error"
    assert session.export() == saved


def test_restore_continuation_identical():
    admitted, first = fresh()
    for _ in range(13):
        assert advance(first)["status"] == "ok"
    restored = restore_session(admitted, first.export())
    for _ in range(26):
        assert advance(first)["status"] == "ok"
        assert advance(restored)["status"] == "ok"
    assert first.export() == restored.export()


def test_seed_reproduction():
    _, a = fresh()
    _, b = fresh()
    for _ in range(20):
        assert advance(a)["status"] == "ok"
        assert advance(b)["status"] == "ok"
    assert a.export() == b.export()


def test_contract_rejects_invalid_author_threshold():
    p = json.loads(PACKAGE_PATH.read_text())
    p["actuation"]["thresholds"][0]["actions"] = -1
    with pytest.raises(PackageRejected):
        admit_package(p)


def test_failed_execution_preserves_rng_and_clock():
    _, s = fresh()
    while s.actuation_observe()["actor"] != "parnecio":
        assert advance(s)["status"] == "ok"
    snapshot = s.export()
    assert s.actuation_step(snapshot["revision"], "blai_01")["status"] == "error"
    assert s.export() == snapshot


def _with_probed_effect(*, blocks=False):
    from gisela.engine.effect_context import EffectContext
    from gisela.engine.pending import DecisionReplay

    document = json.loads(PACKAGE_PATH.read_text())
    document["cards"].append(
        {
            "id": "efecto_v07_prueba",
            "kind": "effect",
            "title": {"text": "Efecto autoral"},
            "actuation_turns": 2 if not blocks else 1,
            "actuation_blocks_actions": blocks,
            "on_actor_turn_start": [
                {
                    "op": "add",
                    "target": {"var": {"scope": "session", "key": "tp_parnecio"}},
                    "value": {"literal": 1},
                }
            ],
        }
    )
    admitted = admit_package(document)
    session = new_session(admitted, seed=SEED)
    draft = session.export()
    session._operations(
        draft,
        [{"op": "apply_effect", "effect": "efecto_v07_prueba", "target": "gillius"}],
        EffectContext("test_effect", DecisionReplay(), session._definitions),
    )
    draft["revision"] += 1
    session._validate_state(draft)
    session._state = (
        draft  # Fixture de laboratorio: preparación por ruta interna de autor.
    )
    return session, admitted


def test_linked_effect_periodic_once_per_actor_turn():
    session, admitted = _with_probed_effect()
    before = session.export()["narrative"]["session_variables"]["tp_parnecio"]
    for _ in range(100):
        if not session.export()["actuation"]["effects"]:
            break
        assert advance(session)["status"] == "ok"
    else:
        pytest.fail("Efecto sin vencimiento")
    assert (
        session.export()["narrative"]["session_variables"]["tp_parnecio"] - before == 2
    )
    assert not any(
        e["card"] == "efecto_v07_prueba" for e in session.export()["world"]["effects"]
    )
    assert restore_session(admitted, session.export()).export() == session.export()


def test_linked_effect_blocks_entire_actor_turn():
    session, _ = _with_probed_effect(blocks=True)
    for _ in range(50):
        if session.actuation_observe()["actor"] == "gillius":
            pytest.fail("Actor paralizado no debió ofrecer acciones")
        if any(
            x["kind"] == "actor_turn_ended" and x["detail"]["actor"] == "gillius"
            for x in session.actuation_observe()["events"]
        ):
            break
        assert advance(session)["status"] == "ok"
    assert (
        sum(
            x["kind"] == "action_consumed" and x["detail"]["actor"] == "gillius"
            for x in session.actuation_observe()["events"]
        )
        == 0
    )
    assert not session.export()["actuation"]["effects"]


def test_message_in_confirmed_history():
    _, session = fresh()
    for _ in range(40):
        if session.actuation_observe()["actor"] == "parnecio":
            break
        assert advance(session)["status"] == "ok"
    result = session.actuation_step(session.export()["revision"], "slash_01")
    assert result["status"] == "ok"
    lines = [x["text"] for x in session.read_history() if x["kind"] == "action"]
    assert any("SLASH resolvió " in x and "puntos de daño" in x for x in lines)
    assert any(
        x["kind"] == "author_message" for x in session.export()["history"]["trace"]
    )


def test_tampered_clock_rejected_by_restore():
    admitted, session = fresh()
    altered = session.export()
    altered["actuation"]["initiative"][0]["score"] += 1
    from gisela.engine.errors import EngineFailure

    with pytest.raises(EngineFailure):
        restore_session(admitted, altered)


@pytest.mark.parametrize(
    "duration",
    [
        None,
        {"identifier": "escudo", "beneficiary": "gillius", "turns": 2},
        ActuationDuration("escudo", "gillius", 0),
        ActuationDuration("escudo", "gillius", True),
        ActuationDuration("escudo", "gillius", 1001),
        ActuationDuration("escudo", "ausente", 2),
    ],
)
def test_invalid_duration_request_is_atomic(duration):
    _, session = fresh()
    before = session.export()
    result = session.actuation_add_duration(before["revision"], duration)
    assert result["status"] == "error"
    assert session.export() == before


def test_duration_refresh_and_identity_conflict():
    _, session = fresh()
    duration = ActuationDuration("escudo_de_prueba", "gillius", 2)
    assert (
        session.actuation_add_duration(session.export()["revision"], duration)["status"]
        == "ok"
    )
    duration = ActuationDuration("escudo_de_prueba", "gillius", 3)
    assert (
        session.actuation_add_duration(session.export()["revision"], duration)["status"]
        == "ok"
    )
    effects = session.export()["actuation"]["effects"]
    assert effects == [
        {
            "id": "escudo_de_prueba",
            "beneficiary": "gillius",
            "remaining": 3,
            "linked": False,
        }
    ]
    before = session.export()
    conflicting = ActuationDuration("escudo_de_prueba", "parnecio", 2)
    assert (
        session.actuation_add_duration(before["revision"], conflicting)["status"]
        == "error"
    )
    assert session.export() == before


def test_duration_rejects_stale_revision_and_gateway_access():
    from gisela.engine.authorized_gateway import ExecutionGateway, Principal

    _, session = fresh()
    before = session.export()
    duration = ActuationDuration("escudo_de_prueba", "gillius", 2)
    assert (
        session.actuation_add_duration(before["revision"] + 1, duration)["status"]
        == "error"
    )
    gateway = ExecutionGateway(
        session, {"tester": Principal("tester", frozenset({"act", "observe_player"}))}
    )
    try:
        assert (
            session.actuation_add_duration(before["revision"], duration)["status"]
            == "error"
        )
    finally:
        gateway.close()
    assert session.export() == before
