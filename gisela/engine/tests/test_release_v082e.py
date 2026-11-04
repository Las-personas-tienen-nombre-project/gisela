"""End-to-end regression across authored Tegularis presentations."""

from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

ROOT = Path(__file__).resolve().parents[3]
PACKAGES = ROOT / "packages/tegularis_the_son_of_the_volcan"
NAMES = (
    "11_presentacion_participantes_v081.package.json",
    "11_presentacion_decisiones_v081.package.json",
    "11_presentacion_cronica_v081.package.json",
    "12_tablas_v082_parcial.package.json",
    "13_tablas_causal_v082c.package.json",
    "14_presentacion_semantica_v082d.package.json",
)


def _request(view):
    options = [choice for choice in view["actions"] if choice["enabled"]]
    if not options:
        return None
    return {
        "session_id": view["session_id"],
        "revision": view["revision"],
        "action_id": options[0]["action_id"],
    }


def _logical_state(session):
    snapshot = session.export()
    return {
        key: snapshot[key]
        for key in (
            "revision",
            "world_revision",
            "turn",
            "status",
            "world_time",
            "world",
            "narrative",
            "history",
            "rng",
            "actuation",
            "cursor",
        )
    }


def test_six_presentations_preserve_identical_gameplay_and_restoration():
    admitted = [admit_package_file(PACKAGES / name) for name in NAMES]
    sessions = [new_session(pkg, seed="a" * 64) for pkg in admitted]
    for step in range(12):
        observations = [session.observe() for session in sessions]
        assert all(view["presentation"] for view in observations)
        assert all(
            view["actuation"] == observations[0]["actuation"] for view in observations
        )
        assert all(
            _logical_state(session) == _logical_state(sessions[0])
            for session in sessions
        )
        if step == 5:
            sessions = [
                restore_session(pkg, session.export())
                for pkg, session in zip(admitted, sessions)
            ]
        requests = [_request(view) for view in observations]
        assert all((request is None) == (requests[0] is None) for request in requests)
        if requests[0] is None:
            break
        assert all(
            session.act(request)["status"] == "ok"
            for session, request in zip(sessions, requests)
        )
    assert all(
        _logical_state(session) == _logical_state(sessions[0]) for session in sessions
    )
