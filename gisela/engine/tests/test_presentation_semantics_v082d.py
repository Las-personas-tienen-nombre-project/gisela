"""Positive and hostile tests for purely presentational semantic formatting."""

from __future__ import annotations

import copy
import io
from contextlib import redirect_stdout

import pytest

from gisela.cli.color import Styler
from gisela.cli.render import show_presentation
from gisela.contracts.presentation_templates_validation import errors
from gisela.engine.presentation_views import project_view


def _definition(**changes):
    result = {
        "component": "event_log",
        "source": "actuation.causal",
        "limit": 10,
        "event_formats": [
            {
                "kind": "variable_changed",
                "variable": "gillius_hp",
                "role": "damage",
                "template": "{variable}: {before} -> {after}",
            }
        ],
    }
    result.update(changes)
    return result


def _observation():
    return {
        "actuation": {
            "causal": [
                {
                    "sequence": 1,
                    "kind": "variable_changed",
                    "source": "actuation",
                    "detail": {"variable": "gillius_hp", "before": 110, "after": 92},
                },
                {
                    "sequence": 2,
                    "kind": "variable_changed",
                    "source": "actuation",
                    "detail": {"variable": "gillius_mp", "before": 20, "after": 10},
                },
            ]
        }
    }


def test_author_format_is_deterministic_and_does_not_mutate_public_data():
    observation = _observation()
    snapshot = copy.deepcopy(observation)
    one = project_view(observation, _definition())
    assert one == project_view(observation, _definition())
    assert observation == snapshot
    assert one["items"][0]["display_text"] == "gillius_hp: 110 -> 92"
    assert one["items"][0]["semantic_role"] == "damage"
    assert "semantic_role" not in one["items"][1]


def test_formatting_never_infers_damage_from_decreasing_value():
    selected = project_view(_observation(), _definition())
    assert selected["items"][1]["detail"]["after"] == 10
    assert "semantic_role" not in selected["items"][1]


@pytest.mark.parametrize(
    "template",
    [
        "{variable.__class__}",
        "{after[0]}",
        "{before!r}",
        "{before:08}",
        "{unknown}",
        "{broken",
    ],
)
def test_unsafe_templates_rejected(template):
    definition = {"event_formats": [{"kind": "variable_changed", "template": template}]}
    assert errors(definition, "views/0")


def test_duplicate_or_unverified_templates_rejected():
    assert errors(
        {"event_formats": [{"kind": "dice_roll", "variable": "hp"}]}, "views/0"
    )
    assert errors({"event_formats": [{"kind": "private_kind"}]}, "views/0")
    assert errors(
        {"event_formats": [{"kind": "dice_roll"}, {"kind": "dice_roll"}]}, "views/0"
    )


def test_missing_fields_have_explicit_policy():
    event = {
        "actuation": {
            "causal": [
                {"sequence": 1, "kind": "skill_started", "detail": {"card": "a"}}
            ]
        }
    }
    rule = {"kind": "skill_started", "template": "{actor}: {card}"}
    assert (
        "display_text"
        not in project_view(event, _definition(event_formats=[rule]))["items"][0]
    )
    rule["missing"] = "placeholder"
    output = project_view(event, _definition(event_formats=[rule]))
    assert output["items"][0]["display_text"] == "-: a"


def test_semantic_color_and_plain_text_have_equal_meaning():
    data = project_view(_observation(), _definition())
    region = dict(data, id="events", component="event_log", label="Eventos")
    presentation = {"regions": [region]}
    out = []
    for mode in ("never", "always"):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            show_presentation(presentation, Styler(mode=mode))
        out.append(buffer.getvalue())
    assert "Daño: gillius_hp: 110 -> 92" in out[0]
    assert "\x1b[" not in out[0]
    assert "\x1b[" in out[1]
    import re

    assert re.sub(r"\x1b\[[0-9;]*m", "", out[1]) == out[0]


