# GISELA. Interactive story engine

GISELA means _enGine for Interactive Stories through Events, Links, and Actions_. It is a narrative engine built around a declarative domain-specific language (DSL) for state-based interactive storytelling. This repository contains the engine, its independent libraries, CLI client GLAUQUIR, tests, documentation, and example narrative packages. The Ren'Py integration belongs to a separate demo repository; it is not required to use GISELA.

This README explains the current implementation. For design history and architecture decisions, use the links at the end. The older documents describe important decisions but some were written before later features were implemented.

## Narrative language and execution

Authors define characters, scenes, events, actions, conditions, relationships, and consequences as structured data rather than writing procedural code for each narrative situation. The architecture separates five concerns:

- **Narrative language:** expresses what may happen, under which conditions, and with what consequences.
- **Schemas and semantic contracts:** validate declarations, references, and supported operations.
- **Engine:** evaluates declarations and executes authorized state transitions.
- **Narrative state:** records facts, character knowledge, relationships, time, and session history.
- **Client presentation:** exposes the narrative through GLAUQUIR, Ren'Py, or other compatible clients.

JSON is the current representation of the DSL; JSON Schema alone does not define its behavior. GISELA's contracts and execution engine establish its narrative semantics. The engine admits packages, starts and restores sessions, and revalidates each action against the current observation before applying changes to confirmed state. It does not execute arbitrary author Python code.

Beyond dialogue trees, declared events can depend on earlier events, world state, character relationships, and reproducible probabilistic evaluations. The same package can produce different outcomes without changing its declarations. Given the same initial state, inputs, and random seed, execution is reproducible.

For the language concepts and execution model, see [Narrative language](docs/architecture/NARRATIVE_LANGUAGE.md).

## Main parts

ALBERTO is the internal world model for characters, places, objects, knowledge, relations, skills, effects, and traits assigned to entities. S.O.F.I.A. is an optional set of five numerical attributes. TRAITS is an independent library for contextual trait contributions. DICE is an independent mathematical evaluator. MARY is an independent mission and objective evaluator. The narrative conditions package provides shared logical operations.

GLAUQUIR is the bundled CLI client. A Ren'Py adapter exists in the separate demo project. Clients show public content and send requests through the authorized client boundary; they do not decide world consequences or commit changes. For formal names and individual guides, read [Names and responsibilities](docs/reference/NAMING.md).

## Start an adventure

Install the development requirements from the repository root.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Run the independent test adventure.

```bash
python tools/glauquir.py --package gisela/packages/h46_faro_de_niebla.package.json
```

Run the Central Clasificadora test adaptation.

```bash
python tools/glauquir.py --package gisela/packages/h46b_central_clasificadora.package.json
```

The game text and current client commands are in Spanish. This does not change the language of the engine contracts. For an interactive walkthrough, read [Quick start](docs/guides/QUICK_START.md) and the [GLAUQUIR command and color guide](docs/guides/GLAUQUIR.md).

## Admission before execution

Every package must be admitted before use. Admission checks JSON structure, semantic references, and other declared constraints. It produces a package digest and frozen definitions. Admission does not create a session and does not calculate future state dependent values prematurely.

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json
```

The admission API is in `gisela.contracts.admit_package`. Use `admit_package_file` for strict file loading or `admit_package` for already loaded definitions. The caller is responsible for rejecting duplicate keys before passing an already parsed dictionary.

A valid schema does not mean every possible operation is executable. The engine also checks whether it supports the admitted operations. Authors should use existing admitted packages and executable tests as references.

## Session lifecycle

Create a session from an admitted package. GISELA initializes the world and enters the declared starting point. It then runs automatic steps until it reaches a public action, a pending decision, a visible evaluation, or the end of the session.

Observe returns the public view of the current confirmed state. It contains a revision, visible content, and a list of offered actions. Act takes the current session identifier, revision, and a currently offered action identifier. It does not accept arbitrary world operations from a client.

A successful action runs against a draft. GISELA resolves conditions, world effects, reactions, objectives, and narrative transitions before committing. A failed action leaves the previous confirmed state unchanged. Repeated or stale requests cannot be used to bypass the authorization boundary.

A turn is associated with executing a narrative node. It is not necessarily one client command or one dice evaluation. Scene exploration can advance fictional time through declared effects without defining an extra narrative turn.

## Python session example

The following sample uses the public session API. It starts a package and reads the first public view. It does not make assumptions about which action the author will offer.

```python
from pathlib import Path
from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

