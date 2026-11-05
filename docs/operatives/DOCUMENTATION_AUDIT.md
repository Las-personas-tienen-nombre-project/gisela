# Documentation audit and reorganization record

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](REVISION_DOCUMENTAL_2026_11_04.md).

## Scope

This review used the repository source tree available at the time. It examined the main README, component README files, authoring guides, implementation modules, versioned contracts, architecture records, ADRs, the roadmap, and milestone reports through H5.

The purpose was to give the demo a clear main README and give GISELA and its major components detailed independent READMEs. The general engine remains in the demo repository temporarily. The future split is documented but was not performed.

## Main findings

The old root README mixed project introduction, executable examples, an earlier implementation inventory, architecture explanations, and milestone notes. It described the Ren'Py adapter as absent even though the H5 bridge files and offline tests were present.

The GISELA README and several authoring guides had grown by adding sections for each completed milestone. The DICE README still said visible evaluations were not implemented, despite E3 runtime and tests. The old roadmap mixed completed milestones with older outstanding tasks without a simple current status summary.

Several component READMEs were too short to describe their supported API and responsibility boundaries. The documentation did not clearly separate the temporary engine home from the ownership of the demo repository.

## Changes

The root README now describes the visual novel demo. The GISELA README describes the engine, with separate READMEs for the executor, contracts, ALBERTO, S.O.F.I.A., TRAITS, DICE, MARY, shared conditions, GLAUQUIR, and Ren'Py.

A naming reference records the official technical expansions and boundaries. The documentation index routes readers by task. The quick start teaches the text client before deeper API material. Actively maintained guide entry points use plain English and preserve the spelling of commands and JSON fields.

A new current roadmap separates offline implementation from graphical acceptance and production. The previous roadmap was preserved under a different name in the same directory so its relative links retain their original location. The old Spanish language policy was also archived and replaced by an English pointer to the current policy.

Historical architecture and decision records were not silently translated or modified. Their original status and language are preserved, including older proposals that no longer describe the complete current implementation. The design trace connects major decisions with current code and tests.

## Evidence and verification

The documentation checker validates the main entry pages for existence, ASCII text, main headings, and local Markdown links. The existing quality checker validates maintained file limits. The SHA256 manifest includes the new files. The package admission and independent code examples were exercised against the actual current modules.

The complete project verifier is `python tools/check_project.py`. Its own recorded result must be checked after applying this documentation change. Tests of the Ren'Py adapter are offline and do not replace graphical acceptance through the real SDK.

## Known remaining work

Historical ADRs, architecture reports, older milestone records, and editorial source material remain in their original language. A fully English historical archive is a separate translation and review task. Changing these documents without preserving decisions and status would reduce traceability.

The future engine repository extraction, graphical acceptance of H5, and final narrative and audiovisual production remain separate project milestones. No engine runtime rules or schemas were changed during this documentation reorganization.
