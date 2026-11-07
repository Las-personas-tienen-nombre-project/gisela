"""C9: independent, noncombat authoring and execution regression."""

import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import admit_package
from gisela.engine.runtime import new_session
from tools import authoring_narrative as n
from tools.build_mvp_casete_authoring import compile_package

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "gisela/packages/mvp_casete.package.json"


def authored_package():
    source = json.loads(CANON.read_text(encoding="utf-8"))
    return source, compile_package(source)


def play(admitted, choice_id):
    session = new_session(admitted, session_id="c9_authoring", seed="0" * 64)
    for _ in range(16):
        view = session.observe()
        if view["status"] == "ended":
            return session.export(), view
        actions = [a for a in view["actions"] if a["enabled"]]
        identifier = choice_id if view["content"]["kind"] == "choice" else None
        selected = next((a for a in actions if a["id"] == identifier), actions[0])
        result = session.act(
            {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": selected["action_id"],
            }
        )
        assert result["status"] == "ok", result
    raise AssertionError("Narrative path did not end")


def test_compiled_mvp_preserves_canon_and_admission():
    source, authored = authored_package()
    assert authored == source
    assert admit_package(authored).digest == admit_package(source).digest
    authored["nodes"][0]["steps"][0]["text"]["text"] = "modified"
    assert source["nodes"][0]["steps"][0]["text"]["text"] != "modified"


@pytest.mark.parametrize(
    "selection,ending,owner_reacted",
    [
        ("prestar", "compartido", ("gisela", True)),
        ("guardar", "solo", ("alberto", False)),
    ],
)
def test_authored_paths_match_reference(selection, ending, owner_reacted):
    owner, reacted = owner_reacted
    source, authored = authored_package()
    baseline = play(admit_package(source), selection)
    compiled = play(admit_package(authored), selection)
    assert compiled == baseline
    snapshot, _ = compiled
    assert snapshot["ending"] == ending
    assert snapshot["world"]["objects"][0]["owner"] == owner
    assert snapshot["narrative"]["session_variables"]["gisela_reacciono"] is reacted


def test_builders_defensively_copy_inputs():
    effects = [n.record_fact("a")]
    guard = n.has_fact("a")
    branch = n.option(
        "yes",
        "Yes",
        {"next": n.target_step("end"), "effects": effects, "enabled_if": guard},
    )
    steps = [n.choice("choose", [branch]), n.ending("end", "done")]
    created = n.node("first", steps)
    effects[0]["fact"] = "changed"
    guard["has_fact"] = "changed"
    steps.clear()
    assert created["steps"][0]["options"][0]["effects"][0]["fact"] == "a"
    assert created["steps"][0]["options"][0]["enabled_if"]["has_fact"] == "a"
    assert len(created["steps"]) == 2


@pytest.mark.parametrize(
    "factory,args",
    [
        (n.choice, ("bad", [])),
        (n.choice, ("bad", [{"id": "a"}, {"id": "a"}])),
        (n.node, ("bad", [{"id": "a"}, {"id": "a"}])),
        (n.option, ("x", "x", {"next": {}, "bogus": 3})),
        (n.option, ("x", "x", {})),
        (n.fact_reaction, ("r", "fact", {"effects": []})),
        (n.text, ("",)),
    ],
)
def test_builders_reject_invalid_forms(factory, args):
    with pytest.raises(ValueError):
        factory(*args)
