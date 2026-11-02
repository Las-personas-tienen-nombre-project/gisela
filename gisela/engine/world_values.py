"""Lectura y escritura tipada de propiedades y relaciones de ALBERTO.

Las definiciones son inmutables y ajenas al estado persistido. La función
write modifica exclusivamente el borrador entregado por GISELA.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite

from .world_base import WorldError, instance, var_access


@dataclass(frozen=True)
class WorldDefinitions:
    """Índices de definiciones admitidas asociados a una sesión."""

    cards: dict
    relations: dict
    variables: dict
    scale: dict = field(default_factory=lambda: {"min": 0, "max": 10})
    traits: dict | None = None


def _property(state: dict, ref: dict, defs: WorldDefinitions):
    """Resuelve una propiedad declarada, sin crearla al consultarla."""
    category, entity = instance(state, ref["entity"])
    if category not in ("characters", "locations", "objects"):
        raise WorldError("INVALID_REFERENCE", "La entidad no admite propiedades")
    card = defs.cards[entity["card"]]
    spec = next((p for p in card.get("properties", []) if p["id"] == ref["key"]), None)
    if spec is None:
        raise WorldError("INVALID_REFERENCE", "Propiedad no declarada: " + ref["key"])
    return entity, spec, entity.get("properties", {}).get(ref["key"], spec["initial"])


def _relation(state: dict, ref: dict, defs: WorldDefinitions):
    """Resuelve una relación dirigida, con valor inicial si está ausente."""
    instance(state, ref["from"])
    instance(state, ref["to"])
    spec = defs.relations.get(ref["key"])
    if spec is None:
        raise WorldError("INVALID_REFERENCE", "Relación no declarada: " + ref["key"])
    entry = next(
        (
            item
            for item in state["world"]["relationships"]
            if all(item[k] == ref[k] for k in ("from", "to", "key"))
        ),
        None,
    )
    return entry, spec, entry["value"] if entry else spec["initial"]


def read(state: dict, target: dict, defs: WorldDefinitions):
    """Consulta un destino tipado sin materializar valores predeterminados."""
    if "var" in target:
        owner, key = var_access(state, target["var"])
        return owner[key]
    if "property" in target:
        return _property(state, target["property"], defs)[2]
    if "relationship" in target:
        return _relation(state, target["relationship"], defs)[2]
    if "stat" in target:
        from .sofia import read as read_stat

        return read_stat(state, target["stat"], defs)
    raise WorldError("UNSUPPORTED_FORMAT", "Destino sin lectura disponible")


def _checked(value, spec: dict) -> None:
    """Rechaza tipos, no finitos y valores fuera de límites declarados."""
    typ = spec["type"]
    valid = {
        "boolean": type(value) is bool,
        "integer": type(value) is int,
        "number": type(value) in (float, int),
        "string": type(value) is str,
    }[typ]
    if not valid:
        raise WorldError("TYPE_MISMATCH", "Valor incompatible con " + typ)
    if spec["id"] == "presentation_color" and value not in {
        "inherit",
        "default",
        "red",
        "yellow",
        "green",
        "cyan",
        "blue",
        "magenta",
        "white",
    }:
        raise WorldError("PROPERTY_RANGE", "Rol de color desconocido")
    if typ in ("integer", "number"):
        if type(value) is float and not isfinite(value):
            raise WorldError("PROPERTY_RANGE", "Valor no finito")
        if ("min" in spec and value < spec["min"]) or (
            "max" in spec and value > spec["max"]
        ):
            raise WorldError("PROPERTY_RANGE", "Valor fuera de límites")


def write(state: dict, assignment: dict, defs: WorldDefinitions) -> list[dict]:
    """Escribe sobre el borrador y emite un suceso solo si cambió el valor."""
    target, value = assignment["target"], assignment["value"]
    previous = read(state, target, defs)
    if "var" in target:
        ref = target["var"]
        spec = defs.variables[(ref["scope"], ref["key"])]
        _checked(value, spec)
        owner, key = var_access(state, ref)
        owner[key] = value
    elif "property" in target:
        ref = target["property"]
        entity, spec, _ = _property(state, ref, defs)
        _checked(value, spec)
        entity.setdefault("properties", {})[ref["key"]] = value
    elif "stat" in target:
        from .sofia import write as write_stat

        return write_stat(state, {"ref": target["stat"], "value": value}, defs)
    elif "relationship" in target:
        ref = target["relationship"]
        entry, spec, _ = _relation(state, ref, defs)
        _checked(value, spec)
        if entry is None:
            state["world"]["relationships"].append({**ref, "value": value})
        else:
            entry["value"] = value
    else:
        raise WorldError("UNSUPPORTED_FORMAT", "Destino sin escritura disponible")
    return [{"on": "state_changed", "target": target}] if previous != value else []
