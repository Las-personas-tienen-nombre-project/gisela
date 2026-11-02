"""Create a compact tar.gz snapshot of the GISELA working tree."""

from __future__ import annotations

import argparse
import os
import tarfile
from datetime import datetime
from pathlib import Path

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
    "node_modules",
    "htmlcov",
}
EXCLUDED_SUFFIXES = (".egg-info",)
EXCLUDED_FILES = {".coverage", ".DS_Store", "Thumbs.db"}


def repository_root() -> Path:
    """Resolve the repository root from this tool's location."""
    return Path(__file__).resolve().parents[1]


def files_to_archive(root: Path, output: Path):
    """Yield useful files while pruning generated directories."""
    output = output.resolve()
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name
            for name in directories
            if name not in EXCLUDED_DIRS and not name.endswith(EXCLUDED_SUFFIXES)
        )
        for filename in sorted(filenames):
            path = current_path / filename
            if (
                path.resolve() == output
                or filename in EXCLUDED_FILES
                or filename.endswith((".pyc", ".pyo", ".swp", ".tmp"))
            ):
                continue
            yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="archivo tar.gz de salida (por defecto, junto al repositorio)",
    )
    args = parser.parse_args(argv)

    root = repository_root()
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    output = args.output or root.parent / f"{root.name}-{stamp}.tar.gz"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tarfile.open(output, "w:gz") as archive:
            for path in files_to_archive(root, output):
                archive.add(path, arcname=Path(root.name) / path.relative_to(root))
    except (OSError, tarfile.TarError) as exc:
        parser.error(f"no se pudo crear {output}: {exc}")

    size = output.stat().st_size
    print(f"Archivo creado: {output} ({size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
