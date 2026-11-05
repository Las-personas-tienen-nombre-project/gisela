# 06 Errors and rejection levels

## Strict JSON input

`admit_package_file` uses the strict JSON reader. Read or parsing failures are reported as `INVALID_INPUT` by the CLI. Callers that pass an already parsed dictionary to `admit_package` must themselves reject duplicate JSON object keys before constructing that dictionary.

## Structural and semantic rejection

The validator returns diagnostics with severity, code, path and message. Blocking errors cause `PackageRejected`. The reference verifier records actual `UNSUPPORTED_VERSION` and `UNKNOWN_NODE` diagnostics. An admitted package is not a guarantee that `check_supported` will accept every operation at session creation.

## Runtime rejection

`INVALID_ACTION` is used for invalid JSON Act shape, an unoffered action, disabled action, or disallowed request parameters. `STALE_PROJECTION` applies when the request session or revision does not match current state. Unsupported execution forms may produce `UNSUPPORTED_FORMAT`; invalid resolved state can produce `INVALID_STATE`. Specific operation failures may have additional codes, which should not be invented by documentation.

The execution draft is transactional. Tests verify that the bad action and stale revision cases leave the snapshot unchanged. A failed action does not authorize client-side repair of state or arbitrary retry with a fabricated action ID.

## Sources

- `gisela/contracts/admit_package.py`, `semantic_validator.py`
- `gisela/engine/action_handler.py`, `support.py`, `errors.py`
- [Executed negative tests](EXECUTION_EVIDENCE.md)
