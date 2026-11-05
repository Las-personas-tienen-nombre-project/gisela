# PA-001: Continuación 7: auditoría offline de GISELA

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Estado: PARCIAL.** Esta intervención se limita a GISELA. No se descargó ni ejecutó el SDK Ren'Py; PT-08 conserva aceptación gráfica pendiente.

## Protocolo y base

Se recuperó el ZIP acumulativo `gisela_PA001_auditoria_parcial_20261031.zip` en una copia de trabajo, manteniendo intacto el original. Se verificó en `gisela/engine/runtime.py` la guarda de agotamiento `INVALID_STATE` dentro de `_commit`, y se examinó la prueba `test_noninitial_exhausted_node_without_scene_is_typed_and_atomic` en `test_pa001_version_restore.py`. Es una verificación de implementación y evidencia de regresión, no prueba de cobertura exhaustiva de rutas.

## Comandos y resultados de esta intervención

1. `python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q`: **INCONCLUSO**, excedió el timeout del entorno (no se recibió resumen final). No se contabiliza como PASS.
2. `python -m unittest gisela.engine.tests.test_e0_transactions gisela.engine.tests.test_e0_error_contracts gisela.engine.tests.test_pending gisela.engine.tests.test_pa001_version_restore gisela.engine.tests.test_turn_boundaries -q`: **39 pruebas, PASS**, salida 0.
3. `python -m unittest gisela.engine.tests.test_e0_gateway gisela.engine.tests.test_e2_evaluations gisela.engine.tests.test_e3_visible gisela.engine.tests.test_mary_integration -q`: **82 pruebas, PASS**, salida 0.
4. `python tools/check_quality.py`: **PASS**, límites 500 líneas por archivo, 30 por función, 3 parámetros explícitos.
5. `python tools/check_documentation.py`: **PASS**, 31 páginas.

Total observado en suites focalizadas: **121 pruebas PASS**; este total no sustituye la regresión integral ni garantiza ausencia de solapamiento conceptual entre casos.

## Hallazgos y límites

- H9: la guarda de inicio y la de confirmación no inicial permanecen presentes, y las pruebas focalizadas pasaron. No se extiende esta conclusión a todas las rutas de causalidad.
- H1-H6: auditoría todavía abierta; no se ha demostrado un defecto adicional en las suites focalizadas, lo cual no equivale a cierre.
- H7: permanece documentado como corregido; H8: frontera intencional ADR-022/023 conservada.
- PT-01/PT-05: falta acreditar matriz completa de anclajes y compatibilidad negativa y de frontera en todas las versiones.
- PT-07: ejecución integral no acreditada por timeout.
- PT-08: Ren'Py explícitamente excluido de esta ejecución, sin aceptación gráfica.

**Cambios:** solo se incorpora este registro de auditoría. No se modificaron código, contratos, schemas, paquetes narrativos ni pruebas; no hubo motivo demostrado para hacerlo en esta intervención.
