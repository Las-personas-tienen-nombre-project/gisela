"""Authoring warnings never affect the engine or change NPC priority."""

import copy
import json
from pathlib import Path

from tools.candidate_shadow_report import candidate_shadows

CANON = (
    Path(__file__).resolve().parents[3]
    / "packages"
    / "tegularis_the_son_of_the_volcan"
    / "10_balance_v078.package.json"
)


def _package():
    return json.loads(CANON.read_text(encoding="utf-8"))


def _dragon(package):
    return next(
        p for p in package["actuation"]["participants"] if p["character"] == "tegularis"
    )


def test_canonical_guarded_firebreath_does_not_shadow_wingblast():
    assert not any(
        x["earlier"] == "firebreath_01" and x["later"] == "wingblast_01"
        for x in candidate_shadows(_package())
    )


def test_unguarded_same_requirements_reports_potential_shadow():
    p = _package()
    _dragon(p)["candidates"][0].pop("when")
    findings = candidate_shadows(p)
    assert any(
        x["earlier"] == "firebreath_01" and x["later"] == "wingblast_01"
        for x in findings
    )


def test_later_guard_or_different_requirements_not_reported():
    p = _package()
    candidates = _dragon(p)["candidates"]
    candidates[0].pop("when")
    candidates[1]["when"] = {"constant": True}
    assert not any(x["later"] == "wingblast_01" for x in candidate_shadows(p))
    candidates[1].pop("when")
    skill = next(s for s in p["initial_state"]["skills"] if s["id"] == "wingblast_01")
    card = next(c for c in p["cards"] if c["id"] == skill["card"])
    card["play"]["requires"] = {"constant": True}
    assert not any(x["later"] == "wingblast_01" for x in candidate_shadows(p))


def test_static_diagnostic_does_not_mutate_package():
    p = _package()
    original = copy.deepcopy(p)
    candidate_shadows(p)
    assert p == original
