# DSL 1.8 — Narrative presentation direction (M2 candidate)

**Current source status:** DSL 1.8 is included in the supplied GISELA
0.4.1 source and is pinned by the production demo as `v0.4.1`. Its original
0.4.0rc1 implementation and 0.3.2 reconciliation were development milestones,
not the current source versions. The source archive contains no `.git` history
or attached SDK session evidence; this document describes the implemented
contract and does not assert graphical acceptance in Ren'Py. The 13 schemas
are under `gisela/contracts/v1_8/`; DSL 1.6 and 1.7 schemas remain available.

## Scope and authority

`nodes[].steps[]` with `op: "narrate"` or `op: "dialogue"` may carry an optional
`presentation` object. This is *stage direction*, not narrative text or a
world operation. It cannot change a clock, action offering, character knowledge,
DICE, RNG, effects, or ending. It must never be used as a predicate.

The independent, existing **package-level** `presentation` object still
controls public layouts/tables and is not changed by this feature. The scene
and actor presentation properties from prior versions also keep their meanings.
`audience: "info"` metadata remains private-by-default author data and is
never a source of runtime stage direction.

## Admitted fields

The object is closed (`additionalProperties: false`), nonempty and checked at
package admission. Every field is optional; omitted fields request normal
client defaults. An unknown resource ID must produce a safe visual fallback.

| Field | Value and budget | Meaning |
| --- | --- | --- |
| `color` | `default`, `red`, `yellow`, `green`, `cyan`, `blue`, `magenta`, `white` | Existing semantic colour hint |
| `box` | `narration` or `dialogue` | Requested text-box mode |
| `portrait` | Resource ID (`[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*`, max 96 chars) | Abstract portrait asset |
| `expression` | Same ID grammar | Abstract expression variant of the portrait |
| `background` | Same ID grammar | Abstract background asset |
| `reveal` | `{"mode":"instant"}` or `{"mode":"typewriter","characters_per_second":N}` | Reveal strategy; `N` is integer 1–120 |
| `transition` | `{"kind":"none"|"fade"|"dissolve", "duration_ms":N}` | Safe transition. Optional integer `N` is 0–3000; default host duration is implementation-defined |
| `advance` | `{"mode":"confirm"}` or `{"mode":"auto","delay_ms":N}` | Manual confirmation or client-scheduled advance; auto delay is integer 250–10000 ms |
| `sound` | `{"cue":ID,"channel":"sfx"|"voice"|"ambient"}` | Optional cue and channel; default channel is client-defined |

`expression` without a registered `portrait` is permitted but has no visible
portrait effect. Identifiers are not filenames, Python expressions, Ren'Py
statements, arbitrary URLs, or filesystem paths. The engine never executes or
resolves assets. `transition` and `sound` should be ignored by a client when
the relevant asset or visual capability is unavailable.

A valid step excerpt is:

```json
{
  "id": "araya_recibe",
  "op": "narrate",
  "text": {"text": "A las 18:45 llegué a la Central Clasificadora."},
  "presentation": {
    "box": "narration",
    "background": "porteria_evening",
    "reveal": {"mode": "typewriter", "characters_per_second": 32},
    "transition": {"kind": "fade", "duration_ms": 350},
    "advance": {"mode": "confirm"},
    "sound": {"cue": "clock_click", "channel": "sfx"}
  }
}
```

This excerpt illustrates syntax only; it does **not** amend the approved demo
script. A complete executable example based on an existing engine laboratory
is at `gisela/packages/author_presentation_v18_example.package.json`.

## Public Observe projection

DSL 1.8 `Observe` includes `"dsl_version": "1.8"` at its top level. While
and only while the current `content.kind` is `narrate` or `dialogue`, an
admitted *present* step-level `presentation` is copied under
`content.presentation`:

```json
{
  "dsl_version": "1.8",
  "content": {
    "kind": "dialogue",
    "speaker": "araya",
    "text": "Texto que está visible ahora.",
    "presentation": {"portrait": "araya_placeholder", "box": "dialogue"}
  }
}
```

This JSON fragment omits the other required observation fields for brevity.
There is **no** future-step array or prefetch projection. A choice, a pending
DICE evaluation, an exploration, or an ending does not acquire step direction
from a different node. The client never receives `info` through `Observe`.

`Observe` is read-only. A visible automatic-advance hint does not itself
execute an action. Only a subsequently submitted, currently offered `advance`
request through `Act`, with the correct revision, can move the cursor. A
client must not synthesize a hidden/unoffered action. Re-observation and
local rendering timers do not advance the engine clock or consume RNG.

## Backward compatibility and packaging

- DSL 1.6 and 1.7 still admit their historical open `presentation` objects;
  their existing `Observe` content shape is unchanged. Their step hints are
  **not** forwarded using the new DSL 1.8 projection unless the authored
  package is deliberately upgraded and validated as DSL 1.8.
- DSL 1.8 has a new manifest `format_version` and session `schema_version`;
  older save digests are not automatically migrated.
- The candidate wheel must include all 13 `v1_8` schema files and the sample.
  Check version and install provenance before pinning a new demo dependency.
- GLAUQUIR is text-first and may ignore these hints. Its normal player
  observation and `glauquir` annotations do not gain access to `info`.
- In the Ren'Py bridge, a *trusted client-side* resource table maps abstract
  IDs to resources. An unknown ID falls back to text/placeholder or silence.
  Rendering must escape Ren'Py text tags and disable substitution. Confirm and
  auto advance must both ultimately use only GISELA's offered `Act` action.

## Tests and acceptance boundaries

`gisela/engine/tests/test_presentation_direction_v18.py` covers typed
validation, invalid fields and paths, current-step-only projection, read-only
re-observation, snapshot restore, 1.6/1.7 compatibility, and replay parity
with and without stage direction. A client adapter test suite is maintained
in the demo repository. Passing these offline tests is **not** a graphical
Ren'Py SDK acceptance, and it is not evidence of M2 completion by itself.
