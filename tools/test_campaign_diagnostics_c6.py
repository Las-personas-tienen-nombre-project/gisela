"""Campaign instrumentation parity and private diagnostics."""

import json

import campaign_execution
import tegularis_campaign_v077 as campaign
from tegularis_campaign_v077 import PACKAGE

from gisela.contracts.admit_package import admit_package_file


def test_cli_diagnostics_persists_aggregated_summary(tmp_path, monkeypatch):
    def execute(attempt):
        assert attempt.diagnostics is True
        return {
            "type": "seed",
            "status": "success",
            "seed": attempt.seed,
            "strategy": attempt.strategy,
            "outcome": "derrota",
            "coverage": {
                "skills_played": {"sample_skill": 2},
                "effects_applied_or_refreshed": {"sample_effect": 1},
            },
            "decision_counts": {
                "selected": {"sample_candidate": 1},
                "candidate_reasons": {"selected": 1, "guard_false": 2},
            },
            "decisions": [],
        }

    monkeypatch.setattr(campaign_execution.SeedRun, "execute", execute)
    assert (
        campaign.main(["--count", "2", "--output-dir", str(tmp_path), "--diagnostics"])
        == 0
    )
    summary = json.loads(next(tmp_path.glob("campaign-*/summary.json")).read_text())
    assert summary["status"] == "completed"
    assert summary["diagnostics_enabled"] is True
    assert summary["successful"] == 2
    assert summary["coverage"] == {
        "skills_played": {"sample_skill": 4},
        "effects_applied_or_refreshed": {"sample_effect": 2},
    }
    assert summary["candidate_selection_counts"] == {"sample_candidate": 2}
    assert summary["candidate_reason_counts"] == {"selected": 2, "guard_false": 4}
    assert (
        summary["npc_candidates_not_selected_in_samples"]
        == summary["declared_npc_candidates"]
    )


def test_full_seed_is_identical_with_and_without_diagnostics():
    admitted = admit_package_file(PACKAGE)
    seed = f"{1:064x}"
    plain_run = campaign_execution.SeedRun(admitted, seed, "attack")
    diagnostic_run = campaign_execution.SeedRun(
        admitted, seed, "attack", diagnostics=True
    )
    plain = plain_run.execute()
    diagnostic = diagnostic_run.execute()
    # Includes RNG, full history, actuation clock and session revision.
    assert plain_run.snapshot == diagnostic_run.snapshot
    assert {key: diagnostic[key] for key in plain} == plain
    assert diagnostic["decisions"]
    assert diagnostic["decision_counts"]["selected"]
    assert sum(diagnostic["coverage"]["skills_played"].values()) > 0
    assert any(
        candidate["reason"] == "selected"
        for item in diagnostic["decisions"]
        for candidate in item["candidates"]
    )
