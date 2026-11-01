"""Adaptador ALBERTO–TRAITS; muta únicamente el borrador entregado."""

from __future__ import annotations

from traits import TraitsError, compile_catalog, validate_assignments
from traits.contracts import validate_assignment

from .world_base import WorldError, instance

ALLOWED = {"characters": "character", "objects": "object", "locations": "location"}


def _checked(catalog, kind: str, assigned: list) -> list[str]:
    """Traduce los errores del núcleo independiente al dominio de GISELA."""
    try:
        return list(validate_assignments(catalog, kind, assigned))
    except TraitsError as exc:
        code = (
            "CAPACITY_EXCEEDED" if str(exc) == "CAPACITY_EXCEEDED" else "INVALID_STATE"
        )
        raise WorldError(code, str(exc)) from exc


def defaults(card: dict, catalog: dict | None) -> list[str]:
    """Materializa los rasgos de la carta sin compartir sus listas."""
    if catalog is None:
        if card.get("traits"):
            raise WorldError("INVALID_STATE", "No se declaró catálogo TRAITS")
        return []
    return _checked(catalog, card["kind"], card.get("traits", []))


def materialize(state: dict, pkg: dict) -> None:
    """Inicializa todas las entidades en v1.3, respetando [] explícito."""
    catalog = compile_catalog(pkg["traits"]) if "traits" in pkg else None
    cards = {card["id"]: card for card in pkg["cards"]}
    for group, kind in ALLOWED.items():
        for item in state["world"][group]:
            inherited = defaults(cards[item["card"]], catalog)
            item["traits"] = (
                _checked(catalog, kind, item["traits"])
                if catalog is not None and "traits" in item
                else inherited
            )
            if catalog is None and item.get("traits"):
                raise WorldError("INVALID_STATE", "Rasgos sin catálogo")


def query(state: dict, request: dict, catalog: dict | None) -> bool:
    """Consulta identidad y rasgo sin conceder permiso de publicarlo."""
    group, entity = instance(state, request["entity"])
    if group not in ALLOWED or catalog is None:
        raise WorldError("INVALID_REFERENCE", "Entidad o catálogo TRAITS no disponible")
    try:
        validate_assignment(catalog, ALLOWED[group], request["trait"])
    except TraitsError as exc:
        raise WorldError("INVALID_REFERENCE", str(exc)) from exc
    return request["trait"] in entity.get("traits", [])


def change(state: dict, effect: dict, catalog: dict | None) -> list[dict]:
    """Alta o baja idempotente, verificada antes de mutar el borrador."""
    group, entity = instance(state, effect["entity"])
    if group not in ALLOWED or catalog is None:
        raise WorldError("INVALID_REFERENCE", "Entidad o catálogo TRAITS no disponible")
    trait_id = effect["trait"]
    try:
        validate_assignment(catalog, ALLOWED[group], trait_id)
    except TraitsError as exc:
        raise WorldError("INVALID_REFERENCE", str(exc)) from exc
    old = entity.get("traits", [])
    candidate = set(old)
    if effect["op"] == "assign_trait":
        candidate.add(trait_id)
    else:
        candidate.discard(trait_id)
    updated = _checked(catalog, ALLOWED[group], sorted(candidate))
    if updated == sorted(old):
        return []
    entity["traits"] = updated
    return []
