# C5 — Un solo árbol mantenido

El código ejecutable y los contratos mantenidos viven exclusivamente en
`gisela/engine/` y `gisela/contracts/`. El proyecto instalable (`pyproject.toml`),
pytest y las herramientas de calidad ya utilizan esas rutas.

Los directorios antiguos de la raíz `engine/` y `contracts/` se eliminaron para
impedir divergencias silenciosas. Tras aplicar el parche pueden quedar
carpetas vacías o cachés `__pycache__` no versionados, que no son fuentes.
No se alteraron las importaciones públicas
`gisela.engine.*` ni `gisela.contracts.*`, y los esquemas históricos permanecen
en `gisela/contracts/v1_3/`, `v1_4/` y `v1_5/`.

Se trasladaron dos pruebas que solo existían en el árbol antiguo a
`gisela/engine/tests/`: `test_layouts_v081.py` y `test_lectura_v081c.py`.
Sus rutas relativas de fixtures se ajustaron al nuevo directorio. La prueba
`test_e0_error_contracts.py` deja de inspeccionar `engine/` de la raíz y
consulta exclusivamente el código instalado.

## Comprobación

```bash
python -m pytest -q gisela/engine/tests/test_source_tree_c5.py \
  gisela/engine/tests/test_layouts_v081.py \
  gisela/engine/tests/test_lectura_v081c.py \
  gisela/engine/tests/test_e0_error_contracts.py
python tools/check_quality.py
```

La supresión de árboles no modifica la semántica de juego. C4 para las copias
del taller y C6–C9 permanecen fuera del alcance de este cambio.
