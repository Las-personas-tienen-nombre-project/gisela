"""Contract tests for bounded public tables and causal event selection."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.contracts.presentation_validation import errors
from gisela.engine.author_presentation import project


def _presentation():
    return {
        "id": "test",
        "views": [
            {
                "id": "status",
                "component": "table",
                "source": "actuation.resources",
                "transform": "pivot_resources",
                "columns": [
                    {"id": "entity", "label": "Participant"},
                    {"id": "hp", "label": "HP", "align": "right"},
                    {"id": "mp", "label": "MP"},
                ],
            },
            {
                "id": "log",
                "component": "event_log",
                "source": "actuation.causal",
                "kinds": ["skill_started", "variable_changed"],
                "limit": 2,
            },
        ],
        "regions": [
            {"id": "table", "component": "table", "view": "status"},
            {"id": "events", "component": "event_log", "view": "log"},
        ],
    }


def _observation():
    return {
        "actuation": {
            "resources": [
                {"entity": "a", "id": "hp", "value": 23},
                {"entity": "a", "id": "mp", "value": 9},
                {"entity": "b", "id": "hp", "value": 12},
            ],
            "causal": [
                {"kind": "skill_started", "sequence": 1, "detail": {"actor": "a"}},
                {"kind": "dice_roll", "sequence": 2, "detail": {}},
                {"kind": "variable_changed", "sequence": 3, "detail": {"before": 10}},
                {"kind": "variable_changed", "sequence": 4, "detail": {"after": 9}},
            ],
        }
    }


def test_public_table_and_ordered_events_are_pure():
    definition, observation = _presentation(), _observation()
    before = copy.deepcopy(observation)
    assert errors(definition) == []
    projected = project(definition, observation)["regions"]
    assert projected[0]["rows"] == [["a", "23", "9"], ["b", "12", "-"]]
    assert [entry["sequence"] for entry in projected[1]["items"]] == [3, 4]
    assert projected[1]["truncated"] is True
    assert observation == before
    assert project(definition, observation)["regions"] == projected


def test_reject_unknown_sources_and_view_mismatch():
    definition = _presentation()
    definition["views"][0]["source"] = "private.state"
    definition["regions"][1]["view"] = "status"
    assert len(errors(definition)) >= 2


def test_generic_noncombat_table_uses_same_primitives():
    definition = _presentation()
    definition["views"][0].update(
        source="actuation.effects",
        columns=[
            {"id": "beneficiary", "label": "Equipo"},
            {"id": "remaining", "label": "Pendientes"},
        ],
    )
    definition["views"][0].pop("transform")
    observation = {
        "actuation": {
            "effects": [{"beneficiary": "bomba_1", "remaining": 2}],
            "causal": [],
        }
    }
    assert not errors(definition)
    assert project(definition, observation)["regions"][0]["rows"] == [["bomba_1", "2"]]


def _production_package():
    path = (
        Path(__file__).resolve().parents[3] / "packages/tegularis_the_son_of_the_volcan"
    )
    return json.loads(
        (path / "14_presentacion_semantica_v082d.package.json").read_text()
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("limit", 0),
        ("limit", 65),
        ("event_formats", [{"kind": "dice_roll"}] * 33),
    ],
)
def test_event_view_schema_bounds_are_enforced(field, value):
    package = _production_package()
    package["presentation"]["views"][1][field] = value
    with pytest.raises(PackageRejected) as caught:
        admit_package(package)
    assert any(item.code == "SCHEMA_INVALID" for item in caught.value.diagnostics)


@pytest.mark.parametrize("violation", ["views", "columns", "template"])
def test_schema_bounds_cover_definitions_columns_and_templates(violation):
    package = _production_package()
    presentation = package["presentation"]
    if violation == "views":
        presentation["views"] = [presentation["views"][0]] * 33
    elif violation == "columns":
        presentation["views"][0]["columns"] *= 4
    else:
        presentation["views"][1]["event_formats"][0]["template"] = "x" * 1001
    with pytest.raises(PackageRejected) as caught:
        admit_package(package)
    assert any(item.code == "SCHEMA_INVALID" for item in caught.value.diagnostics)


@pytest.mark.parametrize("violation", ["absent", "mismatch", "ambiguous"])
def test_admission_checks_region_view_bindings(violation):
    package = _production_package()
    region = package["presentation"]["regions"][1]
    if violation == "absent":
        region["view"] = "undeclared"
    elif violation == "mismatch":
        region["view"] = "estado"
    else:
        region["source"] = "actuation.causal"
    with pytest.raises(PackageRejected) as caught:
        admit_package(package)
    assert any(item.code == "PRESENTATION_INVALID" for item in caught.value.diagnostics)
