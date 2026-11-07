"""Generation drift checks run read-only against canonical sources."""

import shutil

import pytest

from tools.check_generated import check_all, check_canonical


def test_all_declared_outputs_match_sources():
    assert check_all() == (6, 68)


def test_canonical_byte_drift_detected_without_writing(tmp_path, monkeypatch):
    from tools import check_generated

    original = check_generated.TEGULARIS
    sources = (
        "build_v078.py",
        "build_expressions.py",
        "build_json.py",
        "09_cierre_autoral_v077.package.json",
        "v078_public_view.json",
        "10_balance_v078.package.json",
    )
    for filename in sources:
        shutil.copy2(original / filename, tmp_path / filename)
    target = tmp_path / "10_balance_v078.package.json"
    target.write_bytes(target.read_bytes() + b"\n")
    before = target.read_bytes()
    monkeypatch.setattr(check_generated, "TEGULARIS", tmp_path)
    with pytest.raises(ValueError, match="differs"):
        check_canonical()
    assert target.read_bytes() == before
