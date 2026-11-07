# Corrección integral de los siete hallazgos de auditoría pedagógica

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](../../../CHANGELOG.md).

## Alcance

Se actualizó el workshop dentro de `workshops/autoria_dsl_15/`, sin modificar el motor, contratos ni paquetes canónicos de Tegularis. La referencia oficial del DSL y el glosario permanecen fuera del workshop.

| Hallazgo | Corrección aplicada | Evidencia |
|---|---|---|
| Comandos que ejecutaban originales | Ruta única `mi_trabajo/u01..u08.package.json`; comandos sobre la copia; invocación por módulo del validador | `VALIDACION_COPIAS_ALUMNO.json`: 8/8 admitidos |
| Integración antes del laboratorio | Unidades 1 a 8 comienzan con enlace y secuencia mínima; integración productiva después | encabezados de `unidades/` |
| Guía desactualizada | Actualizados `README.md` y `GUIA_DEL_ALUMNO.md` con índice y estado real | revisión de los enlaces |
| Falta de laboratorio U8 | Paquete reducido `paquetes/08_progresivo/08_laboratorio.package.json` y README para crear regiones | paquete admitido y ejecutado; región adicional admitida; vista inexistente rechazada |
| Modificar sin crear | Seis ejercicios de transferencia con declaración omitida y solución de referencia; región propia en U8 | soluciones 2 a 7 admitidas: 6/6 |
| Trazas poco enseñadas | `COMO_COMPROBAR.md` con comandos, resultados, diagnóstico y ficha | guía vinculada desde unidades y guía del alumno |
| U9 sin hitos evidenciables | `evaluacion/09_integracion/HITOS.md` con archivos, predicciones, pruebas negativas y registros por hito | rúbrica y Unidad 9 enlazadas |

## Comprobaciones reproducidas

- `python tools/check_doc_links.py`: aprobado.
- `python tools/check_quality.py`: aprobado.
- `PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/uNN.package.json`, N=01..08: 8/8.
- Admisión de seis soluciones de transferencia: 6/6.
- El nuevo paquete reducido de presentación se admite y concluye un recorrido automático.
- La construcción de una región adicional se admite; una región que apunta a `vista_que_no_existe` se rechaza con `PRESENTATION_INVALID`.
- Archivos incompletos de transferencia: unidades 3, 4 y 5 son rechazadas; unidades 2, 6 y 7 se admiten porque el validador no exige toda la intención pedagógica. La documentación distingue expresamente ambos casos.

## Segundo examen en frío: debilidades y ajustes

1. El comando directo `python gisela/contracts/admit_package.py` falla en este entorno con paquetes con presentación, por imports relativos. Se sustituyó en la documentación del workshop por `python -m gisela.contracts.admit_package` (sin modificar código de GISELA).
2. Las soluciones incompletas no siempre producen error de admisión: el enunciado ya no promete un rechazo en todos los casos.
3. `--auto` solo cubre un recorrido y no certifica ramas, determinismo ni persistencia. Se explicó en la ficha y en los hitos de la Unidad 9.
4. La presentación textual puede no mostrar todos los detalles de cada vista: el laboratorio exige separar esa limitación de la admisión de la declaración.
5. La Unidad 6 conserva respuesta guionizada de introducción y enseña la política NPC autónoma con material productivo; no se las equipara.

## Límites de certificación

La ejecución agregada de todos los recorridos y la regresión general no terminaron en esta pasada. No existe evidencia de un alumno real que complete el taller, ni cobertura dirigida de todas las ramas de Última llama y desenlaces. Se requiere ejecutar estas pruebas por separado antes de certificar el workshop. El motor y las reglas canónicas no han sido cambiados para obtener resultados verdes.
