"""Acceso compatible al cliente GLAUQUIR desde el repositorio fuente."""

# ruff: noqa: I001

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gisela.cli.glauquir import main


if __name__ == "__main__":
    raise SystemExit(main())
