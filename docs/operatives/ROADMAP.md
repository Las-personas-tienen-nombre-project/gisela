# Current project roadmap

This file is a current status guide, not a timeline of every previous implementation step. The previous cumulative roadmap has been preserved in [Roadmap history](ROADMAP_BEFORE_DOC_REVIEW.md). Historical closure reports and architecture decisions remain in their original locations.

## Project direction

This repository belongs to the Las personas tienen nombre visual novel demo. GISELA is being developed here temporarily as an independent general narrative engine. The engine is planned to move to its own repository later. See [Repository scope](../project/REPOSITORY_SCOPE.md).

## Implemented and tested offline

The repository contains the GISELA session executor, ALBERTO world operations, optional S.O.F.I.A. attributes, TRAITS, DICE, MARY, shared narrative conditions, and GLAUQUIR.

E2 implemented hidden declarative evaluations. E3 implemented visible and acknowledged evaluations with pending state, deterministic continuation, and restoration for package format v1.5. Older package contracts remain available.

H4.6 added El faro de niebla, an independent end to end integration adventure. H4.6b added a condensed Central Clasificadora test adaptation. Both can be played in GLAUQUIR, and both have automated test routes.

H5 implemented the Ren'Py adapter and an offline test package. The adapter tests compare GISELA sessions and saved state against direct engine execution. The real Ren'Py SDK visual acceptance and target platform packaging have not been verified here.

These are descriptions of implemented capabilities found in this repository. For the exact list of verified tests run on a particular release, use its test logs and the current `tools/check_project.py` result.

## Outstanding work

Complete graphical acceptance testing of H5 with the actual Ren'Py SDK. Validate text presentation, menu actions, keyboard input, save and load during pending evaluations, schema file distribution, and platform exports.

Review and approve the narrative structure of the Central Clasificadora adaptation. The current package is condensed for engine testing and must not be treated as the final canonical demo script.

H6 concerns the production vertical with visual and sound resources, script integration, and playtest feedback. H7 concerns full validation and deliverable readiness. These milestones are not declared complete by an offline engine test.

Plan the future repository extraction of GISELA separately. Establish dependencies, package distribution, tests, and documentation ownership before moving files.

## Start and verify

```bash
python tools/glauquir.py --package gisela/packages/h46_faro_de_niebla.package.json
python tools/glauquir.py --package gisela/packages/h46b_central_clasificadora.package.json
python tools/check_project.py
```

For a developer route, read [Quick start](../guides/QUICK_START.md), [GISELA](../../gisela/README.md), [Ren'Py](../../renpy/README.md), and the [documentation index](../README.md).

## Historical records

Implementation closure records are under `docs/operatives`. Architectural design records are under `docs/architecture`. Decisions are under `docs/decisions`. Some of these documents describe proposed or incomplete states from earlier milestones. Preserve that distinction when reading them.
