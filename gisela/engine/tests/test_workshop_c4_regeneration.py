"""Regression checks: workshop copies are compiled, not parallel canonical sources."""

import json

import pytest

from docs.history.workshops.autoria_dsl_15.evaluacion.build_canonical_copies import (
    CANON,
    OVERLAYS,
    WORKSHOP,
    apply_overlay,
    compile_copies,
)


def test_all_sixty_eight_copies_match_declared_overlays():
    assert compile_copies() == 68
    overlays = json.loads(OVERLAYS.read_text(encoding="utf-8"))
    assert len(overlays) == 68
    assert sum(bool(value) for value in overlays.values()) > 30


def test_canonical_solution_and_intentional_invalid_exercises_preserved():
    canon = json.loads(CANON.read_text(encoding="utf-8"))
    overlays = json.loads(OVERLAYS.read_text(encoding="utf-8"))
    assert not overlays["soluciones/06_actuacion/05_guarda.package.json"]
    assert (
        apply_overlay(
            canon,
            overlays["ejercicios/06_actuacion/06_referencia_invalida.package.json"],
        )
        != canon
    )


def test_overlay_preconditions_detect_drift_without_modifying_canon():
    original = {"choices": [{"id": "a", "cost": 10}]}
    operations = [
        {
            "path": ["choices", {"by": "id", "value": "a"}, "cost"],
            "op": "set",
            "old": 10,
            "value": 20,
        }
    ]
    assert apply_overlay(original, operations)["choices"][0]["cost"] == 20
    assert original["choices"][0]["cost"] == 10
    with pytest.raises(ValueError, match="Canonical drift"):
        apply_overlay({"choices": [{"id": "a", "cost": 11}]}, operations)


def test_overlay_rejects_unknown_identity_and_wrong_operations():
    with pytest.raises(ValueError, match="Ambiguous/missing"):
        apply_overlay(
            {"choices": []},
            [
                {
                    "path": ["choices", {"by": "id", "value": "x"}, "cost"],
                    "op": "set",
                    "old": 2,
                    "value": 3,
                }
            ],
        )
    with pytest.raises(ValueError, match="precondition"):
        apply_overlay(
            {"name": "original"}, [{"path": ["name"], "op": "add", "value": "x"}]
        )


def test_compilation_rejects_unsafe_path_before_writing(tmp_path):
    overlays = json.loads(OVERLAYS.read_text(encoding="utf-8"))
    recipe = next(iter(overlays))
    overlays["../escape.package.json"] = overlays.pop(recipe)
    src = tmp_path / "overlays.json"
    src.write_text(json.dumps(overlays), encoding="utf-8")
    with pytest.raises(ValueError, match="Unsafe"):
        compile_copies(write=True, overlays_path=src, workshop=tmp_path)
    assert not (tmp_path / "escape.package.json").exists()


def test_readonly_check_rejects_modified_output(tmp_path):
    relative = "ejercicios/06_actuacion/05_guarda.package.json"
    original = WORKSHOP / relative
    changed = json.loads(original.read_text(encoding="utf-8"))
    changed["manifest"]["id"] = "tampered"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(changed), encoding="utf-8")
    with pytest.raises(ValueError, match="differs"):
        compile_copies(workshop=tmp_path)
