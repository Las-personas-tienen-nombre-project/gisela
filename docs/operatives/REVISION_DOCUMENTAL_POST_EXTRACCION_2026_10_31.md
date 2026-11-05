# Revisión de documentación operativa tras la extracción independiente

Estado: VERIFICADO para los controles enumerados. Fecha: 2026-10-31.

## Alcance

Se corrigieron las referencias a orquestadores ausentes del repositorio independiente en las páginas de entrada mantenidas, sin editar los ADR y registros históricos. El archivo `docs/history/GUIA_DOCUMENTACION_ES_CL_original.md` conserva las instrucciones de su época: no se debe interpretar como una orden vigente para ejecutar `tools/check_project.py`.

## Cambios

- Se eliminaron de las páginas activas las instrucciones para ejecutar `tools/check_project.py`, sustituyéndolas por verificadores presentes en este árbol. Esto incluye los README de engine, contracts, narrative_conditions y el documento de validación semántica.
- Se añadió `pytest>=8,<10` a `requirements-dev.txt`, porque la configuración del proyecto contempla pruebas con pytest. No se modificó la suite ni el runtime.
- Se añadió `.gitignore` y se excluyeron de esta entrega los archivos generados `__pycache__`/`*.pyc`. Los archivos que ya estuvieran versionados deben dejar de rastrearse explícitamente en Git; `.gitignore` no los elimina del índice.
- El README documenta la forma de Act, la respuesta de error como diccionario, la exclusividad de la puerta de entrada cuando se vincula `ExecutionGateway`, y enlaza el contrato de clientes.
- La guía rápida explica la instalación editable para imports externos y el uso de recorridos guionizados en lugar de confiar en `--auto` para completar Faro y Central.
- Se añadió una prueba de regresión para evitar que las páginas principales vuelvan a recomendar los orquestadores ausentes.

## Verificación ejecutada

- `python tools/check_doc_links.py`: correcto.
- `python tools/check_quality.py`: correcto.
- `python -m unittest discover -s tools -p 'test_*.py' -q`: 12 pruebas correctas.
- `python -m unittest discover -s gisela/contracts -p 'test_*.py' -q`: 180 pruebas correctas.
- `python -m unittest discover -s dice/tests -p 'test_*.py' -q`: 15 pruebas correctas.
- `python -m unittest discover -s traits/tests -p 'test_*.py' -q`: 25 pruebas correctas.
- `python -m unittest discover -s mary/tests -p 'test_*.py' -q`: 21 pruebas correctas.

No se ejecutó en esta intervención la suite completa del motor ni los recorridos integrales; no se reutiliza como evidencia de esta revisión la cifra de 630 pruebas ni los resultados atribuidos al commit `c9eee2f`, ya que este ZIP no contiene metadatos Git suficientes para corroborar esa revisión.

## Límites

El detector de enlaces comprueba rutas locales Markdown, no enlaces HTTP ni referencias de texto plano dentro de registros históricos. La guía con secciones sección 4, sección 7, sección 8, sección 10 y sección 11 mencionada en la revisión no aparece como documento vigente identificable en este ZIP; las correcciones se aplicaron a los documentos de entrada realmente presentes, sin fabricar esa guía. La aceptación gráfica con Ren'Py queda fuera del alcance de este repositorio independiente.
