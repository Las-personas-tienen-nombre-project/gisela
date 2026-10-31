# H4.5. Invariantes verificadas y pruebas ancladas

Los nombres indicados corresponden a métodos ejecutables de `gisela/engine/tests/test_h45_cli.py`. Las invariantes anteriores siguen cubiertas por los módulos de H2, H3 y H4. Los comandos y módulos de prueba se ejecutan sin Ren'Py.

| Invariante | Prueba que la verifica |
| --- | --- |
| Observe y Session cumplen los schemas extendidos. | `H450Contracts.test_public_view_matches_contract` |
| El inventario público solo contiene objetos propios. | `H450Contracts.test_inventory_only_has_owned_objects` |
| La consulta de una carta desconocida no revela datos. | `H450Contracts.test_unknown_card_does_not_leak` |
| Observe, cartas, Scoresheet e historial son consultas puras. | `H450Contracts.test_observe_and_read_are_pure` |
| El estado público corresponde al protagonista. | `H450Contracts.test_public_status_only_for_player` |
| El historial sobrevive a guardar y restaurar. | `H450Contracts.test_history_persists_without_reexecution` |
| La secuencia del registro se valida antes de restaurar. | `H450Contracts.test_invalid_reading_sequence_rejected` |
| La escena expone título y descripción declarados. | `H45APresentation.test_scene_has_title_and_description` |
| El presentador conserva los textos del paquete. | `H45APresentation.test_renderer_shows_author_text` |
| No se puede seleccionar una opción inhabilitada por número. | `H45APresentation.test_disabled_choice_cannot_be_selected_by_number` |
| Leer una ficha no ejecuta operaciones. | `H45BObjects.test_card_read_does_not_act` |
| Consultar el inventario no modifica la sesión. | `H45BObjects.test_inventory_command_is_pure` |
| Los verbos se resuelven solo contra acciones ofrecidas. | `H45BObjects.test_command_matches_only_offered_actions` |
| Un comando ambiguo nunca selecciona por cuenta propia. | `H45BObjects.test_ambiguous_selection_never_guesses` |
| Una acción de examen declarada tiene prioridad sobre la lectura de ficha. | `H45BObjects.test_examine_prefers_author_action` |
| Una escena autorizada permite jugar habilidades de mano. | `H45CSkills.test_exploration_skill_is_offered_and_consumed` |
| Una escena no autorizada rechaza el intento sin mutación. | `H45CSkills.test_skill_cannot_be_played_in_unpermitted_scene` |
| Guardar y restaurar conserva el resultado de usar una habilidad. | `H45CSkills.test_skill_restore_matches_uninterrupted` |
| El historial conserva el paso narrativo y se puede limitar. | `H45DHistory.test_history_of_scene_and_conversation` |
| El comando history no modifica la sesión. | `H45DHistory.test_history_command_is_read_only` |
| La depuración está desactivada si no se solicita expresamente. | `H45DHistory.test_developer_mode_is_explicit` |
| Los borradores pendientes no aparecen en el historial. | `H45DHistory.test_pending_does_not_publish_a_draft` |
| El juego completo puede recorrerse por consola. | `H45EIntegration.test_cli_script_can_finish_world` |
| EOF termina el cliente sin excepción. | `H45EIntegration.test_eof_exits_cleanly` |
| Los personajes ocultos no se publican en cartas. | `H45EIntegration.test_hidden_character_does_not_leak` |
| Una acción rechazada no se registra como confirmada. | `H45EIntegration.test_rejected_action_does_not_add_history` |
| La lista pública de historial no permite mutar el guardado. | `H45EIntegration.test_public_history_is_defensive_copy` |
| El paquete nuevo se admite con los contratos actuales. | `H45EIntegration.test_package_is_admitted_and_cli_schemas_hold` |
| Guardar y cargar desde la CLI preserva el registro. | `H45EIntegration.test_cli_save_and_load_preserve_history` |
| Un límite inválido de history no altera la sesión. | `H45EIntegration.test_history_rejects_invalid_limit_without_writing` |

## Invariantes anteriores que continúan vigentes

Los controles del motor ya existentes se conservan y se ejecutan en la misma batería:

- Atomicidad, cancelación y restauración de transacciones: `test_pending.py` y `test_h2_closure.py`.
- Conflictos entre reglas y rollback: `test_h34a_values.py` y `test_h34c_effects.py`.
- Capacidades, habilidades y políticas de retorno: `test_h34d_skills.py`.
- Visibilidad, procedencia y autorización exploratorias: `test_h4_exploration.py`.
- Límite de 500 líneas por archivo, 30 por función y tres parámetros explícitos: `tools/test_quality.py` y `tools/check_quality.py`.
- Integridad de definiciones, guardados y tipos: `gisela/contracts/test_*.py`.

Las comprobaciones negativas no equivalen a una demostración matemática de ausencia de defectos. Cada invariante se vincula a evidencia reproducible, con sus límites explicados en [H4_5_REVISION_Y_CIERRE.md](H4_5_REVISION_Y_CIERRE.md).
