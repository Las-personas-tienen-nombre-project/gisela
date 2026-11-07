"""Deterministic contract-boundary mutations; no unexpected validator exceptions."""

import copy
import json
import random
from pathlib import Path

import pytest

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.contracts.semantic_validator import Validator

HERE = Path(__file__).resolve().parent
SMALL = json.loads((HERE.parent / "packages/mvp_casete.package.json").read_text())


@pytest.mark.parametrize(
    "manifest",
    [None, False, 4, [], "1.5", {"format_version": []}, {"format_version": {}}],
)
def test_malformed_manifest_rejects_without_python_exception(manifest):
    package = copy.deepcopy(SMALL)
    package["manifest"] = manifest
    with pytest.raises(PackageRejected):
        admit_package(package)
    assert Validator().validate_package(package)


def test_mutations_in_admission_are_controlled_and_repeatable():
    rng = random.Random(20261107)
    replacements = (None, True, 0, -1, "invalid", [], {}, [1], {"invalid": True})
    for _ in range(75):
        package = copy.deepcopy(SMALL)
        cursor = package
        depth = rng.randrange(1, 5)
        for step in range(depth):
            if not isinstance(cursor, (dict, list)) or not cursor:
                break
            key = rng.choice(
                list(cursor) if isinstance(cursor, dict) else list(range(len(cursor)))
            )
            if (
                step == depth - 1
                or not isinstance(cursor[key], (dict, list))
                or not cursor[key]
            ):
                cursor[key] = copy.deepcopy(rng.choice(replacements))
                break
            cursor = cursor[key]
        try:
            admitted = admit_package(package)
        except PackageRejected as rejected:
            assert rejected.diagnostics
            assert all(item.path.startswith("/") for item in rejected.diagnostics)
        else:
            assert admitted.materialize() == package
