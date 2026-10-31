# PA-001 — Matriz consolidada de trazabilidad de invariantes (intervención 10)

**Estado: PARCIAL; inventario exhaustivo de las 16 invariantes explícitas del protocolo, no demostración exhaustiva de todos sus caminos.**

Fuente del inventario: apartado 4 de las instrucciones de PA-001. Cada fila incluye decisión/documento, punto de código y prueba candidata. Los anclajes son rutas inspeccionables, no certificados de suficiencia.

| ID | Invariante | Fuente | Código | Prueba | Estado | Límite de evidencia |
|---|---|---|---|---|---|---|
| `I01` | Motor único y ALBERTO como subsistema | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/runtime.py; gisela/engine/traits_dice_bridge.py` | `gisela/engine/tests/test_traits_alberto_v13.py` | PARCIAL | La integración existe; no hay prueba negativa de segundo motor. |
| `I02` | Sesión única y autoridad transaccional | `docs/decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md` | `gisela/engine/runtime.py:38,459; gisela/engine/authorized_gateway.py:157` | `gisela/engine/tests/test_e0_transactions.py; test_e0_gateway.py` | RESPALDADA EN RUTAS | E0 demuestra fallos de proyección y revisión simultánea; no prueba todas las rutas. |
| `I03` | Frontend consumidor, sin reglas narrativas duplicadas | `docs/decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md` | `gisela/engine/public_view.py; gisela/engine/projection.py; renpy/` | `gisela/engine/tests/test_h45f_scene.py` | PARCIAL | No se auditó exhaustivamente el adaptador; sin SDK. |
| `I04` | Definiciones inmutables durante la sesión | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/runtime.py:40,60` | `gisela/engine/tests/test_mvp.py` | BRECHA | Falta prueba focalizada de mutación externa de definiciones y de no exposición. |
| `I05` | Estado separado de definiciones | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/runtime.py:40,69; gisela/engine/initialization.py` | `gisela/engine/tests/test_mvp.py` | PARCIAL | Separación estructural visible; aislamiento en todas las rutas no acreditado. |
| `I06` | Condiciones como consultas puras | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/conditions.py:77; gisela/engine/queries.py` | `gisela/engine/tests/test_e0_transactions.py::CommitBoundary.test_e0_t05_read_only_projection_is_pure` | BRECHA | La prueba citada valida proyección, no prueba por sí sola pureza de todas las condiciones. |
| `I07` | Consecuencias declarativas atómicas | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/consequences.py:13; gisela/engine/runtime.py:459` | `gisela/engine/tests/test_e0_transactions.py; test_h34c_effects.py` | RESPALDADA EN RUTAS | Rollback bajo fallos concretos; falta matriz por operación. |
| `I08` | Reacciones con la misma atomicidad | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/reactions.py:111; gisela/engine/runtime.py:459` | `gisela/engine/tests/test_pending.py::test_reaction_suspends_without_publishing_changes` | PARCIAL | Pendiente de verificar conflicto, ciclo y rollback por cada fuente. |
| `I09` | Conflictos de escritura explícitos | `docs/decisions/GISELA_ADR_001_017.md` | `gisela/engine/reactions.py:66; gisela/engine/reaction_writes.py` | `gisela/engine/tests/test_pending.py::test_two_rules_granting_to_same_character_conflict_before_wait` | RESPALDADA EN RUTAS | Conflicto estudiado en concesiones; no todas las operaciones. |
| `I10` | RNG transaccional y reproducible | `docs/decisions/ADR_016_017_DETERMINISMO.md` | `gisela/engine/consequences.py:43; gisela/contracts/rng.py` | `gisela/engine/tests/test_e2_evaluations.py::test_e2_02_random_dice_sum_is_reproducible; test_e2_08_invalid_branch_rolls_back_rng` | PARCIAL | Requiere trazas deterministas transversales tras restauración. |
| `I11` | Acciones cliente validadas contra estado actual | `docs/decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md` | `gisela/engine/action_handler.py:9,129; gisela/engine/authorized_gateway.py:157` | `gisela/engine/tests/test_e0_gateway.py::test_e0_g03_revision_rejects_distinct_command` | RESPALDADA EN RUTAS | Revision obsoleta cubierta; no todas las clases de acción. |
| `I12` | Pendientes íntegros en suspensión/restauración | `docs/decisions/ADR_023_E3_EVALUACIONES_VISIBLES_V15.md` | `gisela/engine/pending.py; gisela/engine/runtime.py:115,444` | `gisela/engine/tests/test_pending.py::test_restore_pending_and_continue_matches_uninterrupted; test_e3_visible.py` | RESPALDADA EN RUTAS | Rutas representativas; orígenes combinados por cubrir. |
| `I13` | Persistencia con identidad, versión e integridad | `docs/decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md` | `gisela/engine/runtime.py:115,179; gisela/engine/authorized_gateway.py:89` | `gisela/engine/tests/test_pa001_version_restore.py; test_e0_gateway.py` | PARCIAL | Versiones 1.2–1.5 cruzadas; matriz completa por estado/capacidad pendiente. |
| `I14` | Errores sin estado parcialmente confirmado | `docs/decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md` | `gisela/engine/runtime.py:459,486; gisela/engine/errors.py` | `gisela/engine/tests/test_e0_transactions.py; test_pa001_version_restore.py` | RESPALDADA EN RUTAS | Casos de proyección y nodo agotado; no prueba universal. |
| `I15` | Ejecución local sin autenticación externa | `docs/decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md` | `gisela/engine/runtime.py:492; gisela/engine/authorized_gateway.py:128` | `gisela/engine/tests/test_mvp.py; test_e0_gateway.py` | PARCIAL | API local existe; falta prueba explícita de independencia del gateway. |
| `I16` | Sin ejecución de Python arbitrario autoral | `gisela/contracts/SEMANTIC_VALIDATION.md` | `gisela/contracts/semantic_validator.py; gisela/engine/consequences.py` | `gisela/contracts/test_semantic_validator.py` | BRECHA | Falta prueba de rechazo dirigida a payloads ejecutables en todas las entradas. |

