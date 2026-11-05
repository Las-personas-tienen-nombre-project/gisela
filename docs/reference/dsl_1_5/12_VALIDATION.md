# 12 Validation and acceptance

The acceptance report lives at [VERIFICATION.md](VERIFICATION.md) and the reproducible command script is [verify_reference_examples.py](verify_reference_examples.py).

Run the following from the repository root.

```bash
PYTHONPATH=. python gisela/contracts/verify_contracts.py
PYTHONPATH=. python docs/reference/dsl_1_5/verify_reference_examples.py
PYTHONPATH=. python -m pytest -q gisela/engine/tests/test_documented_minimal_package.py gisela/engine/tests/test_npc_contests_v05.py gisela/engine/tests/test_npc_traits_v06.py gisela/engine/tests/test_actuation_public_v073.py gisela/engine/tests/test_reference_dodge_contexts.py
PYTHONPATH=. python tools/check_doc_links.py
PYTHONPATH=. python tools/check_quality.py
PYTHONPATH=. python tools/check_gisela.py --full
```

Full suite acceptance is separate from limited test selection. A timed out check is incomplete, not passed. Missing unit coverage of some schema branches must be reported rather than concealed. Do not change the game rules or public contracts merely to get this documentation to pass.
