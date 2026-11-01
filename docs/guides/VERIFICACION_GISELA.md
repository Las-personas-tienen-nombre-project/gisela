# Verificación independiente de GISELA

## Alcance y comandos

`tools/check_gisela.py` es el punto de entrada del **repositorio independiente**.
Instale primero las dependencias de desarrollo y ejecute el kit desde la raíz:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

```bash
python tools/check_gisela.py
python tools/check_gisela.py --full
```

Desde otro directorio, invoque la ruta absoluta, por ejemplo:
`python /ruta/al/repositorio/gisela/tools/check_gisela.py --full`.
El script establece el directorio de trabajo en la raíz que contiene `tools/`.
Requiere Python y las dependencias de desarrollo del repositorio.

El modo normal ejecuta 12 grupos: pruebas de motor y herramientas, Ruff lint y
formato, Radon, Bandit, calidad estructural, enlaces locales Markdown e
invariantes E0, E1, E2 y E3. `--full` ejecuta 18 grupos y
agrega rutas completas y verificaciones de restauración de Faro de Niebla y
Central Clasificadora. Los grupos muestran tiempo y código de salida; si uno
falla, el resultado global es distinto de cero. `--timeout N` limita cada
grupo y un agotamiento se informa con `exit=124`; no convierte fallos en éxito.

## Política estática

Ruff aplica los códigos fijados en `pyproject.toml` y comprueba formato sin
reescribir archivos. Cualquier incidencia bloquea. Radon analiza complejidad
ciclomática en GISELA, MARY, DICE, TRAITS y narrative_conditions: grados D, E y F
bloquean; A, B y C se permiten. El índice de mantenibilidad (MI) se muestra sin
umbral: un módulo C puede reflejar volumen y no demuestra por sí solo un defecto.

Bandit analiza los cinco árboles completos. Cualquier hallazgo en código de
producción y cualquier Medium o High bloquea. Las 19 advertencias Low de pruebas
revisadas en `tools/bandit_low_baseline.json` se muestran como informativas: son
subprocess sin shell para pruebas de integración y un dato sintético, no una
credencial. Una advertencia Low nueva en pruebas bloquea hasta
su revisión y registro; el kit no la presume inocua. Errores de análisis o
herramientas ausentes también bloquean.

Para reproducir un diagnóstico por separado:

```bash
python -m ruff check gisela mary dice traits narrative_conditions tools
python -m ruff format --check gisela mary dice traits narrative_conditions tools
python -m radon cc gisela mary dice traits narrative_conditions -s -a
python -m radon mi gisela mary dice traits narrative_conditions -s
python -m bandit -r gisela mary dice traits narrative_conditions
python tools/check_static_quality.py radon
python tools/check_static_quality.py bandit
```

Bandit puede devolver un código no nulo por las Low informativas. El último
comando aplica la política efectiva; el informe completo conserva los detalles.

## Criterios de coherencia documental

- Las instrucciones vigentes deben nombrar herramientas presentes en el árbol.
- Los ADR registran decisiones aprobadas y no se reescriben. Los controles E0–E3
  los implementan los cuatro scripts `verify_e*_invariants.py`.
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
