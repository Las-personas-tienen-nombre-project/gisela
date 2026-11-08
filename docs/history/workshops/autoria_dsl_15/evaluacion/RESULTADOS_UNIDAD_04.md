# Validación de la Unidad 4: Rasgos y contribuciones

Base: `14_presentacion_semantica_v082d.package.json` (copias independientes). El paquete productivo no se ha modificado.

## Resultados comprobados en esta sesión

- **Admisión pública:** cinco paquetes de inicio y cinco solucionarios **admitidos**, mediante `gisela.contracts.admit_package_file`.
- **Rechazo esperado:** el sexto paquete, con rasgo inexistente, **rechazado** por validación de contratos.
- **TRAITS público:** la herramienta `evaluacion/comprobar_unidad_04.py` comprobó `dodge` activo/inactivo; cancelación +2/-2; rasgo `ojo_certero` solo para atacante con `hit`; reducción física de `escamas` frente a contexto mágico; tres contextos aislados de `pride_redux`; y ausencia de ese rasgo en el estado inicial.
- **Pruebas existentes:** `python -m unittest traits.tests.test_traits gisela.engine.tests.test_traits_dice_bridge -q`: **31 pruebas, OK**.

## Alcance de la evidencia

Estas comprobaciones verifican admisión y evaluación contextual de contribuciones, **no** demuestran la resolución completa de la batalla ni el momento de aplicación real de Pride en una partida dirigida. No se ha ejecutado aquí el recorrido `--auto` de cada variante ni la regresión general. Las propiedades nuevas de `paso_torpe` y `ojo_certero` existen solamente en las copias de práctica.

Para reproducir: desde la raíz, `PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_04.py`; para pruebas de integración, `PYTHONPATH=. python -m unittest traits.tests.test_traits gisela.engine.tests.test_traits_dice_bridge -q`.
