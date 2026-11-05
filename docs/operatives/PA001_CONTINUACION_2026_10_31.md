# PA-001: Continuación de la auditoría, 31 de octubre de 2026

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Estado:** PARCIAL. Complementa `PA001_AUDITORIA_2026_10_31.md`.
**Origen:** ZIP parcial del hito anterior, no una revisión Git. No se modificó lógica narrativa.

## PT-00: Nuevo hallazgo operativo

`tools/check_project.py` emplea `subprocess.run` con captura de salida y sin timeout por proceso. Durante una verificación extensa, los resultados de cada subprocess no se comunican hasta que terminan. Esto retrasa la identificación del componente que consume tiempo. La invocación integral volvió a exceder el límite de ejecución de este entorno: la salida alcanzó `OK: Trazabilidad invariantes E0` antes de interrumpirse. **No se interpreta como fallo del motor ni aprobación integral.**

Se añadió `tools/pa001_diagnose.py`, independiente y optativo, que ejecuta los módulos de pruebas aislados y emite un resultado por archivo (`pass`, `fail`, `timeout`) y, opcionalmente, JSON. No sustituye a `check_project.py` ni cambia sus criterios de aprobación. Se añadieron tres pruebas en `tools/test_pa001_diagnose.py` para asegurar descubrimiento estable y distinción de fallo y timeout.

Uso: `python tools/pa001_diagnose.py --suite gisela/engine/tests --per-file-timeout 30 --output pa001_resultados.json`.

**Limitación:** separar pruebas por archivo no identifica un caso lento dentro de ese archivo; un timeout significa ausencia de resultado, no defecto funcional. La duración depende de recursos y ambiente.

## PT-01 / PT-02: Trazabilidad de invariantes (inspección y ejecución)

| ID PA | Contrato/decisión | Prueba ejecutable existente | Evidencia actual |
| --- | --- | --- | --- |
| PA-T01 | ADR-007/008: cierre de nodo y entrada al siguiente son una sola confirmación | `gisela/engine/tests/test_turn_boundaries.py::TurnBoundariesTest.test_T04_closed_node_and_started_node_share_single_commit` | Test identificado, ejecución individual no acreditada en esta continuación |
| PA-T02 | ADR-007/008: fallo al entrar al siguiente nodo revierte todo el salto | `gisela/engine/tests/test_turn_boundaries.py::TurnBoundariesTest.test_T05_failure_starting_B_rolls_back_whole_jump` | Test identificado, ejecución individual no acreditada en esta continuación |
| PA-T03 | ADR-020: fallo de proyección no publica candidato | `gisela/engine/tests/test_e0_transactions.py::CommitBoundary.test_e0_t01_rejected_projection_preserves_state` | Suite E0 completa: 35 PASS |
| PA-T04 | ADR-020: fallar al proyectar pendiente no publica transacción | `gisela/engine/tests/test_e0_transactions.py::CommitBoundary.test_e0_t02_pending_projection_failure_is_atomic` | Suite E0 completa: 35 PASS |
| PA-T05 | ADR-020: fallo de proyección en cancelación conserva estado | `gisela/engine/tests/test_e0_transactions.py::CommitBoundary.test_e0_t03_cancel_projection_failure_is_atomic` | Suite E0 completa: 35 PASS |
| PA-T06 | ADR-020: restauración congela una copia antes de validarla | `gisela/engine/tests/test_e0_transactions.py::CommitBoundary.test_e0_t06_restore_uses_frozen_snapshot_copy` | Suite E0 completa: 35 PASS |
| PA-T07 | ADR-023: evaluación visible en espera conserva RNG y soporta restauración | `gisela/engine/tests/test_e3_visible.py::E3Visible.test_01_entry_pending_no_world_or_turn_and_restore` | Suite E3 completa: 22 PASS |
| PA-T08 | ADR-023: preflight rechazado no consume RNG | `gisela/engine/tests/test_e3_visible.py::E3Visible.test_08_preflight_failure_before_roll` | Suite E3 completa: 22 PASS |

El anclaje es a pruebas **existentes**; no se crean tests redundantes para cumplir el número de hitos. La existencia de una prueba no implica cobertura de todas las rutas causales.

## PT-03: Gateway

ADR-020 especifica gateway opcional para clientes externos, operación local sin gateway y estado/recibo persistidos atómicamente cuando se usa `JsonCheckpointStore`. Las 35 pruebas E0 pasaron. Se conserva esta frontera: no se ha establecido defecto que justifique cambiarla.

## PT-04: Política y calidad

Se mantiene la política vigente (500 líneas por archivo, 30 por función, tres parámetros explícitos). Modificarla exige decisión explícita. `check_quality.py`: PASS tras añadir las herramientas; `check_documentation.py`: PASS (31 páginas).

## PT-05: Schemas

Vigentes en árbol: `gisela/contracts/v1_3/`, `v1_4/`, `v1_5/`. ADR-020 exige mantener 1.2/1.3 en la frontera donde aplique, aun si los schemas expuestos actualmente requieren verificar sus ubicaciones y compatibilidad. La validación completa y la matriz de persistencia por versión siguen pendientes; **no se declaran soportadas versiones únicamente por existir carpetas**.

## PT-06 / PT-07 / PT-08: Pruebas y aceptación

- `python -m unittest discover -s tools -p test_pa001_diagnose.py -v`: **3 PASS**.
- `python -m unittest discover -s gisela/engine/tests -p 'test_e0_*.py' -q`: **35 PASS**.
- `python -m unittest discover -s gisela/engine/tests -p test_e3_visible.py -q`: **22 PASS**.
- `python tools/check_quality.py`: PASS.
- `python tools/check_documentation.py`: PASS (31 documentos).
- Varios archivos de pruebas del ejecutor pasaron individualmente durante el diagnóstico preliminar, pero el examen conjunto no terminó; no se suman como evidencia de regresión integral.
- `check_project.py`: INCONCLUSO por límite del entorno.
- SDK Ren'Py real / exportaciones: NO EJECUTADOS.

## Decisión de cambio aplicada

**DECIDIDO en esta intervención:** agregar diagnóstico de pruebas sin modificar el ejecutor, ni contratos, ni la política oficial de aceptación. Es reversible, acotado y comprobado con pruebas. No reabre las decisiones arquitectónicas ADR.

**PENDIENTE:** completar ejecución íntegra sin truncamiento, caracterizar fuentes causales no cubiertas, construir matriz de versiones y verificar Ren'Py SDK real. No cerrar H1-H5 por los resultados parciales.
