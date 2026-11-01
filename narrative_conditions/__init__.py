"""Núcleo puro de condiciones. No depende de GISELA, MARY ni ALBERTO."""

from __future__ import annotations

from decimal import Decimal


def compare(left: object, right: object, operator: str) -> bool:
    """Compara valores tipados, sin equiparar booleanos con números."""
    numeric = type(left) in (int, float, Decimal) and type(right) in (
        int,
        float,
        Decimal,
    )
    compatible = type(left) is type(right) or numeric
    if operator == "eq":
        return compatible and left == right
    if operator == "ne":
        return not compatible or left != right
    if operator not in ("lt", "lte", "gt", "gte"):
        raise ValueError(f"Operador desconocido: {operator}")
    if not compatible or type(left) is bool:
        raise ValueError("Comparación ordenada entre tipos incompatibles")
    try:
        return {
            "lt": lambda: left < right,
            "lte": lambda: left <= right,
            "gt": lambda: left > right,
            "gte": lambda: left >= right,
        }[operator]()
    except TypeError as exc:
        raise ValueError("Valores no ordenables") from exc


def evaluate(condition: dict, resolve) -> bool:
    """Evalúa operadores lógicos; delega los predicados del dominio al anfitrión."""
    if "constant" in condition:
        return condition["constant"]
    if "all" in condition:
        return all(evaluate(item, resolve) for item in condition["all"])
    if "any" in condition:
        return any(evaluate(item, resolve) for item in condition["any"])
    if "not" in condition:
        return not evaluate(condition["not"], resolve)
    return bool(resolve(condition))
