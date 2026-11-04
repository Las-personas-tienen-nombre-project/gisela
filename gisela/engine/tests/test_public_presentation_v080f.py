"""Public Observe/Act integration, strictly from confirmed projections."""

import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.engine.runtime import new_session, restore_session

PACKAGE = (
    Path(__file__).resolve().parents[3]
    / "packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json"
)


def source():
    return json.loads(PACKAGE.read_text(encoding="utf-8"))


def session():
    admitted = admit_package(source())
    return admitted, new_session(admitted, seed="0" * 64)


def act(session, view, action):
    return session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": action["action_id"],
        }
    )


def until_player(session):
    for _ in range(30):
        view = session.observe()
        if view["actuation"]["actor"] == "parnecio":
            return view
        result = act(session, view, next(a for a in view["actions"] if a["enabled"]))
        assert result["status"] == "ok"
    pytest.fail("No llegó turno del jugador")


def test_public_resources_and_targets():
    admitted, game = session()
    before = game.export()
    view = game.observe()
    assert len(view["actuation"]["participants"]) == 5
    assert len(view["actuation"]["resources"]) == 15
    assert len(view["actuation"]["initiative"]) == 5
    assert "scratch_hit_parnecio" not in str(view["actuation"]["resources"])
    assert game.export() == before
    view = until_player(game)
    choices = [a for a in view["actions"] if a.get("target")]
    assert {a["target"] for a in choices} == {"gillius", "clarisa", "iosepus"}
    restored = restore_session(admitted, game.export())
    assert restored.observe() == view


def test_authorized_target_and_replay_rejections():
    _, game = session()
    view = until_player(game)
    choice = next(a for a in view["actions"] if a.get("target") == "gillius")
    result = act(game, view, choice)
    assert result["status"] == "ok"
    confirmed = game.export()
    stale = act(game, view, choice)
    assert stale["status"] == "error"
    assert stale["error"]["code"] == "STALE_PROJECTION"
    assert game.export() == confirmed
    invalid = {
        "session_id": game.observe()["session_id"],
        "revision": game.observe()["revision"],
        "action_id": "actturn_nonexistent",
    }
    denied = game.act(invalid)
    assert denied["status"] == "error"
    assert game.export() == confirmed


@pytest.mark.parametrize("field", ["entity", "current", "maximum"])
def test_unpublished_resource_rejected(field):
    package = source()
    item = package["actuation"]["public_resources"][0]
    item[field] = "private_value"
    with pytest.raises(PackageRejected):
        admit_package(package)


def test_invalid_target_rejected():
    package = source()
    package["presentation"]["action_targets"][0]["target"] = "undisclosed"
    with pytest.raises(PackageRejected):
        admit_package(package)
