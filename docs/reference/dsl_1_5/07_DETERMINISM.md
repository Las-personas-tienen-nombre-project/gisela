# 07 Determinism, saving and restoration

## Package identity

The package canonical encoder defines a digest used to bind a session to the admitted definitions. Restoring with a changed package requires an explicit compatibility or migration policy. The public export is a private session snapshot, not the Observe result.

## RNG

The specified generator profile is `sha256_counter_v1`. Its state has `algorithm`, a 64 digit lowercase hexadecimal seed representing 32 bytes, and a nonnegative counter. The generator hashes a fixed domain prefix, the seed bytes and a big endian 64 bit counter. Uniform integer sampling uses rejection sampling instead of an uncorrected modulo operation. Seed text conversion is a host responsibility; it has no implicit universal format.

Declared ordered `roll` operations use their author order. Within a reaction round, the documented ordering for relevant rules is lexicographic `rule.id`, preserving the order of each rule's effects. A failed draft does not advance confirmed RNG. A pending visible evaluation reuses fixed dice on continuation.

## Public tests

The reference verifier checks that two sessions with equal package, seed and initial parameters have equal initial snapshots, and that a restored session reproduces the same projection and next action. The existing actuation public tests exercise a longer restore continuation. Those checks cover tested paths, not an unconditional promise that different future engine versions produce bit identical sessions.

## Sources

- `docs/determinism/RNG_SHA256_CONTADOR.md`, `DIGEST_CANONICO.md`
- `gisela/contracts/rng.py`, `canonical.py`
- `gisela/engine/session_restore.py`, `evaluation_pending.py`
- `gisela/engine/tests/test_actuation_public_v073.py`
