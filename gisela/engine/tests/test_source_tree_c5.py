"""C5: el código mantenido tiene una sola ubicación en el repositorio."""

from importlib import import_module
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("name", ("engine", "contracts"))
def test_no_legacy_root_shadow(name):
    legacy = ROOT / name
    sources = [
        path
        for path in legacy.rglob("*")
        if path.is_file() and path.suffix in {".py", ".json", ".md"}
    ]
    assert not sources, f"Fuentes duplicadas en {name}/: {sources}"


@pytest.mark.parametrize("name", ("gisela.engine", "gisela.contracts"))
def test_public_modules_from_installable_tree(name):
    module = import_module(name)
    expected = ROOT / name.replace(".", "/") / "__init__.py"
    assert Path(module.__file__).resolve() == expected.resolve()
