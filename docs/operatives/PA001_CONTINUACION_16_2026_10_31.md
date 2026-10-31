# PA-001: Intervención 16: validación de solicitudes malformadas durante pendientes

## Alcance y fuente

Continuación acumulativa de la intervención 15. Se examinó la frontera pública `GiselaSession.act` durante una transacción auxiliar pendiente, tanto sin restaurar como después de restaurar un snapshot. No se descargó ni ejecutó Ren'Py.

## Contratos y rutas

- `gisela/engine/action_handler.py`: `_authorize` valida el envelope `act`, rechaza sesión/revisión ajenas, parámetros y acciones no ofrecidas.
- `gisela/engine/pending.py`: `DecisionReplay.select` exige coincidencia con opciones y solicitud actual.
- `gisela/engine/runtime.py`: `GiselaSession.act` delega autorización y ejecución, con un único estado confirmado.
- `gisela/engine/tests/test_pa001_malformed_auxiliary.py`: dos pruebas comportamentales nuevas desde `with_roll` y `reach_choice`, con comparaciones de snapshots y restauración.

## Ejecución verificable

1. `python -m pytest -q gisela/engine/tests/test_pa001_malformed_auxiliary.py`, 2 passed, salida 0.
2. `python -m pytest -q gisela/engine/tests/test_pa001_malformed_auxiliary.py gisela/engine/tests/test_pa001_invalid_pending_recovery.py gisela/engine/tests/test_pa001_error_recovery.py gisela/engine/tests/test_pa001_differential_restore.py gisela/engine/tests/test_pending.py gisela/engine/tests/test_e3_visible.py`, 47 passed, 7 subtests passed, salida 0.
3. `python tools/check_quality.py`, PASS, salida 0.
4. `python tools/check_documentation.py`, PASS, 31 páginas, salida 0.
5. `python tools/check_project.py --help`, interrupción por timeout; **sin resultado final**. El script no expone una ayuda inocua: arranca la comprobación integral. No contar esta ejecución como aprobada.

## Cobertura y límites

- Verificado: solicitudes nulas, listas, cadenas, vacías, con campo desconocido, con parámetros no soportados, campo `action_id` nulo, campo `revision` mal tipado, campo `session_id` ausente, revisión antigua y sesión ajena; rechazo sin cambios en estado, RNG, historial ni pending; respuesta válida posterior y convergencia después de restaurar.
- La prueba compara el resultado exportado completo, no solamente el código de error.
- No se modificó código de producción, schemas, ADR ni paquetes narrativos.
- No se han agotado las clases de fallos posibles en todas las versiones del contrato ni se ha acreditado la regresión integral. PA-001 continúa abierta.
