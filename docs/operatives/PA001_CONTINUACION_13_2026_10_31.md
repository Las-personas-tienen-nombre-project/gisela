# PA-001: Intervención 13: PT-02R (evaluaciones visibles y causalidad anidada)

## Alcance

Comparación diferencial de exportación y observación entre una sesión continua y otra restaurada después de cada suspensión de evaluaciones visibles, decisiones con evaluación y una reacción que aplica un efecto con consecuencia causal propia. No se descargó ni ejecutó Ren'Py.

## Cambios

- Nueva suite `gisela/engine/tests/test_pa001_differential_visible_nested.py` (3 pruebas).
- Sin cambios de producción, contratos, schemas, ADR ni paquetes narrativos.

## Evidencia ejecutada

1. `python -m unittest gisela.engine.tests.test_pa001_differential_visible_nested -v`: **3 OK**; salida 0. La primera ejecución tenía un defecto de fixture: se importó `send` del módulo de evaluaciones para un paquete que necesitaba el helper de efectos. Corregido en el test; la ejecución posterior pasó.
2. `python -m unittest gisela.engine.tests.test_pa001_differential_visible_nested gisela.engine.tests.test_pa001_differential_restore gisela.engine.tests.test_e3_visible gisela.engine.tests.test_h34c_effects -q`: **44 OK**, salida 0.
3. `python tools/check_quality.py`: **OK**, salida 0.
4. `python tools/check_documentation.py`: **OK**, 31 páginas comprobadas, salida 0.

## Garantías ejercitadas

- Dos evaluaciones visibles sucesivas: exportaciones y proyecciones equivalentes al iniciar y tras cada confirmación/restauración; no permanece `pending_evaluation` al finalizar.
- Evaluación visible elegida: elección y confirmación equivalentes tras restaurar en ambos puntos; la elección se registra una vez.
- Reacción `fact_recorded` que aplica un efecto, cuyo `on_apply` registra otro hecho: estado, observación e historial idénticos entre ambas vías; los dos hechos aparecen una vez y una instancia de efecto queda activa.

## Límites de la evidencia y pendientes

El éxito de estas rutas no demuestra equivalencia de todas las combinaciones de evaluaciones, fallos de causalidad anidada, múltiples suspensiones de habilidades o estados de error con acciones obsoletas. La regresión integral del proyecto no se ha acreditado. PT-02 y PA-001 siguen abiertos; la aceptación visual Ren'Py está excluida de esta ronda.