def test_hostile_ansi_in_confirmed_text_is_not_executed():
    event = {
        "actuation": {
            "causal": [
                {
                    "sequence": 1,
                    "kind": "author_message",
                    "detail": {"text": "Hola\x1b[31mMAL\ntexto"},
                }
            ]
        }
    }
    definition = _definition(
        event_formats=[{"kind": "author_message", "template": "{text}"}]
    )
    result = project_view(event, definition)
    assert "\x1b" not in result["items"][0]["display_text"]
    assert "\n" not in result["items"][0]["display_text"]


def test_grouped_events_preserve_semantic_formatting():
    observation = _observation()
    observation["actuation"]["causal"].insert(
        0,
        {
            "sequence": 0,
            "kind": "skill_started",
            "causal_execution_id": "action_00000001",
            "detail": {"actor": "a", "card": "b"},
        },
    )
    observation["actuation"]["causal"][1]["causal_execution_id"] = "action_00000001"
    view = project_view(observation, _definition(group_by="action"))
    assert view["blocks"][0]["events"][1]["semantic_role"] == "damage"


def test_production_package_admission_observe_act_and_restore():
    import json
    from pathlib import Path

    from gisela.contracts.admit_package import admit_package
    from gisela.engine.runtime import new_session, restore_session
    from gisela.engine.tests.test_actuation_public_v073 import request

    root = Path(__file__).resolve().parents[3]
    path = root / "packages/tegularis_the_son_of_the_volcan"
    path /= "14_presentacion_semantica_v082d.package.json"
    admitted = admit_package(json.loads(path.read_text(encoding="utf-8")))
    session = new_session(admitted, seed="a" * 64)
    for _ in range(3):
        view = session.observe()
        assert "presentation" in view
        assert "regions" in view["presentation"]
        assert session.act(request(view))["status"] == "ok"
    clone = restore_session(admitted, session.export())
    assert clone.observe() == session.observe()
    assert clone.export() == session.export()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        show_presentation(session.observe()["presentation"], Styler(mode="never"))
    assert "ACONTECIMIENTOS" in buffer.getvalue().upper()
    assert "\x1b[" not in buffer.getvalue()


def test_non_combat_confirmed_events_use_the_same_primitive():
    observation = {
        "actuation": {
            "causal": [
                {
                    "sequence": 1,
                    "kind": "event_triggered",
                    "detail": {"event": "inspeccion"},
                },
                {
                    "sequence": 2,
                    "kind": "author_message",
                    "detail": {"text": "Revisión finalizada"},
                },
            ]
        }
    }
    definition = _definition(
        event_formats=[
            {
                "kind": "event_triggered",
                "role": "neutral",
                "template": "Inspección: {event}",
            },
            {"kind": "author_message", "role": "buff", "template": "{text}"},
        ]
    )
    result = project_view(observation, definition)
    assert [item["display_text"] for item in result["items"]] == [
        "Inspección: inspeccion",
        "Revisión finalizada",
    ]
    assert result["items"][1]["semantic_role"] == "buff"


def test_literal_braces_and_long_input_are_safe():
    event = {
        "actuation": {
            "causal": [
                {
                    "sequence": 1,
                    "kind": "author_message",
                    "detail": {"text": "A" * 300 + "{{intento}}"},
                }
            ]
        }
    }
    rule = {"kind": "author_message", "template": "Resultado {{confirmado}}: {text}"}
    rendered = project_view(event, _definition(event_formats=[rule]))["items"][0][
        "display_text"
    ]
    assert rendered.startswith("Resultado {confirmado}: ")
    assert len(rendered) < 200


def test_template_limit_counts_substitutions_instead_of_literal_braces():
    valid = {
        "event_formats": [
            {"kind": "author_message", "template": "{{literal}}{text}" * 16}
        ]
    }
    invalid = {"event_formats": [{"kind": "author_message", "template": "{text}" * 17}]}
    assert errors(valid, "views/0") == []
    assert errors(invalid, "views/0")
