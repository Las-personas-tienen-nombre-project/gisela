# Evidencia de la corrección pedagógica 03

## Alcance efectivamente comprobado

- Se verificó el paquete reducido de Unidad 4 con `contribution_total` a través de GISELA: `defender` + `evasion` = **2**; `actor` + `evasion` = **0**; `defender` + etiqueta distinta = **0**; `defender` + `evasion` y otra etiqueta = **2**. El estado de la sesión permaneció idéntico antes y después de la consulta.
- Se ejecutaron las pruebas ya existentes de políticas reales `play_first_skill`: `engine/tests/test_npc_skill_priorities.py`, **12/12 aprobadas**. Incluyen recursos insuficientes, guardas, rama `otherwise`, referencia inválida y restauración.
- Se agregó Unidad 9 y su rúbrica. Su especificación de evaluación autónoma es **material didáctico**, no evidencia de que alumnos hayan reproducido el encuentro.

## Limitaciones

La Unidad 6 mínima conserva su respuesta guionizada y lo indica expresamente. La selección NPC real se estudia y comprueba con el paquete oficial `tegularis_npc_prioridades_v03`. No se ha certificado una nueva política autónoma construida por un alumno ni la cobertura exhaustiva de Última llama. No se han modificado el motor, los contratos, los esquemas ni el balance canónico.

## Repetición

```bash
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_puentes_04_06.py
PYTHONPATH=. python -m pytest -q engine/tests/test_npc_skill_priorities.py
python tools/check_quality.py
python tools/check_doc_links.py
```
