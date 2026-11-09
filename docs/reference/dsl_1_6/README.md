# GISELA DSL 1.6 — absolute clock targets

DSL 1.6 extends DSL 1.5 without changing the behavior of existing `advance_time` packages. The reference for all otherwise unchanged features is [DSL 1.5](../dsl_1_5/README.md). Implemented contracts live in `gisela/contracts/v1_6`; admission, execution, and persistence rules are authoritative.

## New operation

```json
{"op": "advance_time_to", "at": "1998-07-25T03:00:00-04:00"}
```

`at` is a concrete ISO 8601 timestamp, including `:00` seconds and an explicit numeric UTC offset. No expressions, relative dates, local timezone names, or implicit daylight-saving transitions are accepted. The target must be a real calendar date. The operation is rejected when the destination is earlier than or equal to the current clock, has a different UTC offset, or is not an integral number of minutes ahead. A failed action must not commit any earlier effects in its transaction.

A successful operation advances the clock directly, returning the same single `clock_advanced` event as `advance_time`. It does not iterate through intermediate minutes, draw RNG, or invent missed events. Stories remain responsible for explicit overdue-recovery actions. The condition guarding an authoring action should normally include both `world_time >= start` and `world_time < target`, plus any narrative prerequisites. Because DSL 1.6 does not expose a seconds-modulo predicate, stories must preserve a minute-aligned clock if exact minute-level availability is required.

## Compatibility and limitations

- Existing 1.2–1.5 packages remain supported by the 1.6-capable engine; the new operation is **not** accepted in a 1.5 package.
- Sessions and package digests are versioned. A new package cannot restore snapshots saved against an old package digest, even when narrative results are equivalent. Use the original package and compatible runtime to read historical saves. Do not rewrite digests to bypass validation.
- A different action ID is observable in action lists, fact provenance, history, debugging and any integration that stores action identifiers. The migration is equivalent in game-state effects after normalizing those explicitly changed origins, **not** byte-for-byte identical persistence.
- The current demo keeps a constant numeric UTC offset for its one night. Cross-offset travel is intentionally not part of this operation.
- `0.1.24` is the candidate engine version in these local sources; a corresponding remote Git tag and Ren'Py SDK rebuild must be verified before declaring a published release.

## Verification

`gisela/engine/tests/test_absolute_time_v16.py` verifies admission rejection, strict time ordering, offset consistency, minute alignment, atomic rollback, RNG state, legacy 1.5 admission and restore, and parity with the relative operator. Run `python tools/check_gisela.py --full` for the engine regression suite.
