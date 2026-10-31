# Inicio rápido: GISELA independiente

Ejecutar desde la raíz del repositorio, con Python 3.10 o posterior.

```bash
python -m venv .venv
source .venv/bin/activate
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
```

Para integrar el motor desde Python, consulte el [ejemplo de sesión en el README](../../README.md#python-session-example), la [API de clientes](../architecture/API_CLIENTES.md) y los [contratos](../../gisela/contracts/README.md). La CLI y los ejemplos son herramientas de demostración; Ren'Py no forma parte de este repositorio.
