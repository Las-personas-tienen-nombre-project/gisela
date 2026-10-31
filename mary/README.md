# MARY. Mission Assignment, Resolution and Yield

MARY is an independent library that evaluates declared missions and objectives. It reads authorized events and previous progress, then proposes the next progress state and any declared yields. It does not edit GISELA world state or commit a transaction.

## What MARY handles

A mission can group objectives. An objective can be satisfied by an exact condition, by collecting distinct experiences, or by accumulated weighted progress, according to the declared definitions. MARY tracks progress using serializable values and computes which public missions can be shown to a player.

The library needs no character system or random generator. Its input is a compiled mission plan, an event context, and the current progress snapshot.

## Public API

`compile_plan(definitions)` validates and compiles a mission plan. `initial_progress(plan)` creates the initial progress state. `evaluate(plan, context, progress)` returns a proposed update and output events without mutating its inputs. `validate_progress(plan, progress)` checks persisted progress. `public_quests(plan, progress)` returns the missions and objectives that are permitted in the public view.

Invalid plans and progress raise `MaryError`. The schema is `mary/schemas/definitions.schema.json`.

## Mission progression

Progress is driven by meaningful events supplied by the host. It is not inferred from arbitrary player text. Distinct event requirements should not count the same experience twice. The evaluator controls completion transitions according to the declared mission plan and current progress.

MARY does not write a fact directly into the world when an objective completes. Instead it returns proposed yields. GISELA decides whether the enclosing action can commit them.

## Yields

A yield identifies its objective source and the proposed effect. It is not proof that the effect happened. The host can reject the proposal when other transaction rules fail. In GISELA, the objective progress and all authorized consequences must commit together. A failed transaction must not leave a completed mission while rolling back its world effects.

## Public information

Mission data may contain information that is not visible to a player. `public_quests` constructs the mission projection according to the plan and progress. The client should show this public projection rather than reading the private progress snapshot directly.

GLAUQUIR supports the current Spanish commands `misiones`, `quests`, and `objetivos`. The client gets this data through Observe.

## Integration and independence

MARY uses the shared `narrative_conditions` library for pure condition composition. It does not import GISELA, ALBERTO, DICE, S.O.F.I.A., or TRAITS. `gisela/engine/mary_bridge.py` integrates MARY within the GISELA causal execution and commit boundary.

This separation allows a different host to reuse MARY without implementing a GISELA session.

## Tests and live examples

```bash
python -m unittest discover -s mary/tests -p 'test_*.py' -q
python -m unittest gisela.engine.tests.test_mary_integration -q
python tools/h46_walkthrough.py --route completa
```

The El faro de niebla package contains declared mission content used by integration tests. For precise input fields, examine the schema and tests rather than inferring a contract from informal descriptions.

## Important limits

MARY cannot authenticate a player, perform random evaluations, select scene actions, or publish hidden character state. Its outputs remain proposals until the host transaction succeeds. The project does not provide a general mission editor or graphical MARY user interface in this library.

See [naming](../docs/reference/NAMING.md), [GISELA](../gisela/README.md), [narrative conditions](../narrative_conditions/README.md), and the original MARY design and ADR 018 under `docs/architecture` and `docs/decisions`.
