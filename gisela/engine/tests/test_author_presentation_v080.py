"""Regresión dirigida: presentación autoral sobre Observe público."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.engine.author_presentation import project
from gisela.engine.runtime import new_session, restore_session

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json"


def _package():
    return json.loads(PACKAGE.read_text(encoding="utf-8"))


def test_package_accepts_author_presentation_and_observe_stays_pure():
    admitted = admit_package(_package())
    session = new_session(admitted, seed="0" * 64)
    before = session.export()
    one = session.observe_glauquir()
    two = session.observe_glauquir()
    assert one["presentation"] == two["presentation"]
    assert one["presentation"]["regions"][1]["items"] == [
        item for item in one["actions"] if item["enabled"]
    ]
    assert before == session.export()


def test_restore_projection_is_deterministic():
    admitted = admit_package(_package())
    session = new_session(admitted, seed="1" * 64)
    restored = restore_session(admitted, session.export())
    assert session.observe()["presentation"] == restored.observe()["presentation"]


@pytest.mark.parametrize(
    "patch",
    [
        {"component": "python"},
        {"source": "history.trace"},
        {"source": "actuation.causal.0.detail"},
        {"maximum": "_private"},
    ],
)
def test_invalid_region_is_rejected(patch):
    payload = _package()
    payload["presentation"]["regions"][0]["children"][0].update(patch)
    with pytest.raises(PackageRejected):
        admit_package(payload)


def test_empty_and_missing_public_data_are_safe():
    definition = {
        "id": "queue",
        "regions": [
            {"id": "queue_items", "component": "entity_collection", "source": "actors"},
            {"id": "queue_age", "component": "stat", "source": "content.age"},
            {"id": "queue_message", "component": "text", "text": "Sala de espera"},
        ],
    }
    source = {"actors": [], "content": {"kind": "exploring"}}
    expected = project(definition, source)
    assert expected["regions"][0]["items"] == []
    assert expected["regions"][1]["missing"] is True
    assert project(definition, copy.deepcopy(source)) == expected


def test_legacy_package_keeps_observe_shape():
    payload = _package()
    payload.pop("presentation")
    session = new_session(admit_package(payload), seed="0" * 64)
    assert "presentation" not in session.observe()


def _project_region(component, content, options=None):
    node = {
        "id": "sample",
        "component": component,
        "source": "content.value",
        **(options or {}),
    }
    definition = {"id": "sample_view", "regions": [node]}
    return project(definition, {"content": content})["regions"][0]


@pytest.mark.parametrize(
    "component",
    [
        "text",
        "stat",
        "meter",
        "entity_status",
        "entity_collection",
        "choice_list",
        "event_log",
        "initiative_order",
    ],
)
@pytest.mark.parametrize("content", [{}, {"value": None}])
def test_missing_or_null_source_has_the_same_public_placeholder(component, content):
    result = _project_region(component, content, {"maximum": "content.maximum"})
    assert result == {
        "id": "sample",
        "component": component,
        "label": "",
        "missing": True,
        "text": "No disponible",
    }


@pytest.mark.parametrize(
    "content",
    [
        {},
        {"value": False},
        {"value": None},
        {"value": 0},
        {"value": 1},
        {"value": "true"},
        {"value": {}},
        {"value": []},
    ],
)
def test_condition_requires_a_true_boolean(content):
    result = _project_region(
        "conditional",
        content,
        {
            "children": [{"id": "message", "component": "text", "text": "Visible"}],
        },
    )
    assert result == {
        "id": "sample",
        "component": "conditional",
        "label": "",
        "visible": False,
        "children": [],
    }


def test_nested_containers_keep_order_labels_and_literal_text():
    node = {
        "id": "details",
        "component": "section",
        "label": "Detalles",
        "children": [
            {"id": "message", "component": "text", "text": "Visible"},
            {"id": "resource", "component": "stat", "source": "content.value"},
        ],
    }
    before = copy.deepcopy(node)
    result = _project_region("conditional", {"value": True}, {"children": [node]})
    assert result == {
        "id": "sample",
        "component": "conditional",
        "label": "",
        "children": [
            {
                "id": "details",
                "component": "section",
                "label": "Detalles",
                "children": [
                    {
                        "id": "message",
                        "component": "text",
                        "label": "",
                        "text": "Visible",
                    },
                    {
                        "id": "resource",
                        "component": "stat",
                        "label": "",
                        "missing": True,
                        "text": "Tipo incompatible",
                    },
                ],
            }
        ],
    }
    assert node == before


@pytest.mark.parametrize(
    "component,value,expected",
    [
        ("stat", 7, {"text": "7"}),
        ("stat", 2.5, {"text": "2.5"}),
        ("stat", "Activo", {"text": "Activo"}),
        ("stat", True, {"missing": True, "text": "Tipo incompatible"}),
        ("stat", {}, {"missing": True, "text": "Tipo incompatible"}),
        ("stat", [], {"missing": True, "text": "Tipo incompatible"}),
        ("text", "a" * 1001, {"text": "a" * 1000}),
        ("entity_status", [], {"missing": True, "text": "Tipo incompatible"}),
    ],
)
def test_scalar_projection_preserves_types_and_text_limit(component, value, expected):
    assert _project_region(component, {"value": value}) == {
        "id": "sample",
        "component": component,
        "label": "",
        **expected,
    }


@pytest.mark.parametrize(
    "value,maximum,expected",
    [
        (3, 10, {"value": 3, "maximum": 10, "text": "3/10"}),
        (-2, 10, {"value": -2, "maximum": 10, "text": "-2/10"}),
        (1.5, 2.5, {"value": 1.5, "maximum": 2.5, "text": "1.5/2.5"}),
        (True, 10, {"missing": True, "text": "Magnitud no disponible"}),
        (3, True, {"missing": True, "text": "Magnitud no disponible"}),
        (3, 0, {"missing": True, "text": "Magnitud no disponible"}),
        (3, -1, {"missing": True, "text": "Magnitud no disponible"}),
        (3, None, {"missing": True, "text": "Magnitud no disponible"}),
        ("3", 10, {"missing": True, "text": "Magnitud no disponible"}),
        (3, "10", {"missing": True, "text": "Magnitud no disponible"}),
    ],
)
def test_meter_keeps_numbers_and_rejects_invalid_magnitudes(value, maximum, expected):
    result = _project_region(
        "meter", {"value": value, "maximum": maximum}, {"maximum": "content.maximum"}
    )
    assert result == {"id": "sample", "component": "meter", "label": "", **expected}


def test_meter_missing_maximum_is_safe():
    result = _project_region("meter", {"value": 3}, {"maximum": "content.maximum"})
    assert result["missing"] is True and result["text"] == "Magnitud no disponible"


@pytest.mark.parametrize(
    "component",
    [
        "entity_collection",
        "choice_list",
        "event_log",
        "initiative_order",
    ],
)
def test_collections_are_bounded_independent_copies(component):
    content = {
        "value": [
            {"id": str(index), "enabled": True, "detail": {"rolls": [1]}}
            for index in range(66)
        ]
    }
    before = copy.deepcopy(content)
    result = _project_region(component, content)
    assert result["items"] == before["value"][:64]
    assert content == before
    result["items"][0]["detail"]["rolls"].append(2)
    assert content == before
    content["value"][1]["detail"]["rolls"].append(3)
    assert result["items"][1]["detail"]["rolls"] == [1]


@pytest.mark.parametrize(
    "component",
    [
        "entity_collection",
        "choice_list",
        "event_log",
        "initiative_order",
    ],
)
def test_collections_reject_non_lists(component):
    assert _project_region(component, {"value": {}}) == {
        "id": "sample",
        "component": component,
        "label": "",
        "missing": True,
        "text": "Tipo incompatible",
    }


def test_choice_list_slices_before_filtering_enabled_offers():
    content = {
        "value": [
            {"id": "off", "enabled": False},
            "invalid",
            {"id": "unspecified"},
            {"id": "available", "enabled": True},
            *[{"id": f"disabled_{index}", "enabled": False} for index in range(60)],
            {"id": "outside_window", "enabled": True},
        ]
    }
    result = _project_region("choice_list", content)
    assert result["items"] == [{"id": "available", "enabled": True}]


def test_entity_status_has_no_shared_nested_values():
    content = {"value": {"effects": [{"id": "bless", "remaining": 3}]}}
    result = _project_region("entity_status", content)
    assert result["value"] == content["value"]
    result["value"]["effects"][0]["remaining"] = 0
    assert content["value"]["effects"][0]["remaining"] == 3
    content["value"]["effects"].append({"id": "shield"})
    assert len(result["value"]["effects"]) == 1
