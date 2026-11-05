# 04 Execution and transaction verification

## Public execution boundary

The public `GiselaSession` provides `new_session`, `restore_session`, `observe`, `act`, and `export`. Admission does not create a session. A session starts from a fixed admitted package and a seed. `observe` returns the current public projection. `act` checks the request schema, session identity, revision, and currently offered enabled action before attempting execution.

An invalid action ID returns `INVALID_ACTION`. An old revision or different session returns `STALE_PROJECTION`. Those rejected requests do not change the confirmed snapshot. An accepted action commits a new revision only after validation. In the tested minimal package, the choice `abrir` produces ending `adentro`, while `seguir` produces `afuera`.

The results are produced by [verify_reference_examples.py](verify_reference_examples.py) and logged in [EXECUTION_EVIDENCE.md](EXECUTION_EVIDENCE.md). The source JSON is the complete executable package `gisela/packages/ejemplo_minimo.package.json`. This example has no actuation, traits or presentation views and does not prove those subsystems.

## Host authority

A trusted local host may call session APIs. External clients should use `ExecutionGateway` with trusted principal capabilities. An offered `action_id` is an execution token from the current Observe projection, not an arbitrary author operation. A gateway `command_id` provides idempotency for the bound external client and is not part of the versioned Act JSON.

## Sources

- `gisela/engine/runtime.py`, `action_handler.py`, `authorized_gateway.py`
- `gisela/engine/tests/test_documented_minimal_package.py`, `test_actuation_public_v073.py`
