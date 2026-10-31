# PA-001: Intervención 15: respuestas inválidas en estados pendientes

## Alcance

Continuación sobre el ZIP acumulativo de la intervención 14, sin descarga ni ejecución del SDK de Ren'Py. Se investigó la conservación del estado y la recuperación tras acciones inválidas durante evaluaciones visibles y transacciones pendientes. Se compararon ejecuciones continuas con ejecuciones restauradas desde el snapshot exportado.

## Cambio incorporado

- Nueva suite `gisela/engine/tests/test_pa001_invalid_pending_recovery.py` con tres pruebas comportamentales.
- No se modificó código de producción, contratos, schemas, ADR ni paquetes narrativos.

## Evidencia ejecutada

- `python -m unittest gisela.engine.tests.test_pa001_invalid_pending_recovery -v`: **3/3 PASS**; código de salida 0.
- `python -m unittest gisela.engine.tests.test_pa001_invalid_pending_recovery gisela.engine.tests.test_pa001_error_recovery gisela.engine.tests.test_pa001_differential_visible_nested gisela.engine.tests.test_pa001_differential_restore gisela.engine.tests.test_e3_visible gisela.engine.tests.test_pending -q`: **48/48 PASS**, código de salida 0.
- `python tools/check_quality.py`: **PASS**, código de salida 0.
- `python tools/check_documentation.py`: **PASS**, 31 páginas, código de salida 0.
- `python tools/check_project.py --help`: **timeout**, sin resultado final de la regresión integral. No se considera aprobada.

## Garantías comprobadas en las rutas examinadas

1. En una evaluación visible al inicio, acciones no ofrecidas devuelven `INVALID_ACTION` sin cambiar exportación, RNG, historial, revisión ni estado pendiente. Tras restaurar, una confirmación válida converge con la ejecución continua.
2. Durante una evaluación visible iniciada desde una opción, acciones no ofrecidas conservan intacta la transacción suspendida. `continue_evaluation` confirma una sola selección, tanto tras restauración como en ejecución continua.
3. Durante una transacción pendiente con consumo aleatorio diferido, una resolución inexistente y otras acciones no ofrecidas mantienen intacto el snapshot. Una resolución válida posterior produce el mismo estado e historial en ambas ejecuciones y mantiene el contador RNG esperado.

## Límites y pendientes

No se ensayaron todas las combinaciones de entradas malformadas con formato de acción válido pero datos auxiliares inválidos, ni todas las reacciones anidadas detrás de evaluaciones visibles. Estas tres pruebas no representan una regresión integral y no justifican cerrar PT-02 o PA-001. La aceptación gráfica Ren'Py continúa excluida.
