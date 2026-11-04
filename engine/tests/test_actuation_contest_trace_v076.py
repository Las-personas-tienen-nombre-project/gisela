"""Contratos de proyección pública para concursos DICE confirmados."""

import copy

from gisela.contracts.semantic_validator import Validator
from gisela.engine.actuation_public import _contests
from gisela.engine.tests.test_actuation_public_v073 import fresh, request


def test_confirmed_contest_is_projected_without_mutation():
    _, session = fresh()
    trace = session._state["history"]["trace"]
    example = {"rolls": [4], "die_value": 4, "base": 8, "bonus": 2, "total": 14}
    trace.append(
        {
            "kind": "contest_resolved",
            "source": "test_card",
            "detail": {
                "profile": "sample",
                "winner": "left",
                "left": example,
                "right": {**example, "total": 12},
                "left_traits": [{"private": "not_public"}],
                "right_traits": [],
            },
        }
    )
    before = copy.deepcopy(session._state)
    view = session.observe()
    assert session._state == before
    contest = view["actuation"]["contests"][-1]
    assert contest["left"]["total"] == 14
    assert "left_traits" not in contest
    schema = Validator()
    schema.use_version("1.5")
    assert schema.check_schema("observe", view)


def test_rejected_action_keeps_confirmed_contests():
    _, session = fresh()
    before = session.observe()["actuation"]["contests"]
    invalid = request(session.observe())
    invalid["action_id"] = "actturn_unoffered"
    snapshot = session.export()
    assert session.act(invalid)["status"] == "error"
    assert session.export() == snapshot
    assert session.observe()["actuation"]["contests"] == before


def test_contest_projection_is_bounded_and_non_destructive():
    _, session = fresh()
    entry = {
        "kind": "contest_resolved",
        "source": "x",
        "detail": {
            "profile": "p",
            "winner": "right",
            "left": {"rolls": [1], "die_value": 1, "base": 1, "bonus": 0, "total": 2},
            "right": {"rolls": [2], "die_value": 2, "base": 1, "bonus": 0, "total": 3},
        },
    }
    session._state["history"]["trace"].extend(copy.deepcopy(entry) for _ in range(15))
    assert len(_contests(session._state)) == 15
    assert len(session.observe()["actuation"]["contests"]) == 12
