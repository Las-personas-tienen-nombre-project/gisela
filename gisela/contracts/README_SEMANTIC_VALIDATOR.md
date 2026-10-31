# Semantic validator reference

This document explains the static package validator. It describes the code in `semantic_validator.py` and the semantic validation modules. The older validator notes were written when the executor was not yet complete. Those earlier status statements are no longer accurate for the current v1.5 integration.

## Purpose

JSON Schema checks shape and basic field constraints. Semantic validation checks references and other relationships that JSON Schema cannot prove by itself. Both are required for offline package admission.

The validator does not execute a story, settle reactions, draw random numbers, or confirm world changes. Those tasks belong to the GISELA executor.

## Admission entry point

`admit_package_file` reads JSON strictly, validates the declared package, and returns an admitted copy and digest. A blocking error rejects admission. Warnings are reported but do not block by default. Use `reject_warnings` when conservative author checks are needed.

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json --json
```

The diagnostic record identifies severity, code, path, and a message. The path describes the affected location in the package. The digest identifies the admitted definitions for compatible session restoration.

## Reference and identity checks

The validator checks stable identifiers, entry destinations, node and step references, card ownership, world instances, declared variables, action targets, and typed operations. It checks the relationship between a selected option and its containing choice step. It distinguishes a scene action from an action belonging to a scene element, even when their author identifiers are the same.

The current semantic code is split among `semantic_definitions.py`, `semantic_packages.py`, `semantic_sessions.py`, `semantic_evaluations.py`, `semantic_traits.py`, `semantic_expressions.py`, and shared helpers. `evaluation_plan.py` normalizes admitted evaluate declarations.

## Static and dynamic boundaries

The validator can confirm that an evaluation profile and declared branch are structurally usable. It cannot precompute an effective attribute that may change during play. GISELA resolves the value from the current draft at execution time.

Static validation also cannot replace replay validation of pending decisions or visible results. Session restoration validates the saved state and reconstructs pending causal context through the executor.

## Compatibility

The repository contains historical v1.2, v1.3, and v1.4 contracts and current v1.5 contracts. Use the format version declared by the package and never reinterpret a saved session as a newer format without an explicit migration.

## Verification

```bash
python gisela/contracts/verify_contracts.py
python -m unittest discover -s gisela/contracts -p 'test_*.py' -q
python tools/check_project.py
```

Read [Contracts](README.md) for the main authoring and version guide, [Engine](../engine/README.md) for dynamic semantics, and `SEMANTIC_VALIDATION.md` for the technical boundary summary.
