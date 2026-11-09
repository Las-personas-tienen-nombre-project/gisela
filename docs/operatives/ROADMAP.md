# Current project roadmap

This file is a current status guide, not a timeline of every previous implementation step. The previous cumulative roadmap has been preserved in [Roadmap history](../../CHANGELOG.md). Most completed implementation reports were retired during D2 and are recoverable through Git. Preserved evidence and architectural decisions remain available through the links below.

## 2026-11-09 active contract work: M2 reconciled source candidate

The latest supplied repositories declare GISELA **0.3.2 / DSL 1.7** and a
production demo dependency pinned to Git tag `v0.3.2`. The user reports green
checks for those source revisions. The archives do not include `.git` metadata,
so neither tag provenance nor their external test logs can be independently
recovered here.

The **0.4.0rc1 / DSL 1.8** M2 source candidate has been rebased onto the
0.3.2 code without changing the existing DSL 1.6/1.7 schemas or the demo's
published dependency. M2 adds validated current-step presentation hints and an
`Observe` projection; see [stage direction](../reference/PRESENTATION_DIRECTION_1_8.md).
The original M2 report covers the earlier 0.3.1 candidate and must not be
misread as verification of this reconciled tree. The reconciliation report
records fresh evidence. Visual acceptance in a real Ren'Py SDK and release
provenance remain pending.

The productive demo is still DSL 1.6 and its narrative text is not rewritten.
M3 textual source comparison may proceed as an audit; any authorial wording
change requires separate approval.

## Project direction

GISELA now lives in its own repository. The narrative demo and the Ren'Py host are separate integration targets, not prerequisites for running the engine. See [Repository scope](../reference/REPOSITORY_SCOPE.md).

## Implemented and tested offline

The repository contains the GISELA session executor, ALBERTO world operations, optional S.O.F.I.A. attributes, TRAITS, DICE, MARY, shared narrative conditions, and GLAUQUIR.

E2 implemented hidden declarative evaluations. E3 implemented visible and acknowledged evaluations with pending state, deterministic continuation, and restoration for package format v1.5. Older package contracts remain available.

H4.6 added El faro de niebla, an independent end to end integration adventure. H4.6b added a condensed Central Clasificadora test adaptation. Both can be played in GLAUQUIR, and both have automated test routes.

GLAUQUIR now filters unavailable actions in normal play, groups declared scene roles, and supports semantic ANSI color. A separate privileged diagnostic can show directed disposition; it does not add private relationship data to Observe. See the [GLAUQUIR guide](../guides/GLAUQUIR.md) for the exact command and color contract.

The current CLI also labels available actions with letters and accepts them as shortcuts. Interactive terminals with Python `readline` support command recall and cursor movement; this input history is separate from the engine's narrative history.

DSL 1.5 also supports author-defined presentation regions and named views: public
tables, causal grouping, restricted templates, and visual roles. These additions
project public data without changing logical state or random outcomes. See the [presentation examples](../history/workshops/presentacion/README.md). The former
[nine-unit Tegularis workshop](../history/workshops/autoria_dsl_15/README.md) remains
available as legacy teaching material with executable laboratories. The [Spanish author course](../workshop/es/README.md) now includes three introductory chapters, nine executable workshops, a [capability catalog](../workshop/es/10_capacidades.md), and a [DSL lookup guide](../workshop/es/11_referencia_dsl.md). A final editorial review and English translation remain outstanding.

H5 implemented a Ren'Py adapter in the source demo repository (not included here) and an offline test package. The adapter tests compare GISELA sessions and saved state against direct engine execution. The real Ren'Py SDK visual acceptance and target platform packaging have not been verified here.

These describe capabilities implemented across the engine and its original demo; Ren'Py files are not included here. For the exact list of verified tests run on a particular release, use its test logs and the tests executed in this repository.

## Outstanding work

Complete graphical acceptance testing of H5 with the actual Ren'Py SDK. Validate text presentation, menu actions, keyboard input, save and load during pending evaluations, schema file distribution, and platform exports.

Review and approve the narrative structure of the Central Clasificadora adaptation. The current package is condensed for engine testing and must not be treated as the final canonical demo script.

H6 concerns the production vertical with visual and sound resources, script integration, and playtest feedback. H7 concerns full validation and deliverable readiness. These milestones are not declared complete by an offline engine test.

Repository extraction is complete. Future work may verify standalone package distribution and external client integration without bringing demo-only files into the engine repository.

## Start and verify

```bash
python tools/glauquir.py --package gisela/packages/h46_faro_de_niebla.package.json
python tools/glauquir.py --package gisela/packages/h46b_central_clasificadora.package.json
python tools/check_gisela.py
python tools/check_gisela.py --full
```

For a developer route, read [Quick start](../guides/QUICK_START.md), [GLAUQUIR](../guides/GLAUQUIR.md), [GISELA](../../gisela/README.md), [Ren'Py integration status](../../CHANGELOG.md), and the [documentation index](../README.md).

## Documentation work

The Spanish-first [author course](../workshop/es/README.md) is drafted through its reference guide. The current documentation task is editorial review, navigation consistency, and verification; English translation remains outstanding. Older author manuals and legacy workshops have been moved to the [historical archive](../history/README.md), with their verified tools and integrity evidence preserved. See the [documentation index](../README.md) for entry points. Workshop 08 uses the separate GLAUQUIR `--actuation` laboratory, not the normal narrative flow.

## Historical records

Completed milestones and document retirements are summarized in the [changelog](../../CHANGELOG.md); retired reports remain recoverable through Git. Preserved execution logs are indexed in [evidence](evidence/README.md), and architectural decisions are in [decisions](../decisions/GISELA_ADR_001_017.md). Documents under [architecture](../architecture/) may describe proposals or historical compatibility boundaries; their titles alone do not establish current implementation.
