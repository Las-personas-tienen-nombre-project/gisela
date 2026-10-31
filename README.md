# GISELA — independent narrative engine

Candidate extraction EX-001 from `las-personas-tienen-nombre(20261031-201649).zip`.

GISELA is the narrative engine; the Ren'Py demo is its consumer. This candidate does not modify the source demo.

## Development installation

```sh
python -m pip install -e .
python -m pytest -q gisela/contracts gisela/engine/tests
```

## License boundary

Source code is intended for release under Apache License 2.0, subject to a final rights and dependency audit. All stories, literary texts, original characters and narrative packages (including test examples) are **all rights reserved** and not covered by the software license. Do not upload narrative packages without checking publication permission.

## Extraction status

This is a candidate source tree, not yet a finished public repository. The demo has not yet been migrated to consume an installed package. The Ren'Py SDK was not downloaded. See `EX001_ESTADO.md`.
