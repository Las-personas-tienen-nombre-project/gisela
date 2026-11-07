# GISELA DSL 1.5 official reference

This index describes the public contracts in the supplied repository. It is not a beginner tutorial.

## Authority

Public versioned schemas and semantic admission are the first source for authoring syntax. Public execution and repeatable tests determine observed behavior. Documentation and examples do not override these sources. A schema permits structure but does not by itself guarantee execution.

## Source inventory

- Versioned contracts are in `gisela/contracts/v1_5`. Earlier contract versions remain for compatibility.
- Semantic admission is in `gisela/contracts/admit_package.py` and `semantic_validator.py`, with dedicated semantic modules.
- Public engine code and tests are in `gisela/engine` and `gisela/engine/tests`.
- Productive packages are in `gisela/packages`, including Tegularis and Faro de Niebla.
- Existing architecture is in `docs/architecture`.
- Current guides are in `docs/guides`. Earlier teaching material is linked from `docs/history/README.md`; the Tegularis workshop stays at its original path for executable exercises.
- Historical changes are summarized in `CHANGELOG.md`; preserved execution evidence is in `docs/operatives/evidence`, and retired reports are recoverable through Git.

## Reference chapters

- [Syntax](01_SYNTAX.md)
- [Semantics](02_SEMANTICS.md)
- [Relationships](03_RELATIONSHIPS.md)
- [Execution](04_EXECUTION.md)
- [Examples](05_EXAMPLES.md)
- [Errors](06_ERRORS.md)
- [Determinism](07_DETERMINISM.md)
- [Observe Act](08_OBSERVE_ACT.md)
- [Presentation](09_PRESENTATION.md)
- [Tegularis](10_TEGULARIS.md)
- [Traceability](11_TRACEABILITY.md)
- [Validation](12_VALIDATION.md)

## Public schema field inventory

Each linked page records fields from a v1.5 JSON schema, including required status, types and explicit constraints. Nested field paths reflect JSON structure. A missing default means that the schema does not declare one. Some requirements are conditional inside oneOf or other schema branches and cannot be inferred from the root field list.

The tables are a structural inventory, not a claim that every accepted declaration executes.
- [act](act.md)
- [card](card.md)
- [common](common.md)
- [initial_state](initial_state.md)
- [node](node.md)
- [observe](observe.md)
- [package](package.md)
- [result](result.md)
- [rule](rule.md)
- [scene](scene.md)
- [scoresheet](scoresheet.md)
- [session](session.md)
- [world_snapshot](world_snapshot.md)

## Semantic and runtime references

- [Narrative language](../../architecture/NARRATIVE_LANGUAGE.md)
- [Contract admission](../../../gisela/contracts/README.md)
- [Client Observe and Act API](../../architecture/API_CLIENTES.md)
- [Presentation views](../../architecture/PRESENTACION_DECLARATIVA_V082.md)
- [Visible evaluations](../../architecture/E3_EVALUACIONES_VISIBLES.md)
- [Localization and author notes](../../guides/LOCALIZACION_Y_ANOTACIONES.md)
- [Determinism](../../determinism/DIGEST_CANONICO.md)
- [Engine execution](../../../gisela/engine/README.md)
- [Tegularis integration](../../../gisela/packages/tegularis_the_son_of_the_volcan/README.md)

## Audits

- [Traceability matrix](TRACEABILITY.md)
- [Discrepancies and limits](DISCREPANCIES.md)
- [Verification report](VERIFICATION.md)
