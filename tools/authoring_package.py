"""Small authoring-time constructors for complete GISELA 1.5 packages.

Only shape assembly and defensive copying happen here. The package contract
and semantic validator remain the source of truth for admissibility.
"""

from copy import deepcopy

from tools.authoring_narrative import _name


def manifest(identifier, entry, *, language="es_cl"):
    return {
        "id": _name(identifier),
        "format_version": "1.5",
        "language": _name(language),
        "languages": [language],
        "entry": {"node": _name(entry)},
    }


def variable(identifier, initial, *, type_name="boolean"):
    if type_name not in ("boolean", "integer", "string"):
        raise ValueError("Unsupported session variable type")
    if (
        type_name == "boolean"
        and type(initial) is not bool
        or type_name == "integer"
        and type(initial) is not int
        or type_name == "string"
        and not isinstance(initial, str)
    ):
        raise ValueError("Initial value does not match variable type")
    return {
        "scope": "session",
        "id": _name(identifier),
        "type": type_name,
        "initial": deepcopy(initial),
    }


def initial_state(*, world_time="2000-01-01T12:00:00Z", variables=None):
    """Derive initial session values from declared variable descriptors."""
    defined = variables if variables is not None else []
    if not isinstance(defined, (list, tuple)):
        raise ValueError("Variables must be declared as a sequence")  # noqa: TRY004
    values = {}
    for entry in defined:
        if not isinstance(entry, dict) or set(entry) != {
            "scope",
            "id",
            "type",
            "initial",
        }:
            raise ValueError("Invalid variable descriptor")
        checked = variable(entry["id"], entry["initial"], type_name=entry["type"])
        if entry["scope"] != "session" or checked["id"] in values:
            raise ValueError("Duplicate or unsupported variable")
        values[checked["id"]] = checked["initial"]
    return {
        "world_time": _name(world_time),
        "locations": [],
        "characters": [],
        "objects": [],
        "skills": [],
        "effects": [],
        "capacities": [],
        "facts": [],
        "session_variables": values,
    }


def ending(identifier, title):
    return {"id": _name(identifier), "title": {"text": _name(title)}}


def assemble(spec):
    """Assemble a complete package, without modifying the authoring spec."""
    required = {"manifest", "nodes", "endings", "initial_state"}
    optional = {"cards", "scenes", "rules"}
    if (
        not isinstance(spec, dict)
        or required - spec.keys()
        or spec.keys() - (required | optional)
    ):
        raise ValueError("Package spec has missing or unsupported sections")
    for key in ("nodes", "endings", "cards", "scenes", "rules"):
        if key in spec and not isinstance(spec[key], (list, tuple)):
            raise ValueError(f"{key} must be a sequence")
    result = {
        key: deepcopy(spec.get(key, []))
        for key in ("cards", "scenes", "nodes", "rules", "endings")
    }
    result["manifest"] = deepcopy(spec["manifest"])
    result["initial_state"] = deepcopy(spec["initial_state"])
    return {
        key: result[key]
        for key in (
            "manifest",
            "cards",
            "scenes",
            "nodes",
            "rules",
            "endings",
            "initial_state",
        )
    }
