"""Los constructores reproducen los paquetes publicados sin expandir su formato."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

from gisela.contracts.canonical import package_digest

HERE = Path(__file__).resolve().parent


def test_builders_reproduce_packages_in_isolation(tmp_path):
    for path in HERE.glob("build_*.py"):
        shutil.copy2(path, tmp_path / path.name)
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    shutil.copy2(HERE.parents[1] / "tools" / "authoring_expressions.py", tools_dir)
    for name in (
        "05_actuacion_v07_laboratorio.package.json",
        "02_diseno_productivo_completo.json",
    ):
        shutil.copy2(HERE / name, tmp_path / name)
    for script, output in (
        ("build_v071.py", "07_cartas_v071.package.json"),
        ("build_v072.py", "08_desenlaces_v072.package.json"),
        ("build_v077.py", "09_cierre_autoral_v077.package.json"),
    ):
        result = subprocess.run(
            [sys.executable, str(tmp_path / script)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        actual = (tmp_path / output).read_text()
        expected = (HERE / output).read_text()
        assert json.loads(actual) == json.loads(expected)
        assert package_digest(json.loads(actual)) == package_digest(
            json.loads(expected)
        )
        assert actual == expected
        assert len(actual.splitlines()) <= 700


def test_v077_invalid_burst_is_rejected_with_optimizations(tmp_path):
    for path in HERE.glob("build_*.py"):
        shutil.copy2(path, tmp_path / path.name)
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    shutil.copy2(HERE.parents[1] / "tools" / "authoring_expressions.py", tools_dir)
    package = json.loads((HERE / "08_desenlaces_v072.package.json").read_text())
    burst = next(
        p for p in package["actuation"]["event_policies"] if p["id"] == "ultima_llama"
    )
    burst["outcomes"][1]["effects"].pop()
    (tmp_path / "08_desenlaces_v072.package.json").write_text(json.dumps(package))
    for options in ([], ["-O"]):
        result = subprocess.run(
            [sys.executable, *options, str(tmp_path / "build_v077.py")],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0
        assert (
            "ValueError: ultima_llama: se esperaban 8 efectos; hay 7" in result.stderr
        )
        assert not (tmp_path / "09_cierre_autoral_v077.package.json").exists()


def test_v078_builder_reproduces_canonical_bytes(tmp_path):
    """No se puede volver a publicar una copia parcial del paquete canónico."""
    for source in ("build_v078.py", "build_expressions.py", "build_json.py",
                   "09_cierre_autoral_v077.package.json", "v078_public_view.json"):
        shutil.copy2(HERE / source, tmp_path / source)
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    shutil.copy2(HERE.parents[1] / "tools" / "authoring_expressions.py", tools_dir)
    result = subprocess.run(
        [sys.executable, str(tmp_path / "build_v078.py")],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "10_balance_v078.package.json").read_bytes() == (
        HERE / "10_balance_v078.package.json"
    ).read_bytes()
