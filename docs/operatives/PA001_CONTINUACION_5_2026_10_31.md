# PA-001: Continuación 5: matriz completa 1.2-1.5 y error de nodo agotado

**Estado:** parcial, basado en `gisela_pa001_continuacion_4_20261031.zip`. Se mantienen las decisiones de ADR-020, ADR-022, ADR-023 y GISELA_ADR_001_017. No se incorporaron dependencias, subsistemas ni schemas nuevos.

## Matriz de compatibilidad demostrada

| Formato | Referencia | Admisión | Ejecución | Exportación/restauración inicial | Rechazo digest y versión |
|---|---|---|---|---|---|
| 1.2 | h4_exploracion.package.json | PASS | PASS | PASS | PASS |
| 1.3 | fixture de `test_traits_alberto_v13` | PASS | PASS | PASS | PASS |
| 1.4 | fixture E2 de evaluación oculta, con paso `narrate` observable | PASS | PASS | PASS | PASS |
| 1.5 | h46b_central_clasificadora.package.json | PASS | PASS | PASS | PASS |

La matriz usa casos representativos en el estado inicial; **no** certifica todos los estados intermedios ni operaciones pendientes de cada formato. `e1_reparacion_sin_jugador.package.json` v1.4 usa presentación reservada E3: se admite estáticamente pero el runtime lo rechaza con `UNSUPPORTED_FORMAT`, según ADR-022 y ADR-023. H8 se clasifica **CONSERVAR (frontera intencional)**; debe documentarse en la interfaz de admisión si se exige una comprobación explícita de ejecutabilidad, sin cambiar por ello el contrato.

## H9: defecto descubierto y corregido

**Hecho:** la fixture v1.4 oculta sin paso observable, sin escena y sin final supera la admisión, pero `new_session` fallaba con un `KeyError: current_scene` desde `reading_log._display`. `GISELA_ADR_001_017.md` exige un error técnico identificable cuando se agota un nodo sin escena, transición ni final. El error Python crudo incumplía la frontera pública.

**Corrección mínima:** `GiselaSession._confirm_initial` verifica `status == 'exploring'` sin `current_scene` antes de incorporar el registro de lectura o publicar estado, y lanza `EngineFailure('INVALID_STATE', ...)`. No se altera el tratamiento de finales explícitos ni de escenas válidas. Este guard cubre la ruta inicial observada; la comprobación de rutas equivalentes no iniciales queda abierta.

**Prueba ancla:** `gisela/engine/tests/test_pa001_version_restore.py::test_v14_exhausted_node_without_scene_has_engine_error`. Falló antes del cambio (KeyError) y pasó después (INVALID_STATE). Las otras tres pruebas nuevas anclan exportación/restauración y rechazo de digest o versión en v1.3 y v1.4.

## Validaciones ejecutadas después de modificar el runtime

- `python -m unittest gisela.engine.tests.test_pa001_version_restore -q`, 8/8 PASS.
- `python -m unittest gisela.engine.tests.test_e2_evaluations -q`, 23/23 PASS.
- `python -m unittest discover -s gisela/contracts -p 'test_*.py' -q`, 180/180 PASS.
- `python tools/check_quality.py`, PASS.
- `python tools/check_documentation.py`, PASS (31 páginas).

## Pendientes

- PT-02: verificar fin de nodo sin escena en rutas no iniciales y reactividad/reanudación.
- PT-05: ampliar restauración a pendientes y recorridos de acciones de cada versión cuando corresponda.
- PT-07: ejecutar regresión integral en entorno sin los límites actuales; H4.6 completa no acreditada.
- PT-08: aceptación gráfica en Ren'Py real no acreditada.
- H1-H6 siguen abiertos salvo verificaciones específicas ya documentadas; H7 corregido, H8 conservado con justificación, H9 corregido en ruta inicial.
