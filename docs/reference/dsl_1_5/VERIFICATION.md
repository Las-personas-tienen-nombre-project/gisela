# DSL 1.5 reference verification

## Repository identification

Python distribution version: 0.1.21. Authored package format: 1.5. The extracted reference uses the 13 versioned schema files in gisela/contracts/v1_5.

## Executed checks

- `python tools/check_doc_links.py`: PASS. Local Markdown destinations and anchors are valid.
- `python tools/check_quality.py`: PASS. Repository file and function size checks are satisfied.
- `PYTHONPATH=. python gisela/contracts/verify_contracts.py`: PASS. Thirteen schemas and contract examples were checked. The verifier explicitly states that semantic package admission is not runtime execution.
- `PYTHONPATH=. python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json`: PASS. The example was admitted. Admission does not establish runtime coverage.
- `PYTHONPATH=. python -m unittest discover -s gisela/contracts -p 'test_*.py' -q`: PASS. 181 tests completed.
- `PYTHONPATH=. python tools/check_gisela.py --full`: INCOMPLETE. The run reached the motor and libraries test group but exceeded the available execution time. No full suite pass is claimed.

## Verification boundary

The structural field inventory was generated from the schemas, not manually inferred. Each field retains its source schema and status. It has not been exhaustively reviewed against every semantic validator branch. The current verification does not cover all possible public runtime behaviors, conditional choices, Tegularis trajectories, or the full workshop suite. Therefore this is a verified structural reference and an incomplete semantic and executable reference, not a fully accepted final DSL manual.

## Maintainability audit

This work only adds field inventories, a central index, coverage and discrepancies, and one link in the existing documentation index. Existing narrative language, architecture, guides, implementation, package files, schemas and tests were not edited. No DSL capability or contract has been changed. The field pages are an extracted index pointing to canonical contracts, not an independent normative schema. A future maintenance pass should automate comparing each field inventory with new schema versions and add reproducible runtime examples before upgrading its coverage status.

## Additional execution in this delivery

- `PYTHONPATH=. python docs/reference/dsl_1_5/verify_reference_examples.py`: PASS. Both narrative endings, invalid version and dangling node, pure Observe, invalid and stale action rollback, restore equivalence, and equal-seed initial equivalence. Reproducible details are in `EXECUTION_EVIDENCE.md`.
- `PYTHONPATH=. python -m pytest -q gisela/engine/tests/test_documented_minimal_package.py gisela/engine/tests/test_npc_contests_v05.py gisela/engine/tests/test_npc_traits_v06.py gisela/engine/tests/test_actuation_public_v073.py`: PASS. 33 tests and 2 subtests.
- `PYTHONPATH=. python -m pytest -q gisela/engine/tests/test_reference_dodge_contexts.py`: PASS. 1 test covering 3 contexts, both positive and negative.
- `PYTHONPATH=. python gisela/contracts/verify_contracts.py`: PASS. 13 schemas and 7 example snapshots.
- `PYTHONPATH=. python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json`: PASS. Admission only.
- `PYTHONPATH=. python tools/check_doc_links.py`: PASS.
- `PYTHONPATH=. python tools/check_quality.py`: PASS.

## Coverage qualification

The twelve topical chapters are a cross-reference guide built from existing canonical documents and selected public runtime checks. They do not constitute exhaustive field-by-field behavioral proof for every one of the 13 schemas. The per-schema inventories are structural. In particular, all optional branches, every invalid expression variant, every possible runtime error, and every Tegularis outcome remain outside the verified examples. No full language completion claim is made.

## Full verification attempt for this delivery

- `PYTHONPATH=. timeout 145s python tools/check_gisela.py --full`: INCOMPLETE. The full command was interrupted by its time limit while the first large pytest group was still running at 88 percent. A completed summary, final exit status for the entire suite, and subsequent quality stages were not produced. This attempt is not a pass.

## Follow-up repository verification, 2026-11-04

After reviewing the Dodge test's B101 assertion and fixing its import order,
`python tools/check_gisela.py --full` completed with exit 0 and 18 of 18 checks
passing: 841 core tests and 128 subtests, plus 69 tool tests and 100 subtests.
The six narrative routes with restoration also passed. See the
[completed run](../../operatives/evidence/reparacion_y_revision_2026_11_04/check_gisela_full_final.log)
and the [review report](../../operatives/REVISION_DOCUMENTAL_2026_11_04.md).

The earlier incomplete attempts above remain historical records. This follow-up
also simplified display punctuation and authored example text, without changing
the DSL schemas. Edited packages have new digests and require their matching
saved states. A passing repository suite does not expand the field-by-field
semantic coverage claimed for this reference.
