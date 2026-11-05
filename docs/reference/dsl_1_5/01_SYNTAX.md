# 01 Syntax and admission

## Normative inputs

Use `gisela/contracts/v1_5/*.schema.json`, not the unversioned compatibility schemas. The format version is `1.5` and the Python distribution currently identifies itself as `0.1.21`. These are different versions.

A package must contain `manifest`, `cards`, `scenes`, `nodes`, `rules`, `initial_state`, and `endings`. Other root members, including `traits`, `dice_profiles`, `mary`, `actuation`, `presentation`, and `strings`, are conditional or optional according to the package schema.

The manifest has required `id`, `format_version`, `language`, and `entry`. The entry is a node or a scene. All additional required fields must be read from the nested conditional branches of the actual schema, not guessed from a flat root inventory.

## Value constraints and defaults

Names and identifiers use the declared lowercase identifier patterns and length limits. The schema rejects unknown properties where `additionalProperties` is false. `manifest.variables` declares `scope`, `id`, `type`, and `initial`, with scopes `session` or `world` and types `boolean`, `integer`, `number`, `string`. Do not assume optional fields receive a default value merely because they are absent. Distinguish schema defaults from initialization code behavior.

Use the 13 linked schema inventory pages in this directory for required status, type, explicit enum, range, maximum, and definition paths. Each structural inventory is subordinate to the actual schema and must be checked against `semantic_definitions.py`, `semantic_packages.py`, `semantic_expressions.py`, `semantic_evaluations.py` and `semantic_traits.py` for cross references and type rules.

## Admission stages

1. Read JSON with `load_json_strict` or `admit_package_file` so duplicate object keys can be rejected.
2. Validate schema and semantic references using `admit_package`.
3. Build a session with `new_session` to establish executable support.
4. Use Observe and Act to establish actual behavior.

Warnings are not blocking by default. `reject_warnings=True` rejects warnings as well. Admission is not execution. See [verified examples](EXECUTION_EVIDENCE.md), and [schema field inventory](package.md).

## Rejection examples

Changing the minimal package `manifest.format_version` to `1.6` is rejected with `UNSUPPORTED_VERSION`. Changing a choice destination to an undeclared node is rejected with `UNKNOWN_NODE`. Both results are exercised by [the executable verification script](verify_reference_examples.py).

## Sources

- `gisela/contracts/admit_package.py`
- `gisela/contracts/semantic_validator.py`
- `gisela/contracts/semantic_packages.py`
- `gisela/contracts/v1_5/package.schema.json`
- `gisela/contracts/v1_5/common.schema.json`
