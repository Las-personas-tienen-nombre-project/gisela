# Inicio rápido: GISELA independiente

Ejecutar desde la raíz del repositorio, con Python 3.10 o posterior.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Probar el cliente textual incluido, sin instalar Ren'Py:

```bash
python tools/glauquir.py --package gisela/packages/h46_faro_de_niebla.package.json
```

Otro paquete de ejemplo:

```bash
python tools/glauquir.py --package gisela/packages/h46b_central_clasificadora.package.json
```

Para crear un relato propio con una elección y dos finales, sigue [Crea tu primer paquete](CREAR_PAQUETE.md).

Admisión de un paquete:

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json
```

Pruebas offline integrales (pueden tardar):

```bash
python tools/check_quality.py
python tools/check_doc_links.py
python -m unittest discover -s tools -p 'test_*.py' -q
python -m unittest discover -s gisela/contracts -p 'test_*.py' -q
python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q
```

Para integrar el motor desde Python, consulte el [ejemplo de sesión en el README](../../README.md#python-session-example), la [API de clientes](../architecture/API_CLIENTES.md) y los [contratos](../../gisela/contracts/README.md). La CLI y los ejemplos son herramientas de demostración; Ren'Py no forma parte de este repositorio.

## Uso desde otro directorio

Para importar `gisela` desde un script ubicado fuera de la raíz del repositorio, instale el proyecto en modo editable desde su directorio raíz: `python -m pip install -e .`. Esto no es necesario para ejecutar las herramientas desde la raíz, pero evita depender del directorio de trabajo al importar el paquete.

Para probar los recorridos deterministas (sin utilizar el modo `--auto` del cliente):

```bash
python tools/h46_walkthrough.py --route completa --verify-restores
python tools/h46b_walkthrough.py --route casete --verify-restores
```

Las demás rutas están descritas en la ayuda (`--help`) de cada script. El modo `--auto` de GLAUQUIR no sustituye estos recorridos: puede repetir acciones disponibles sin terminar la historia.
