# 10 Tegularis integration and dodge

## Production declarations

The Tegularis v0.7.2 ending package is `gisela/packages/tegularis_the_son_of_the_volcan/08_desenlaces_v072.package.json`. The source declares `dodge` as a TRAITS definition with an actor role requirement of `defender`, tag requirement of `evasion`, and `bonus` contribution of `2`. Character card definitions and effective runtime sources must not be conflated.

The associated `dodge_parnecio` skill is a separate skill card and an initial skill instance. A passive trait source does not automatically create a playable Dodge action. Rejection of an unauthorized `play_dodge_parnecio_01` action is covered by `test_npc_traits_v06.py`.

## Context positive and negative

A contribution is conditional on the contest context role and tags. The positive executable proof is `test_npc_contests_v05.py::test_dodge_contributes_to_contest_when_context_matches`. A source-derived trait bonus of `2` in an evasion defender context is tested in `test_npc_traits_v06.py::test_admission_and_passive_source_projection`. A new public execution test also checks both negative contexts. `test_reference_dodge_contexts.py` confirms defender plus evasion gives 2, defender plus hit gives 0, and actor plus evasion gives 0.

Tegularis also exercises actuation, automatic actor decisions, skill cards, resources, contests and event traces. The source defines those features but documentation should only elevate tested branches to verified status. Tests of one contest do not prove the balance or every NPC choice sequence.

## Sources

- `gisela/packages/tegularis_the_son_of_the_volcan/08_desenlaces_v072.package.json`
- `gisela/engine/tests/test_npc_contests_v05.py`, `test_npc_traits_v06.py`, `test_actuation_public_v073.py`, `test_reference_dodge_contexts.py`
- `gisela/engine/traits_dice_bridge.py`, `world_traits.py`
