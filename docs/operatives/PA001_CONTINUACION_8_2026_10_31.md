# PA-001: Continuación 8: compatibilidad negativa y regresión offline

**Estado: PARCIAL.** Solo GISELA. No se descargó ni ejecutó Ren'Py.

## PT-05: defecto o riesgo investigado

La matriz anterior verificaba versiones 1.2-1.5 separadamente, pero no comprobaba todos los cruces entre versiones. Se añadió `test_snapshots_cannot_cross_supported_versions` a `gisela/engine/tests/test_pa001_version_restore.py`. Admite un paquete representativo de cada versión (1.2: `h4_exploracion`; 1.3: fixture TRAITS; 1.4: fixture de evaluación oculta; 1.5: `h46b_central_clasificadora`), crea snapshots de sesión y comprueba las **12 combinaciones cruzadas**. En todos los casos debe producir `EngineFailure` con código `RESTORE_MISMATCH`. Los cuatro casos de misma versión ya estaban cubiertos con roundtrip; esto no prueba todas las capacidades de cada versión.

| Versión de destino | Snapshot 1.2 | Snapshot 1.3 | Snapshot 1.4 | Snapshot 1.5 |
|---|---|---|---|---|
| 1.2 | roundtrip previo | rechazo | rechazo | rechazo |
| 1.3 | rechazo | roundtrip previo | rechazo | rechazo |
| 1.4 | rechazo | rechazo | roundtrip previo | rechazo |
| 1.5 | rechazo | rechazo | rechazo | roundtrip previo |

No se modificaron código de producción, schemas, ADR ni paquetes narrativos. Este hito amplía evidencia negativa, **no demuestra un defecto de producción**.

## Ejecución y resultados (código de retorno 0 en cada comando)

1. `python -m unittest gisela.engine.tests.test_pa001_version_restore gisela.engine.tests.test_pending -q`: **24 PASS** (antes de añadir la prueba).
2. `python -m unittest gisela.engine.tests.test_traits_alberto_v13 gisela.engine.tests.test_traits_dice_bridge gisela.engine.tests.test_h34c_effects gisela.engine.tests.test_h34d_skills gisela.engine.tests.test_h2_closure -q`: **63 PASS**.
3. `python -m unittest gisela.engine.tests.test_h34a_values gisela.engine.tests.test_h34b_sofia gisela.engine.tests.test_h3_world gisela.engine.tests.test_h45f_scene gisela.engine.tests.test_h46_adventure -q`: **88 PASS**.
4. `python -m unittest gisela.engine.tests.test_pa001_version_restore -q`: **10 PASS**, incluida nueva prueba de 12 cruces.
5. `python -m unittest gisela.engine.tests.test_e0_transactions gisela.engine.tests.test_e0_error_contracts gisela.engine.tests.test_pending gisela.engine.tests.test_pa001_version_restore gisela.engine.tests.test_turn_boundaries -q`: **40 PASS**, incluida nueva prueba.
6. `python tools/check_quality.py`: **PASS**, límites 500/30/3.
7. `python tools/check_documentation.py`: **PASS**, 31 páginas (antes de añadir este documento).

Las cifras reflejan ejecuciones independientes y **no son un total de casos únicos**. Los controles de calidad y documentación se repetirán tras incorporar este documento.

## Pendientes y criterios de cierre

- PT-01: matriz exhaustiva documental-código-prueba todavía pendiente.
- PT-02/PT-03: rutas causales, pendientes y gateway requieren ampliar matriz de cobertura; no se infiere exhaustividad de estas suites.
- PT-05: faltan fronteras de todas las capacidades por versión, incluidos estados pendientes y determinismo posterior a restauración.
- PT-07: la ejecución integral continua sin acreditarse (timeout previo). Estas suites particionadas no reemplazan íntegramente el resultado agregado.
- PT-08: aceptación gráfica Ren'Py excluida y expresamente abierta por instrucción del usuario.

**Cierre:** intervención 8 verificada parcialmente, PA-001 permanece ABIERTA.
