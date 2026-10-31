# DICE. Dice Interpretation and Chance Engine

DICE is an independent mathematical library. It validates game specific evaluation profiles, calculates numeric results, and returns an outcome category. It does not own a session, a random generator, a character, a mission, or a narrative consequence.

## Design boundary

A caller provides a compiled profile and a request containing `base`, `bonus`, and `difficulty`. When a profile needs random draws, the caller provides a function that returns a valid die result. The library calls that function without managing its state or persisting anything.

GISELA owns the deterministic random state. It validates effective inputs and budgets, supplies draws, selects the declared consequence branch, and commits its state. DICE can also be used independently of GISELA, TRAITS, and S.O.F.I.A.

## Public API

`compile_profile(document)` validates a neutral `dice.profile.v1` document and returns a defensive compiled mapping. `evaluate(profile, request, draw=None)` validates the request and reuses that compilation while the mapping remains intact; a raw or subsequently mutated profile is validated again before use. It then makes any required draws and returns a `dice.result.v1` result. Contract problems raise `DiceError`.

The profile schema lives in `dice/schemas/profile.schema.json`. It defines the accepted modes and value budgets. Code verifies that band thresholds are ordered and unique and that outcome identifiers are unique.

## Modes

`deterministic` uses no die draws. `single_die` uses one draw. `dice_sum` adds several draws. `dice_pool` uses the largest result in the pool. Profile settings specify the die count and sides when required.

The result total is calculated from base plus bonus plus die value minus difficulty. The selected outcome is the highest declared band whose lower threshold the total reaches. If no threshold is reached, the first band is the fallback.

## Independent example

```python
from dice import compile_profile, evaluate

profile = compile_profile({
    "schema_version": "dice.profile.v1",
    "id": "check",
    "mode": "deterministic",
    "bands": [
        {"id": "fail", "min": -100},
        {"id": "pass", "min": 5}
    ]
})
result = evaluate(profile, {"base": 4, "bonus": 2, "difficulty": 0})
assert result["outcome"] == "pass"
assert result["rolls"] == []
assert result["total"] == 6
```

For a random profile, the caller must provide `draw(sides)`. The returned value must be an integer between one and the number of sides. An invalid value raises `DiceError`.

## Result structure

A result identifies the profile and outcome band. It also includes the list of rolls, combined die value, base, bonus, difficulty, and total. This is a mathematical result, not a public player projection. Some of these details can include private inputs and should not automatically be displayed.

## Use inside GISELA

The engine resolves numerical attributes from S.O.F.I.A., optional contextual TRAITS bonuses, and declared constants before calling DICE. The bridge in `gisela/engine/traits_dice_bridge.py` does not confer transaction authority on DICE.

A hidden evaluation commits its chosen branch within the enclosing transaction. A visible or acknowledged evaluation fixes a result and the random state first, then waits for an authorized continuation before applying branch effects. All evaluation origins use the GISELA executor. The current behavior is implemented for v1.5 packages.

DICE itself does not know whether a result will be hidden or shown. Presentation belongs to GISELA and its client. The old README statement that visible results were not implemented is no longer current.

## Error handling and limits

The library rejects malformed profiles, invalid numerical requests, invalid draw functions, duplicate outcome bands, and unsupported values. It does not retry failed author operations, draw a second random result for a player, or commit any world mutation.

Avoid interpreting a DICE result as approval to execute arbitrary operations. Only the author declared branch can be selected by GISELA after authorization and validation.

## Tests

```bash
python -m unittest discover -s dice/tests -p 'test_*.py' -q
python -m unittest gisela.engine.tests.test_e2_evaluations -q
python -m unittest gisela.engine.tests.test_e3_visible -q
```

For a complete game package using DICE in all three presentations, inspect `gisela/packages/h46_faro_de_niebla.package.json`. The automated route is available through `tools/h46_walkthrough.py`.

## References

Read [GISELA](../gisela/README.md), [contracts](../gisela/contracts/README.md), [TRAITS](../traits/README.md), and [naming](../docs/reference/NAMING.md). Original decisions for visible evaluations are in `docs/decisions/ADR_023_E3_EVALUACIONES_VISIBLES_V15.md`.
