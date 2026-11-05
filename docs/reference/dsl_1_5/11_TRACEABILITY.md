# 11 Evidence and traceability method

The schema field inventory and [existing structural traceability matrix](TRACEABILITY.md) identify the published declaration names, but do not prove complete execution. For semantic claims, use this evidence map.

| Mechanism | Contract | Semantic validator | Runtime | Executable proof |
| --- | --- | --- | --- | --- |
| Package and node entry | package, node, common | semantic_packages | runtime | test_documented_minimal_package and verify_reference_examples |
| Choice destination | common, node | semantic_expressions, semantic_packages | runtime | verify_reference_examples |
| Cards and initial state | card, initial_state | semantic_definitions | initialization | test_npc_traits_v06 |
| Conditional traits | package, card, common and TRAITS schema | semantic_traits | world_traits, traits_dice_bridge | test_npc_contests_v05, test_npc_traits_v06, test_reference_dodge_contexts |
| Visible evaluate | common, result, session | semantic_evaluations | evaluation_execution, evaluation_pending | E3 integration tests in engine/tests |
| Observe and Act | observe, act | semantic_validator | projection, action_handler | test_actuation_public_v073, verify_reference_examples |
| Persistence | session | semantic_sessions | session_restore | test_actuation_public_v073, verify_reference_examples |
| Presentation | package, observe | semantic_packages and presentation admission | presentation_views | test_release_v082e, test_release_v082f |
| Actuation | package, observe, act | semantic_actuation | actuation and actuation_session | test_actuation_public_v073 |

A passed test proves only its scenario. A published schema rule is guaranteed structurally, but any dynamic semantics require an implementation contract or reproducible execution check. All untested branches remain not established. The script intentionally uses only public admission and session APIs.