## Brechas prioritarias de PT-01

1. I04: probar aislamiento de definiciones frente a modificación del paquete de entrada y mutación externa.
2. I06: ampliar pruebas de `predicate` a cada tipo de condición y acceso a mundo; comparación literal y error de expresión ya están cubiertos.
3. I16: comprobar prohibición efectiva de ejecución autoral por entradas de schema y validación semántica.
4. I03 e I15: asegurar con tests focalizados frontera frontend/motor y uso local sin gateway.
5. I08, I10, I12 e I13: tabla de rutas reactivas, replay y pendientes por versión/capacidad.

## Criterios y alcance

- **RESPALDADA EN RUTAS**: hay pruebas comportamentales concretas, sin afirmación de universalidad.
- **PARCIAL**: hay código y pruebas relacionadas pero falta una dimensión esencial de la propiedad.
- **BRECHA**: no se ha identificado una prueba que compruebe directamente la totalidad de la propiedad declarada.
- La revisión no sustituye la regresión integral ni la integración gráfica.
- No se descargó ni ejecutó el SDK de Ren’Py.

## Ejecución de la intervención 10

- `python -m unittest discover -s gisela/engine/tests -p test_pa001_invariants.py -q`: 2/2 PASS (pruebas nuevas I06).
- `python -m unittest discover -s gisela/engine/tests -p test_e0_transactions.py -q`: 8/8 PASS.
- `python -m unittest discover -s gisela/engine/tests -p test_pending.py -q`: 15/15 PASS.
- `python -m unittest discover -s gisela/engine/tests -p test_pa001_version_restore.py -q`: 10/10 PASS.
- `python tools/check_quality.py`: PASS.
- `python tools/check_documentation.py`: PASS; 31 páginas seleccionadas por el control.
- No se ejecutó la regresión integral. PT-01 no puede declararse completamente verificado; PT-08 excluido por instrucción expresa.
