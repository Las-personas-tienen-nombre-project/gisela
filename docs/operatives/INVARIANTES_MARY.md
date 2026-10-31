# Invariantes verificadas de MARY v1

Cada invariante identifica su prueba automatizada. «Verificada» se refiere al alcance implementado, no a funciones futuras de quest, password o integración visual.

| Invariante | Anclaje de prueba |
|---|---|
| MARY importa sin GISELA ni ALBERTO | `MaryIndependent.test_independent_imports` |
| Compilar no altera las definiciones del autor | `test_source_definitions_not_modified` |
| Evaluar no modifica contexto ni progreso de entrada | `test_first_evaluation_is_pure`, `test_no_effects_outside_results` |
| Un hecho repetido cuenta una sola vez | `test_two_distinct_experiences`, `test_weighted_progress_is_unique` |
| Los yields persistentes se proponen exactamente una vez | `test_yield_occurs_once`, `MaryGisela.test_scene_action_commits_progress_and_yield` |
| `milestone` permanece; `current` se recalcula | `test_milestone_latches_and_current_reverses` |
| Fracaso y cumplimiento simultáneos no producen recompensa | `test_failure_precedes_completion` |
| No se publica el objetivo oculto por Observe | `test_hidden_objective_never_leaks`, `MaryGisela.test_admit_and_show_mission_without_hidden_objective` |
| El guardado conserva estado y no repite yields al restaurar | `test_snapshot_json_roundtrip`, `test_save_restore_does_not_duplicate_yield` |
| El estado inyectado o incompleto se rechaza | `test_unknown_progress_and_types_rejected`, `test_missing_progress_rejected_on_restore`, `test_foreign_progress_rejected_on_restore` |
| Cancelación o acción rechazada no modifica progreso | `test_rejected_action_does_not_change_mary` |
| Error reactivo posterior revierte progreso, inventario y yields | `test_reaction_failure_rolls_back_mary_and_transfer` |
| La reproducción de una misma acción produce el mismo estado | `test_restored_future_action_determinism`, `test_deterministic_order` |
| Las referencias del autor se comprueban en admisión | `test_unknown_yield_rejected_before_start`, `test_unknown_condition_fact_rejected`, `test_unknown_value_reference_rejected` |
| Paquetes sin MARY conservan su comportamiento | `test_old_packages_unchanged` y batería completa previa |
| El lenguaje común diferencia booleanos y números | `test_boolean_and_integer_not_equal`, `test_decimal_and_integer_compare` |
| Los presupuestos y el schema impiden planes ilimitados | `test_many_objectives_within_budget`, `test_ambiguous_condition_rejected` |

**Pendiente deliberado:** reinicio de objetivos por jornada, condiciones de alcanzabilidad futura, yields de inventario y permisos de terceros; no se anuncian como implementados.

- **Integridad del manifiesto:** el actualizador conserva entradas existentes, es idempotente y no escribe si falta un archivo: `tools/test_manifest_update.py::test_preserves_previous_entries_and_is_repeatable` y `test_missing_file_does_not_replace_manifest`.
