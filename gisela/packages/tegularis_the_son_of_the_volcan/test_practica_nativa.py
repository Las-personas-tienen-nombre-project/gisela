"""Comprobaciones de la práctica realmente compatible con GISELA v1.5."""

from __future__ import annotations

from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

PKG = Path(__file__).with_name("01_cartas_gisela_v15.package.json")


def take(session, name=None):
    view = session.observe()
    options = [a for a in view["actions"] if a["enabled"]]
    matching = [a for a in options if name in (a["id"], a["action_id"])] if name else []
    action = (matching or [options[0]])[0]
    res = session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": action["action_id"],
        }
    )
    assert res["status"] == "ok", res


def reach(session, kind):
    for _ in range(16):
        if session.observe()["content"]["kind"] == kind:
            return
        take(session, "continue")
    raise AssertionError("no se alcanzó " + kind)


def test():
    admission = admit_package_file(PKG)
    s = new_session(admission, seed="a" * 64)
    assert len(s.export()["world"]["characters"]) == 5
    assert len(s.export()["world"]["skills"]) == 32
    reach(s, "skill_window")
    actions = s.observe()["actions"]
    assert {"slash_01", "double_slash_01", "blai_01"}.issubset(
        {a["id"] for a in actions}
    )
    assert not any(a["id"] == "dodge_parnecio_01" for a in actions)
    assert not any(a["id"] == "proteccion_01" for a in actions)
    assert next(a for a in actions if a["id"] == "double_slash_01")["enabled"] is False
    before = s.export()
    bad = s.act(
        {
            "session_id": s.observe()["session_id"],
            "revision": s.observe()["revision"],
            "action_id": "play_firebreath_01",
        }
    )
    assert bad["error"]["code"] == "INVALID_ACTION"
    assert s.export() == before
    take(s, "slash_01")
    assert s.export()["narrative"]["session_variables"]["tp_parnecio"] == 10
    reached = restore_session(admission, s.export())
    assert reached.export() == s.export()
    reach(s, "skill_window")
    assert next(a for a in s.observe()["actions"] if a["id"] == "double_slash_01")[
        "enabled"
    ]
    take(s, "double_slash_01")
    assert s.export()["narrative"]["session_variables"]["tp_parnecio"] == 0
    reach(s, "skill_window")
    take(s, "slash_01")
    reach(s, "skill_window")
    take(s, "slash_01")
    assert s.observe()["content"]["kind"] == "ending"
    assert s.export()["narrative"]["session_variables"]["tp_parnecio"] == 20


def test_alternate_skill_costs():
    admission = admit_package_file(PKG)
    # Segunda trayectoria: tres Slashes y Blai; el consumo de TP debe quedar reflejado.
    q = new_session(admission, seed="b" * 64)
    for _ in range(3):
        reach(q, "skill_window")
        take(q, "slash_01")
    reach(q, "skill_window")
    assert next(a for a in q.observe()["actions"] if a["id"] == "blai_01")["enabled"]
    take(q, "blai_01")
    assert q.export()["narrative"]["session_variables"]["tp_parnecio"] == 0
    assert q.observe()["content"]["kind"] == "ending"


def test_seeded_replay():
    admission = admit_package_file(PKG)
    # Reproducibilidad de la tirada y del estado final.
    a = new_session(admission, seed="c" * 64)
    b = new_session(admission, seed="c" * 64)
    for x in (a, b):
        reach(x, "skill_window")
        take(x, "slash_01")
    assert a.export() == b.export()
    print(
        "VALIDACIÓN: admisión + 9 verificaciones de contrato/ejecución/restauración/replay: OK"
    )


if __name__ == "__main__":
    test()
    test_alternate_skill_costs()
    test_seeded_replay()
