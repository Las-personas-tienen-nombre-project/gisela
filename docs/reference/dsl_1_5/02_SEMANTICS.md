# 02 Semantics and evaluation

## Execution sequence

Admission freezes declarations and computes a digest, but does not begin narrative execution. `new_session` initializes instances, variables, histories and the RNG. It then enters the declared starting node or scene. A node entry increments the narrative turn and creates an execution identity. Narrative steps advance through their declared destinations and conditions. Scene entries enter exploration without an implicit turn or physical movement.

When an authorized action is chosen, GISELA creates a draft, evaluates active conditions and expressions, applies declared operations, settles automatic reactions, validates the draft, and commits it. Failure discards the draft and leaves confirmed state unchanged. An automatic transition can also open another node. The engine has an explicit limit on automatic steps and reaction rounds. Do not treat implementation caps as unrestricted authoring capacity.

## Reads and writes

`value` expressions read declared variables, statistics, properties, relationships, or other supported references according to their schema branch and evaluation context. `condition` expressions gate an action, option, branch or rule. An lvalue identifies a writable target, but writing must use a recognized operation. Operations include `set`, `add`, `transfer`, `move_character`, `learn_fact`, `set_belief`, `record_fact`, `roll`, `apply_effect`, `end_effect`, `assign_trait`, `remove_trait`, and others listed in `support.SUPPORTED_OPS`. A structurally admitted operation can still be unsupported in a particular execution context.

The `evaluate` declaration has an evaluation ID, DICE profile, presentation policy, inputs and outcome branches. `hidden` results execute without a visible pause. In DSL 1.5, `visible` and `acknowledged` evaluation results can produce a pending evaluation and a continuation action. A continuation must reuse its fixed result rather than draw again. The result can select a declared branch, effects, and destination.

## Guarantees and limits

Guaranteed by the public contract: structural kinds, permitted expression forms, and validation rules. Verified by runtime tests: atomic rejected actions and deterministic continuation for tested paths. Not established: a single total execution order for all possible nested actions and effects beyond the explicit published ordering rules.

## Sources

- `gisela/engine/runtime.py`, `action_handler.py`, `reactions.py`, `evaluation_execution.py`, `evaluation_pending.py`
- `gisela/contracts/semantic_expressions.py`, `semantic_evaluations.py`
- `docs/architecture/E2_EVALUACIONES_OCULTAS.md`, `E3_EVALUACIONES_VISIBLES.md`
