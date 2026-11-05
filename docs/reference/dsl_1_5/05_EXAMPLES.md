# 05 Complete and invalid examples

## Complete authored package

`gisela/packages/ejemplo_minimo.package.json` is the canonical small, complete JSON example for a narrative choice with two endings. `gisela/packages/h46_faro_de_niebla.package.json` is a more involved package with scenes and entities. The Tegularis packages are integration examples; not every package represents the same capability level.

To verify the small package, run these commands from the repository root.

```bash
PYTHONPATH=. python gisela/contracts/admit_package.py gisela/packages/ejemplo_minimo.package.json
PYTHONPATH=. python docs/reference/dsl_1_5/verify_reference_examples.py
```

The second command runs both options to their endings, rejects unoffered and stale actions, tests restoration, and checks two invalid mutations of the complete package. It calls only public entry points.

## Invalid package cases

The verifier modifies a copy of the complete minimal JSON package. The first case uses `manifest.format_version` equal to `1.6` and expects `UNSUPPORTED_VERSION`. The second changes a choice destination to `missing_node` and expects `UNKNOWN_NODE`. These are intentionally invalid authoring inputs and must never be advertised as working DSL examples.

## Limits

The tests do not cover all enumerated schema branches, conditional fields, or every runtime operation. The full versioned field pages remain structural reference pages until each branch is tied to a dedicated executable fixture.

## Sources

- `gisela/packages/ejemplo_minimo.package.json`
- `gisela/engine/tests/test_documented_minimal_package.py`
- `gisela/contracts/admit_package.py`
