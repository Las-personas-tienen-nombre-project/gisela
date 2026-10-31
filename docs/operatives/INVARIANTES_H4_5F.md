# H4.5f. Registro de invariantes y pruebas ancladas

Los nombres de las pruebas corresponden a `gisela/engine/tests/test_h45f_scene.py`. Los tests de H2 a H4.5e siguen vigentes. Cada invariante tiene una comprobación negativa o positiva reproducible; se conservan las limitaciones de su alcance.

| Invariante | Test |
| --- | --- |
| Los lugares asociados a escenas deben existir en ALBERTO. | `H45F1Location.test_unknown_scene_location_rejected_by_admission` |
| `scene.location` no admite referencias sin ligadura. | `H45F1Location.test_dynamic_scene_location_rejected` |
| El protagonista debe ocupar el lugar de la escena física de entrada. | `H45F1Location.test_initial_scene_and_player_location_must_match` |
| No se restaura una escena física incompatible con su mundo guardado. | `H45F1Location.test_invalid_restore_is_rejected_before_observe` |
| Cambiar solamente la escena física a otro lugar revierte la transacción. | `H45F1Location.test_set_scene_without_movement_rolls_back_atomically` |
| Movimiento y transición coordinados se confirman y restauran. | `H45F1Location.test_coordinated_move_and_scene_survive_restore` |
| Una escena sin lugar conserva la visibilidad narrativa declarada. | `H45F1Location.test_scene_without_place_uses_declarative_visibility` |
| Un actor ausente deja de publicarse y de aportar una carta conocida. | `H45F2Presence.test_departed_actor_disappears_from_actors_and_cards` |
| Un objeto propio puede mostrarse; la propiedad ajena no se revela automáticamente. | `H45F2Presence.test_owned_object_is_visible_but_foreign_inventory_is_not` |
| Transferir un objeto oculta sus acciones y revoca su ficha; un ID anterior no se recicla. | `H45F2Presence.test_transfer_hides_object_actions_and_read_public` |
| Una lista de actores no admite duplicados literales. | `H45F2Presence.test_duplicate_literal_actor_rejected` |
| Un actor por consulta permitido en el contrato más amplio se rechaza si el ejecutor no sabe resolverlo. | `H45F2Presence.test_dynamic_actor_contract_is_not_silently_executed` |
| Una acción vinculada a un personaje desaparece al salir este del lugar. | `H45F2Presence.test_actor_element_follows_character_location` |
| Las entidades dinámicas sin ligadura y lugares remotos se rechazan. | `H45F2Presence.test_unbound_entity_and_remote_location_rejected` |
| La descripción de un elemento visible cumple Observe y sobrevive a restauración. | `H45F3Inspection.test_element_description_is_authorized_and_conforms` |
| Leer un elemento no ejecuta consecuencias ni cambia el estado. | `H45F3Inspection.test_element_inspection_does_not_run_authored_action` |
| `examinar` conserva prioridad para la interacción declarada. | `H45F3Inspection.test_examinar_prefers_authored_interaction` |
| La descripción de un elemento oculto no llega al cliente. | `H45F3Inspection.test_hidden_element_description_never_reaches_client` |
| Si no existe descripción propia se utiliza una ficha pública autorizada. | `H45F3Inspection.test_element_without_description_uses_public_card` |

## Evidencia complementaria

- Admisión estructural y semántica: `gisela/contracts/test_*.py`.
- Autorización y procedencia de acciones: `gisela/engine/tests/test_h4_exploration.py`.
- Consultas públicas, habilidades, historial y consola: `gisela/engine/tests/test_h45_cli.py`.
- Integridad de transacciones, RNG y restauración: `test_pending.py`, `test_h2_closure.py` y `test_h34d_skills.py`.
- Límites estructurales: `tools/test_quality.py` y `tools/check_quality.py`.

Las pruebas comprueban escenarios representativos, no todas las combinaciones de reglas de futuras historias. Un texto de una acción general de escena no identifica automáticamente un personaje físico. Ese control sigue siendo una responsabilidad explícita de autoría declarativa.
