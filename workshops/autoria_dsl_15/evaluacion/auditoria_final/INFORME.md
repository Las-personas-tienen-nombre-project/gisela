# Auditoría de aceptación del workshop GISELA DSL 1.5

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](../../../../docs/operatives/REVISION_DOCUMENTAL_2026_11_04.md).

**Fecha:** 2026-11-04. **Base:** `GISELA_workshop_correccion_pedagogica_03_unidad_09.tar.gz`.

## Dictamen

**Aceptación final: PENDIENTE.** El material documental está presente (nueve unidades, guía del alumno, guía del instructor, laboratorios y rúbrica), pero la suite general y los recorridos dirigidos de todos los desenlaces no están certificados. No hay evidencia de aprendizaje observada con alumnos reales.

## Controles reproducidos en esta auditoría

| Control | Resultado | Evidencia |
|---|---|---|
| Nueve unidades de documentación | Presente | `unidades/01_...` a `09_...` |
| JSON en ejercicios, soluciones y laboratorios | 84/84 sintácticamente válidos | inventario local |
| Calidad estructural | Aprobado | `logs/quality.log` |
| Enlaces Markdown locales | Aprobado | `logs/links.log` |
| Comportamiento dirigido `dodge` | +2, 0, 0, +2 y consulta pura | `logs/traits_npc.log` |
| Políticas NPC prioritarias | 12/12 pruebas aprobadas | `logs/npc_tests.log` |
| Balance y cierre de Tegularis | 14/14 pruebas aprobadas | `logs/tegularis_tests.log` |
| Suite dirigida conjunta NPC + Tegularis | 26/26 pruebas aprobadas | `logs/focused_suite.log` |
| Verificación Unidad 4 | Terminada satisfactoriamente | `logs/workshop_u4.log` |
| Verificación Unidad 5 | Admisión y propiedades aprobadas | `logs/workshop_u5.log` |
| Verificación Unidad 6 | Admisión y propiedades aprobadas | `logs/workshop_u6.log` |
| Verificación Unidad 7 | Admisión y propiedades aprobadas; ramas no certificadas | `logs/workshop_u7.log` |
| Integridad de motor/contratos/paquete canónico examinados | Tres archivos con SHA-256 idéntico al repositorio base | comprobación de hashes |

Los verificadores de unidades comprueban en parte **admisión y propiedades**: no equivalen a cobertura dinámica de todas las ramas. La Unidad 8 requiere un recorrido más largo y no concluyó en la ejecución de esta auditoría.

## Regresión general y problemas de ejecución

Se intentó ejecutar una regresión amplia de contratos, motor, bibliotecas y Tegularis. El primer intento no pudo colectar un test por falta de ruta de importación (`test_actuation_public_v073`); al suministrar `PYTHONPATH=.:engine/tests`, se superó esa dificultad. A continuación, fallaron pruebas por **disposición del árbol de trabajo**: algunos tests esperan el proyecto `gisela` dentro de una raíz superior junto a `docs/` y `tools/` (`test_determinism.py` y `test_h45_cli.py`). Al introducir enlaces simbólicos **fuera del repositorio** para reproducir esa disposición, la ejecución progresó más allá de esos casos, pero se interrumpió aproximadamente a mitad de la suite debido al límite temporal. **No hay resultado completo ni se puede declarar la regresión verde o roja.** Consulte `logs/regression*.log` y `logs/first_failure*.log`.

La corrección correcta es ejecutar los tests con el layout y entorno documentados oficialmente; no modificar las pruebas ni el motor para forzar el resultado.

## Bloqueadores de aceptación

1. Completar y registrar la regresión íntegra sin límite interrumpido, en el layout esperado.
2. Ejecutar y registrar todos los ejercicios y solucionarios, no solamente admitirlos o comparar propiedades.
3. Probar dirigidamente acierto, fallo, empates, Pride, Última llama y **todos los desenlaces** con semillas, decisiones y trazas causales reproducibles.
4. Certificar determinismo y guardado/restauración de la reconstrucción final de Tegularis, no solo en laboratorios aislados.
5. Verificar que el desafío autónomo puede resolverse con documentación oficial y sin consultar solucionarios, mediante una prueba pedagógica controlada.

## Límites y arquitectura documental

La referencia DSL y el glosario **no se duplican en el workshop**: deben mantenerse en la documentación general de GISELA. Los materiales didácticos enlazan esa referencia. No se ha alterado el motor para pasar las verificaciones.

## Repetición mínima de controles aprobados

Desde la raíz de GISELA, con el layout que exigen sus tests:

```bash
python tools/check_quality.py
python tools/check_doc_links.py
PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_puentes_04_06.py
PYTHONPATH=. python -m pytest -q engine/tests/test_npc_skill_priorities.py \
  packages/tegularis_the_son_of_the_volcan/test_balance_v078.py \
  packages/tegularis_the_son_of_the_volcan/test_cierre_v077.py
```

**No declarar aprobado el workshop completo** hasta cerrar los cinco bloqueadores.
