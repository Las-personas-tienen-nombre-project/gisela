# GISELA package and session contracts

This directory defines JSON schemas, package admission, semantic validation, canonical encoding, and deterministic random utilities. It is the contract boundary between authored story data and the GISELA executor.

## Contract versions

The repository retains v1.2, v1.3, v1.4, and v1.5 schemas. Current integration packages use v1.5. Version 1.3 introduced TRAITS integration contracts. Version 1.4 added declarative evaluation admission and hidden execution. Version 1.5 adds visible evaluation state and continuation, plus optional client presentation roles and diagnostic disposition configuration. Older package and save semantics must not be silently changed.

The unversioned schemas at the top of this directory are part of the earlier contract set. Do not assume they are the current v1.5 authoring reference. Use the version directory appropriate for the package.

## Package components

A package declares a manifest, cards, nodes, scenes, rules, and initial state as required by its schema. The manifest identifies format version, language, entry point, and declared data such as variables, facts, and relations. Cards describe entities and other reusable definitions. Scenes describe places, actors, elements, and actions. Nodes contain narrative steps and choices. Rules describe automatic reactions.

A package may declare DICE profiles, a TRAITS catalog, and MARY definitions where the selected contract version permits them. These are optional capabilities and must not be used to impose game specific behavior on the engine.

For a first package, follow [Crea tu primer paquete](../../docs/guides/CREAR_PAQUETE.md). Its small v1.5 package is complete and playable. For an example with scenes, characters, objects, skills, traits, DICE, and missions, inspect `gisela/packages/h46_faro_de_niebla.package.json`.

## Admission

Run strict file admission from the repository root.

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json
```

Use the library API for applications.

```python
from pathlib import Path
from gisela.contracts.admit_package import admit_package_file

admitted = admit_package_file(Path("gisela/packages/h46_faro_de_niebla.package.json"))
print(admitted.digest)
package = admitted.materialize()
```

`admit_package_file` reads JSON strictly and checks the package. `admit_package` accepts a dictionary that the caller has already parsed. That caller is responsible for rejecting duplicate JSON keys before constructing the dictionary. Admission returns frozen source definitions, diagnostics, and a digest. It does not start a session or precompute values that can change during play.

Structural and semantic errors reject a package. Warnings do not reject it by default. Set `reject_warnings` for a stricter authoring check. Engine capability checks remain necessary because the full schema may describe more than the current executor accepts.

## Session and observation

The session schema describes committed state, history, random state, and the optional current pending operation. Session export is private data. Restore validates the snapshot against the exact admitted package and checks pending replay when applicable.

The Observe contract describes public content and offered actions. It must not expose private world data merely because it exists in the snapshot. The Act contract accepts the current session identifier, revision, and offered action identifier. It is not a general purpose operation language.

In v1.5, `presentation.color` accepts `default`, `red`, `yellow`, `green`, `cyan`, `blue`, `magenta`, or `white` on a card, scene actor, or scene element. An instance can override its card with a declared string property `presentation_color` whose initial value is `inherit`; an ordinary `set` changes or resets it. Admission, writes, and restore validate these values. `Observe` publishes only the effective color role. The [client API](../../docs/architecture/API_CLIENTES.md#glauquir-y-presentación-v15-vigente) specifies precedence and privacy.

`manifest.disposition_display` is optional and separate from `relationship_fields`: it names a numeric relationship field and declares `minimum`, `neutral`, and `maximum`, plus four optional normalized `thresholds`. It is validated at admission. The directed effective value and its category are available only through a privileged `debug_query`, never through `Observe`. A package without this configuration remains playable and its diagnostic disposition is `unknown`.

Scene actors may declare `unknown_name`, `known_if`, and a stable public `public_id`; elements may declare `public_id` and `public_entity`; scene actions may declare `public_id`. These are optional author supplied aliases, so authors must review any remaining IDs and labels that could reveal information the player has not learned. The action execution token remains `action_id` from the current observation.

## Evaluate declarations

E1 admitted `evaluate` from node steps, choice options, and scene actions. E2 implemented hidden results. E3 implemented visible and acknowledged results in v1.5. The executor resolves effective attributes and traits at execution time, uses GISELA random state, and selects the declared branch.

When a visible result is pending, Observe offers `continue_evaluation`. That continuation reuses fixed dice, rather than drawing again. Do not assume that DICE itself owns pending state, session identity, or the consequences of a branch.

## Deterministic contracts

`canonical.py` implements canonical package encoding and digests. `rng.py` provides the reproducible random stream used by GISELA. A package digest detects changed definitions when a session is restored. Random state is part of the session and is committed or rolled back under GISELA authority.

The detailed original specifications are in [Canonical digest](../../docs/determinism/DIGEST_CANONICO.md) and [Random stream](../../docs/determinism/RNG_SHA256_CONTADOR.md).

## Validation modules

`admit_package.py` is the authoring admission gateway. `semantic_validator.py` provides the main validation facade. The `semantic_*` modules split reference and type checks by responsibility. `evaluation_plan.py` normalizes admitted evaluation definitions. `verify_contracts.py` checks the available schemas and examples.

For the meaning of every field, inspect the schema for the package version and the matching semantic validator. Do not infer meaning from a similar field in an older schema.

## Examples and verification

The `examples` and `semantic_examples` directories contain validation fixtures. Some are snapshots or negative cases, not complete playable adventures. Playable packages live under `gisela/packages`.

```bash
python gisela/contracts/verify_contracts.py
python -m unittest discover -s gisela/contracts -p 'test_*.py' -q
python tools/check_quality.py
python tools/check_doc_links.py
```

## Compatibility and safety

A valid session must be restored against the same admitted package digest. A changed package needs an explicit migration policy, not a silent format reinterpretation. Keep internal snapshots separate from public Observe results. Validate the client authority at the session gateway and do not treat an arbitrary external string as authentication.

## Related documents

Read [GISELA](../README.md), [Engine](../engine/README.md), [naming](../../docs/reference/NAMING.md), and the current E2 and E3 implementation records in `docs/operatives`. Earlier contract design documents remain available in `docs/architecture` and the decision records in `docs/decisions`.
