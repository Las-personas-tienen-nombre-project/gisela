# GISELA — C9: construcción narrativa mínima

Esta capa es **solo de autoría**, no un nuevo lenguaje ni un runtime. Los
constructores de `tools/authoring_narrative.py` producen diccionarios para el
contrato JSON existente. `tools/authoring_expressions.py` construye expresiones.
La admisión del paquete compilado sigue siendo obligatoria.

## Ejemplo real, sin combate

`tools/build_mvp_casete_authoring.py` reconstruye los nodos y la reacción del
paquete publicado `gisela/packages/mvp_casete.package.json`. Reutiliza las
cartas, escenas, estado inicial y manifest del archivo existente. Por tanto,
**no constituye todavía un generador completo de paquetes desde cero**.

Incluye una elección de prestar o guardar el casete, una condición sobre un
hecho, una reacción de Gisela y dos desenlaces. Los dos caminos se comprueban
con admisión y ejecución reales, usando una semilla fija.

Desde la raíz del repositorio:

```sh
python tools/build_mvp_casete_authoring.py --check
python tools/check_generated.py
python -m pytest -q gisela/engine/tests/test_narrative_authoring_c9.py
```

Sin `--check`, el ejemplo escribe el JSON compilado a stdout, sin tocar los
archivos publicados. La comprobación integrada en `check_generated.py` compara
la estructura completa del MVP, no los bytes de su presentación textual.

## Límites deliberados

- Los constructores no interpretan condiciones ni ejecutan efectos.
- Las comprobaciones locales solo detectan errores simples de autoría, como
  identificadores repetidos; los contratos y el validador siguen siendo la
  autoridad para el documento completo.
- No se generalizan operaciones de combate de Tegularis.
- La receta de ejemplo lee el MVP como base; la siguiente evolución, si es
  necesaria, deberá separar también manifest, cartas y estado inicial.
