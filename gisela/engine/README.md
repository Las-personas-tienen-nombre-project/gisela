# GISELA execution engine

This directory contains the active session executor. The executor implements the narrative authority described in [GISELA](../README.md). It is not a separate story engine and it does not contain rules specific to Las personas tienen nombre.

## Public boundary

`GiselaSession` in `runtime.py` provides `new_session`, `restore_session`, `observe`, `act`, and `export`. A host may use `ExecutionGateway` from `authorized_gateway.py` to bind a trusted principal with selected capabilities. The gateway is not a replacement for authentication by the host.

Clients must use the actions supplied by Observe and the matching revision. They must not call internal world writers or construct arbitrary consequences. The engine owns the confirmed state, random state, and causal history.

## Main execution path

Admission first freezes and validates package definitions. A session then materializes declared world state, selects its starting node or scene, and produces an observation.

An Act request is checked against the current revision and offered action. The selected action runs in a draft. The executor evaluates conditions and effective inputs, applies declared world operations, settles reactions and objectives, and follows node transitions. It validates the resulting state before committing. Failure discards the draft.

The executor must not leave a node closed if entering the next node fails. Its transition boundary is atomic. Limits on automatic steps and reaction rounds prevent unbounded processing and are enforced by the implementation and tests.

## Pending transactions

A requested action may need an auxiliary decision. The executor records enough of the initiating request to replay it from confirmed state. It does not publish partially applied world changes. The next valid Act supplies a choice that was offered by the current observation. Restore checks that the pending request can still be reconstructed.

The implementation uses `DecisionRequired` and `DecisionReplay`. A new client should not provide its own replay engine.

## Visible evaluations

E2 implemented hidden evaluations in v1.4. E3 added visible and acknowledged evaluations in v1.5. All evaluation origins use the same routes. An evaluation can be declared in a node step, a choice option, or a scene action, including an element action.

Hidden evaluations resolve and apply their branch as part of the original commit. Visible evaluations record a fixed result and random state before exposing an observation. Their effects are committed after the offered `continue_evaluation` action. Replay uses fixed results without rolling again. Multiple pending evaluation points can be replayed in order as one causal operation.

The public pending view contains the outcome and the individual dice. It does not expose internal inputs such as private traits or attributes. The difference between visible and acknowledged presentation does not require two execution engines.

## World operations

`world.py` and the `world_*` modules implement entity state and operations. `world_base.py` supplies shared lookups and errors. `world_entities.py` covers entity changes, `world_values.py` handles values and relations, `world_traits.py` handles assigned traits, `world_skills.py` handles skill state, and `world_effects.py` handles effects. Specific capabilities are described in [ALBERTO](../../docs/architecture/ALBERTO.md).

`sofia.py` computes optional numerical attribute components and allows writes to current values on transaction drafts. TRAITS and DICE remain imported through integration routes rather than through each other.

## Rules, reactions, and objectives

`conditions.py` adapts declared predicates to world state. `consequences.py` applies declared operations. `reactions.py`, `reaction_nested.py`, and `reaction_writes.py` settle automatic rules with conflict controls. `mary_bridge.py` integrates MARY progress and yields under the same commit authority.

These modules must not introduce a second committed state or a second random source.

## Presentation and private data

`projection.py`, `public_view.py`, and `scene_presence.py` construct the authorized public scene and action list. `queries.py` supports explicitly privileged development queries. A player observation and a private exported snapshot are different interfaces. Do not copy private state directly into text, menus, or logs.

`reading_log.py` records confirmed public narrative history. `scene_actions.py` presents and traces scene actions. `skill_window.py` manages offered skills in their declared windows.

## Persistence and authorization

`authorized_gateway.py` binds principals with capabilities such as `act` and `observe_player`. Optional private export and debug access require their own capabilities. `checkpoint_store.py` handles durable checkpoint integration, while session export remains a JSON compatible snapshot. Gateway receipts protect repeated commands, and the session controls revisions and causal state.

Never treat a string supplied by a remote client as proof of a trusted principal. Authentication belongs to the host. Do not persist a draft as if it were confirmed state.

## Module map

`runtime.py` owns session setup and orchestration. `action_handler.py` handles authorized actions. `initialization.py` creates initial state. `evaluation_execution.py` resolves evaluation routes. `evaluation_pending.py` manages pending visible evaluations. `pending.py` contains the replay primitives. `expiration.py` handles declared expiration. `skill_execution.py` and `support_skills.py` support skill effects. `support.py` checks executable capabilities. `errors.py` defines engine errors.

`scene_actions.py` and `public_view.py` build the public scene and card projections. `presentation.py` resolves explicit color roles and calculates private diagnostic disposition; `queries.py` exposes that calculation through the diagnostic API. GLAUQUIR applies ANSI styles separately.

This map lists entry points and responsibilities rather than every private helper. Read source and tests before extending behavior.

## Declarative presentation

The maintained engine projects optional author-defined regions and views from
public Observe data. Tables, causal event groups, and restricted templates
are pure projections: they do not modify logical state or draw random values.
The causal window contains at most 40 entries. A visual role is an author
label and does not prove that a resource change represents damage or healing.
See the [presentation contract](../../docs/architecture/PRESENTACION_DECLARATIVA_V082.md)
and [workshops](../../docs/guides/workshops/README.md).

## Implementation tests

```bash
python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q
python -m unittest gisela.engine.tests.test_e2_evaluations -q
python -m unittest gisela.engine.tests.test_e3_visible -q
python -m unittest gisela.engine.tests.test_presentation_color -q
python tools/check_gisela.py
```

The focused tests cover transactional failures, pending replay, stale actions, version compatibility, deterministic evaluations, scene actions, color projection, and narrative integration packages. The [official verification kit](../../docs/guides/VERIFICACION_GISELA.md) also runs static, structural, documentation, and invariant checks. Passing these checks does not prove graphical Ren'Py behavior.

## Rules for extensions

Keep story definitions out of Python control flow. Reuse the authorized Act and Observe boundary. Evaluate values from the current draft, not from a value cached at package admission. Preserve exact once effects, node transition atomicity, session version compatibility, and private data boundaries. Extend the existing replay mechanism when an operation needs suspension, rather than inventing another state machine.

## Technical references

See [GISELA contracts](../contracts/README.md), [current v1.5 architecture](../../docs/architecture/GISELA_Arquitectura_Consolidada_v1_5.md), [E2 design](../../docs/architecture/E2_EVALUACIONES_OCULTAS.md), [E3 design](../../docs/architecture/E3_EVALUACIONES_VISIBLES.md), and [ADR records](../../docs/decisions). Architecture and decision records were written during earlier stages and must be read together with current code.