source = Path("gisela/packages/h46_faro_de_niebla.package.json")
admitted = admit_package_file(source)
session = new_session(admitted)
view = session.observe()
print(view["status"])
print(view["actions"])
snapshot = session.export()
restored = restore_session(admitted, snapshot)
assert restored.export() == snapshot
```

An optional boundary for authenticated external clients is `ExecutionGateway` from `gisela.engine.authorized_gateway`. The gateway binds trusted client identities and their granted capabilities. Do not take the principal identity from untrusted Act input. The host is responsible for authenticating a caller before binding it.

## Hidden and visible DICE evaluations

DICE is a pure numerical library. GISELA resolves effective values, calls DICE through its own reproducible random source, chooses the declared branch, and applies its effects.

A hidden evaluation resolves within the action transaction. A visible or acknowledged evaluation fixes the result and random state, then exposes a pending evaluation without applying its branch consequences. The client later chooses the offered continuation action. Saving or restoring must not roll new dice for that pending result. Several visible results can be preserved in an ordered replay when a causal operation contains multiple evaluation points.

The default public view of a pending evaluation exposes the result category and dice only. Private attributes and internal contributions are not published automatically. Refer to [Engine execution](engine/README.md) and [Contracts](contracts/README.md).

## Auxiliary decisions and replay

Some effects need an additional choice before the enclosing transaction can finish. GISELA preserves the causal request and reconstructs it on continuation using the recorded answers. A rejected branch does not commit a partial world change. A restore validates the pending operation against the same package.

Only one top level causal operation can be pending at a time. The pending evaluation and pending transaction mechanisms do not create independent session authorities.

## Author-defined presentation

Packages using DSL 1.5 can declare ordered presentation regions and named views.
Tables display public resources, participants, effects, or actors. Event views
can filter the public causal trace, group records by their published execution
identity, and apply restricted text templates and author-defined visual roles.
These projections do not change the logical state or consume random numbers.
The public causal window contains at most 40 entries; a visual role alone does
not establish that a resource change represents damage or healing.

See the [presentation workshops](docs/guides/workshops/README.md) for examples and
the [nine-unit authoring workshop](workshops/autoria_dsl_15/README.md) for the learning path.
Workshop documentation and automated checks do not certify learning with real students.

## World state and progression

ALBERTO stores current entities and relations. Conditions can inspect allowed facts and other values. World operations on drafts can transfer objects, move characters, change current attributes, manage skills and effects, change assigned traits, and advance fictional time when declared and supported.

MARY observes authorized causal events and proposes mission progress and yields. GISELA is responsible for confirming those results alongside the original action. No library may commit a separate partial state.

## Save and restore

`session.export()` returns a deep copy of the confirmed session state. `restore_session` validates the saved structure, the admitted package digest, and the reconstructability of pending actions. Hosts manage storage. The exported data is not a player observation and must not be published to untrusted clients because it can contain private information.

The package digest prevents silently loading a save against changed definitions. It does not verify external artwork or sound files. Session migration across incompatible package versions is not automatic.

## Contracts and compatibility

Current packages use v1.5 for visible evaluation and optional presentation roles. Earlier v1.2, v1.3, and v1.4 contracts remain present for compatibility. Do not assign v1.5 meaning to older saved sessions. JSON schemas and semantic validation are under `gisela/contracts`.

## Tests

Run the official standalone verification kit from the repository root:

```bash
python tools/check_gisela.py
python tools/check_gisela.py --full
```

The normal kit covers tests, static checks, structural quality, local documentation links, and invariants. `--full` adds complete narrative routes with restore checks. See the [verification guide](docs/guides/VERIFICACION_GISELA.md) for dependencies and limits; the historical `tools/check_project.py` monorepo orchestrator is not included here.

## Known limits

The Ren'Py H5 bridge was implemented in the separate demo project and is not included in this repository. The real graphical SDK and exported builds still need acceptance testing. The Central Clasificadora adventure is a condensed narrative test, not an approved final script. Musical recordings, rights clearance, finished art, and distribution are outside this engine milestone.

## Further reading

Read [Engine implementation](engine/README.md) for transaction and source module details, [Contracts](contracts/README.md) for authoring formats, [Documentation index](docs/README.md) for learning paths, and [Current roadmap](docs/operatives/ROADMAP.md) for the implementation status.

Read ADR 020 for authorized callers, ADR 021 for evaluation authoring, ADR 022 for hidden evaluations, and ADR 023 for visible evaluations. These source decision records remain in `docs/decisions` in their original language. The implemented v1.5 design is recorded in `docs/architecture/E3_EVALUACIONES_VISIBLES.md`.


## License and Copyright

GISELA, its software components, development tools, and associated source code are licensed under the **Apache License, Version 2.0**. See the [LICENSE](LICENSE.md) file for details.

**Narrative content is excluded from the Apache 2.0 license.**

All stories, literary works, scenes, dialogue, original characters, and narrative packages included in this repository are **Copyright (c) 2026. All rights reserved.**

This includes demonstration and testing materials, such as *El faro de niebla* and *Las personas tienen nombre*, as well as any other narrative content provided with GISELA.

These materials are included solely for demonstration, development, and testing purposes. Their inclusion does not grant permission to modify, redistribute, republish, or commercially exploit them without prior authorization from the copyright holder.

This restriction does not affect the rights granted to the GISELA software under the Apache License 2.0.
