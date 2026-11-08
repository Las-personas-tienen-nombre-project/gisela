"""Las relaciones del taller 09 activan reglas sin lógica especial en el motor."""

from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session

PACKAGE = (
    Path(__file__).resolve().parents[3]
    / "docs/workshop/es/09_reglas_relaciones/reglas.package.json"
)


def run(choice):
    session = new_session(admit_package_file(PACKAGE))
    for _ in range(12):
        view = session.observe()
        actions = [action for action in view["actions"] if action["enabled"]]
        if not actions:
            return view["content"], session.export()
        action = next(
            (action for action in actions if action["id"] == choice), actions[0]
        )
        result = session.act(
            {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": action["action_id"],
            }
        )
        assert result["status"] == "ok"
    raise AssertionError("La historia no llegó a un final")


def test_cooperation_triggers_the_rule():
    ending, state = run("ayudar")
    assert ending["ending"] == "luz_encendida"
    assert state["world"]["relationships"][0]["value"] == 2


def test_working_alone_does_not_trigger_the_rule():
    ending, state = run("apartarse")
    assert ending["ending"] == "luz_apagada"
    assert state["world"]["relationships"][0]["value"] == -1


def test_repeated_run_is_deterministic():
    first, state1 = run("ayudar")
    second, state2 = run("ayudar")
    assert first == second
    assert state1["history"]["trace"] == state2["history"]["trace"]
