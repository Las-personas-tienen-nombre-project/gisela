"""Campañas, persistencia y reproducción verificadas sin alterar el motor."""

import copy
import json
import logging
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import campaign_artifacts as artifacts
import campaign_execution as execution
import campaign_replay as replaying
import pytest
import tegularis_campaign_v077 as campaign

from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import load_json_strict
from gisela.engine.runtime import new_session


@pytest.fixture(scope="module")
def admitted():
    return admit_package_file(campaign.PACKAGE)


@pytest.fixture
def runtime():
    return artifacts.environment()


def records(output):
    return [json.loads(line) for line in output.splitlines()]


def summary_at(output):
    return json.loads(next(output.glob("campaign-*/summary.json")).read_text())


def successful(attempt, outcome="derrota"):
    return {
        "type": "seed",
        "status": "success",
        "seed": attempt.seed,
        "strategy": attempt.strategy,
        "outcome": outcome,
    }


def rejected_diagnostic(folder, admitted, runtime):
    attempt = execution.SeedRun(admitted, "a" * 64, "attack")
    session = new_session(admitted, seed=attempt.seed)
    attempt.capture(session, "act")
    attempt.initial_turn = attempt.snapshot["turn"]
    attempt.request = {
        "session_id": attempt.snapshot["session_id"],
        "revision": attempt.snapshot["revision"],
        "action_id": "actturn_unoffered",
    }
    with pytest.raises(execution.CampaignError) as caught:
        attempt.act(session)
    error = artifacts.failure_document(attempt, caught.value, runtime)
    destination = artifacts.save_failure(folder, attempt, error)
    return attempt, destination


def test_continue_after_seed_failure_and_aggregate(tmp_path, monkeypatch, capsys):
    attempted = []

    def execute(attempt):
        attempted.append(attempt.seed)
        if attempt.seed == f"{1:064x}":
            raise RuntimeError("fallo reproducible")
        return successful(
            attempt, "derrota" if len(attempted) == 1 else "destruccion_mutua"
        )

    monkeypatch.setattr(execution.SeedRun, "execute", execute)
    code = campaign.main(["--count", "3", "--output-dir", str(tmp_path)])
    output = capsys.readouterr()
    assert code == 1 and output.err == ""
    items = records(output.out)
    assert [item["seed"] for item in items[:-1]] == attempted
    summary = summary_at(tmp_path)
    assert summary["status"] == "completed"
    assert (summary["successful"], summary["failed"], summary["pending"]) == (2, 1, 0)
    assert summary["outcomes"] == {"derrota": 1, "destruccion_mutua": 1}
    assert summary["errors"] == {"builtins.RuntimeError": 1}
    failure = load_json_strict(Path(items[1]["diagnostic"]) / "error.json")
    assert "Traceback" in failure["traceback"]
    assert "fallo reproducible" in failure["traceback"]
    assert not failure["snapshot_available"]
    assert load_json_strict(Path(items[1]["diagnostic"]) / "snapshot.json") is None
    assert "results" not in items[-1]


@pytest.mark.parametrize("outcome", ["derrota", "destruccion_mutua"])
def test_valid_endings_exit_zero(tmp_path, monkeypatch, outcome):
    monkeypatch.setattr(
        execution.SeedRun, "execute", lambda attempt: successful(attempt, outcome)
    )
    assert campaign.main(["--count", "1", "--output-dir", str(tmp_path)]) == 0
    assert summary_at(tmp_path)["outcomes"] == {outcome: 1}


@pytest.mark.parametrize("exception", [OSError, ImportError, MemoryError])
def test_infrastructure_failure_stops_remaining_seeds(tmp_path, monkeypatch, exception):
    calls = []

    def fail(attempt):
        calls.append(attempt.seed)
        raise exception("infraestructura no disponible")

    monkeypatch.setattr(execution.SeedRun, "execute", fail)
    assert campaign.main(["--count", "3", "--output-dir", str(tmp_path)]) == 2
    summary = summary_at(tmp_path)
    assert len(calls) == 1
    assert summary["status"] == "aborted"
    assert (summary["attempted"], summary["failed"], summary["pending"]) == (1, 1, 2)


