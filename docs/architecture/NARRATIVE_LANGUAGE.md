# GISELA narrative language

GISELA's domain-specific language (DSL) describes state-based interactive stories. Authors declare possible narrative situations and their conditions and consequences; the engine decides which declarations apply to a particular session. JSON is the current representation of the language, not its complete semantic specification. This document describes the implemented concepts rather than teaching package authoring.

## Declarations and meaning

A narrative package supplies a manifest, initial state, cards, nodes, scenes, rules, and endings. Optional sections add capabilities such as localized strings, traits, DICE profiles, and MARY objectives when the selected contract version supports them. The package declares definitions; a session stores changing instances and progress separately. Package definitions remain fixed during that session.

- **Cards** define reusable kinds of characters, places, objects, skills, and effects. **Scenes** describe an explorable presentation context, its visible actors and elements, and actions that may be offered there. A scene is distinct from a physical location.
- **Nodes** contain ordered narrative steps, including text, dialogue, choices, conditions, consequences, transitions, and endings. Entering a node starts an execution; a client command does not necessarily start a new turn.
- **Actions and choices** represent author-declared possibilities. Their conditions can control visibility or availability. The engine rechecks an offered action when it receives an Act request.
- **Rules** react to declared triggers and may apply further consequences within the same causal operation. The author does not supply procedural Python code for each situation.

Schema validation constrains the shape and types of declarations. Semantic validation checks references and other relationships that JSON Schema cannot establish alone. Admission freezes validated definitions and computes a digest. Executability also depends on support in the current engine; schema validity by itself does not guarantee a playable story.

## Narrative state and causality

A session records its active node or scene, world instances, time, revisions, random state, and history. Historical facts record occurrences; individual character knowledge and beliefs are separate from that history. Relationships and other world values may change through declared consequences. Conditions can consult permitted state, so earlier events can affect later choices and reactions without rewriting the package.

GISELA evaluates an authorized action against a draft state. It applies declared consequences, resolves reactions and optional objectives, validates the result, and either commits the causal operation or discards it. Pending decisions and visible evaluations preserve the information needed for deterministic continuation or restoration without exposing a partially committed world.

Declared evaluations can use effective world values, traits, and a reproducible random stream. The same package may therefore yield different outcomes for different choices, states, or seeds. With the same admitted package, initial state, inputs, and random seed, execution is reproducible. Restoring a session checks the package digest and the saved state; it does not silently migrate a save to changed definitions.

## Presentation boundary

Observe publishes the current authorized view and offered actions. Act accepts a current offered action and revision, rather than arbitrary world operations from a client. GLAUQUIR, Ren'Py, and other compatible clients present that view and submit choices; they do not decide narrative consequences or own the confirmed state. Private session snapshots and public observations serve different purposes.

The language supports conditional state and event simulation within declared rules. It does not generate stories autonomously or imply general-purpose intelligence for characters.

For field-level syntax and versioned constraints, use the [package contracts](../../gisela/contracts/README.md). For transaction and replay behavior, use the [execution model](../../gisela/engine/README.md). The [v1.5 architecture](GISELA_Arquitectura_Consolidada_v1_5.md) records the broader design and its historical stages.
