"""Contract tests for the C8 authoring-only composition primitives."""

import copy

import pytest

from tools.authoring_composition import apply_overlay, replace_field, safe_output


def test_overlay_preserves_base_and_isolates_nested_values():
    base = {"cards": [{"id": "a", "cost": 10}], "metadata": {}}
    old = copy.deepcopy(base)
    replacement = {"effects": [1]}
    output = apply_overlay(
        base,
        [
            {
                "path": ["cards", {"by": "id", "value": "a"}, "cost"],
                "op": "set",
                "old": 10,
                "value": 20,
            },
            {"path": ["metadata", "extra"], "op": "add", "value": replacement},
        ],
    )
    replacement["effects"].append(2)
    assert output["cards"][0]["cost"] == 20
    assert output["metadata"]["extra"] == {"effects": [1]}
    assert base == old


@pytest.mark.parametrize(
    "selector",
    [
        {"by": "id", "value": "missing"},
        {"by": "id", "value": "a"},
        {"by": "", "value": "a"},
        True,
        -1,
        1,
    ],
)
def test_unsafe_or_ambiguous_selectors_fail(selector):
    data = {"rows": [{"id": "a", "v": 1}, {"id": "a", "v": 2}]}
    with pytest.raises(ValueError):
        apply_overlay(
            data, [{"path": ["rows", selector, "v"], "op": "set", "old": 1, "value": 3}]
        )


@pytest.mark.parametrize(
    "recipe",
    [
        None,
        {},
        [{"path": ["x"], "op": "set", "value": 2}],
        [{"path": ["x"], "op": "remove", "old": 1, "value": 2}],
        [{"path": ["x"], "op": "set", "old": 1}],
        [{"path": ["x"], "op": "unknown"}],
        [{"path": ["x", "nested"], "op": "add", "value": 2}],
        [{"path": [1], "op": "add", "value": 2}],
    ],
)
def test_invalid_recipes_do_not_mutate_base(recipe):
    base = {"x": 1}
    with pytest.raises(ValueError):
        apply_overlay(base, recipe)
    assert base == {"x": 1}


@pytest.mark.parametrize(
    "relative",
    [
        "../outside.json",
        "/absolute.json",
        "a/../../outside.json",
        "a\\outside.json",
        "a//b.json",
        "./a.json",
    ],
)
def test_output_rejects_unsafe_paths(tmp_path, relative):
    with pytest.raises(ValueError):
        safe_output(tmp_path, relative)


def test_output_rejects_symlink_escape(tmp_path):
    outside = tmp_path.parent / "outside"
    outside.mkdir(exist_ok=True)
    (tmp_path / "linked").symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match="Unsafe"):
        safe_output(tmp_path, "linked/file.json")


def test_field_replacement_copies_both_inputs():
    base = {"presentation": {"id": "before"}, "other": [1]}
    incoming = {"id": "after"}
    result = replace_field(base, "presentation", incoming)
    incoming["id"] = "changed"
    result["other"].append(2)
    assert result["presentation"]["id"] == "after"
    assert base == {"presentation": {"id": "before"}, "other": [1]}


def test_presentation_check_is_readonly_and_detects_drift(tmp_path):
    import json
    import shutil

    from packages.tegularis_the_son_of_the_volcan.build_presentations import (
        CANON,
        SOURCES,
        compile_variants,
    )

    shutil.copy2(CANON, tmp_path / CANON.name)
    shutil.copy2(SOURCES, tmp_path / SOURCES.name)
    names = compile_variants(tmp_path)
    assert len(names) == 6
    before = {name: (tmp_path / name).read_bytes() for name in names}
    assert compile_variants(tmp_path, check=True) == names
    assert before == {name: (tmp_path / name).read_bytes() for name in names}
    first = tmp_path / names[0]
    data = json.loads(first.read_text(encoding="utf-8"))
    data["manifest"]["id"] = "drift"
    first.write_text(json.dumps(data), encoding="utf-8")
    tampered = first.read_bytes()
    with pytest.raises(ValueError, match="diferente"):
        compile_variants(tmp_path, check=True)
    assert first.read_bytes() == tampered
