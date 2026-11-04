"""Artefactos privados locales, publicación atómica y huella del entorno."""

from __future__ import annotations

import hashlib
import importlib.metadata
import os
import platform
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

from gisela.contracts.canonical import canonical_json

ROOT = Path(__file__).resolve().parents[1]
TREES = ("gisela", "mary", "dice", "traits", "narrative_conditions")


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_bytes(path, content):
    """Nunca expone un archivo parcial; los temporales tienen modo 0600."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def atomic_json(path, value):
    atomic_bytes(path, canonical_json(value) + b"\n")


def environment():
    """La huella incluye fuentes y contratos, incluso cambios sin commit."""
    sources = [
        path
        for tree in TREES
        for path in (ROOT / tree).rglob("*")
        if path.is_file()
        and path.suffix in (".py", ".json")
        and not {".venv", ".git", "__pycache__", "tests", "packages"}.intersection(
            path.relative_to(ROOT).parts
        )
        and not path.name.startswith("test_")
    ]
    sources.extend((ROOT / "tools").glob("campaign_*.py"))
    sources.append(ROOT / "tools/tegularis_campaign_v077.py")
    digest = hashlib.sha256()
    for path in sorted(sources):
        digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
        digest.update(path.read_bytes() + b"\0")
    dependencies = {}
    for name in (
        "gisela-narrative-engine",
        "jsonschema",
        "referencing",
        "attrs",
        "rpds-py",
        "jsonschema-specifications",
    ):
        try:
            dependencies[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            dependencies[name] = None
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "optimize": sys.flags.optimize,
        "platform": platform.platform(),
        "dependencies": dependencies,
        "source_sha256": digest.hexdigest(),
    }


def exception_record(exc):
    """Serializa el traceback explícitamente: frontera de captura revisada."""
    return {
        "exception": f"{type(exc).__module__}.{type(exc).__qualname__}",
        "message": str(exc),
        "traceback": "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
    }


def failure_document(attempt, exc, runtime):
    snapshot = attempt.snapshot or {}
    clock = snapshot.get("actuation", {})
    order = clock.get("order", [])
    index = clock.get("index", 0)
    return {
        "format_version": 1,
        "seed": attempt.seed,
        "strategy": attempt.strategy,
        "phase": attempt.phase,
        "actions": attempt.actions,
        "max_actions": attempt.max_actions,
        "initial_turn": attempt.initial_turn,
        "snapshot_available": attempt.snapshot is not None,
        "revision": snapshot.get("revision"),
        "turn": snapshot.get("turn"),
        "actuation": snapshot.get("actuation"),
        "round": clock.get("round"),
        "actor": order[index] if 0 <= index < len(order) else None,
        "request": attempt.request,
        "response": attempt.response,
        "package_digest": attempt.admitted.digest,
        "environment": runtime,
        **exception_record(exc),
    }


def save_failure(folder, attempt, failure):
    """Publica el directorio completo con un único rename en el mismo volumen."""
    staging = Path(tempfile.mkdtemp(prefix=".seed-", dir=folder))
    destination = folder / attempt.seed
    try:
        atomic_json(staging / "snapshot.json", attempt.snapshot)
        atomic_json(staging / "error.json", failure)
        atomic_json(staging / "package.json", attempt.admitted.materialize())
        history = (attempt.snapshot or {}).get("history", {})
        events = sorted(
            [*history.get("facts", []), *history.get("trace", [])],
            key=lambda event: event["sequence"],
        )
        atomic_bytes(
            staging / "events.jsonl",
            b"".join(canonical_json(event) + b"\n" for event in events),
        )
        hashes = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in staging.iterdir()
        }
        atomic_json(staging / "manifest.json", hashes)
        os.rename(staging, destination)
        sync_directory(folder)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return destination


def create_campaign(output):
    """Cada ejecución tiene su propio directorio privado y no sobrescribe otra."""
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    return Path(tempfile.mkdtemp(prefix="campaign-", dir=output))
