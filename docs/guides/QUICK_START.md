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
glauquir --package gisela/packages/h46_faro_de_niebla.package.json
```

Otro paquete de ejemplo:

```bash
glauquir --package gisela/packages/h46b_central_clasificadora.package.json
```

Dentro de la sesión, use `mirar`, `acciones` y `accion ID`; las acciones bloqueadas se reservan al diagnóstico. La [guía de GLAUQUIR](GLAUQUIR.md) reúne los comandos, el modo `--developer` y las opciones de color.

También puede elegir una acción con la letra que aparece junto a ella (`A`, `B`, …, `AA`); las letras cambian con las opciones visibles. En un terminal, `↑` recorre los comandos de esta ejecución y recupera el comando completo (`accion ID`) cuando se eligió una letra. `←` y `→` permiten editar el texto antes de enviarlo.

Para crear un relato propio con una elección y dos finales, sigue [Crea tu primer paquete](CREAR_PAQUETE.md).

Desde cualquier directorio, `glauquir` inicia el paquete de ejemplo incorporado si se omite `--package`. Para comprobar un paquete propio antes de jugar, ejecuta `gisela validate historia.package.json`; `--json` entrega diagnósticos estructurados.

Admisión de un paquete:

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json
```

Verificación oficial desde la raíz (el modo completo añade recorridos con restauración):

```bash
python tools/check_gisela.py
python tools/check_gisela.py --full
```

Véase la [guía de verificación](VERIFICACION_GISELA.md) para dependencias, alcance y criterios bloqueantes.

Para integrar el motor desde Python, consulte el [ejemplo de sesión en el README](../../README.md#python-session-example), la [API de clientes](../architecture/API_CLIENTES.md) y los [contratos](../../gisela/contracts/README.md). La CLI y los ejemplos son herramientas de demostración; Ren'Py no forma parte de este repositorio.

## Uso desde otro directorio

Para importar `gisela` desde un script ubicado fuera de la raíz del repositorio, instale el proyecto en modo editable desde su directorio raíz: `python -m pip install -e .`. Esto no es necesario para ejecutar las herramientas desde la raíz, pero evita depender del directorio de trabajo al importar el paquete.

Para probar los recorridos deterministas (sin utilizar el modo `--auto` del cliente):

```bash
python tools/h46_walkthrough.py --route completa --verify-restores
python tools/h46b_walkthrough.py --route casete --verify-restores
```

Las demás rutas están descritas en la ayuda (`--help`) de cada script. El modo `--auto` de GLAUQUIR no sustituye estos recorridos: puede repetir acciones disponibles sin terminar la historia.
