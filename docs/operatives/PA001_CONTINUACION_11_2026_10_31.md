# PA-001 — Intervención 11: pruebas comportamentales de brechas de invariantes

**Estado: PARCIAL.** Continuación de la matriz de la intervención 10. No se descargó ni utilizó SDK Ren'Py; no hay aceptación gráfica.

## Alcance y cambios

Se añade `gisela/engine/tests/test_pa001_behavior_gaps.py` con ocho pruebas nuevas. No se modificó código de producción ni contratos. Los casos emplean el paquete real `mvp_casete.package.json`, admisión auténtica y sesión GISELA.

| Invariante | Pruebas nuevas | Resultado | Límite |
|---|---|---|---|
| I04 — definiciones inmutables | mutación del objeto original tras admisión; mutación de copia materializada | PASS | Demuestra aislamiento por API pública; no prueba que código interno nunca altere definiciones |
| I05 — definición/estado separados | modificación de snapshot exportado frente a paquete y sesión | PASS | Una sesión y un paquete representativos |
| I06 — consultas puras | nueve hojas de consulta de mundo, comparación y reloj; referencia inexistente sin inserción | PASS | No cubre todos los operadores compuestos, consultas avanzadas ni TRAITS |
| I16 — no ejecutar Python autoral | rechazo por admisión de `op: python` en paso, efecto `op: python` y campo `python` extra | PASS | Verifica frontera de admisión para tres estructuras; no demuestra exhaustividad ante todas las entradas alternativas |

Los textos de ataque de I16 son cadenas inertes; no se ejecutó código suministrado como autoría. No se alteró la definición de la política de seguridad.

## Evidencia y comandos (directorio raíz del repositorio)

- `python -m unittest discover -s gisela/engine/tests -p test_pa001_behavior_gaps.py -q`: **8 tests, OK**. La primera ejecución obtuvo error del propio test por referenciar `steps[2]` (diálogo) en lugar del paso de opción `steps[3]`; corregido antes de registrar el pase.
- `python -m unittest discover -s gisela/engine/tests -p test_pa001_invariants.py -q`: **2 tests, OK**.
- `python -m unittest discover -s gisela/engine/tests -p test_mvp.py -q`: **22 tests, OK**.
- `python -m unittest discover -s gisela/engine/tests -p test_e0_transactions.py -q`: **8 tests, OK**.
- `python -m unittest discover -s gisela/engine/tests -p test_pending.py -q`: **15 tests, OK**.
- `python -m unittest discover -s gisela/engine/tests -p test_pa001_version_restore.py -q`: **10 tests, OK**.
- `python -m unittest discover -s gisela/contracts -p test_semantic_validator.py -q`: **69 tests, OK**.
- `python tools/check_quality.py`: **OK**.
- `python tools/check_documentation.py`: **OK**, 31 páginas.

**134 ejecuciones de tests** en estas suites, sin afirmar unicidad entre todas las suites ni equivalencia a regresión integral.

## Hallazgos y decisiones

- No se detectaron defectos de producción en estas rutas.
- Se mantiene la arquitectura aprobada y el control mecánico de 500 líneas.
- La evidencia de I04, I05, I06 e I16 aumenta, pero ninguna propiedad se declara probada universalmente.
- Próximas comprobaciones: variantes compuestas de condiciones, queries avanzadas, caminos autorales alternos, replay reactivo y RNG post-restauración; además de regresión integral con resultado final comprobable.
- La aceptación de Ren'Py permanece **NO EJECUTADA** por instrucción expresa.
