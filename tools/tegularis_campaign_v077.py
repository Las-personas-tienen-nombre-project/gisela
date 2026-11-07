"""Campañas Observe/Act con diagnóstico privado, resumen y replay local."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Permite ejecutar el archivo desde una extracción sin instalación editable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from campaign_artifacts import (
    atomic_json,
    create_campaign,
    environment,
    exception_record,
    failure_document,
    save_failure,
)
from campaign_diagnostics import merge_coverage
from campaign_execution import FATAL_ERRORS, SeedRun
from campaign_replay import captured_logger, replay

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.support import check_supported

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json"
DEFAULT_OUTPUT = ROOT / ".local/tegularis-campaigns"


def emit(record):
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":")), flush=True)


def execute_seed(attempt, folder, runtime):
    """La captura amplia se limita a una semilla y siempre registra el traceback."""
    with captured_logger() as log:
        return seed_with_log(attempt, (folder, runtime), log)


def seed_with_log(attempt, destination, log):
    folder, runtime = destination
    logger, buffer = log
    try:
        return attempt.execute()
    except Exception as exc:
        logger.exception("Fallo en semilla %s", attempt.seed)
        failure = failure_document(attempt, exc, runtime)
        failure["traceback"] = buffer.getvalue()
        destination = save_failure(folder, attempt, failure)
        return {
            "type": "seed",
            "status": "error",
            "seed": attempt.seed,
            "strategy": attempt.strategy,
            "phase": attempt.phase,
            "exception": failure["exception"],
            "error": str(exc)[:500],
            "fatal": isinstance(exc, FATAL_ERRORS),
            "diagnostic": str(destination),
        }


def new_summary(args):
    return {
        "type": "summary",
        "format_version": 1,
        "status": "running",
        "start": f"{args.start:064x}",
        "requested": args.count,
        "strategy": args.strategy,
        "attempted": 0,
        "successful": 0,
        "failed": 0,
        "pending": args.count,
        "outcomes": {},
        "errors": {},
        "results": [],
        "exit_code": None,
        "diagnostics_enabled": args.diagnostics,
    }


def save_summary(folder, summary):
    results = summary["results"]
    summary["successful"] = sum(item["status"] == "success" for item in results)
    summary["failed"] = sum(item["status"] == "error" for item in results)
    summary["pending"] = summary["requested"] - summary["attempted"]
    summary["outcomes"] = dict(
        Counter(item["outcome"] for item in results if item["status"] == "success")
    )
    summary["errors"] = dict(
        Counter(item["exception"] for item in results if item["status"] == "error")
    )
    if summary["diagnostics_enabled"]:
        coverage = {}
        for item in results:
            if item["status"] == "success":
                merge_coverage(coverage, item["coverage"])
        summary["coverage"] = coverage
        selected = Counter()
        reasons = Counter()
        for item in results:
            if item["status"] == "success":
                selected.update(item["decision_counts"]["selected"])
                reasons.update(item["decision_counts"]["candidate_reasons"])
        summary["candidate_selection_counts"] = dict(sorted(selected.items()))
        summary["candidate_reason_counts"] = dict(sorted(reasons.items()))
        summary["npc_candidates_not_selected_in_samples"] = sorted(
            set(summary.get("declared_npc_candidates", [])) - set(selected)
        )
    atomic_json(folder / "summary.json", summary)


def abort_summary(folder, summary, error):
    summary.update(status="aborted", exit_code=2, infrastructure_error=error)
    try:
        save_summary(folder, summary)
    except (OSError, MemoryError, ValueError) as exc:
        # La avería que impide persistir se comunica sin afirmar que se guardó.
        print(f"No se pudo guardar summary.json: {exc}", file=sys.stderr)


def campaign(args):
    folder = create_campaign(args.output_dir).resolve()
    summary = new_summary(args)
    summary["directory"] = str(folder)
    with captured_logger() as log:
        return campaign_with_log(args, (folder, summary), log)


def declared_npc_candidates(admitted):
    """Inventory the authored NPC decisions without altering the session."""
    return sorted(
        {
            candidate["skill_instance"]
            for participant in admitted.materialize()
            .get("actuation", {})
            .get("participants", [])
            for candidate in participant.get("candidates", [])
        }
    )


def campaign_with_log(args, destination, log):
    folder, summary = destination
    logger, buffer = log
    active = None
    try:
        save_summary(folder, summary)
        admitted = admit_package_file(args.package or PACKAGE)
        check_supported(admitted.materialize())
        runtime = environment()
        summary.update(package_digest=admitted.digest, environment=runtime)
        if args.diagnostics:
            summary["declared_npc_candidates"] = declared_npc_candidates(admitted)
        for number in range(args.start, args.start + args.count):
            active = f"{number:064x}"
            summary["attempted"] += 1
            result = execute_seed(
                SeedRun(admitted, active, args.strategy, diagnostics=args.diagnostics),
                folder,
                runtime,
            )
            summary["results"].append(result)
            active = None
            save_summary(folder, summary)
            emit(result)
            if result.get("fatal"):
                summary["infrastructure_error"] = {
                    "exception": result["exception"],
                    "message": result["error"],
                    "diagnostic": result["diagnostic"],
                }
                break
        aborted = "infrastructure_error" in summary
        summary["status"] = "aborted" if aborted else "completed"
        summary["exit_code"] = 2 if aborted else int(bool(summary["failed"]))
        save_summary(folder, summary)
    except Exception as exc:
        logger.exception("Fallo global de campaña")
        error = {**exception_record(exc), "traceback": buffer.getvalue()}
        if active is not None:
            summary["results"].append(
                {
                    "type": "seed",
                    "seed": active,
                    "status": "error",
                    "exception": error["exception"],
                    "error": error["message"][:500],
                    "fatal": True,
                    "diagnostic": None,
                }
            )
        abort_summary(folder, summary, error)
        print(f"Campaña interrumpida: {type(exc).__name__}: {exc}", file=sys.stderr)
    compact = {
        key: value
        for key, value in summary.items()
        if key not in {"results", "environment", "infrastructure_error"}
    }
    emit(compact)
    return summary["exit_code"]


def arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int)
    parser.add_argument("--count", type=int)
    parser.add_argument("--strategy", choices=("pass", "attack", "shield"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--replay", type=Path)
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Registra cobertura y decisiones privadas de la campaña",
    )
    parser.add_argument(
        "--package", type=Path, help="Paquete del encuentro que se validará"
    )
    args = parser.parse_args(argv)
    if args.replay is not None:
        if args.diagnostics or any(
            getattr(args, key) is not None
            for key in ("start", "count", "strategy", "output_dir", "package")
        ):
            parser.error("--replay es excluyente con las opciones de campaña")
        return args
    args.start = 0 if args.start is None else args.start
    args.count = 4 if args.count is None else args.count
    args.strategy = args.strategy or "attack"
    args.output_dir = args.output_dir if args.output_dir is not None else DEFAULT_OUTPUT
    if args.start < 0 or args.count < 1 or args.start + args.count > 2**256:
        parser.error("--count debe ser positivo y las semillas caber en 256 bits")
    return args


def main(argv=None):
    args = arguments(argv)
    with captured_logger() as (logger, _buffer):
        return dispatch(args, logger)


def dispatch(args, logger):
    try:
        if args.replay is not None:
            code, result = replay(args.replay)
            emit(result)
            return code
        return campaign(args)
    except Exception as exc:
        logger.exception("No se pudo iniciar la operación")
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        emit(
            {
                "type": "replay" if args.replay else "summary",
                "status": "aborted",
                "error": str(exc)[:500],
                "exit_code": 2,
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
