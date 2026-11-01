"""Infraestructura compartida de validación semántica GISELA."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

if __package__:
    from .canonical import CanonicalError, package_digest
else:
    from canonical import CanonicalError, package_digest

__all__ = [
    "ATTRS",
    "COLLECTION_KINDS",
    "ROOT",
    "Any",
    "CanonicalError",
    "Counter",
    "Diagnostic",
    "Draft202012Validator",
    "FormatChecker",
    "Path",
    "RefLocation",
    "Registry",
    "Resource",
    "argparse",
    "asdict",
    "data_type",
    "dataclass",
    "datetime",
    "json",
    "package_digest",
    "pointer",
    "sys",
    "type_compatible",
]
ROOT = Path(__file__).resolve().parent
COLLECTION_KINDS = {
    "locations": "location",
    "characters": "character",
    "objects": "object",
    "skills": "skill",
    "effects": "effect",
}
ATTRS = {"strength", "openness", "fortune", "intelligence", "awareness"}


@dataclass(frozen=True)
class RefLocation:
    """Ruta de diagnóstico y ámbito de resolución de una referencia."""

    path: str
    context: str = ""


@dataclass(frozen=True)
class Diagnostic:
    """Hallazgo estático con severidad, código, ruta JSON y explicación."""

    severity: str
    code: str
    path: str
    message: str


def pointer(*parts: Any) -> str:
    """Construye una ruta JSON Pointer para localizar un diagnóstico."""
    """Construye JSON Pointer; acepta un prefijo ya formado."""
    result = ""
    for i, part in enumerate(parts):
        if i == 0 and isinstance(part, str) and "/" in part:
            result += "/" + part.lstrip("/").rstrip("/")
        else:
            result += "/" + str(part).replace("~", "~0").replace("/", "~1")
    return result or "/"


def data_type(value: Any) -> str | None:
    """Clasifica un escalar JSON para comprobar compatibilidad declarativa."""
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, (float, __import__("decimal").Decimal)):
        return "number"
    if isinstance(value, str):
        return "string"
    return None


def type_compatible(actual: str | None, expected: str | None) -> bool:
    """Compara tipos inferidos sin ejecutar la expresión de una historia."""
    return actual == expected or (actual == "integer" and expected == "number")
