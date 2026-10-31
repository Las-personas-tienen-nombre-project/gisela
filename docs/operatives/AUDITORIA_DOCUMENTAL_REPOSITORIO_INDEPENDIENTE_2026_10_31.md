# Auditoría documental del repositorio independiente: 2026-10-31

## Alcance

Revisión del ZIP `gisela.zip` entregado para comprobar rutas locales enlazadas desde Markdown, independencia del lector respecto del demo, documentación de entrada y viabilidad de verificar regresiones. Los documentos de `docs/history` son antecedentes históricos, no instrucciones vigentes. No se alteraron las reglas narrativas, los schemas ni el motor.

## Hallazgos y resolución

1. **Enlaces locales rotos.** Se encontraron referencias Markdown a guías, índice, referencia de nombres, módulo `renpy/` y archivos de la antigua estructura que no existen en esta extracción. Se corrigieron enlaces hacia documentos presentes, se crearon guías de orientación que señalan documentos existentes, y en registros históricos se convirtieron enlaces no recuperables en referencias textuales, sin inventar su contenido.
2. **Identidad desactualizada.** El README raíz, el README del paquete y el roadmap aún describían la futura extracción de GISELA. Se actualizaron para explicar que este es el repositorio independiente; Ren'Py pertenece al demo externo.
3. **Instrucciones de prueba no ejecutables.** El ZIP recibido no incluye `tools/check_project.py`. Se sustituyó su recomendación operativa en los puntos de entrada por comandos presentes. Se mantienen referencias históricas en los informes PA-001 y otros registros de la etapa anterior.
4. **Ausencia de orientación documental autónoma.** Se agregaron `docs/README.md`, `docs/guides/QUICK_START.md`, `docs/reference/NAMING.md` y `docs/reference/REPOSITORY_SCOPE.md`, con rutas a implementaciones y contratos existentes.
5. **Regresión de enlaces.** Se incorporó `tools/check_doc_links.py` y `tools/test_doc_links.py`. Detectan destinos Markdown locales inexistentes sin utilizar red. No validan destinos externos, redirecciones, ni semántica del contenido enlazado. Se verificaron manualmente los dos destinos locales con fragmento `#` utilizados en las nuevas guías.

## Evidencia de ejecución en esta revisión

| Comprobación | Resultado |
| --- | --- |
| `python tools/check_doc_links.py` | PASS, sin destinos Markdown locales rotos |
| `python -m unittest tools.test_doc_links -q` | 3 PASS |
| `python tools/check_quality.py` | PASS |
| `python -m unittest discover -s tools -p 'test_*.py' -q` | 11 PASS (incluye las nuevas pruebas de enlace) |
| `python -m unittest discover -s gisela/contracts -p 'test_*.py' -q` | 180 PASS |
| `python -m unittest discover -s dice/tests -p 'test_*.py' -q` | 15 PASS |
| `python -m unittest discover -s traits/tests -p 'test_*.py' -q` | 25 PASS |
| `python -m unittest discover -s mary/tests -p 'test_*.py' -q` | 21 PASS |
| `python tools/glauquir.py --package gisela/packages/h46_faro_de_niebla.package.json --auto` | EXIT 2; recorrido no acreditado |
| Suite completa `gisela/engine/tests` | TIMEOUT del entorno; no acreditada en esta intervención |
| SDK gráfico Ren'Py | No incluido, no comprobado |

## Límites pendientes

- Los links HTTP/HTTPS externos requieren comprobación de red y no están cubiertos por el verificador local.
- Se conservan documentos históricos cuyos comandos corresponden al antiguo monorrepositorio; el índice distingue expresamente esa condición.
- El verificador reconoce los destinos de enlaces Markdown convencionales; no analiza todos los enlaces HTML, referencias en código de ejemplo ni todas las reglas de generación de fragmentos de cada plataforma.
- El resultado de GLAUQUIR no afecta por sí solo a la corrección de enlaces, pero exige investigación independiente antes de declarar aprobación integral.

## Comprobación continua recomendada

Ejecutar `python tools/check_doc_links.py` y `python -m unittest tools.test_doc_links -q` en cada cambio de documentación, junto con los controles de calidad existentes. No es necesario un nuevo coordinador o subsistema de documentación.
