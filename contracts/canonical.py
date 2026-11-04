"""GISELA-CJSON-1. Serialización canónica del contenido JSON del paquete.

No depende del orden de claves, espacios ni representación de decimales.
No lee archivos ni calcula hashes de recursos externos al paquete JSON.
"""

from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal

DOMAIN = b"GISELA-PACKAGE-DIGEST-v1\n"
SAFE_INTEGER = 9007199254740991
MAX_EXPONENT = 4096


class CanonicalError(ValueError):
    """Rechazo de un valor que no pertenece al perfil JSON canónico."""


def _string(value: str) -> str:
    """Codifica una cadena UTF-8 sin sustitutos Unicode aislados."""
    if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise CanonicalError("Una cadena JSON contiene un sustituto Unicode aislado")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _decimal(value: Decimal) -> str:
    """Normaliza un decimal finito dentro de los límites del perfil."""
    if not value.is_finite():
        raise CanonicalError("Numero no finito")
    if value.is_zero():
        return "0"
    sign, raw_digits, exponent = value.as_tuple()
    digits = list(raw_digits)
    while len(digits) > 1 and digits[-1] == 0:
        digits.pop()
        exponent += 1
    if abs(exponent) > MAX_EXPONENT or len(digits) > MAX_EXPONENT:
        raise CanonicalError("Numero excede el limite del perfil canonico")
    sequence = "".join(map(str, digits))
    point = len(sequence) + exponent
    if point > MAX_EXPONENT or point < -MAX_EXPONENT:
        raise CanonicalError("Numero excede el limite del perfil canonico")
    if point <= 0:
        raw = "0." + "0" * (-point) + sequence
    elif point >= len(sequence):
        raw = sequence + "0" * (point - len(sequence))
    else:
        raw = sequence[:point] + "." + sequence[point:]
    return ("-" if sign else "") + raw


def canonical_json(value) -> bytes:
    """Devuelve UTF-8 canónico; rechaza valores ajenos al perfil JSON.

    Para preservar decimales de entrada use decimal.Decimal. No cambia el
    objeto entregado ni calcula el digest de recursos externos.
    """

    def enc(obj):
        """Codifica recursivamente un valor JSON con claves ordenadas."""
        if obj is None:
            return "null"
        if obj is True:
            return "true"
        if obj is False:
            return "false"
        if isinstance(obj, str):
            return _string(obj)
        if isinstance(obj, int):
            if abs(obj) > SAFE_INTEGER:
                raise CanonicalError("Entero fuera de rango interoperable")
            return str(obj)
        if isinstance(obj, Decimal):
            return _decimal(obj)
        if isinstance(obj, float):
            if not math.isfinite(obj):
                raise CanonicalError("Numero no finito")
            return _decimal(Decimal(repr(obj)))
        if isinstance(obj, list):
            return "[" + ",".join(enc(x) for x in obj) + "]"
        if isinstance(obj, dict):
            if not all(isinstance(k, str) for k in obj):
                raise CanonicalError("Las claves de objeto JSON deben ser cadenas")
            return (
                "{"
                + ",".join(_string(k) + ":" + enc(obj[k]) for k in sorted(obj))
                + "}"
            )
        raise CanonicalError(
            f"Tipo no permitido en JSON canonico: {type(obj).__name__}"
        )

    return enc(value).encode("utf-8")


def package_digest(package: dict) -> str:
    """Retorna 64 dígitos hexadecimales del paquete con dominio separado."""
    return hashlib.sha256(DOMAIN + canonical_json(package)).hexdigest()
