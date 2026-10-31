# PA-001 — Continuación 9: aislamiento de suites offline

**Estado: PARCIAL.** No se descargó ni ejecutó Ren'Py.

## Alcance

Se partió del ZIP acumulativo de la intervención 8. Se inspeccionó la matriz PT-05 existente y se intentó comprobar la regresión integral con pruebas particionadas. No se modificó el código de producción ni los contratos.

## Evidencia observada

- `python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q`: ejecución inconclusa por timeout; no se considera PASS.
- Ejecutadas individualmente con código 0: `test_e0_error_contracts`, `test_e0_gateway`, `test_e0_transactions`, `test_e2_evaluations`, `test_e3_visible`, `test_h2_closure`, `test_h34a_values`, `test_h34b_sofia`, `test_h34c_effects`, `test_h34d_skills` y `test_h3_world`.
- El intento posterior de recorrer todas las suites también fue interrumpido antes de concluir; no extrapolar resultados a las suites no ejecutadas.
- `python tools/check_quality.py`: PASS, límites 500/30/3.
- `python tools/check_documentation.py`: PASS (31 páginas antes de incorporar esta nota).

## Hallazgos y límites

Esta intervención no aporta un defecto nuevo confirmado. La compatibilidad entre versiones 1.2–1.5 sigue respaldada por la prueba cruzada de la intervención 8, pero falta cobertura exhaustiva por capacidad y estado pendiente. PT-01 (trazabilidad completa), PT-02 (rutas exhaustivas), PT-05 (fronteras), PT-07 (regresión integral) permanecen abiertos. PT-08 queda excluido por instrucción del usuario y no aprobado.

**No se declara cerrada PA-001.**