def test_configuration_failure_aborts_before_seeds(tmp_path, monkeypatch):
    monkeypatch.setattr(campaign, "PACKAGE", tmp_path / "missing.json")
    assert campaign.main(["--output-dir", str(tmp_path)]) == 2
    summary = summary_at(tmp_path)
    assert summary["attempted"] == 0
    assert summary["status"] == "aborted"
    assert "Traceback" in summary["infrastructure_error"]["traceback"]


def test_unsupported_shared_configuration_aborts_before_seeds(tmp_path, monkeypatch):
    def unsupported(package):
        raise ValueError("Formato común no ejecutable por este motor")

    monkeypatch.setattr(campaign, "check_supported", unsupported)
    assert campaign.main(["--output-dir", str(tmp_path)]) == 2
    summary = summary_at(tmp_path)
    assert summary["attempted"] == 0 and summary["pending"] == 4
    assert "Formato común" in summary["infrastructure_error"]["message"]


@pytest.mark.parametrize(
    "options",
    [
        ["--start", "-1"],
        ["--count", "0"],
        ["--count", "-1"],
        ["--start", str(2**256)],
        ["--start", str(2**256 - 1), "--count", "2"],
        ["--replay", ".", "--count", "1"],
        ["--replay", ".", "--strategy", "attack"],
        ["--replay", ".", "--output-dir", "."],
    ],
)
def test_invalid_arguments(options):
    with pytest.raises(SystemExit) as caught:
        campaign.arguments(options)
    assert caught.value.code == 2


def test_snapshot_and_confirmed_events_are_exact(tmp_path, admitted, runtime):
    attempt, destination = rejected_diagnostic(tmp_path, admitted, runtime)
    assert load_json_strict(destination / "snapshot.json") == attempt.snapshot
    assert (
        load_json_strict(destination / "snapshot.json")["rng"]
        == attempt.snapshot["rng"]
    )
    history = attempt.snapshot["history"]
    expected = sorted(history["trace"] + history["facts"], key=lambda x: x["sequence"])
    assert records((destination / "events.jsonl").read_text()) == expected
    error = load_json_strict(destination / "error.json")
    assert error["request"] == attempt.request and error["response"] == attempt.response
    assert error["revision"] == attempt.snapshot["revision"]
    assert stat.S_IMODE(destination.stat().st_mode) == 0o700
    assert all(
        stat.S_IMODE(path.stat().st_mode) == 0o600 for path in destination.iterdir()
    )


