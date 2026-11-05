# PA-001: Continuación 4: H4.6b y versiones de restauración

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Estado:** PARCIAL. Fuente: `gisela_pa001_continuacion_3_20261031.zip`. No se alteró la lógica narrativa ni la semántica del ejecutor.

## Resultados verificados

- H4.6b completo: `python -m unittest gisela.engine.tests.test_h46b_central -q`, **11/11 PASS**, 21,708 s.
- Los cuatro métodos pendientes se ejecutaron individualmente y pasaron: `test_rng_reproducible_entre_semillas`, `test_mary_y_reaccion_causal`, `test_compartir_proyeccion_sin_privados` y `test_rechazo_y_revision_obsoleta`.
- Contratos: `python -m unittest discover -s gisela/contracts -p 'test_*.py' -q`, **180/180 PASS**.
- Nueva batería `python -m unittest gisela.engine.tests.test_pa001_version_restore -q`, **4/4 PASS**.
- `python tools/check_quality.py` y `python tools/check_documentation.py`, **PASS**.
- `python -m unittest gisela.engine.tests.test_h46_adventure -q`, **no concluyó en el límite agregado de ejecución**. La prueba de estrés aislada había pasado en el hito previo; esto no prueba un fallo funcional.

## Matriz de versiones observadas

| Formato | Paquete de referencia | Admisión estática | Ejecución | Restauración |
|---|---|---|---|---|
| 1.2 | `h4_exploracion.package.json` | PASS | PASS | Roundtrip y observación idénticos PASS; rechazo digest/versión PASS |
| 1.3 | Sin paquete de referencia en `gisela/packages` | No comprobado en esta pasada | No comprobado | No comprobado |
| 1.4 | `e1_reparacion_sin_jugador.package.json` | PASS | Rechazo `UNSUPPORTED_FORMAT` de evaluación visible E3, **esperado según `support.py`** | No procede para ese paquete |
| 1.5 | `h46b_central_clasificadora.package.json` | PASS | PASS | Roundtrip y observación idénticos PASS; rechazo digest/versión PASS |

**Hallazgo H8, Diferencia entre admisión y ejecutabilidad.** El paquete 1.4 E1 es estructural y semánticamente admisible, pero su evaluación visible no es soportada en ejecución. Es una frontera documentada en el código (`check_supported`); no debe confundirse con compatibilidad de runtime. Antes de modificar algo, revisar el propósito del ejemplo y la documentación de la admisión, y decidir si necesita un diagnóstico de capacidad adicional.

## Invariantes nuevas ancladas a tests

1. Una restauración con el mismo paquete preserva snapshot y observación: `test_pa001_version_restore.py::test_roundtrip_preserves_observation_and_state` (1.2, 1.5).
2. Una restauración con digest alterado se rechaza: `test_pa001_version_restore.py::test_rejects_foreign_package_digest` (1.2, 1.5).
3. La alteración de la versión del snapshot se rechaza: `test_pa001_version_restore.py::test_rejects_foreign_schema_version` (1.2, 1.5).
4. La admisión estática no supone soporte runtime de una evaluación E3 en 1.4: `test_pa001_version_restore.py::test_admitted_v14_e3_example_remains_not_executable`.
5. La integración H4.6b preserva resultados y restauraciones descritos en sus 11 casos: `test_h46b_central.py` completo PASS.

## Cambios y decisión

- Añadido `gisela/engine/tests/test_pa001_version_restore.py`: pruebas de caracterización, sin nuevas dependencias.
- Sin alteraciones en `runtime.py`, `support.py` ni schemas. Se evita cambiar el contrato de admisión sin un requisito aprobado.
- H6: el conjunto H4.6b queda **verificado**; no se identifica defecto. H4.6 completo y la regresión integral quedan pendientes.
- H8: **ABIERTO** hasta acordar la semántica que promete la CLI de admisión frente a la capacidad del runtime.
- PT-05: avance en snapshots 1.2/1.5; falta 1.3 y una referencia 1.4 realmente ejecutable, si existiera, además de matrices exhaustivas.
- PT-07 y PT-08 continúan pendientes; no se acreditó Ren'Py gráfico real.
