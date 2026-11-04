"""Reproduce una operación fallida usando exclusivamente su diagnóstico local."""

from __future__ import annotations

import hashlib
import io
import logging
from contextlib import contextmanager

from campaign_artifacts import environment, exception_record
from campaign_execution import FATAL_ERRORS, SeedRun, choose

from gisela.contracts.admit_package import admit_package_file
from gisela.contracts.semantic_validator import load_json_strict
from gisela.engine.runtime import restore_session


@contextmanager
def captured_logger():
    """El log de excepción vive en memoria hasta su escritura atómica."""
    buffer = io.StringIO()
    logger = logging.getLogger("tegularis_campaign")
    previous = logger.handlers, logger.propagate, logger.level
    logger.handlers = [logging.StreamHandler(buffer)]
    logger.propagate = False
    logger.setLevel(logging.ERROR)
    try:
        yield logger, buffer
    finally:
        logger.handlers, logger.propagate, level = previous
        logger.setLevel(level)


def load_failure(folder):
    required = {"error.json", "snapshot.json", "package.json", "events.jsonl"}
    manifest = load_json_strict(folder / "manifest.json")
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError("Manifiesto de diagnóstico incompleto")
    for name in sorted(required):
        actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
        if actual != manifest[name]:
            raise ValueError(f"Artefacto alterado: {name}")
    failure = load_json_strict(folder / "error.json")
    if failure["format_version"] != 1:
        raise ValueError("Versión de diagnóstico no admitida")
    if failure["environment"] != environment():
        raise ValueError("El entorno o código del motor difiere del diagnóstico")
    admitted = admit_package_file(folder / "package.json")
    if admitted.digest != failure["package_digest"]:
        raise ValueError("El digest del paquete difiere del diagnóstico")
    attempt = SeedRun(admitted, failure["seed"], failure["strategy"])
    attempt.snapshot = load_json_strict(folder / "snapshot.json")
    attempt.actions = failure["actions"]
    attempt.initial_turn = failure["initial_turn"]
    attempt.max_actions = failure["max_actions"]
    attempt.request = failure["request"]
    return attempt, failure


def reproduce(attempt, failure):
    """Las fases sin restauración fiable se repiten desde su semilla original."""
    phase = failure["phase"]
    if phase not in {"act", "observe", "choose", "validate_end"}:
        attempt.actions = 0
        attempt.snapshot = None
        attempt.phase = "initialize"
        attempt.execute()
        return
    # Restaurar es preparación del replay: un error aquí no reproduce un Act.
    attempt.phase = "replay_setup"
    session = restore_session(attempt.admitted, attempt.snapshot)
    attempt.phase = phase
    if phase == "act":
        attempt.act(session)
    elif phase == "observe":
        session.observe()
    else:
        attempt.view = session.observe()
        if phase == "choose":
            choose(attempt.view, attempt.strategy)
        else:
            attempt.result()


def replay_operation(attempt, failure, logger):
    try:
        reproduce(attempt, failure)
    except FATAL_ERRORS:
        raise
    except Exception as exc:
        logger.exception("Reproducción de semilla %s", attempt.seed)
        actual = exception_record(exc)
        if attempt.phase == "replay_setup":
            raise ValueError("No se pudo restaurar el snapshot para replay") from exc
        matches = (
            attempt.phase == failure["phase"]
            and actual["exception"] == failure["exception"]
            and actual["message"] == failure["message"]
            and attempt.response == failure["response"]
        )
        return int(not matches), {
            "type": "replay",
            "seed": attempt.seed,
            "reproduced": matches,
            "phase": attempt.phase,
            "exception": actual["exception"],
            "message": actual["message"],
        }
    return 1, {"type": "replay", "seed": attempt.seed, "reproduced": False}


def replay(folder):
    """0: fallo reproducido; 1: comportamiento distinto; 2: replay inviable."""
    attempt, failure = load_failure(folder)
    with captured_logger() as (logger, _buffer):
        return replay_operation(attempt, failure, logger)
