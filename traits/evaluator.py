"""Pertinencia y contribuciones aditivas deterministas de TRAITS."""

from __future__ import annotations

from .contracts import (
    REQUEST_SCHEMA,
    TraitsError,
    validate_assignments,
    validate_schema,
)


def evaluate(catalog: dict, request: dict) -> dict:
    """Evalúa una instantánea neutral sin tocar mundo, sesión o RNG."""
    validate_schema(REQUEST_SCHEMA, request)
    participants = request["participants"]
    if len({person["entity"] for person in participants}) != len(participants):
        raise TraitsError("Participantes duplicados en la evaluación")
    context = {"tags": set(request["tags"]), "slots": set(request["slots"])}
    contributions = []
    for participant in participants:
        contributions.extend(evaluate_participant(catalog, participant, context))
    contributions.sort(
        key=lambda item: (item["source_entity"], item["source_trait"], item["rule_id"])
    )
    totals = {
        slot: sum(item["amount"] for item in contributions if item["slot"] == slot)
        for slot in sorted({item["slot"] for item in contributions})
    }
    return {
        "schema_version": "traits.result.v1",
        "contributions": contributions,
        "totals": totals,
    }


def evaluate_participant(catalog: dict, participant: dict, context: dict) -> list:
    """Reúne reglas pertinentes para una entidad sin mutar sus datos."""
    result = []
    assigned = validate_assignments(catalog, participant["kind"], participant["traits"])
    for trait_id in assigned:
        for rule in catalog["traits"][trait_id]["contributions"]:
            if not applies(rule["when"], participant["role"], context["tags"]):
                continue
            slot = rule["add"]["slot"]
            if slot not in context["slots"]:
                raise TraitsError(f"Ranura no admitida: {slot}")
            result.append(
                {
                    "source_entity": participant["entity"],
                    "source_trait": trait_id,
                    "rule_id": rule["id"],
                    "slot": slot,
                    "amount": rule["add"]["amount"],
                }
            )
    return result


def applies(when: dict, role: str, tags: set) -> bool:
    """Una regla requiere su rol y todas sus etiquetas habilitadas."""
    return (
        when["role"] == role
        and set(when.get("all_tags", [])) <= tags
        and not (set(when.get("none_tags", [])) & tags)
    )
