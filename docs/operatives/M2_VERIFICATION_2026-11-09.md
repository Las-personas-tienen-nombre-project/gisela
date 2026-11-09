# M2 source candidate verification — 2026-11-09

**Candidate only:** Python distribution `0.4.0rc1`, DSL 1.8. The incoming
source archive declared `0.3.1` / DSL 1.7; neither the original Git history
nor its published tag is present in the supplied archive. This work does not
publish a replacement revision or claim to have updated the demo dependency.

## Scope of changes

- Add thirteen versioned v1.8 JSON schemas; preserve all preexisting schemas.
- Admit a closed, typed stage-direction object on `narrate` / `dialogue` steps;
  validate abstract IDs, reveal timing, transitions, advance policy, and sound.
- Publish **only current step** `content.presentation` to public `Observe` for
  v1.8; author-only `info` is never included.
- Keep observations read-only: stage hints neither change RNG, state, time nor
  action eligibility. An automatic advance hint cannot act without an offered
  `advance` action submitted through `Act`.
- Add a laboratory package, dedicated noninterference tests, and the
  [contract reference](../reference/PRESENTATION_DIRECTION_1_8.md).
- Do not modify the approved production script or author an unsolicited scene.

## Observed verification

| Command / gate | Observed result | Interpretation |
| --- | --- | --- |
| `python -m pytest -q gisela/contracts gisela/engine/tests` | 846 passed, 1 skipped, 176 subtests; exit 0 | Completed broad engine/contract suite |
| `python tools/check_gisela.py --full` — engine/contract group | 966 passed, 1 skipped, 184 subtests; exit 0 | Completed official principal group |
| `python tools/check_gisela.py --full` — all 18 gates | 13/18, exit 1 | **Not green** in this environment |
| First tools group in official full run | 71 passed, 2 failed, 90 subtests | One Ruff executable absence; one replay environment-fingerprint mismatch |
| Replay failure rerun in isolation | 1 passed; exit 0 | Original mismatch not reproduced |
| Stable tools group, excluding Ruff-dependent test | 72 passed, 1 deselected, 90 subtests; exit 0 | Non-Ruff tools tests passed |
| `python tools/check_quality.py` | exit 0 | Structural constraints satisfied |
| `python tools/check_doc_links.py` | exit 0 | Local documentation links resolved |
| M2-specific tests | 6 passed, 19 subtests | Step-only, RNG, save/restore and compatibility witnesses |

The four remaining static-tool gates (Ruff lint, Ruff format, Radon, Bandit)
failed because the commands are not installed in this execution environment.
The original all-tools group failed twice: Ruff was unavailable, and the
Tegularis replay fingerprint changed between two operations. Rerunning the
Tegularis case alone and then the entire stable tools group passed, so the
replay failure is **not reproduced**; the original full-run failure remains
recorded rather than rewritten as a pass.

The full-suite skip requires an external productive package not installed in
this engine-only environment. These results do not constitute a released
version or full acceptance of M2.

## Determinism and artifacts

Tests use explicit 64-character seeds: `1` (observation/restore), `c`
(direction-vs-control parity), `9` (auto hint cannot advance), and `2`
(legacy compatibility). The laboratory sample's admission digest is
`0325f4b52c53fa92129b2709ee60e50a2538d4d6bd6af1c406781723e934f807`.
A locally built candidate wheel includes all thirteen v1.8 schemas and the
example package. Distribution integrity is tracked separately in the
SHA-256 inventory shipped with the deliverables.

## Remaining acceptance

1. Install Ruff, Radon and Bandit in a reproducible developer environment;
   run the full official guard to an unambiguous **18/18** summary.
2. Confirm the built candidate wheel against the actual Git commit/tag and
   package provenance. No original Git tag can be reconstructed from this tar.
3. Pin only an accepted version in the demo and repeat its official guards.
4. Perform SDK-based Ren'Py visual tests for text reveal, transitions,
   optional registered audio, click/Enter/Space, save/load and both endings.
5. Keep M3 narrative wording and any remaining author decisions separate.
