"""Admisión de definiciones MARY; no conoce a ningún motor anfitrión."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

SCHEMA = json.loads(
    (Path(__file__).parent / "schemas" / "definitions.schema.json").read_text(
        encoding="utf8"
    )
)


class MaryError(ValueError):
    """Definición o progreso no válido para MARY."""


def compile_plan(definitions: dict) -> dict:
    """Valida una definición cerrada, sin ejecutar ni modificar su entrada."""
    issues = sorted(
        Draft202012Validator(SCHEMA).iter_errors(definitions),
        key=lambda x: tuple(map(str, x.absolute_path)),
    )
    if issues:
        raise MaryError(f"Definición MARY inválida: {issues[0].message}")
    data = copy.deepcopy(definitions)
    objectives = {item["id"]: item for item in data["objectives"]}
    missions = {item["id"]: item for item in data["missions"]}
    if len(objectives) != len(data["objectives"]) or len(missions) != len(
        data["missions"]
    ):
        raise MaryError("Identificadores duplicados")
    if set(objectives) & set(missions):
        raise MaryError("Objetivo y misión con un mismo identificador")
    for objective in objectives.values():
        if objective["mode"] == "current" and "yield" in objective:
            raise MaryError(
                "Un objetivo reversible no puede emitir un yield irreversible"
            )
        if objective.get("visibility") == "public" and not objective.get("title"):
            raise MaryError("Un objetivo público necesita título")
        criterion = objective["criterion"]
        if criterion["kind"] == "distinct" and criterion["minimum"] > len(
            criterion["facts"]
        ):
            raise MaryError("Umbral mayor que las experiencias disponibles")
        if criterion["kind"] == "weighted" and criterion["minimum"] > sum(
            criterion["weights"].values()
        ):
            raise MaryError("Umbral mayor que el peso total")
    for mission in missions.values():
        if not set(mission["objectives"]) <= objectives.keys():
            raise MaryError(f"Misión {mission['id']} referencia objetivos desconocidos")
    return {"objectives": objectives, "missions": missions}
