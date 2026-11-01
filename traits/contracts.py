"""Contratos de TRAITS v1: datos puros, sin importar GISELA ni DICE."""

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
REQUEST_SCHEMA = json.loads(
    (Path(__file__).parent / "schemas" / "evaluation.schema.json").read_text(
        encoding="utf8"
    )
)


class TraitsError(ValueError):
    """Un catálogo, asignación o contexto no satisface el contrato TRAITS."""


def validate_schema(schema: dict, data: dict) -> None:
    """Informa del primer error de esquema de forma determinista."""
    issues = sorted(
        Draft202012Validator(schema).iter_errors(data),
        key=lambda error: (tuple(map(str, error.absolute_path)), error.message),
    )
    if issues:
        raise TraitsError(f"Contrato TRAITS inválido: {issues[0].message}")


def compile_catalog(definitions: dict) -> dict:
    """Compila definiciones neutrales sin modificar los datos de autoría."""
    validate_schema(SCHEMA, definitions)
    data = copy.deepcopy(definitions)
    by_id = {trait["id"]: trait for trait in data["traits"]}
    if len(by_id) != len(data["traits"]):
        raise TraitsError("Identificadores de rasgo duplicados")
    for trait in by_id.values():
        validate_trait(trait, by_id)
    return {
        "schema_version": "traits.v1",
        "max_traits": data.get("max_traits", 5),
        "traits": by_id,
    }


def validate_trait(trait: dict, catalog: dict) -> None:
    """Comprueba referencias y reglas internas de una definición."""
    excluded = set(trait.get("excludes", []))
    if trait["id"] in excluded or not excluded <= catalog.keys():
        raise TraitsError(f"Exclusión inválida en {trait['id']}")
    rules = trait["contributions"]
    if len({rule["id"] for rule in rules}) != len(rules):
        raise TraitsError(f"Reglas duplicadas en {trait['id']}")
    for rule in rules:
        when = rule["when"]
        if set(when.get("all_tags", [])) & set(when.get("none_tags", [])):
            raise TraitsError(
                f"Condiciones contradictorias en {trait['id']}:{rule['id']}"
            )


def validate_assignments(catalog: dict, kind: str, assigned: list) -> tuple[str, ...]:
    """Valida capacidad, existencia, clase y exclusiones simétricas."""
    if not isinstance(assigned, list) or any(not isinstance(v, str) for v in assigned):
        raise TraitsError("Los rasgos asignados deben ser una lista de identificadores")
    if len(assigned) != len(set(assigned)):
        raise TraitsError("Asignación duplicada de rasgo")
    if len(assigned) > catalog["max_traits"]:
        raise TraitsError("CAPACITY_EXCEEDED")
    for trait_id in assigned:
        validate_assignment(catalog, kind, trait_id)
    check_exclusions(catalog, set(assigned))
    return tuple(sorted(assigned))


def validate_assignment(catalog: dict, kind: str, trait_id: str) -> None:
    """Un rasgo se puede asignar solo a su clase y sin exclusiones."""
    trait = catalog["traits"].get(trait_id)
    if trait is None:
        raise TraitsError(f"Rasgo desconocido: {trait_id}")
    if kind not in trait["entity_kinds"]:
        raise TraitsError(f"Clase incompatible para {trait_id}: {kind}")


def check_exclusions(catalog: dict, assigned: set) -> None:
    """Comprueba exclusiones unilaterales en sentido simétrico."""
    for trait_id in sorted(assigned):
        if set(catalog["traits"][trait_id].get("excludes", [])) & assigned:
            raise TraitsError(f"Rasgos incompatibles con {trait_id}")


def has_trait(assigned: list | tuple, trait_id: str) -> bool:
    """Consulta pura de pertenencia; no autoriza proyección pública."""
    return trait_id in assigned
