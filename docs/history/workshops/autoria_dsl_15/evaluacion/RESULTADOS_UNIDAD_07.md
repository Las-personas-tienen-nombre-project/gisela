# Evidencia: Unidad 7 (integración de Tegularis)

## Base inspeccionada

Repositorio de `GISELA_workshop_unidad_06.tar.gz`; paquete `14_presentacion_semantica_v082d.package.json`. Todos los ejercicios se derivan de copias completas; no se cambió el paquete productivo de referencia ni el motor.

## Verificaciones ejecutadas

- `PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_07.py`: **aprobado**, 6/6 paquetes de práctica admitidos, 6/6 soluciones admitidas e idénticas al canon, 1/1 referencia inválida rechazada; condiciones estructurales sobre umbral de Pride, efecto concedido, fase de Última llama y captura de escudo confirmadas. Registro: `LOG_UNIDAD_07.txt`.
- `PYTHONPATH=. python -m pytest -q packages/tegularis_the_son_of_the_volcan/test_desenlaces_v072.py packages/tegularis_the_son_of_the_volcan/test_balance_v078.py packages/tegularis_the_son_of_the_volcan/test_cierre_v077.py`: **21/21 aprobadas**. Registro: `LOG_UNIDAD_07_PRUEBAS.txt`.

## Alcance y limitaciones

Los seis ejercicios se entregan como **variaciones admitidas, deliberadamente no canónicas**: se usan para investigar una mecánica y corregirla, no como nuevas versiones balanceadas de Tegularis. Los solucionarios son copias exactas del paquete original.

Las 21 pruebas pertenecen al repositorio existente y verifican sus escenarios específicos; no sustituyen una campaña de cobertura dirigida con todas las combinaciones de escudo grupal, protecciones individuales, estados, tiradas y desenlaces, ni certifican por sí solas que los seis paquetes alterados hayan alcanzado sus ramas modificadas en una sesión GLAUQUIR. La ejecución de cada rama de los ejercicios y la regresión total quedan **pendientes**.

Durante la inspección se constató que una referencia inexistente en la operación `apply_effect` de la política de Pride puede ser admitida por el validador actual. **No se presenta esa admisión como un comportamiento válido de ejecución.** El caso de rechazo de esta unidad usa una habilidad NPC inexistente, que sí se comprueba que es rechazada. Conviene revisar por separado la cobertura semántica de referencias en las políticas de acontecimientos antes de convertirla en una garantía de autoría.

## Próximo paso

Unidad 8: presentación declarativa y comparación de trazas de un mismo encuentro, asegurando que los cambios visuales no modifiquen el estado lógico.
