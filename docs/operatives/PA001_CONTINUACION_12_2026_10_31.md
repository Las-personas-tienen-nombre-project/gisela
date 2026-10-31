# PA-001: Intervención 12: PT-02R

## Alcance

Comparación diferencial entre ejecución continua y ejecución restaurada, incluyendo reacciones causales, operaciones pendientes, consumo reproducible de RNG y rollback. Sin descarga, instalación ni ejecución de Ren'Py.

## Cambios

- Añadido `gisela/engine/tests/test_pa001_differential_restore.py` con tres pruebas comportamentales por API pública `observe/act/export/restore_session`.
- Sin cambios de producción, contratos, schemas ni ADR.

## Evidencia

Comando: `python -m unittest gisela.engine.tests.test_pa001_differential_restore -v`.
Resultado: **3 tests OK**, código 0.

Comando: `python -m unittest gisela.engine.tests.test_pa001_differential_restore gisela.engine.tests.test_h2_closure gisela.engine.tests.test_pending gisela.engine.tests.test_mary_integration gisela.engine.tests.test_e0_transactions -q`.
Resultado: **49 tests OK**, código 0.

Comando: `python tools/check_quality.py`.
Resultado: **OK**, código 0.

Intento `python tools/check_project.py --help`: excedió tiempo disponible, interrumpido. El script no ofrece un modo `--help` convencional y ejecuta comprobaciones al invocarse; **no cuenta como regresión integral aprobada**.

## Invariantes y observaciones

- I07/I08/I09: consulta, efectos y reacciones se observan en dos vías de ejecución, incluida la reacción sobre `fact_recorded` y la detección de conflicto de escritura.
- I10/I15: las rutas ejercitadas confirman que el RNG queda idéntico tras restauración, no se consume al cancelar, y un conflicto revierte sus efectos.
- I11/I13/I14: una solicitud pendiente sobre habilidad se restaura, resuelve y confirma una sola vez; historial y contadores coinciden. Un conflicto conserva instantánea y proyección.
- La comparación estricta de `export()` incluye estado, historial, identidad, RNG, revisiones y pendientes; `observe()` comprueba paridad visible.

No se confirmó defecto nuevo en las rutas ejercitadas. La evidencia es **focalizada, no exhaustiva**: no se cubrieron todas las variantes causales, evaluaciones visibles, ni todos los puntos de suspensión. No se declara cerrada PA-001.

## Pendientes

Extender diferencial a evaluaciones visibles y operaciones anidadas; ejecutar la regresión integral mediante separación de suites lentas y registrar resultados finales; completar la matriz y la documentación de cierre. Ren'Py queda fuera de alcance por instrucción expresa.
