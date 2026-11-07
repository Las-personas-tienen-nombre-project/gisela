"""v0.8.1: authorial compositions never affect the confirmed logical game."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gisela.cli.render import show_presentation
from gisela.contracts.admit_package import admit_package
from gisela.engine.runtime import new_session, restore_session

ROOT = Path(__file__).resolve().parents[3]
FOLDER = ROOT / "packages/tegularis_the_son_of_the_volcan"
BASE = FOLDER / "10_balance_v078.package.json"
VARIANTS = (
    "participantes",
    "decisiones",
    "cronica",
)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _view(name):
    path = FOLDER / f"11_presentacion_{name}_v081.package.json"
    admitted = admit_package(_load(path))
    return admitted, new_session(admitted, seed="0" * 64)


def test_all_layouts_admitted_and_authorial_only():
    original = _load(BASE)
    presentations = []
    for name in VARIANTS:
        variant = _load(FOLDER / f"11_presentacion_{name}_v081.package.json")
        saved = variant.pop("presentation")
        expected = {
            key: copy.deepcopy(value)
            for key, value in original.items()
            if key != "presentation"
        }
        assert variant == expected
        assert saved["action_targets"] == original["presentation"]["action_targets"]
        presentations.append(saved["regions"])
        admit_package(_load(FOLDER / f"11_presentacion_{name}_v081.package.json"))
    assert presentations[0] != presentations[1] != presentations[2]


def test_same_actions_and_causal_history_across_layouts():
    sessions = [_view(name)[1] for name in VARIANTS]
    for _ in range(18):
        views = [session.observe_glauquir() for session in sessions]
        public = [
            {
                key: value
                for key, value in view.items()
                if key not in ("presentation", "session_id")
            }
            for view in views
        ]
        assert public[0] == public[1] == public[2]
        first_ids = [item["id"] for item in views[0]["presentation"]["regions"]]
        second_ids = [item["id"] for item in views[1]["presentation"]["regions"]]
        assert first_ids != second_ids
        actions = [item for item in views[0]["actions"] if item["enabled"]]
        if not actions:
            break
        action = actions[0]["action_id"]
        for session, view in zip(sessions, views):
            command = {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": action,
            }
            reply = session.act(command)
            assert reply["status"] == "ok"
    traces = [session.export()["history"]["trace"] for session in sessions]
    assert traces[0] == traces[1] == traces[2]


@pytest.mark.parametrize("name", VARIANTS)
def test_renderer_and_restoration(name, capsys):
    admitted, session = _view(name)
    first = session.observe_glauquir()
    projected = first["presentation"]
    before = session.export()
    show_presentation(projected)
    shown = capsys.readouterr().out
    assert "ACCIONES AUTORIZADAS" in shown
    assert "PARNECIO" in shown.upper()
    assert "HP" in shown.upper()
    assert str(first["actuation"]["resources"][-3]["value"]) in shown
    assert "[accion " in shown
    assert session.export() == before
    restored = restore_session(admitted, before)
    assert restored.observe_glauquir() == first


def test_public_events_are_readable_and_keep_causal_identity(capsys):
    from gisela.cli.render import show_causal

    confirmed = [
        {
            "sequence": 4,
            "kind": "dice_roll",
            "detail": {"sides": 20, "result": 8, "store": "test"},
        },
        {
            "sequence": 5,
            "kind": "variable_changed",
            "detail": {"variable": "hp", "before": 50, "after": 42},
        },
        {
            "sequence": 6,
            "kind": "encounter_completed",
            "detail": {"outcome": "victoria"},
        },
    ]
    show_causal(confirmed)
    shown = capsys.readouterr().out
    assert "#4 Tirada d20: 8" in shown
    assert "#5 hp: 50 -> 42" in shown
    assert "#6 Desenlace: victoria" in shown
    assert shown.index("#4") < shown.index("#5") < shown.index("#6")
