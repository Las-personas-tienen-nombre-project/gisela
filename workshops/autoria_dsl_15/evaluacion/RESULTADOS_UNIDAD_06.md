# Resultados de comprobación: Unidad 6

Fuente: `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`. Se conservaron sin cambios los paquetes canónicos; las alteraciones son copias dentro de `ejercicios/06_actuacion/`.

## Comprobaciones ejecutadas

- **Admisión semántica:** cinco paquetes válidos de ejercicios y sus cinco solucionarios admitidos. Los valores modificados de los ejercicios difieren de los originales; los cinco solucionarios son idénticos al paquete de referencia completo. Herramienta de instructor: `PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_unidad_06.py`.
- **Rechazo dirigido:** `06_referencia_invalida.package.json`, que menciona `habilidad_inexistente`, fue rechazado como corresponde. Se debe corregir antes de usar el paquete.
- **Pruebas existentes dirigidas:** `PYTHONPATH=. pytest -q engine/tests/test_actuation_public_v073.py engine/tests/test_npc_skill_priorities.py engine/tests/test_npc_skill_arguments_v04.py` Resultado: **34 passed**, evidencia `LOG_UNIDAD_06_PRUEBAS.txt`. Incluyen Observe/Act, revisiones, rechazo sin mutación, restauración, selección condicionada y referencias.
- **Ejecución por GLAUQUIR:** `python -m gisela.cli.glauquir --auto --actuation --rounds 1 --package workshops/autoria_dsl_15/soluciones/06_actuacion/01_iniciativa.package.json` Resultado: salida 0 y una ronda finalizada, evidencia `LOG_UNIDAD_06_GLAUQUIR.txt`.

## Alcance y límites

La admisión valida estructura y contratos, **no** demuestra que cada política se dispare en cada escenario. Una ronda automática no demuestra todas las ramas ni prueba los cambios de comportamiento de las cinco variaciones: las pruebas dirigidas existentes cubren mecanismos subyacentes, no son una comparación de traces de cada ejercicio. No se ejecutó la regresión general en esta etapa. La verificación de balance completo y cobertura de ramas del paquete final sigue pendiente de la integración en unidades 7 y 9.

**Estado:** material de Unidad 6 preparado, admitido y comprobado de manera dirigida; no certificación final del workshop.
