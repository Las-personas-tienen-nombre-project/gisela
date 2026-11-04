"""Confirmed public causal scopes remain exact across actions and restore."""

from __future__ import annotations

from gisela.contracts.admit_package import admit_package
from gisela.contracts.semantic_validator import Validator
from gisela.engine.consequences import apply_operation
from gisela.engine.effect_context import EffectContext
from gisela.engine.pending import DecisionReplay
from gisela.engine.presentation_views import project_view
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.tests.test_actuation_public_v073 import fresh, request


def _advance(session, amount):
    for _ in range(amount):
        view = session.observe()
        if view["status"] == "ended":
            break
        assert session.act(request(view))["status"] == "ok"


def test_confirmed_action_records_are_correlated_and_restorable():
    admitted, session = fresh()
    _advance(session, 4)
    public = session.observe()["actuation"]["causal"]
    starts = [event for event in public if event["kind"] == "skill_started"]
    assert starts
    for start in starts:
        identifier = start["causal_execution_id"]
        children = [e for e in public if e.get("causal_execution_id") == identifier]
        assert children[0] == start
        assert children[-1]["kind"] == "skill_played"
        assert len(children) >= 3
    assert len({s["causal_execution_id"] for s in starts}) == len(starts)
    state = session.export()
    clone = restore_session(admitted, state)
    assert clone.observe() == session.observe()
    _advance(session, 2)
    _advance(clone, 2)
    assert clone.export() == session.export()
    validator = Validator()
    validator.use_version("1.5")
    assert validator.check_schema("observe", session.observe())


def test_grouping_never_steals_an_unrelated_or_incomplete_record():
    events = [
        {
            "sequence": 1,
            "kind": "skill_started",
            "causal_execution_id": "action_00000001",
        },
        {"sequence": 2, "kind": "variable_changed"},
        {
            "sequence": 3,
            "kind": "skill_started",
            "causal_execution_id": "action_00000003",
        },
        {
            "sequence": 4,
            "kind": "variable_changed",
            "causal_execution_id": "action_00000001",
        },
        {
            "sequence": 5,
            "kind": "variable_changed",
            "causal_execution_id": "action_00000999",
        },
        {
            "sequence": 6,
            "kind": "skill_played",
            "causal_execution_id": "action_00000003",
        },
    ]
    result = project_view(
        {"actuation": {"causal": events}},
        {
            "component": "event_log",
            "source": "actuation.causal",
            "group_by": "action",
            "limit": 10,
        },
    )
    blocks = result["blocks"]
    assert [b["kind"] for b in blocks] == ["action", "event", "action", "event"]
    assert [e["sequence"] for e in blocks[0]["events"]] == [1, 4]
    assert [e["sequence"] for e in blocks[2]["events"]] == [3, 6]
    assert blocks[-1]["event"]["sequence"] == 5
    assert [e["sequence"] for e in result["items"]] == [1, 2, 3, 4, 5, 6]


def test_bounded_window_does_not_invent_action_start():
    events = [
        {
            "sequence": 1,
            "kind": "skill_started",
            "causal_execution_id": "action_00000001",
        },
        {"sequence": 2, "kind": "dice_roll", "causal_execution_id": "action_00000001"},
        {
            "sequence": 3,
            "kind": "skill_played",
            "causal_execution_id": "action_00000001",
        },
    ]
    definition = {
        "component": "event_log",
        "source": "actuation.causal",
        "group_by": "action",
        "limit": 2,
    }
    result = project_view({"actuation": {"causal": events}}, definition)
    assert [block["kind"] for block in result["blocks"]] == ["event", "event"]
    assert result["truncated"]


def test_rejected_act_does_not_publish_any_causal_identifier():
    _, session = fresh()
    before = session.export()
    view = session.observe()
    action = request(view)
    action["action_id"] = "actturn_not_offered"
    assert session.act(action)["status"] == "error"
    assert session.export() == before
    assert session.act(request(view))["status"] == "ok"
    committed = session.export()
    assert session.act(request(view))["status"] == "error"
    assert session.export() == committed


def test_legacy_trace_without_execution_ids_remains_valid():
    admitted, session = fresh()
    for item in session._state["history"]["trace"]:
        item.pop("causal_execution_id", None)
    clone = restore_session(admitted, session.export())
    assert clone.observe() == session.observe()


def test_bad_execution_id_is_rejected_by_contract():
    admitted, session = fresh()
    _advance(session, 1)
    snapshot = session.export()
    item = next(e for e in snapshot["history"]["trace"] if e.get("causal_execution_id"))
    item["causal_execution_id"] = "../../private"
    import pytest

    from gisela.engine.errors import EngineFailure

    with pytest.raises(EngineFailure):
        restore_session(admitted, snapshot)


def test_nested_skills_have_independent_causal_scopes():
    admitted, _ = fresh()
    package = admitted.materialize()
    cards = {card["id"]: card for card in package["cards"]}
    cards["slash"]["play"].update(
        requires={"constant": True},
        outcomes=[],
        effects=[
            {"op": "play_skill", "skill_instance": "hachazo_01"},
            {"op": "emit_message", "template": "exterior", "values": {}},
        ],
    )
    cards["hachazo"]["play"].update(
        requires={"constant": True},
        outcomes=[],
        effects=[
            {"op": "emit_message", "template": "interior", "values": {}},
        ],
    )
    cards["hachazo"]["return_policy"] = {"default": "hand"}
    session = new_session(admit_package(package), seed="a" * 64)
    for _ in range(30):
        view = session.observe()
        if view["actuation"]["actor"] == "parnecio":
            break
        assert session.act(request(view))["status"] == "ok"
    offset = len(session.export()["history"]["trace"])
    slash = next(item for item in view["actions"] if item["id"] == "slash_01")
    assert session.act(request(view, slash))["status"] == "ok"
    trace = session.export()["history"]["trace"][offset:]
    starts = [item for item in trace if item["kind"] == "skill_started"]
    assert len(starts) == 2
    outer, inner = (item["causal_execution_id"] for item in starts)
    assert outer != inner
    messages = {
        item["detail"]["text"]: item["causal_execution_id"]
        for item in trace
        if item["kind"] == "author_message"
    }
    assert messages == {"exterior": outer, "interior": inner}
    completed = [
        item["causal_execution_id"] for item in trace if item["kind"] == "skill_played"
    ]
    assert completed == [inner, outer]


def test_effect_lifecycle_children_keep_the_explicit_causal_scope():
    admitted, _ = fresh()
    package = admitted.materialize()
    effect = next(
        card for card in package["cards"] if card["id"] == "ef_armadura_parnecio"
    )
    effect["on_apply"] = [{"op": "emit_message", "template": "aplicado", "values": {}}]
    effect["on_expire"] = [
        {"op": "emit_message", "template": "finalizado", "values": {}}
    ]
    session = new_session(admit_package(package), seed="a" * 64)
    state = session.export()
    context = EffectContext(
        "prueba_causal",
        DecisionReplay(),
        session._definitions,
        causal_execution_id="action_00000001",
    )
    apply_operation(
        state,
        {"op": "apply_effect", "effect": effect["id"], "target": "parnecio"},
        context,
    )
    instance = next(
        item for item in state["world"]["effects"] if item["card"] == effect["id"]
    )
    apply_operation(
        state, {"op": "end_effect", "effect_instance": instance["id"]}, context
    )
    messages = [
        item for item in state["history"]["trace"] if item["kind"] == "author_message"
    ]
    assert [item["detail"]["text"] for item in messages] == ["aplicado", "finalizado"]
    assert all(item["causal_execution_id"] == "action_00000001" for item in messages)
