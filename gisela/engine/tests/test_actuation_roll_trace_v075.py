"""Tiradas confirmadas de la operación general roll en Observe."""

from test_actuation_public_v073 import fresh, request

from gisela.contracts.semantic_validator import Validator


def test_rolls_are_structured_and_do_not_mutate_on_observe():
    _, session = fresh()
    before = session.export()
    view = session.observe()
    assert session.export() == before
    assert view["actuation"]["rolls"]
    for roll in view["actuation"]["rolls"]:
        assert 1 <= roll["result"] <= roll["sides"]
        assert ":" in roll["store"]
    schema = Validator()
    schema.use_version("1.5")
    assert schema.check_schema("observe", view)


def test_rejected_action_does_not_add_rolls():
    _, session = fresh()
    view = session.observe()
    before = session.export()
    invalid = request(view)
    invalid["action_id"] = "actturn_not_offered"
    assert session.act(invalid)["status"] == "error"
    assert session.export() == before
    assert session.observe()["actuation"]["rolls"] == view["actuation"]["rolls"]


def test_rolls_stable_after_restore():

    from gisela.engine.runtime import restore_session

    admitted, session = fresh()
    for _ in range(6):
        view = session.observe()
        if view["status"] == "ended":
            break
        assert session.act(request(view))["status"] == "ok"
    clone = restore_session(admitted, session.export())
    assert (
        clone.observe()["actuation"]["rolls"] == session.observe()["actuation"]["rolls"]
    )
