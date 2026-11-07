"""Pure JSON composition utilities for authoring-time tools, never runtime.

The base object is never mutated. All operations have checked preconditions;
list selectors require a unique named identity. Output paths are validated
before any caller writes files.
"""

import copy
from pathlib import Path


def resolve_path(root, path):
    current = root
    for part in path:
        if isinstance(current, dict) and isinstance(part, str):
            if part not in current:
                raise ValueError(f"Missing object key: {part!r} in {path!r}")
            current = current[part]
        elif isinstance(current, list):
            if isinstance(part, int) and not isinstance(part, bool):
                if part < 0 or part >= len(current):
                    raise ValueError(f"Invalid list index: {part!r} in {path!r}")
                current = current[part]
            elif isinstance(part, dict) and set(part) == {"by", "value"}:
                key = part["by"]
                if not isinstance(key, str) or not key:
                    raise ValueError(f"Invalid list identity key: {part!r}")
                matches = [
                    item
                    for item in current
                    if isinstance(item, dict)
                    and key in item
                    and item[key] == part["value"]
                ]
                if len(matches) != 1:
                    raise ValueError(f"Ambiguous/missing list identity: {part!r}")
                current = matches[0]
            else:
                raise ValueError(f"Invalid list selector: {part!r}")
        else:
            raise ValueError(f"Invalid path segment: {part!r}")  # noqa: TRY004
    return current


def apply_overlay(base, operations):
    """Apply a checked sequence of add/set/remove operations to a deep copy."""
    if not isinstance(operations, list):
        raise ValueError("Overlay operations must be a list")  # noqa: TRY004
    result = copy.deepcopy(base)
    for index, change in enumerate(operations):
        try:
            _apply_change(result, change)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Overlay operation {index}: {exc}") from exc
    return result


def _apply_change(result, change):
    if not isinstance(change, dict) or set(change) - {"path", "op", "old", "value"}:
        raise ValueError("Unknown overlay property")
    path = change.get("path")
    if not isinstance(path, list) or not path:
        raise ValueError("Overlay path must be nonempty")
    parent = resolve_path(result, path[:-1])
    key = path[-1]
    if not isinstance(parent, dict) or not isinstance(key, str):
        raise TypeError(f"Overlay must target a dictionary key: {path!r}")
    exists = key in parent
    op = change.get("op")
    if op == "add":
        if exists or "old" in change or "value" not in change:
            raise ValueError(f"Add precondition failed: {path!r}")
        parent[key] = copy.deepcopy(change["value"])
    elif op in ("set", "remove"):
        if not exists or "old" not in change or parent[key] != change["old"]:
            raise ValueError(f"Canonical drift at {path!r}")
        if op == "set" and "value" in change:
            parent[key] = copy.deepcopy(change["value"])
        elif op == "remove" and "value" not in change:
            del parent[key]
        else:
            raise ValueError(f"Invalid overlay operation: {path!r}")
    else:
        raise ValueError(f"Unknown overlay operation: {op!r}")


def safe_output(root, relative, *, depth=None):
    """Check destination syntax, traversal and symlink escapes; do not write."""
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or "//" in relative
    ):
        raise ValueError(f"Unsafe output path: {relative!r}")
    path = Path(relative)
    if (
        path.is_absolute()
        or any(part in (".", "..") for part in relative.split("/"))
        or (depth is not None and len(path.parts) != depth)
    ):
        raise ValueError(f"Unsafe output path: {relative!r}")
    root = Path(root).resolve()
    target = root / path
    if not target.resolve().is_relative_to(root):
        raise ValueError(f"Unsafe output path: {relative!r}")
    return target


def replace_field(base, field, value):
    """Copy a document, replacing one top-level field."""
    if not isinstance(base, dict) or not isinstance(field, str) or not field:
        raise ValueError("Replacement requires a document and field name")
    result = copy.deepcopy(base)
    result[field] = copy.deepcopy(value)
    return result
