# PA-001: Continuación 3: H6, H7 y compatibilidad

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Estado:** PARCIAL. Fuente: `gisela_pa001_continuacion_2_20261031.zip`. No se alteró la lógica del motor.

## Hallazgos y evidencia

- **H6 (precisado; no defecto demostrado):** `test_h46_adventure.py` completó consecutivamente los casos 01-11. Aislamiento de `H46Faro.test_12_seed_determinism_and_stress`: **PASS (17,524 s)**. El límite anterior de 9 segundos era insuficiente; no se puede inferir un ciclo infinito. El archivo H4.6b completó hasta `test_reconocimiento_y_restauracion`; el siguiente `test_rng_reproducible_entre_semillas` empezó, pero la ejecución se interrumpió por límite del entorno. **PENDIENTE** ejecutar sus métodos restantes individualmente y medirlos.
- **H7 (CORREGIDO):** el texto de ayuda de `gisela/contracts/admit_package.py` decía "contratos v1.2", sin reflejar versiones admitidas posteriores. Cambiado únicamente a "paquetes autorales", para evitar prometer una versión fija. Prueba anclada: `gisela/contracts/test_cli_description_pa001.py::TestAdmissionCliHelp.test_help_does_not_claim_legacy_only` (**PASS**).
- **Contratos:** `python -m unittest discover -s gisela/contracts -p 'test_*.py' -q` **180/180 PASS**, incluyendo el nuevo test. Esto prueba los casos implementados, **no** acredita compatibilidad exhaustiva entre versiones de snapshots.
- **Calidad:** `python tools/check_quality.py` **PASS**. `python tools/check_documentation.py` **PASS** (31 páginas). Manifiesto actualizado: 306 entradas.

## Invariantes comprobadas y límites

| Propiedad | Fuente / contrato | Prueba | Evidencia |
|---|---|---|---|
| La CLI no limita engañosamente la admisión a una única versión heredada | `admit_package.py` y contrato de admisión vigente | `test_cli_description_pa001.py` | PASS |
| Mismo seed y ruta completa producen el mismo estado final en Faro | determinismo GISELA; contrato H4.6 | `test_h46_adventure.py::H46Faro.test_12_seed_determinism_and_stress` | PASS, cuatro semillas, repetidas |
| Restauración de pendiente no adelanta las consecuencias del Faro | arquitectura v1.5, suspensión atómica | `test_h46_adventure.py::H46Faro.test_07_pending_is_fixed_and_restorable` | PASS dentro de la ejecución 01-11 |
| La selección obsoleta no altera el estado | Observe/Act, revisión | `test_h46_adventure.py::H46Faro.test_09_stale_action_and_unoffered_do_not_mutate` | PASS dentro de 01-11 |
| Gateway reintenta exactamente una vez por ID de comando | ADR-020 | `test_h46_adventure.py::H46Faro.test_10_gateway_nonhuman_exactly_once` | PASS dentro de 01-11 |

## Cambios

1. Una cadena descriptiva de la CLI, sin modificar lógica de admisión.
2. Una prueba de regresión acotada para H7.
3. Este documento, y actualización del manifiesto.

## Pendientes abiertos

- H6: completar H4.6b con ejecución individual por método y el archivo H4.6 completo en un entorno sin límite agregado.
- PT-05: matriz formal de versiones de paquetes y snapshots; las 180 pruebas contractuales no sustituyen pruebas de restauración cruzada.
- PT-07: regresión integral `check_project.py` concluida y Ren'Py real.

**Regla de decisión:** no optimizar código narrativo basándose únicamente en una duración de prueba. Medir, caracterizar y demostrar primero.
