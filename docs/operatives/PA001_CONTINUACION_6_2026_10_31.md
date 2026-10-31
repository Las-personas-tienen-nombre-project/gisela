# PA-001 — Continuación 6: alcance exclusivamente GISELA

**Estado: PARCIAL; auditoría abierta.** Se excluye expresamente de esta intervención descargar el SDK de Ren'Py o efectuar integración gráfica. No se ha declarado PT-08 aprobado.

## PT-02 — Defecto H9 y transacción

Se verificó la presencia de la guarda `INVALID_STATE` tanto en `_confirm_initial` como en `_commit` de `gisela/engine/runtime.py`. La regresión `test_noninitial_exhausted_node_without_scene_is_typed_and_atomic` verifica que al agotar un nodo observable sin escena, transición ni final, `act` produce error tipado y que `export()` conserva exactamente el estado anterior. La regresión `test_v14_exhausted_node_without_scene_has_engine_error` comprueba el inicio de sesión. Esta cobertura no demuestra por sí sola todos los posibles caminos mediante reacciones causales, suspensión y reanudación.

## Ejecución comprobada en esta intervención

Desde la raíz del proyecto:

- `python -m unittest gisela.engine.tests.test_pa001_version_restore gisela.engine.tests.test_pending gisela.engine.tests.test_turn_boundaries -q`: **28 tests, PASS**, retorno 0, 2.650 s.
- `python tools/check_quality.py`: **PASS**, retorno 0; máximo 500 líneas por archivo, 30 por función y 3 parámetros explícitos.
- `python tools/check_documentation.py`: **PASS**, retorno 0; 31 páginas.

Se recuperaron asimismo 22 archivos `.status` de la ejecución segmentada anterior, todos con retorno cero, pero sus resultados se consideran evidencia histórica de esa ejecución y no una nueva regresión integral. La salida de `test_h46_adventure` informa 15 tests aprobados en 34,633 s; no se encontró `.status` correspondiente en el directorio de registros segmentados, por lo que no se incorpora al recuento de 22.

## Pendientes obligatorios

- Completar matriz de trazabilidad de cada invariante con contrato, implementación y prueba.
- Profundizar en recorridos no iniciales de reacciones, suspensión/restauración y rollback, incluyendo RNG y operaciones anidadas.
- Completar estados pendientes y transiciones por versiones soportadas.
- Ejecutar y acreditar la regresión integral sin timeout.
- Mantener PT-08 (aceptación gráfica con SDK) fuera de alcance de esta intervención y **no acreditado**.

No se alteraron contratos aprobados ni se incorporaron dependencias. H1–H6 no se consideran cerrados por estas pruebas focalizadas. Se conserva el estado de H7 corregido, H8 frontera intencional y H9 corregido en los dos caminos caracterizados.
