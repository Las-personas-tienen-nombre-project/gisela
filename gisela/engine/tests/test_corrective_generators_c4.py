"""Regresiones de reproducibilidad para los paquetes 10–14 de Tegularis."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = (
    Path(__file__).resolve().parents[3] / "packages" / "tegularis_the_son_of_the_volcan"
)
INPUTS = (
    "build_presentations.py",
    "v081_v082_presentations.json",
    "10_balance_v078.package.json",
)


def _sandbox(tmp_path):
    script_dir = tmp_path / "packages" / "tegularis_the_son_of_the_volcan"
    script_dir.mkdir(parents=True)
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    root = HERE.parents[1]
    shutil.copy2(root / "tools" / "authoring_composition.py", tools_dir)
    for filename in INPUTS:
        shutil.copy2(HERE / filename, script_dir / filename)
    return script_dir


def test_variants_reproduced_byte_for_byte_in_isolation(tmp_path):
    directory = _sandbox(tmp_path)
    result = subprocess.run(
        [sys.executable, str(directory / "build_presentations.py")],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    definitions = json.loads((HERE / "v081_v082_presentations.json").read_text())
    assert len(definitions) == 6
    for filename, presentation in definitions.items():
        actual = (directory / filename).read_bytes()
        assert actual == (HERE / filename).read_bytes(), filename
        decoded = json.loads(actual)
        canon = json.loads((directory / INPUTS[-1]).read_text())
        actual_presentation = decoded.pop("presentation")
        assert decoded == canon_without_presentation(canon)
        assert actual_presentation == presentation


def canon_without_presentation(canon):
    return {key: value for key, value in canon.items() if key != "presentation"}


def test_variant_builder_rejects_traversal_without_writing(tmp_path):
    directory = _sandbox(tmp_path)
    source = directory / "v081_v082_presentations.json"
    source.write_text(json.dumps({"../escape.package.json": {"id": "bad"}}))
    result = subprocess.run(
        [sys.executable, str(directory / "build_presentations.py")],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert not (tmp_path.parent / "escape.package.json").exists()


def test_variant_builder_rejects_invalid_source_without_partial_writes(tmp_path):
    directory = _sandbox(tmp_path)
    source = directory / "v081_v082_presentations.json"
    source.write_text(
        json.dumps(
            {
                "11_ok.package.json": {"id": "ok"},
                "12_invalid.package.json": {"regions": []},
            }
        )
    )
    result = subprocess.run(
        [sys.executable, str(directory / "build_presentations.py")],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert not (directory / "11_ok.package.json").exists()
