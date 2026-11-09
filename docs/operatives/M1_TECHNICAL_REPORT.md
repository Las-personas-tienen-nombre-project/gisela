# M1 technical report — GISELA 0.3.0rc1 source candidate

Date: 2026-11-09. **Candidate only; M1 not accepted yet.**

## Input and design

Input archive SHA-256: `5a8e70a4270571d82ac13b97227e0aced9edc2e4fb4a3ae19a52a2f5635244e9`.
The supplied tree contained GISELA 0.2.0 and DSL 1.6. No `.git` directory
was present; the source commit/tag is not independently verifiable here.
The demo's approved roadmap was present, but the engine's active roadmap
was older. Historic patches were not reused.

The normative M1 design is [Author annotations 1.7](../reference/AUTHOR_ANNOTATIONS_1_7.md).
A new versioned schema directory retains 13 files; the 1.6 schemas are
unchanged. Local `info` notes coexist with `glauquir`; an optional root
`author_annotations` array adds RFC 6901 addressed notes for any target,
including deeply nested predicates, effects, DICE inputs and scalars.
Admission validates pointers, duplicates, self-targets and budgets. An
explicit `inspect_author_annotations(AdmittedPackage)` API exposes both
local and addressed notes to author tools, never normal player `Observe`.

## Verification

- `python -m pytest -q gisela/engine/tests/test_author_annotations_v17.py`:
  **11 passed, 12 subtests passed**.
- `python -m pytest -q gisela/engine/tests/test_absolute_time_v16.py
  gisela/engine/tests/test_localization_annotations_v15.py
  gisela/engine/tests/test_e3_visible.py`: **43 passed, 17 subtests passed**.
- DICE reproducibility: session `dice`, seed `e` repeated 64 times,
  `probar_radio` => roll `[2]`, outcome `distorsion`, RNG counter `1`;
  the confirmed continuation is identical with/without `info`.
- Roll-operation reproducibility: session `die`, seed `a` repeated 64 times,
  three roll actions and their state/history were compared.
- Navigation equivalence: session `m1`, seed `4` repeated 64 times,
  25 deterministic first-offered-action steps or until no offer/ending.
- `python tools/check_quality.py`: **exit 0**.
- `python tools/check_doc_links.py`: **exit 0**.
- `python -m pip wheel --no-deps --no-build-isolation .`: **exit 0**, local
  wheel `gisela_narrative_engine-0.3.0rc1-py3-none-any.whl`; checked that the
  wheel contains all 13 v1.7 schema files and its annotated example package.
- `python tools/check_gisela.py --full`: **INCOMPLETE**. The first large
  pytest battery reached 83%, then the external 300-second process timeout
  expired, leaving no final success or failure summary.
- `ruff`, `radon` and `bandit`: **NOT EXECUTED**: absent from the environment;
  package installation was blocked by DNS/network failure.

The test sample
`gisela/packages/author_annotations_v17_example.package.json` was admitted
and its 8 notes inspected. Full GLAUQUIR+Ren'Py acceptance, the complete
engine regression, exact Git tag provenance, and demo pinning are pending.
Do not mistake these partial checks for a green 18/18 run.

## Version and persistence

The source advertises `0.3.0rc1`; there is no claimed v0.3.0 release.
The admitted package hash includes all annotation data. A modified package
digest cannot restore preexisting saves without an explicitly authorized
migration. Observations and session snapshots are not metadata channels.

## Remaining work

1. Install pinned static tools and run the official 18-check `--full` suite
   to completion, separately distinguishing code failures from infrastructure.
2. Re-run full M1 noninterference scenarios and wheel/source install checks.
3. Publish and verify a release Git revision before changing the demo pin.
4. Integrate and remap annotations in the compiled demo package, prove no
   narrative or logical drift, and update the distribution manifest.
5. Start M2 only after all M1 acceptance gates are closed.
