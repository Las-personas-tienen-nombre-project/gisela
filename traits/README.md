# TRAITS. Qualitative trait evaluator

TRAITS means Trait Rules and Attribute Interaction Tracking System. It is an independent Python library for validating trait catalogs and evaluating contextual contributions. It does not depend on GISELA, ALBERTO, S.O.F.I.A., DICE, or a particular story.

## Why TRAITS exists

A qualitative trait can affect a calculation only in a declared context. A trait catalog defines which kinds of entities may have each trait, how traits exclude one another, and which contributions they can provide. A calculation request names the participants, their roles, and context tags. TRAITS returns matching contributions in a stable order.

TRAITS does not decide whether a character succeeds. It does not manage dice, random state, sessions, or narrative consequences. A caller such as GISELA decides how to use the returned contributions.

## Public API

`compile_catalog(definitions)` validates a trait catalog and returns a compiled representation. `validate_assignments(catalog, kind, assigned)` checks identifiers, entity kinds, exclusions, and capacity, returning a stable ordered result. `has_trait(assigned, trait_id)` checks membership without deciding publication permissions. `evaluate(catalog, request)` calculates a contribution list and totals for requested slots.

The library exports `TraitsError` for contract violations. Its schemas are `traits/schemas/definitions.schema.json` and `traits/schemas/evaluation.schema.json`.

## Example

This example does not need a GISELA session.

```python
from traits import compile_catalog, evaluate

catalog = compile_catalog({
    "schema_version": "traits.v1",
    "traits": [{
        "id": "fragile",
        "entity_kinds": ["object"],
        "contributions": [{
            "id": "handling",
            "when": {"role": "target", "all_tags": ["handling"]},
            "add": {"slot": "difficulty", "amount": 2}
        }]
    }]
})
request = {
    "schema_version": "traits.evaluation.v1",
    "participants": [{
        "entity": "vase", "kind": "object", "role": "target", "traits": ["fragile"]
    }],
    "tags": ["handling"],
    "slots": ["difficulty"]
}
result = evaluate(catalog, request)
assert result["totals"] == {"difficulty": 2}
```

## Assignment rules

The default maximum number of assigned traits is five per entity. A package can configure `max_traits` within the library schema limits. This limit counts all assigned traits, not only traits active in the current calculation.

Assignments must contain known trait identifiers, match permitted entity kinds, respect exclusions, and contain no duplicates. A conflicting or invalid assignment raises `TraitsError`. The library does not mutate the entity instance.

## Context and contributions

Each contribution rule names a participant role and required or excluded tags. It writes an additive integer amount to an explicitly named calculation slot. The evaluation request lists the slots that it accepts. A contribution for an undeclared slot is an error, not an implicit change to an unrelated calculation.

The returned details can reveal private traits. TRAITS does not decide which details are safe for a player. The host or GISELA public projection must handle that decision.

## Integration with GISELA

The engine stores current assigned traits in ALBERTO entity instances using `gisela/engine/world_traits.py`. Trait changes are made on transaction drafts. The engine uses `gisela/engine/traits_dice_bridge.py` to obtain neutral contributions for DICE without making DICE import TRAITS.

TRAITS can operate without S.O.F.I.A. and DICE can operate without TRAITS. These are optional integrations, not mandatory dependencies in the standalone libraries.

## Tests

```bash
python -m unittest discover -s traits/tests -p 'test_*.py' -q
python -m unittest gisela.engine.tests.test_traits_alberto_v13 -q
python -m unittest gisela.engine.tests.test_traits_dice_bridge -q
```

## Documentation and limitations

The schema is the authoritative reference for accepted fields and numeric limits. The current engine uses assigned traits in v1.3 and later contracts. Older design proposals in `docs/architecture` may use future tense for features that are already implemented. Read the actual v1.5 schemas and tests to establish the current behavior.

See [naming](../docs/reference/NAMING.md) and the original integration design at `docs/architecture/TRAITS_DICE_INTEGRACION_FASE_1.md`.
