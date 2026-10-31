# Verificación independiente de GISELA

## Alcance y comandos

`tools/check_gisela.py` es el punto de entrada del **repositorio independiente**.
No utiliza `project_check` ni el antiguo `tools/check_project.py` del monorrepositorio
del demo «Las personas tienen nombre». Desde la raíz de GISELA:

```bash
python tools/check_gisela.py
python tools/check_gisela.py --full
```

Desde otro directorio, invoque la ruta absoluta, por ejemplo:
`python /ruta/al/repositorio/gisela/tools/check_gisela.py --full`.
El script establece el directorio de trabajo en la raíz que contiene `tools/`.
Requiere Python y las dependencias de desarrollo del repositorio.

El modo normal ejecuta pruebas de motor, contratos, bibliotecas y herramientas,
calidad, enlaces locales Markdown e invariantes E0, E1, E2 y E3. `--full`
agrega rutas completas y verificaciones de restauración de Faro de Niebla y
Central Clasificadora. Los grupos muestran tiempo y código de salida; si uno
falla, el resultado global es distinto de cero. `--timeout N` limita cada
grupo y un agotamiento se informa con `exit=124`; no convierte fallos en éxito.

## Criterios de coherencia documental

- Las instrucciones vigentes deben nombrar herramientas presentes en el árbol.
- Los ADR registran decisiones aprobadas: sus menciones históricas a
  `check_project.py` no se reescriben. Los controles E0–E3 los implementan ahora
  los cuatro scripts `verify_e*_invariants.py`, ejecutados por `check_gisela.py`.
- Informes de hitos y registros previos pueden conservar comandos históricos:
  no constituyen instrucciones actuales de ejecución.
- `check_doc_links.py` valida destinos Markdown locales, **no** afirmaciones
  arquitectónicas, esquemas, comandos históricos ni enlaces de Internet.
- `test_doc_links.py` verifica que las páginas operativas de entrada no
  recomienden orquestadores retirados y que los scripts citados en el conjunto
  de páginas actuales exista físicamente.

## Alcance de la evidencia

Un resultado satisfactorio certifica las comprobaciones ejecutadas, no pruebas
gráficas de Ren'Py, equivalencia semántica de todos los documentos ni ejecución
en plataformas no ensayadas. Conserve siempre el resumen final y códigos de
salida de una ejecución real de `check_gisela.py --full`.