def test_replay_in_new_process_without_original_package(tmp_path, admitted, runtime):
    _, destination = rejected_diagnostic(tmp_path, admitted, runtime)
    moved = tmp_path / "portable" / "failed-seed"
    moved.parent.mkdir()
    shutil.move(destination, moved)
    script = campaign.ROOT / "tools/tegularis_campaign_v077.py"
    result = subprocess.run(
        [sys.executable, str(script), "--replay", str(moved)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert records(result.stdout)[0]["reproduced"] is True


def test_replay_uses_saved_package_and_detects_changed_behavior(
    tmp_path, admitted, monkeypatch
):
    _, destination = rejected_diagnostic(tmp_path, admitted, artifacts.environment())
    monkeypatch.setattr(campaign, "PACKAGE", tmp_path / "absent.json")
    assert campaign.main(["--replay", str(destination)]) == 0
    monkeypatch.setattr(replaying, "reproduce", lambda attempt, failure: None)
    assert campaign.main(["--replay", str(destination)]) == 1


def test_replay_rejects_corruption_and_environment_mismatch(
    tmp_path, admitted, monkeypatch
):
    _, destination = rejected_diagnostic(tmp_path, admitted, artifacts.environment())
    monkeypatch.setattr(replaying, "environment", lambda: {"source_sha256": "other"})
    assert campaign.main(["--replay", str(destination)]) == 2
    (destination / "snapshot.json").write_text("{}")
    with pytest.raises(ValueError, match="Artefacto alterado"):
        replaying.load_failure(destination)


def test_atomic_file_failure_keeps_previous_document(tmp_path, monkeypatch):
    path = tmp_path / "summary.json"
    artifacts.atomic_json(path, {"status": "running"})

    def fail_replace(source, destination):
        raise OSError("interrupción antes de rename")

    monkeypatch.setattr(artifacts.os, "replace", fail_replace)
    with pytest.raises(OSError):
        artifacts.atomic_json(path, {"status": "completed"})
    assert json.loads(path.read_text()) == {"status": "running"}
    assert list(tmp_path.iterdir()) == [path]


def test_incomplete_diagnostic_is_never_published(tmp_path, admitted, monkeypatch):
    attempt = execution.SeedRun(admitted, "0" * 64, "attack")
    write = artifacts.atomic_json

    def interrupted(path, document):
        if path.name == "package.json":
            raise OSError("disco lleno")
        write(path, document)

    monkeypatch.setattr(artifacts, "atomic_json", interrupted)
    with pytest.raises(OSError):
        artifacts.save_failure(tmp_path, attempt, {})
    assert list(tmp_path.iterdir()) == []


def test_diagnostic_write_failure_aborts_campaign(tmp_path, monkeypatch):
    def fail(attempt):
        raise RuntimeError("defecto del motor")

    def disk_full(folder, attempt, failure):
        raise OSError("disco lleno")

    monkeypatch.setattr(execution.SeedRun, "execute", fail)
    monkeypatch.setattr(campaign, "save_failure", disk_full)
    assert campaign.main(["--count", "3", "--output-dir", str(tmp_path)]) == 2
    summary = summary_at(tmp_path)
    assert summary["attempted"] == 1 and summary["pending"] == 2
    assert summary["results"][0]["diagnostic"] is None


def test_logging_handlers_are_restored():
    logger = logging.getLogger("tegularis_campaign")
    before = logger.handlers, logger.propagate, logger.level
    with replaying.captured_logger() as (outer, buffer):
        with replaying.captured_logger() as (inner, other):
            inner.error("interior")
        outer.error("exterior")
        assert "interior" not in buffer.getvalue()
        assert "interior" in other.getvalue()
    assert (logger.handlers, logger.propagate, logger.level) == before


def test_real_seed_sessions_do_not_share_state(admitted, monkeypatch):
    sessions = []
    factory = execution.new_session

    def record(package, *, seed):
        session = factory(package, seed=seed)
        sessions.append(session)
        return session

    monkeypatch.setattr(execution, "new_session", record)
    attempts = [
        execution.SeedRun(admitted, f"{i:064x}", "attack", max_actions=1)
        for i in range(2)
    ]
    for attempt in attempts:
        with pytest.raises(execution.CampaignError, match="1 acciones"):
            attempt.execute()
    original = copy.deepcopy(attempts[0].snapshot)
    sessions[1].act({"session_id": "wrong", "revision": 0, "action_id": "wrong"})
    assert attempts[0].snapshot == original
    assert sessions[0] is not sessions[1]
    assert attempts[0].snapshot["rng"]["seed"] != attempts[1].snapshot["rng"]["seed"]


def test_limit_failure_replays_from_seed(tmp_path, admitted, runtime):
    attempt = execution.SeedRun(admitted, "b" * 64, "attack", max_actions=1)
    result = campaign.execute_seed(attempt, tmp_path, runtime)
    assert result["status"] == "error" and result["phase"] == "limit"
    code, result = replaying.replay(Path(result["diagnostic"]))
    assert code == 0 and result["reproduced"]


def test_restore_failure_records_post_action_snapshot(tmp_path, admitted, monkeypatch):
    attempt = execution.SeedRun(admitted, "c" * 64, "attack")
    session = new_session(admitted, seed=attempt.seed)
    expected = session.export()

    def fail_restore(package, snapshot):
        raise RuntimeError("fallo de restauración")

    monkeypatch.setattr(execution, "restore_session", fail_restore)
    with pytest.raises(RuntimeError) as caught:
        attempt.verify_restore(session)
    failure = artifacts.failure_document(attempt, caught.value, {})
    destination = artifacts.save_failure(tmp_path, attempt, failure)
    assert failure["phase"] == "restore"
    assert load_json_strict(destination / "snapshot.json") == expected


def test_default_artifacts_are_ignored_by_git():
    root = campaign.ROOT
    ignore = (root / ".gitignore").read_text().splitlines()
    assert ".local/tegularis-campaigns/" in ignore
    if (root / ".git").exists():
        result = subprocess.run(
            [
                "git",
                "check-ignore",
                ".local/tegularis-campaigns/campaign-test/snapshot.json",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0


def test_full_seed_range_can_be_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(execution.SeedRun, "execute", successful)
    options = [
        "--start",
        str(2**256 - 1),
        "--count",
        "1",
        "--output-dir",
        str(tmp_path),
    ]
    assert campaign.main(options) == 0
    summary = summary_at(tmp_path)
    assert summary["start"] == "f" * 64
    assert summary["results"][0]["seed"] == "f" * 64


def test_initialization_failure_replays_without_snapshot(
    tmp_path, admitted, monkeypatch
):
    def initialization_error(package, *, seed):
        raise RuntimeError("fallo antes de crear la sesión")

    monkeypatch.setattr(execution, "new_session", initialization_error)
    attempt = execution.SeedRun(admitted, "d" * 64, "pass")
    result = campaign.execute_seed(attempt, tmp_path, artifacts.environment())
    code, repeated = replaying.replay(Path(result["diagnostic"]))
    assert code == 0 and repeated["reproduced"]
    assert repeated["phase"] == "initialize"


def test_snapshot_precedes_even_an_action_that_mutates_then_raises(
    tmp_path, admitted, monkeypatch
):
    class BrokenSession:
        def __init__(self, package, *, seed):
            self.session = new_session(package, seed=seed)

        def observe(self):
            return self.session.observe()

        def export(self):
            return self.session.export()

        def act(self, request):
            self.session._state["rng"]["counter"] += 99
            raise RuntimeError("fallo después de mutación defectuosa")

    monkeypatch.setattr(execution, "new_session", BrokenSession)
    attempt = execution.SeedRun(admitted, "e" * 64, "attack")
    expected = new_session(admitted, seed=attempt.seed).export()
    result = campaign.execute_seed(attempt, tmp_path, artifacts.environment())
    snapshot = load_json_strict(Path(result["diagnostic"]) / "snapshot.json")
    assert snapshot == expected
    assert result["phase"] == "act"


def test_replay_detects_optimized_interpreter(tmp_path, admitted, runtime):
    _, destination = rejected_diagnostic(tmp_path, admitted, runtime)
    result = subprocess.run(
        [
            sys.executable,
            "-O",
            str(campaign.ROOT / "tools/tegularis_campaign_v077.py"),
            "--replay",
            str(destination),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "entorno o código" in result.stderr


def test_turn_invariant_remains_active_with_optimizations():
    code = (
        "import sys; sys.path.insert(0, 'tools'); "
        "from campaign_execution import SeedRun; "
        "attempt = SeedRun(None, '0'*64, 'attack'); "
        "attempt.snapshot = {'turn': 2}; attempt.initial_turn = 1; "
        "attempt.result()"
    )
    result = subprocess.run(
        [sys.executable, "-O", "-c", code],
        cwd=campaign.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "CampaignError: El encuentro modificó el turno narrativo" in result.stderr


def test_campaign_uses_current_balance_package_by_default():
    assert campaign.PACKAGE.name == "10_balance_v078.package.json"
    admitted = admit_package_file(campaign.PACKAGE)
    actors = {card["id"]: card for card in admitted.materialize()["cards"]}
    assert actors["gillius"]["sofia"]["awareness"] == 6


def test_package_override_is_accepted():
    args = campaign.arguments(["--package", str(campaign.PACKAGE), "--count", "1"])
    assert args.package == campaign.PACKAGE


def test_replay_rejects_package_override():
    with pytest.raises(SystemExit):
        campaign.arguments(
            ["--replay", "/tmp/example", "--package", str(campaign.PACKAGE)]
        )
