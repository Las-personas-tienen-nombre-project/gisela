"""C9: compile a new standalone package, admit it, and run both outcomes."""

import json

import pytest

from gisela.contracts.admit_package import admit_package
from gisela.engine.runtime import new_session
from tools import authoring_package as p
from tools.build_night_shift_authoring import OUTPUT, build_package, rendered
from tools.check_generated import check_independent_narrative


def play(choice):
    session = new_session(
        admit_package(build_package()), session_id="c9_independent", seed="0" * 64
    )
    for _ in range(16):
        view = session.observe()
        if view["status"] == "ended":
            return session.export()
        actions = [a for a in view["actions"] if a["enabled"]]
        target = next((a for a in actions if a["id"] == choice), actions[0])
        reply = session.act(
            {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": target["action_id"],
            }
        )
        assert reply["status"] == "ok", reply
    raise AssertionError("Narrative scenario did not end")


def test_independent_package_is_full_and_reproducible():
    package = build_package()
    assert set(package) == {
        "manifest",
        "cards",
        "scenes",
        "nodes",
        "rules",
        "endings",
        "initial_state",
    }
    assert json.loads(rendered()) == package
    assert OUTPUT.read_bytes() == rendered()
    check_independent_narrative()
    assert (
        admit_package(package).digest
        == admit_package(json.loads(OUTPUT.read_text())).digest
    )


@pytest.mark.parametrize(
    "choice,ending,contesto",
    [
        ("atender", "silencio", True),
        ("ignorar", "ronda", False),
    ],
)
def test_each_narrative_path_is_deterministic(choice, ending, contesto):
    first = play(choice)
    assert first == play(choice)
    assert first["ending"] == ending
    vars_ = first["narrative"]["session_variables"]
    assert vars_["contesto"] is contesto
    assert vars_["eco"] is contesto


def test_variable_initialization_has_one_source_and_rejects_duplicates():
    descriptors = [p.variable("flag", False)]
    state = p.initial_state(variables=descriptors)
    assert state["session_variables"] == {"flag": False}
    descriptors[0]["initial"] = True
    assert state["session_variables"]["flag"] is False
    with pytest.raises(ValueError):
        p.initial_state(variables=[p.variable("flag", False), p.variable("flag", True)])
    with pytest.raises(ValueError):
        p.initial_state(variables=[{"id": "x"}])


def test_assembly_is_defensive_and_rejects_bad_sections():
    spec = {
        "manifest": p.manifest("test", "intro"),
        "nodes": [],
        "endings": [],
        "initial_state": p.initial_state(),
    }
    compiled = p.assemble(spec)
    spec["manifest"]["id"] = "changed"
    assert compiled["manifest"]["id"] == "test"
    assert compiled["cards"] == []
    with pytest.raises(ValueError):
        p.assemble({**spec, "invented": 4})
    with pytest.raises(ValueError):
        p.assemble({**spec, "nodes": "invalid"})


@pytest.mark.parametrize(
    "type_name,value",
    [
        ("boolean", 0),
        ("integer", True),
        ("string", []),
        ("float", 2.0),
    ],
)
def test_variables_reject_invalid_values(type_name, value):
    with pytest.raises(ValueError):
        p.variable("value", value, type_name=type_name)
