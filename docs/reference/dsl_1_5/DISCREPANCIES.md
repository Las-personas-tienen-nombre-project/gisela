# Discrepancies and open limits

## Source hierarchy

The v1.5 schemas and public semantic validators determine admitted syntax. The public engine implementation and tests determine actual execution. Productive examples demonstrate their tested paths. Existing explanatory documents have lower authority where they conflict.

## Confirmed scope limits

- Schemas at the root of the contracts directory are older and must not replace versioned v1.5 schemas.
- The Python distribution version is 0.1.21, while the current authored format is DSL 1.5. These values identify different things.
- Structural acceptance does not prove semantic admission, execution, or determinism.
- Presentation roles describe author supplied labels, not engine proven combat damage or healing. See the existing presentation contract.
- The public Observe payload is not the private session snapshot.
- Earlier documents under architecture include proposals. Proposal titles are not proof of public implementation.
- The archived documentation audit reports tests from its original run. Those outcomes are historical, not results of this delivery.

## Remaining work

- Verify conditional schema branches and cross references at field level against the semantic validator.
- Add minimal admitted packages and both positive and negative runtime tests for each behavior.
- Trace every error message to its exact public rejection path.
- Confirm all Tegularis mechanics through public entry points and evidence, rather than assuming a schema alone suffices.

No engine defects are claimed without a reproducible public example.

## Status after topical reference pass

Twelve topic chapters were added, along with a public API example verifier and a three-context Dodge test. The 13 schema inventories remain structural extraction, and there is no exhaustive semantic or executable test for every schema branch. An earlier general engine test attempt reached 88 percent before its time limit. A subsequent full repository run completed with 18/18 checks on 2026-11-04 (see [verification](VERIFICATION.md)); this does not close field-by-field semantic or executable coverage. The remaining gap concerns reference coverage, not a demonstrated engine fault.
