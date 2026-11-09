# M2 source reconciliation — 2026-11-09

Incoming archive: GISELA 0.3.2 with DSL 1.7. The former M2 candidate was
built against 0.3.1. The patch originally failed only at `pyproject.toml`;
all other code and contract hunks were applied cleanly on 0.3.2. Package
version and 13 schema resources were then updated manually. No existing 1.6
or 1.7 JSON schemas were rewritten.

Candidate: GISELA 0.4.0rc1 / DSL 1.8. A source candidate does not prove a
published Git tag, dependency update or Ren'Py SDK acceptance. Verification
results and hashes are supplied with the handoff. User-reported green checks
for incoming 0.3.2 are evidence of the incoming baseline, not automatically
tests of this reconciled candidate.

## Verification on reconciled source

- `python -m pytest -q gisela/contracts gisela/engine/tests`: **846 passed,
  176 subtests passed, 1 skipped**, exit 0 (157.38 seconds).
- `python -m pytest -q gisela/engine/tests/test_presentation_direction_v18.py`:
  **6 passed, 19 subtests passed**, exit 0.
- `python tools/check_gisela.py --full`: **13/18** checks, exit 1. Its main
  engine/contract/library group passed **966 tests, 184 subtests, 1 skipped**.
  The five failing checks were the tooling suite's Ruff-dependent static test,
  Ruff lint, Ruff format, Radon and Bandit: these modules are not installed in
  the execution environment. This is not a green overall check.
- An attempted additional isolated tools suite exceeded its execution bound
  without a final summary and is **not counted** as passing.
- Local candidate wheel: `gisela_narrative_engine-0.4.0rc1-py3-none-any.whl`
  created with `pip wheel --no-build-isolation`, containing all **13** DSL 1.8
  schema files. No tagged Git provenance can be verified from these archives.
- Three existing demo laboratory walkthroughs (`casete`, `solo`, `radio`) ran
  against this candidate source with snapshot restore, all exit 0; these are
  historical laboratory scenarios, **not** an exhaustive product-demo witness.

**Pending:** complete official 18/18 check in the actual developer
installation, verify Git tag/source origin and run Ren'Py SDK graphical tests.
