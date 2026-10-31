# Static and dynamic validation boundaries

This page lists the responsibilities of the semantic package validator and the GISELA executor. It is a current reading guide. Historical design decisions remain in the ADR and architecture records.

## Static validation at admission

Check that declared identifiers, types, references, entry points, choice destinations, owner and element actions, initial world values, and optional feature definitions satisfy the selected contract version.

Check that authored evaluation profiles, context references, and outcomes can be normalized without relying on a value that changes during play. Preserve the package digest and diagnostics. Admission does not create a session or authorize a client.

## Dynamic execution checks

The executor checks the offered action and revision, resolves the current state and any effective attributes, runs world operations and reactions on a draft, and commits only a valid result. It checks transition atomicity, conflicts, bounded processing, and random state ownership.

Pending auxiliary choices and visible evaluations require replay verification when resumed or restored. A static schema cannot prove that a saved pending operation will reproduce the same causal request.

## Privacy and authority

Observe is a public projection. Private session export and development queries require a trusted boundary. An external caller does not gain authority by supplying a session identifier or another principal identifier in untrusted input.

## Compatibility and test evidence

Current integration packages use v1.5. Older contracts remain supported within their defined semantics. A modified package digest can make a saved snapshot incompatible.

```bash
python gisela/contracts/verify_contracts.py
python -m unittest discover -s gisela/contracts -p 'test_*.py' -q
python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q
```

For repository checks run `python tools/check_quality.py` and `python tools/check_doc_links.py` in addition to the suites above. See [Contracts README](README.md), [Validator README](README_SEMANTIC_VALIDATOR.md), and [GISELA](../README.md).
