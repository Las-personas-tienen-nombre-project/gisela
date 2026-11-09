# Author annotations — candidate DSL 1.7 contract (M1)

Status: implementation specification, 2026-11-09. This is additive to DSL 1.6;
1.6 and earlier schemas are not changed. This document does not imply a tagged
GISELA v0.3.0 release.

## Syntax and ownership

An annotation is an inert object with exactly `audience` and `text`:

```json
{"audience":"info","text":{"text":"Editorial context, never player text."}}
```

`info` text may be either a nonempty plain string (maximum 8192 Unicode
characters) or the existing `localized_text` form (`{"text":"..."}` or
`{"text_key":"..."}`). Local `glauquir` annotations retain their original
`localized_text` contract, rendering and audience. No purpose categories are
required. `info` is not a secrecy boundary: distributing a JSON package also
distributes its notes.

Existing local `annotations` arrays remain usable in DSL 1.7 at the same
schema-defined owners (node, step, scene and action), with the `info` audience
added. Strict predicate, value, effect and other objects are NOT extended with
arbitrary fields. The root object has a new, optional `author_annotations`
array, whose entries have exactly `target` and `annotations`:

```json
{
  "author_annotations": [
    {"target":"", "annotations":[{"audience":"info","text":"Whole package"}]},
    {"target":"/nodes/0/steps/0/text/text",
     "annotations":[{"audience":"info","text":{"text":"Source paragraph"}}]},
    {"target":"/rules/0/effects/0/value/literal",
     "annotations":[{"audience":"info","text":"A primitive value"}]}
  ]
}
```

`author_annotations` is a **root-only** field. `target` uses RFC 6901 JSON
Pointer over the **final compiled package**, with empty string for the root;
`~1` escapes `/`, `~0` escapes `~`. Array indices use canonical decimal
notation (`0`, `1`, ...), without leading zeroes or `-`. Object member
lookup is exact and case-sensitive. Pointers must resolve in the final
admitted JSON, can refer to object, array or any primitive (including null),
and may not enter either `author_annotations` or any local `annotations`
metadata subtree. A pointer is unique within the root addressed list;
multiple notes on one target belong in its `annotations` array. Missing,
malformed, duplicate or self-referential addresses are admission errors.

## Limits, order, compilation

At most 512 addressed entries; 32 notes per local/addressed annotation array;
4096 annotation records and 1 MiB cumulative `info` text encoded as UTF-8;
8192 characters per `info` text literal; at most 2048 characters and 64
segments per pointer. Malformed escapes, out-of-range arrays, noncanonical
indices, and metadata cycles are rejected before session startup.

Inspection order is deterministic: local notes in canonical depth-first JSON key
order (local annotation array order), then addressed entries in declared
array order (and each entry's annotation order). Consumers should rely on
that documented ordering, not on arbitrary dictionary re-sorting. Inspectors
return `target`, `audience`, `text` (the full original string or localization
object), `source` (`local`/`addressed`), and `order`. Source text remains
unaltered; localization lookup remains a separate concern. Explicit inspection
is only available on an admitted package through the author-facing API
`inspect_author_annotations(admitted)`, never through normal `Observe`.

Generators MUST create/validate pointers against the final emitted package.
Reordering/rewriting any array after pointer construction requires remapping
its addressed targets and re-admitting the result. Missing targets are errors,
not silently dropped. Canonical serialization preserves metadata; changing
metadata changes the package digest and therefore invalidates old save/digest
compatibility even when narrative behavior remains identical. Saved session
snapshots do not contain author annotations. Untrusted note text must be
rendered as text, not interpreted as markup or executable code.

## Noninterference and clients

Author notes must not alter conditions, effects, RNG, clocks, DICE, outcome
selection, history, public observations, available actions, or endings.
`glauquir` remains the only note audience eligible for its legacy normal
client annotation projection. Normal Ren'Py and GLAUQUIR play must not call
this inspector or display `info`; developers and editors may explicitly call
it and can therefore inspect notes on unreachable branches. No Python or
Ren'Py expression is admitted as code within annotations.

For a string whose key contains `/` or `~`, a valid address might be
`/strings/my~1key~0name`; this is illustrative and does not relax the
underlying schema requirements for such keys.
