# GISELA documentation

Start with the [project README](../README.md) for the engine and its component definitions. Code, versioned contracts, and tests determine actual behavior. This index links to explanations and working material; it does not define a separate contract.

## Write a story (authors)

Start with the [Spanish author course](workshop/es/README.md). Follow [what GISELA is](workshop/es/01_que_es_gisela.md), [use cases](workshop/es/02_casos_de_uso.md), and [installation](workshop/es/03_instalacion.md), then the nine workshops in order. If you already know what you need, use the [capability catalog](workshop/es/10_capacidades.md) or [find a DSL field by task](workshop/es/11_referencia_dsl.md). An English course translation is not yet available.

For short, standalone instructions, use [Quick start](guides/QUICK_START.md), [Create a package](guides/CREAR_PAQUETE.md), or the [GLAUQUIR client guide](guides/GLAUQUIR.md).

## Look up a rule (reference)

- [DSL 1.6 absolute time extension](reference/dsl_1_6/README.md): the new `advance_time_to` operation, guarantees and compatibility.
- [DSL 1.5 official reference](reference/dsl_1_5/README.md): normative chapters and schema field inventory, not a beginner course.
- [Errors and validation](reference/dsl_1_5/06_ERRORS.md) and [validation reference](reference/dsl_1_5/12_VALIDATION.md): diagnose rejected packages.
- [Known discrepancies](reference/dsl_1_5/DISCREPANCIES.md): documented limitations and differences.

## Develop GISELA

- [Repository scope](reference/REPOSITORY_SCOPE.md)
- [Narrative language](architecture/NARRATIVE_LANGUAGE.md) and [architecture](architecture/GISELA_Arquitectura_Consolidada_v1_5.md)
- [Client API](architecture/API_CLIENTES.md), [engine](../gisela/engine/README.md), and [contracts](../gisela/contracts/README.md)
- [ALBERTO](architecture/ALBERTO.md), [S.O.F.I.A.](architecture/SOFIA.md), [MARY](architecture/MARY.md), [TRAITS](../traits/README.md), and [DICE](../dice/README.md)
- [Verification](guides/VERIFICACION_GISELA.md)

## Project status and history

- [Roadmap](operatives/ROADMAP.md): implemented work and outstanding tasks.
- [Changelog](../CHANGELOG.md): significant changes by milestone.
- [Decisions](decisions/GISELA_ADR_001_017.md): architectural reasoning.
- [Historical archive](history/README.md): older material kept for reference.
- [Past test evidence](operatives/evidence/README.md): dated results, not proof of the current build.

The Ren'Py host is maintained in a separate repository. Narrative content may have different rights from the engine software.

- [DSL 1.7 author annotations](reference/AUTHOR_ANNOTATIONS_1_7.md): `info` syntax, RFC 6901 pointers, inspection and privacy.
- [DSL 1.8 narrative presentation direction (M2 source candidate)](reference/PRESENTATION_DIRECTION_1_8.md): typed step hints, Observe projection, safety and compatibility.

- [M2 reconciliation against GISELA 0.3.2](operatives/M2_RECONCILIATION_2026-11-09.md): source candidate verification and release blockers.
