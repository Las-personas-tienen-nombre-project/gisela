# GISELA changelog

This file summarizes changes relevant to using, authoring, integrating, and maintaining GISELA. It is not a normative specification. For current behavior, consult contracts, code, and tests. Dates and versions come from preserved repository records; missing release dates have not been inferred.

## 2026-11-07 - Documentation and author course preparation

- Archived the three Spanish *El paraguas olvidado* manuals for reuse. Their staged practice packages are not included in this repository.
- Kept the older Tegularis workshop in place because its scripts rely on fixed paths. It is no longer presented as the main learning path.
- Centralized project-level component definitions in the root README, and aligned the documentation index and roadmap in English.
- The new author course will be written in Spanish first and translated later. No engine or DSL contracts changed.

## 2026-11-07 - D2 documentation consistency

- Clarified where retired records and historical evidence can be found in the roadmap and DSL reference index.
- Removed outdated milestone headings and unsupported future commitments from the current ALBERTO and S.O.F.I.A. descriptions.
- Distinguished incomplete verification attempts from the complete run recorded on November 4. DSL semantic coverage remains partial.

## 2026-11-07 - D2 architecture cleanup

- Removed nine incremental v0.7, E1, and TRAITS/DICE proposal documents that no longer described current contracts. Git preserves their history.
- Kept E2 as the v1.4 compatibility reference and E3 as the v1.5 reference.
- Removed obsolete H2, H3, and H4 implementation reports from the consolidated architecture.
- Updated references in ALBERTO, S.O.F.I.A., E0, and TRAITS without changing code or DSL contracts.

## 2026-11-07 - D2 historical documentation cleanup

- Consolidated milestones here and retired redundant operational reports and implementation records from active documentation. Git retains their earlier versions.
- Kept contracts, ADRs, explicitly marked proposals, architecture references, eight reports protected by tests, and evidence under `docs/operatives/evidence/`.
- Updated links to current references and this changelog. See the [historical index](docs/history/README.md).

## 2026-11-04 - Documentation review

- Separated current guides, DSL 1.5 reference, and historical records.
- Fixed document links and paths and ran documentation checks.
- Recorded results of link and reference example tests. Dated results are not a permanent guarantee for future builds.

## 2026-10-31 - Standalone repository and PA-001 stabilization

- GISELA became a standalone engine repository. The Ren'Py demo and graphical integration are not runtime dependencies.
- PA-001 expanded checks for format compatibility, restore, invalid state rejection, and offline regressions.
- Completion reports record results at their dates, not permanent certification.

## E0-E3 - Declarative evaluations

- **E0:** defined authority, commit, and persistence boundaries.
- **E1:** normalized the `evaluate` authoring form and related contracts.
- **E2:** added hidden evaluation execution.
- **E3:** added visible, acknowledged evaluations with deterministic continuation and restore in DSL 1.5.

References: [E0](docs/architecture/E0_FRONTERA_AUTORIZADA_Y_PERSISTENCIA.md), E1 (archived in Git), [E2](docs/architecture/E2_EVALUACIONES_OCULTAS.md), [E3](docs/architecture/E3_EVALUACIONES_VISIBLES.md), and [ADR-023](docs/decisions/ADR_023_E3_EVALUACIONES_VISIBLES_V15.md).

## H2-H5 - Engine, world, CLI, and integration

- **H2:** session execution, transactions, suspension, and restore for the supported subset of that milestone.
- **H3:** added ALBERTO operations and S.O.F.I.A. attributes, properties, effects, and skills in stages.
- **H4:** scene exploration and actions, the GLAUQUIR text client, and invariant tests.
- **H4.6:** *El faro de niebla* and *Central Clasificadora* laboratory packages for integrated test routes.
- **H5:** Ren'Py adapter in the separate original narrative repository. Acceptance with the real graphical SDK remained outstanding in the snapshot roadmap.

References: [client API](docs/architecture/API_CLIENTES.md), [ALBERTO](docs/architecture/ALBERTO.md), [GLAUQUIR](docs/guides/GLAUQUIR.md), and [repository scope](docs/reference/REPOSITORY_SCOPE.md).

## v0.7-v0.8.2 - Language, subsystems, and presentation

- Incremental integration of events, cards, author time, MARY, DICE, TRAITS, and evaluation traceability.
- Declarative presentation with regions, views, tables, causal grouping, and restricted templates, without changing logical state when public data is rendered.
- Revisions to Observe/Act projections, CLI behavior, and determinism checks.

References: [narrative language](docs/architecture/NARRATIVE_LANGUAGE.md), [declarative presentation](docs/architecture/PRESENTACION_DECLARATIVA_V082.md), [DSL 1.5](docs/reference/dsl_1_5/README.md), and [presentation examples](docs/guides/workshops/README.md).
