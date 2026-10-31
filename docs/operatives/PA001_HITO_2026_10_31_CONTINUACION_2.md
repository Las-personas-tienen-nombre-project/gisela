# PA-001 — Continuación 2: caracterización, contratos y riesgos

**Estado:** PARCIAL; no equivale a la aprobación del plan. **Origen:** `gisela_pa001_continuacion_20261031.zip`. Se mantiene intacta la semántica del motor. No hay refactorizaciones sin defecto reproducible.

## PT-01 / PT-02: invariantes ancladas en pruebas ejecutadas

| Invariante | Fuente arquitectónica | Test / suite | Resultado de esta ejecución |
|---|---|---|---|
| El cierre de A y entrada a B se confirman como una sola frontera | ADR-007/008 y arquitectura v1.5 §4-5 | `test_turn_boundaries.py::TurnBoundariesTest.test_T04_closed_node_and_started_node_share_single_commit` | suite 4/4 PASS |
| Fallar al entrar a B revierte el salto completo | ADR-007/008 y arquitectura v1.5 §7 | `test_turn_boundaries.py::TurnBoundariesTest.test_T05_failure_starting_B_rolls_back_whole_jump` | suite 4/4 PASS |
| La sesión puede suspenderse sin publicar mundo a medio ejecutar | arquitectura v1.5 §8 | `test_pending.py` | suite 15/15 PASS; no equivale a cobertura de todos los orígenes |
| Admisión, proyecciones y transacciones del MVP básico | arquitectura v1.5 §9,11,14 | `test_mvp.py` | suite 22/22 PASS |
| Cierre de nodo y causalidad | arquitectura v1.5 §4,5 | `test_h2_closure.py` | suite 10/10 PASS |
| Operaciones de entidades y ubicación del mundo | arquitectura v1.5 §6 | `test_h3_world.py` | suite 18/18 PASS |
| Valores y atributos opcionales | arquitectura v1.5 §2,6 | `test_h34a_values.py`, `test_h34b_sofia.py` | 18/18 + 18/18 PASS |
| Efectos y habilidades | arquitectura v1.5 §6 | `test_h34c_effects.py`, `test_h34d_skills.py` | 16/16 + 17/17 PASS |
| Proyección y navegación de escenas | arquitectura v1.5 §9 | `test_h45f_scene.py` | 19/19 PASS |
| Paquetes admitidos cumplen sus contratos estáticos comprobados | arquitectura v1.5 §1,11 | `python -m unittest discover -s gisela/contracts -p 'test_*.py' -q` | 179/179 PASS |

**Importante:** un test correcto establece únicamente la propiedad que realmente comprueba. La matriz no afirma prueba formal de todas las rutas equivalentes. El total de suites del ejecutor confirmado *en esta continuación* es 157 tests (4+15+22+10+18+18+18+16+17+19). No se incluye una ejecución integral en este total.

## PT-05: observaciones sobre versionado

El árbol conserva contratos de base y subdirectorios `v1_3`, `v1_4`, `v1_5`. La arquitectura vigente §1 prescribe schema + semántica + prueba dinámica; §10 prohíbe migraciones automáticas de guardados entre paquetes con digests diferentes. Se ejecutaron 179 pruebas de contratos; esta evidencia **no** establece una matriz completa de pares (versión de paquete, versión de snapshot), ni avala migraciones cruzadas. No introducir adaptadores implícitos ni aceptar snapshots por similitud estructural.

## Hallazgos nuevos o afinados

1. **H6 — Rendimiento/diagnóstico de integración:** la suite `test_h46_adventure.py` no concluyó con un límite de 9 s, sin diagnóstico de fallo. La ejecución de `test_h46b_central.py` quedó interrumpida por el límite del comando contenedor. Es preciso aislar métodos concretos y distinguir un caso que tarda de un posible bucle. No se puede atribuir causalidad al motor sin más evidencia.
2. **H7 — Mensaje de CLI de admisión potencialmente obsoleto:** `gisela/contracts/admit_package.py::cli()` usa una descripción fija «contratos v1.2», mientras que el árbol contiene contratos posteriores. Es una divergencia de presentación, no evidencia de admisión incorrecta. Requiere confirmar el alcance de la CLI antes de actualizar la etiqueta; no modificar la lógica de admisión.
3. La fuente de verdad de los contratos es el schema complementado por validación semántica; la aprobación de una definición no sustituye su ejecutabilidad ni restaurabilidad (arquitectura vigente §1 y §11).

## Cambios y decisiones

**Cambios de código:** ninguno en esta continuación. **Documentación:** este registro con anclajes y resultados. **DECIDIDO durante la ejecución:** no modificar persistencia ni máquina de ejecución por hipótesis de complejidad. **PENDIENTE:** aislar métodos lentos de H4.6/H4.6b, obtener regresión integral concluyente, matriz de restauración por versión y ejecución real del SDK Ren'Py. **NO VERIFICADO:** salida completa de `check_project.py`; no se interpreta su timeout como éxito ni como fallo.

## Comandos de reproducción

```bash
python -m unittest discover -s gisela/contracts -p 'test_*.py' -q
python -m unittest discover -s gisela/engine/tests -p test_turn_boundaries.py -q
python -m unittest discover -s gisela/engine/tests -p test_pending.py -q
python -m unittest discover -s gisela/engine/tests -p test_mvp.py -q
python -m unittest discover -s gisela/engine/tests -p test_h2_closure.py -q
python -m unittest discover -s gisela/engine/tests -p test_h3_world.py -q
```

## Criterio de salida de este avance

Este hito documenta invariantes y la evidencia obtenida; **no cierra PT-02, PT-05 ni el conjunto PA-001**.
