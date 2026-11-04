"""Selecciona las fuentes mantenidas antes de que pytest recorra paquetes espejo."""

from importlib import import_module
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def pytest_sessionstart(session):
    """Falla explícitamente si se resuelve una copia ajena al árbol canónico."""
    for name in ("gisela", "gisela.contracts", "gisela.engine"):
        module = import_module(name)
        expected = ROOT / name.replace(".", "/") / "__init__.py"
        if Path(module.__file__).resolve() != expected.resolve():
            raise pytest.UsageError(
                f"{name} se importó desde {module.__file__}; se esperaba {expected}"
            )
