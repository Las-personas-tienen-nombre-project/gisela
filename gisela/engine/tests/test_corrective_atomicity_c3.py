"""C3: failed commit paths preserve the entire snapshot, including RNG."""

from pathlib import Path
from unittest import mock

import pytest

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session
from gisela.engine.world_base import WorldError

PACKAGE = Path(__file__).resolve().parents[2] / "packages/mvp_casete.package.json"


def _request(session):
    view = session.observe()
    action = next(item for item in view["actions"] if item["enabled"])
    return {
        "session_id": view["session_id"],
        "revision": view["revision"],
        "action_id": action["action_id"],
    }


@pytest.mark.parametrize(
    "boundary", ["_execute_source", "_validate_state", "_project_state"]
)
def test_fault_injection_preserves_full_state_and_retry(boundary):
    admitted = admit_package_file(PACKAGE)
    session = new_session(admitted, seed="9" * 64)
    baseline = session.export()
    request = _request(session)
    if boundary == "_execute_source":
        failure = WorldError("BUDGET_EXCEEDED", "falla deliberada")
    else:
        failure = WorldError("INVALID_STATE", "falla deliberada")
    with mock.patch.object(session, boundary, side_effect=failure):
        result = session.act(request)
    assert result["status"] == "error"
    assert session.export() == baseline
    expected = new_session(admitted, seed="9" * 64)
    expected_result = expected.act(_request(expected))
    retry = session.act(request)
    assert retry["status"] == expected_result["status"] == "ok"
    assert session.export() == expected.export()


def test_unexpected_structural_error_is_logged_without_partial_commit(caplog):
    session = new_session(admit_package_file(PACKAGE), seed="a" * 64)
    baseline = session.export()
    request = _request(session)
    with mock.patch.object(session, "_execute_source", side_effect=KeyError("corrupt")):
        response = session.act(request)
    assert response["error"]["code"] == "INVALID_STATE"
    assert session.export() == baseline
    assert "corrupt" in caplog.text
