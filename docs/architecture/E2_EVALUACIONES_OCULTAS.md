# E2: Integración ejecutable de evaluaciones ocultas

**Estado:** implementado sobre GISELA v1.4. Las versiones v1.2/v1.3 no cambian.

## Recorrido causal

```text
Admisión E1 -> índice de rutas de EvaluationRoutes
  -> Act autorizado o avance de paso automático
  -> datos efectivos ALBERTO / S.O.F.I.A. / TRAITS
  -> validación numérica previa al RNG
  -> DICE (RNG inyectado de GISELA)
  -> rama declarada y RNG propuesto
  -> efectos de rama -> settle / reacciones / MARY
  -> destino y ejecución automática -> proyección y validación
  -> commit único en GiselaSession
```

La evaluación no añade turno ni expone su resultado en `Observe`. Un paso oculto se ejecuta como paso automático entre puntos observables. Las opciones se ejecutan tras `choose`, y las acciones de escena tras `interact`. La ruta de autoría es distinta de la identidad del solicitante.

`EvaluationRoutes` utiliza `compile_package_evaluations` y mapea una clave de procedencia inequívoca para cada paso, opción y acción (de escena o elemento). Los tres orígenes llaman una sola operación `execute`. Las ramas se aplican como consecuencias ordinarias con el mismo `EffectContext` que ya usa GISELA.

## Contratos y límites

- `session.schema.json` v1.4 se vuelve ejecutable, sin añadir propiedades de E3; snapshots v1.4 se comprueban contra digest y restauran con el validador de versión correspondiente.
- `initial_state` materializa TRAITS en v1.4 igual que en v1.3; el catálogo es opcional.
- Las sumas numéricas efectivas respetan ±1.000.000 en cada componente neutral. Los resultados y RNG se confirman solo con el mundo y sus reacciones.
- `pending_transaction` existente modela decisiones auxiliares; se reconstruye el borrador sin fijar una tirada visible.
- `visible` y `acknowledged` permanecen **fuera del runtime E2**. E3 debe versionar cualquier nueva forma incompatible de guardado.

## Verificación

`python tools/check_project.py` ejecuta las pruebas y la matriz E2, verificable mediante `python tools/verify_e2_invariants.py`. La batería `gisela/engine/tests/test_e2_evaluations.py` prueba las rutas, perfiles, RNG, efectos, replay, MARY, la frontera E0, rollback y restore. Los tests de E0/E1 y los paquetes anteriores constituyen la regresión.
