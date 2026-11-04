"""Bounded, side-effect-free projections from collections in public Observe."""

from __future__ import annotations

import copy

from .author_presentation import read_public


def _tabular(view: dict, definition: dict) -> dict:
    records = read_public(view, definition["source"])
    if not isinstance(records, list):
        return {"headers": [], "rows": [], "missing": True}
    if definition.get("transform") == "pivot_resources":
        records = _pivot(records, definition)
    columns = definition["columns"]
    rows = []
    for record in records[: definition.get("limit", 64)]:
        if not isinstance(record, dict):
            continue
        rows.append([_cell(record.get(col["id"]), definition) for col in columns])
    return {
        "headers": [col["label"] for col in columns],
        "align": [col.get("align", "left") for col in columns],
        "rows": rows,
        "truncated": len(records) > len(rows),
    }


def _cell(value, definition):
    if value is None:
        return definition.get("missing", "—")
    if type(value) not in (str, int, float, bool):
        return definition.get("missing", "—")
    return str(value)[:160]


def _pivot(records: list, definition: dict) -> list[dict]:
    groups = {}
    for item in records[:64]:
        if not isinstance(item, dict) or not {"entity", "id", "value"} <= item.keys():
            continue
        entity, key = item["entity"], item["id"]
        if not isinstance(entity, str) or not isinstance(key, str):
            continue
        row = groups.setdefault(entity, {"entity": entity})
        if key in row:
            raise ValueError("Recurso público duplicado en tabla")
        row[key] = item["value"]
    return list(groups.values())


def _events(view: dict, definition: dict) -> dict:
    records = read_public(view, definition["source"])
    if not isinstance(records, list):
        return {"items": [], "missing": True}
    kinds = set(definition.get("kinds", []))
    selected = [
        entry
        for entry in records[:64]
        if isinstance(entry, dict) and (not kinds or entry.get("kind") in kinds)
    ]
    field, expected = definition.get("filter_field"), definition.get("filter_value")
    if field:
        selected = [item for item in selected if item.get(field) == expected]
    limit = definition.get("limit", 10)
    result = selected[-limit:]
    output = {
        "items": copy.deepcopy(result),
        "count": len(selected),
        "truncated": len(selected) > limit,
    }
    from .presentation_semantics import apply

    apply(output["items"], definition.get("event_formats", []))
    if definition.get("group_by") == "action":
        output["blocks"] = _causal_blocks(output["items"])
    return output


def project_view(view: dict, definition: dict) -> dict:
    """Project one author view, reading no object except the given observation."""
    if definition["component"] == "table":
        return _tabular(view, definition)
    return _events(view, definition)


def _causal_blocks(events: list[dict]) -> list[dict]:
    """Group only explicitly correlated records with visible action starts.

    Incomplete groups remain flat, never fabricated or attributed by proximity.
    """
    starts = {
        event.get("causal_execution_id")
        for event in events
        if event.get("kind") == "skill_started" and event.get("causal_execution_id")
    }
    blocks = []
    groups = {}
    for item in events:
        identifier = item.get("causal_execution_id")
        if identifier not in starts:
            blocks.append({"kind": "event", "event": copy.deepcopy(item)})
        elif identifier in groups:
            groups[identifier]["events"].append(copy.deepcopy(item))
        else:
            block = {
                "kind": "action",
                "causal_execution_id": identifier,
                "events": [copy.deepcopy(item)],
            }
            blocks.append(block)
            groups[identifier] = block
    return blocks
