# Seguimiento de certificación: workshop GISELA DSL 1.5

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](../../../../../CHANGELOG.md).

Fecha: 2026-11-04.
Base: `GISELA_workshop_auditoria_final_pendiente.tar.gz`.

## Dictamen

**Certificación integral: pendiente.** No se declara regresión aprobada ni reproducción autónoma de Tegularis certificada. Este intento se limita a la reproducción de controles dirigidos y a registrar los límites de tiempo de las suites extensas.

## Controles ejecutados sobre el archivo entregado

| Control | Resultado | Evidencia |
|---|---|---|
| `python tools/check_quality.py` | Aprobado | `evidencia_certificacion/focused.log` |
| `python tools/check_doc_links.py` | Aprobado | `evidencia_certificacion/focused.log` |
| `pytest` de prioridades NPC, balance v0.7.8 y cierre v0.7.7 | 26/26 aprobadas, 16,61 s | `evidencia_certificacion/focused.log` |
| Suite amplia de contratos, motor, Tegularis y bibliotecas | Interrumpida por límite externo tras imprimir progreso al 34%; no hay recuento final | `evidencia_certificacion/regression.log` |
| Suite dirigida de desenlaces v0.7.2, actuación nativa v0.7 y cartas v0.7.1 | Interrumpida por límite externo después de 38 indicadores de progreso; no hay recuento final | `evidencia_certificacion/branches.log` |

Se usó `PYTHONPATH=.:engine/tests` para la regresión y para las suites dirigidas. Las dos ejecuciones interrumpidas **no cuentan como aprobadas**, independientemente de los puntos impresos.

## Reproducción

Desde la raíz del repositorio:

```sh
PYTHONPATH=.:engine/tests python -m pytest -q \
  gisela/contracts gisela/engine/tests \
  gisela/packages/tegularis_the_son_of_the_volcan \
  mary/tests dice/tests traits/tests narrative_conditions/tests

PYTHONPATH=.:engine/tests python -m pytest -q \
  engine/tests/test_npc_skill_priorities.py \
  packages/tegularis_the_son_of_the_volcan/test_balance_v078.py \
  packages/tegularis_the_son_of_the_volcan/test_cierre_v077.py
```

Para la suite amplia debe emplearse un entorno que permita completar el proceso y conservar su código de salida. Esta ejecución fue terminada por el límite del entorno, sin traceback en el fragmento registrado; esto no prueba ni descarta fallos posteriores.

## Bloqueadores remanentes

1. Regresión integral completada y registrada.
2. Ejecución verificable de los 84 JSON del workshop según su naturaleza (válidos y negativos), no solo análisis de sintaxis.
3. Cobertura dirigida y trazas de cada rama de Última llama, Pride, acierto, fallo, empate y todos los desenlaces.
4. Comparaciones deterministas y de restauración en la reconstrucción final.
5. Evidencia pedagógica del ejercicio autónomo por un alumno, sin consultar solucionarios.

La guía del DSL y el glosario permanecen en la documentación general de GISELA, no se duplican aquí. No se modificó el motor, sus contratos ni los paquetes canónicos para esta auditoría.
