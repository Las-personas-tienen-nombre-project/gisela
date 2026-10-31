# GISELA — Informe de implementación del validador semántico estático v0.1

**Fecha:** 29 de octubre de 2026  
**Contratos:** JSON Schema v1.1, arquitectura consolidada v1.2, ADR-001–014.

## Resultado

Se preparó un validador semántico estático independiente de Ren'Py y de cualquier ejecutor narrativo. Conserva inalterados los 13 schemas JSON v1.1 y añade `semantic_validator.py`, `test_semantic_validator.py`, documentación y ejemplos. Los scripts son ejecutables offline con Python, `jsonschema` y `referencing`.

El validador comprueba identidades, referencias cruzadas, destinos narrativos, tipado de operaciones y condiciones, posiciones del mundo, capacidades de habilidades, atributos, hechos, localización, estados de snapshots, historial, transacciones pendientes (solo invariantes comprobables) y la pertenencia de un `Act` a una proyección aportada.

## Ejecución comprobada

| Prueba | Resultado |
|---|---|
| Suite estructural original | 41/41 |
| Suite semántica nueva | 69/69 |
| Verificación de 13 schemas, paquete y 7 fixtures originales | Correcta |
| Paquete autoral de ejemplo bajo validador semántico | 0 errores, 0 advertencias |
| Snapshot `session_node` | 0 errores, advertencia `DIGEST_UNVERIFIED` |
| Nueva fixture de operación pendiente | 0 errores, advertencias `DIGEST_UNVERIFIED` y `REPLAY_UNVERIFIED` |

La cifra **110/110** cubre pruebas del validador y schemas; no representa cobertura de comportamiento de GISELA. Las fixtures ilustrativas antiguas no deben confundirse con snapshots restaurables.

## Debilidades de la especificación encontradas

1. `history.executions[].selected_options` almacena solo `option_id`, aunque este ID es único únicamente dentro del `choice` que lo declara. Falta asociarlo con `step_id` en la traza de la ejecución.
2. `pending_transaction.source.scene_action` contiene escena y acción, pero omite el elemento al que pertenece una acción de elemento. El validador impone unicidad de `action.id` dentro de una misma escena; para permitir reutilización por elemento habrá que añadir `element` al contrato.
3. La prueba semántica de integridad de historial detecta que `turn=1` con cero ejecuciones es incoherente: la estructura JSON por sí sola no lo detecta.
4. Los snapshots de ejemplo usan digests ficticios; todavía no está definido el procedimiento canónico para calcularlos. No puede declararse una restauración íntegra.
5. El tipo de referencia contextual puede analizarse parcialmente, pero la ligadura real de `$actor`, `$target` y la selección concreta de consultas depende del contexto runtime. El validador no suplanta ese contexto.
6. Las políticas de retorno y las coincidencias de varias condiciones de habilidad exigen evaluación dinámica; solo se rechazan contradicciones incondicionales comprobables.

## Criterio de corrección aplicado

- No se ha creado una segunda autoridad transaccional: el validador es una herramienta de admisión, no administra sesiones.
- No se ha introducido interpretación de reglas dentro de Ren'Py.
- No se han establecido restricciones a la calidad narrativa, a los finales ni a los ciclos interactivos sin evidencia técnica.
- No se han alterado los schemas v1.1 por iniciativa propia. Los cambios de contrato detectados constan como correcciones necesarias antes de codificar el historial del motor.
- No se afirma que la validación esté cerrada: reanudación, atomicidad, privacidad y determinismo real requieren un ejecutor.

**Siguiente decisión técnica:** elegir si `selected_options` debe convertirse en lista de `{step_id, option_id}` o en eventos de selección en `history.trace` con procedencia inequívoca. La primera alternativa es más sencilla si se requiere una vista resumida de las elecciones de cada ejecución; la segunda elimina redundancias y aprovecha el historial único. Recomiendo la segunda solo si la traza queda formalmente definida como autoritativa para elecciones; en caso contrario, prefiero la primera por claridad.
