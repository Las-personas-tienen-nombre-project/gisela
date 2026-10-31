# PA-001 — Intervención 14 — recuperación tras fallos causales anidados

## Alcance

Se continuó PT-02R sobre la intervención 13, sin SDK de Ren'Py. Se verificó si un error en la ejecución de efectos con consecuencia anidada o un conflicto de escrituras reactivas deja la sesión intacta, conserva la equivalencia después de restaurar y permite elegir otra acción válida.

## Cambios

- Nueva suite `gisela/engine/tests/test_pa001_error_recovery.py` (dos pruebas comportamentales).
- Sin modificaciones de código de producción, contratos, ADR, schemas ni paquetes autorales.

## Evidencia

- `python -m unittest gisela.engine.tests.test_pa001_error_recovery -v`: 2 pruebas OK, salida 0.
- `python -m unittest gisela.engine.tests.test_pa001_error_recovery gisela.engine.tests.test_pa001_differential_restore gisela.engine.tests.test_pa001_differential_visible_nested gisela.engine.tests.test_h34c_effects gisela.engine.tests.test_h34a_values -q`: 42 pruebas OK, salida 0.
- `python tools/check_quality.py`: OK, salida 0.
- `python tools/check_documentation.py`: OK, 31 páginas, salida 0.
- `python tools/check_project.py --help`: interrupción por timeout en esta ejecución; NO es evidencia de regresión integral aprobada.

## Garantías verificadas

1. El intento de aplicar dos efectos con `unique_per_target` falla con `EFFECT_ALREADY_ACTIVE` y no confirma el efecto, ni el hecho anidado emitido por `on_apply`. Reintentar mantiene el mismo resultado y snapshot, tanto en sesión continua como restaurada.
2. Dos reacciones a `fact_recorded` que escriben valores diferentes en una misma variable provocan `REACTION_CONFLICT`. Exportación, observación y estado confirmado permanecen intactos tras el fallo y durante la restauración.
3. Tras ambos errores, la elección alternativa `guardar` se confirma correctamente y las sesiones continua/restaurada conservan exportación y observación equivalentes.

## Límites

No se han probado todas las variantes de fallos con evaluaciones visibles ni reintentos de resoluciones pendientes malformadas; el conjunto tampoco acredita la regresión integral. PT-02 y PA-001 continúan abiertos. No se descargó ni ejecutó Ren'Py.
