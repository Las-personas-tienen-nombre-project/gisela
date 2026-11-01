# Narrative conditions. Shared pure logic

`narrative_conditions` is an independent Python library for composing condition trees and making typed comparisons. It is not a story executor, a database, or a permission manager.

## Supported operations

`evaluate(condition, resolve)` supports `constant`, `all`, `any`, and `not`. A condition that is not one of these pure logical forms is delegated to the resolver supplied by the caller. The caller defines how a game specific predicate is answered.

`compare(left, right, operator)` supports `eq`, `ne`, `lt`, `lte`, `gt`, and `gte`. It checks compatible value types before ordering. Boolean values are not silently treated as integers. Compatible numerical comparisons include Decimal values.

## Example

```python
from narrative_conditions import compare, evaluate

assert compare(4, 5, "lt")
assert evaluate(
    {"all": [{"constant": True}, {"not": {"constant": False}}]}, lambda query: False
)
```

This example uses only the pure operations. A domain predicate needs a caller supplied resolver. Do not invent a universal resolver that can inspect every character and private value.

## Responsibility boundary

GISELA and MARY can both use the shared logic while retaining their own meaning for domain predicates. This package does not decide which facts a player may observe. It does not mutate world state, store progress, consume random numbers, or execute consequences.

## Error behavior

An unknown comparison operator raises a value error. Ordered comparison of incompatible values is rejected. Equality and inequality preserve type rules instead of relying on accidental Python compatibility between Boolean and integer values.

## Verification

The main user of this code is the GISELA and MARY test suite.

```bash
python -m unittest discover -s mary/tests -p 'test_*.py' -q
python tools/check_quality.py
python tools/check_doc_links.py
```

For detailed rationale see ADR 018 under `docs/decisions`. The original record is retained in Spanish as a historical decision document.
