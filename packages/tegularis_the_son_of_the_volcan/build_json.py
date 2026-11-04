"""Formato compacto de paquetes, sin modificar su contenido canónico."""

import json


def _dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ": "))


def compact_json(data):
    rows = ["{"]
    for index, (key, value) in enumerate(data.items()):
        suffix = "," if index < len(data) - 1 else ""
        label = "  " + _dump(key) + ": "
        if isinstance(value, (dict, list)) and value:
            left, right = ("{", "}") if isinstance(value, dict) else ("[", "]")
            members = _members(value)
            rows.append(label + left)
            rows.extend(
                "    " + entry + ("," if n < len(members) - 1 else "")
                for n, entry in enumerate(members)
            )
            rows.append("  " + right + suffix)
        else:
            rows.append(label + _dump(value) + suffix)
    return "\n".join(rows + ["}"]) + "\n"


def _members(value):
    if isinstance(value, dict):
        return [_dump(key) + ": " + _dump(item) for key, item in value.items()]
    return [_dump(item) for item in value]
