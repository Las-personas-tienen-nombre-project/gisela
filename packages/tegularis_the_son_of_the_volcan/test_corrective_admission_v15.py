"""Regresión P0: los contratos de candidatos se verifican antes de iniciar."""

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import PackageRejected, admit_package

HERE = Path(__file__).resolve().parent
BASE = json.loads((HERE / "10_balance_v078.package.json").read_text())


def _altered(change):
    package = copy.deepcopy(BASE)
    participant = next(p for p in package["actuation"]["participants"] if p["character"] == "tegularis")
    change(participant)
    return package


@pytest.mark.parametrize(
    ("change", "fragment"),
    [
        (lambda p: p["candidates"][0].update(when={"inventada": True}), "/when"),
        (lambda p: p["candidates"][0].update(when={"compare": {"left": {"literal": 1}, "op": "eq"}}), "/when"),
        (lambda p: p["candidates"][0].update(arguments={"x": "basura"}), "/arguments"),
        (lambda p: p.update(action_traits={}), "/action_traits"),
        (lambda p: p.update(action_traits={"tags": "bad"}), "/action_traits"),
        (lambda p: p.update(action_traits={"tags": 123}), "/action_traits"),
        (lambda p: p.update(action_traits={"tags": [], "slot": "other"}), "/action_traits"),
    ],
)
def test_malformed_actuation_is_rejected_with_path(change, fragment):
    with pytest.raises(PackageRejected) as caught:
        admit_package(_altered(change))
    assert any(
        item.code == "SCHEMA_INVALID" and fragment in item.path
        for item in caught.value.diagnostics
    )


def test_valid_action_traits_does_not_break_admission():
    package = _altered(lambda p: p.update(action_traits={"tags": [], "slot": "bonus"}))
    admit_package(package)


def test_bad_argument_name_still_has_semantic_diagnostic():
    package = _altered(lambda p: p["candidates"][0].update(arguments={"unknown": {"literal": 1}}))
    with pytest.raises(PackageRejected) as caught:
        admit_package(package)
    assert any(d.code == "ACTUATION_PARAMETERS" for d in caught.value.diagnostics)


def test_valid_action_traits_initializes():
    from gisela.engine.runtime import new_session

    package = _altered(lambda p: p.update(action_traits={"tags": [], "slot": "bonus"}))
    session = new_session(admit_package(package), seed="a" * 64)
    assert session.export()["actuation"]["order"]
