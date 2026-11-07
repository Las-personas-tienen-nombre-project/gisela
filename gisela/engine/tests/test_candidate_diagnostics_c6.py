"""C6 private instrumentation: no new authority or public data."""

import copy
from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.candidate_diagnostics import capture, record
from gisela.engine.runtime import new_session
from tools.campaign_diagnostics import (
    confirmed_delta,
    merge_coverage,
    summarize_decisions,
)

PACKAGE = (
    Path(__file__).resolve().parents[3]
    / "packages"
    / "tegularis_the_son_of_the_volcan"
    / "10_balance_v078.package.json"
)


def test_capture_is_nested_and_does_not_escape():
    options = [{"skill_instance": "a"}, {"skill_instance": "b"}]
    with capture() as outer:
        record("dragon", (options, "b"), ["guard_false", "selected"])
        with capture() as inner:
            record("dragon", (options, "a"), ["selected"])
        record("dragon", (options, "b"), ["requirements_false", "selected"])
    record("dragon", (options, "a"), ["selected"])
    assert len(outer) == 2 and len(inner) == 1
    assert outer[0]["candidates"] == [
        {"skill_instance": "a", "reason": "guard_false"},
        {"skill_instance": "b", "reason": "selected"},
    ]
    assert inner[0]["candidates"][1]["reason"] == "not_evaluated"
    assert summarize_decisions(outer)["selected"] == {"b": 2}


def test_confirmed_coverage_only_counts_new_events():
    before = {
        "history": {"trace": [{"kind": "skill_played", "source": "old"}]},
        "actuation": {"events": []},
    }
    after = copy.deepcopy(before)
    after["history"]["trace"].append({"kind": "skill_played", "source": "new"})
    after["actuation"]["events"].append(
        {"kind": "effect_started", "detail": {"effect": "e1"}}
    )
    result = confirmed_delta(before, after)
    assert result == {
        "skills_played": {"new": 1},
        "effects_applied_or_refreshed": {"e1": 1},
    }
    combined = {}
    merge_coverage(combined, result)
    merge_coverage(combined, result)
    assert combined["skills_played"] == {"new": 2}


def test_capture_does_not_alter_new_session_snapshot_or_observe():
    admitted = admit_package_file(PACKAGE)
    with capture() as records:
        diagnostic = new_session(admitted, seed="1" * 64)
    standard = new_session(admitted, seed="1" * 64)
    assert diagnostic.export() == standard.export()
    assert diagnostic.observe() == standard.observe()
    assert records == []
