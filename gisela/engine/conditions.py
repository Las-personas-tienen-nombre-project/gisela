"""Evaluación de expresiones y condiciones declaradas por el autor."""

from __future__ import annotations

from .world_base import WorldError, find, var_access


def value(state: dict, expression: dict, definitions=None):
    """Lee una expresión sin mutar el mundo ni exponer la profundidad interna."""
    return _ValueEvaluator(definitions).evaluate(state, expression)


class _ValueEvaluator:
    """Conserva definiciones durante una evaluación recursiva acotada."""

    def __init__(self, definitions):
        self.definitions = definitions

    def evaluate(self, state, expression, depth=0):
        """Lee literales, variables, turno o reloj sin mutar el mundo."""
        if depth > 8:
            raise WorldError(
                "BUDGET_EXCEEDED", "Expresión aritmética demasiado profunda"
            )
        if "math" in expression:
            return self.arithmetic(state, expression["math"], depth)
        if "trait_total" in expression:
            from .traits_dice_bridge import contribution_total

            return contribution_total(
                state, expression["trait_total"], self.definitions
            )
        if "literal" in expression:
            return expression["literal"]
        if "var" in expression:
            owner, key = var_access(state, expression["var"])
            return owner[key]
        if (
            "property" in expression
            or "relationship" in expression
            or "stat" in expression
        ):
            from .world_values import read

            return read(state, expression, self.definitions)
        if "turn" in expression:
            return state["turn"]
        if "clock" in expression:
            return state["world_time"]
        raise WorldError("UNSUPPORTED_FORMAT", "Expresión todavía no disponible")

    def arithmetic(self, state, formula, depth):
        a = self.evaluate(state, formula["left"], depth + 1)
        b = self.evaluate(state, formula["right"], depth + 1)
        if type(a) not in (int, float) or type(b) not in (int, float):
            raise WorldError("TYPE_MISMATCH", "La aritmética requiere números")
        op = formula["op"]
        if op == "floor_divide":
            if b == 0:
                raise WorldError("PROPERTY_RANGE", "División por cero")
            result = a // b
        elif op == "min":
            result = min(a, b)
        elif op == "max":
            result = max(a, b)
        elif op == "add":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "multiply":
            result = a * b
        else:
            raise WorldError("UNSUPPORTED_FORMAT", "Operación matemática desconocida")
        if type(result) is float and not __import__("math").isfinite(result):
            raise WorldError("PROPERTY_RANGE", "Resultado aritmético no finito")
        return result


def _knowledge(state: dict, condition: dict) -> bool:
    """Consulta conocimientos y creencias sin inferir hechos históricos."""
    if "knows" in condition:
        query = condition["knows"]
        return query["fact"] in find(state, "characters", query["character"]).get(
            "knowledge", []
        )
    query = condition["believes"]
    return (
        find(state, "characters", query["character"])
        .get("beliefs", {})
        .get(query["claim"])
        is query["value"]
    )


def _skill(state: dict, condition: dict) -> bool:
    """Comprueba una carta de habilidad y la zona autorizada."""
    query = condition["has_skill"]
    find(state, "characters", query["character"])
    return any(
        item["character"] == query["character"]
        and item["card"] == query["skill"]
        and (query["zone"] == "either" or item["zone"] == query["zone"])
        for item in state["world"]["skills"]
    )


def _compare(state: dict, query: dict, definitions=None) -> bool:
    """Compara usando el lenguaje común y traduce errores del dominio."""
    from narrative_conditions import compare

    try:
        return compare(
            value(state, query["left"], definitions),
            value(state, query["right"], definitions),
            query["op"],
        )
    except ValueError as exc:
        raise WorldError("INVALID_STATE", str(exc)) from exc


def _leaf(state: dict, cond: dict, definitions=None) -> bool:
    """Resuelve solo predicados del mundo de GISELA/ALBERTO."""
    if "has_trait" in cond:
        from .world_traits import query

        return query(state, cond["has_trait"], definitions)
    if "has_fact" in cond:
        return any(
            item["fact"] == cond["has_fact"] for item in state["history"]["facts"]
        )
    if "knows" in cond or "believes" in cond:
        return _knowledge(state, cond)
    if "has_skill" in cond:
        return _skill(state, cond)
    if "has_effect" in cond:
        query = cond["has_effect"]
        return any(
            item["target"] == query["target"] and item["card"] == query["effect"]
            for item in state["world"]["effects"]
        )
    if "owns" in cond:
        return (
            find(state, "objects", cond["owns"]["object"]).get("owner")
            == cond["owns"]["owner"]
        )
    if "at_location" in cond:
        return (
            find(state, "characters", cond["at_location"]["character"])["location"]
            == cond["at_location"]["location"]
        )
    if "compare" in cond:
        return _compare(state, cond["compare"], definitions)
    raise WorldError("UNSUPPORTED_FORMAT", "Condición todavía no implementada")


def predicate(state: dict, cond: dict, definitions=None) -> bool:
    """Comparte la lógica booleana; ALBERTO interpreta sus propias consultas."""
    from narrative_conditions import evaluate

    return evaluate(cond, lambda item: _leaf(state, item, definitions))
