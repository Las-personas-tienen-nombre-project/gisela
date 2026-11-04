"""Public Observe/Act contract, authorization and replay for v0.7.3."""

from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.authorized_gateway import ExecutionGateway, Principal
from gisela.engine.runtime import new_session, restore_session

PACKAGE = (
    Path(__file__).resolve().parents[2]
    / "packages/tegularis_the_son_of_the_volcan/08_desenlaces_v072.package.json"
)


def fresh():
    a = admit_package_file(PACKAGE)
    return a, new_session(a, seed="a" * 64)


def request(v, action=None):
    options = [x for x in v["actions"] if x["enabled"]]
    assert options
    return {
        "session_id": v["session_id"],
        "revision": v["revision"],
        "action_id": (action or options[0])["action_id"],
    }


def test_public_schema_and_first_action():
    _, s = fresh()
    view = s.observe()
    validator = Validator()
    validator.use_version("1.5")
    assert validator.check_schema("observe", view)
    assert view["actuation"]["round"] == 1
    assert s.act(request(view))["status"] == "ok"
    assert s.observe()["revision"] == view["revision"] + 1
    assert validator.check_schema("observe", s.observe())


def test_stale_and_unoffered_do_not_mutate():
    _, s = fresh()
    v = s.observe()
    wrong = request(v)
    wrong["action_id"] = "actturn_nonexistent"
    before = s.export()
    assert s.act(wrong)["status"] == "error" and s.export() == before
    assert s.act(request(v))["status"] == "ok"
    changed = s.export()
    assert s.act(request(v))["status"] == "error" and s.export() == changed


def test_restore_continuation_public():
    a, s = fresh()
    for i in range(15):
        v = s.observe()
        if v["status"] == "ended":
            break
        assert s.act(request(v))["status"] == "ok"
    clone = restore_session(a, s.export())
    assert clone.observe() == s.observe()
    for i in range(8):
        v = s.observe()
        if v["status"] == "ended":
            break
        req = request(v)
        assert s.act(req) == clone.act(req)
        assert s.export() == clone.export()


def test_gateway_bound_client_and_idempotency():
    _, s = fresh()
    gateway = ExecutionGateway(
        s,
        {
            "player": Principal(
                "player", frozenset({"act", "observe_player", "observe_glauquir"})
            )
        },
    )
    client = gateway.bind("player")
    v = client.observe()
    req = request(v)
    first = client.act(req, "turn01")
    assert first["status"] == "ok"
    assert client.act(req, "turn01") == first
    assert client.observe()["revision"] == v["revision"] + 1
    assert client.observe_glauquir()["actuation"] == client.observe()["actuation"]
    gateway.close()


def test_confirmed_messages_visible():
    _, s = fresh()
    v = s.observe()
    assert not v["actuation"]["messages"]
    assert s.act(request(v))["status"] == "ok"
    assert any("FIREBREATH" in x for x in s.observe()["actuation"]["messages"])


def test_observe_is_pure_and_preserves_narrative_clock():
    _, s = fresh()
    before = s.export()
    first = s.observe()
    assert first == s.observe()
    assert s.export() == before
    assert s.act(request(first))["status"] == "ok"
    after = s.export()
    assert after["turn"] == before["turn"]
    assert after["rng"] != before["rng"]


def test_rejected_forced_player_action_and_end_is_immutable():
    _, s = fresh()
    for _ in range(10):
        v = s.observe()
        if v["actuation"]["actor"] == "parnecio":
            break
        assert s.act(request(v))["status"] == "ok"
    assert s.observe()["actuation"]["actor"] == "parnecio"
    snapshot = s.export()
    impossible = {
        "session_id": v["session_id"],
        "revision": v["revision"],
        "action_id": "actturn_advance",
    }
    assert s.act(impossible)["status"] == "error"
    assert s.export() == snapshot
