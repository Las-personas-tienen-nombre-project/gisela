"""Regresión dirigida: presentación autoral sobre Observe público."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.engine.author_presentation import project
from gisela.engine.runtime import new_session, restore_session

ROOT = Path(__file__).resolve().parents[2]
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


@pytest.mark.parametrize("patch", [
    {"component": "python"},
    {"source": "history.trace"},
    {"source": "actuation.causal.0.detail"},
    {"maximum": "_private"},
])
def test_invalid_region_is_rejected(patch):
    payload = _package()
    payload["presentation"]["regions"][0]["children"][0].update(patch)
    with pytest.raises(PackageRejected):
        admit_package(payload)


def test_empty_and_missing_public_data_are_safe():
    definition = {"id": "queue", "regions": [
        {"id": "queue_items", "component": "entity_collection", "source": "actors"},
        {"id": "queue_age", "component": "stat", "source": "content.age"},
        {"id": "queue_message", "component": "text", "text": "Sala de espera"},
    ]}
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
