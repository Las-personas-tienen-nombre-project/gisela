# 3. Instalación y requisitos

En este capítulo instalarás GISELA y ejecutarás tu primera historia. No necesitas saber programar, pero sí utilizar una terminal y escribir algunos comandos.

## Requisitos

- Python 3.10 o posterior.
- Una copia descargada o clonada del repositorio de GISELA. Esta guía parte de que ya la tienes; no incluye una dirección de descarga.
- Una terminal y conexión a internet para instalar las dependencias.
- Un editor de texto que permita guardar archivos JSON en UTF-8 para los talleres.

No necesitas instalar Ren'Py. **Raíz del repositorio** significa la carpeta principal de GISELA, que contiene `pyproject.toml`, `README.md` y el directorio `docs`. Abre la terminal en esa carpeta antes de copiar los comandos. Si no tienes todavía una copia del repositorio, solicítala a quien te proporcionó el curso; no hay una dirección de descarga verificada en estas instrucciones.

## 1. Crear un entorno de Python

Un **entorno virtual** es una carpeta local donde se instalan las herramientas de este proyecto, separadas de las de otros programas.

En Linux, abre una terminal y escribe:

```bash
python -m venv .venv
source .venv/bin/activate
```

En Windows, abre PowerShell en la carpeta del repositorio y escribe:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

En Linux, instala GISELA después de activar el entorno:

```bash
python -m pip install -e .
```

En Linux, si cierras la terminal, tendrás que volver a abrirla en la raíz del repositorio y ejecutar `source .venv/bin/activate` antes de usar `glauquir` o `gisela`. En Windows, los comandos siguientes usan directamente los ejecutables del entorno para evitar tener que cambiar la política de ejecución de PowerShell.

## 2. Ejecutar El faro de niebla

En Linux:

```bash
glauquir --package gisela/packages/h46_faro_de_niebla.package.json
```

En Windows, desde PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package gisela/packages/h46_faro_de_niebla.package.json
```

Al comenzar verás una escena y una lista de acciones. El inicio del ejemplo incluido muestra:

```text
ESCLUSA DEL MUELLE: 19:00

El agua golpea las tablas. Desde aquí se llega al archivo,
al taller y a la escalera de la cúpula.

PERSONAS
  Elio

ACCIONES
  A) Hablar con Elio e iniciar la guardia  [accion escuchar_aviso]
>
```

Para elegir la acción, escribe `A` y presiona Enter. También puedes escribir `1` o `accion escuchar_aviso`. La historia continuará y mostrará las siguientes acciones disponibles.

Durante la partida puedes escribir `mirar` para volver a ver la situación, `acciones` para consultar las opciones, `ayuda` para conocer los comandos y `salir` para terminar. Las letras pueden cambiar cuando cambian las acciones visibles.

## 3. Comprobar un paquete

En Linux:

```bash
gisela validate gisela/packages/h46_faro_de_niebla.package.json
```

En Windows:

```powershell
.\.venv\Scripts\gisela.exe validate gisela/packages/h46_faro_de_niebla.package.json
```

Este comando comprueba la admisión del paquete narrativo antes de ejecutarlo. Si termina sin errores, todavía debes jugar los caminos relevantes para comprobar que la historia se comporta como esperas. En los talleres repetirás estas dos comprobaciones.

## 4. Problemas frecuentes

Si no se reconoce `python`, comprueba la instalación de Python. En algunas distribuciones de Linux el comando se llama `python3`; puedes utilizarlo para crear el entorno virtual y, una vez activado, usar `python` normalmente.

Si no se reconoce `glauquir`, comprueba que instalaste GISELA. En Linux, también debes activar el entorno virtual. En Windows, utiliza la ruta completa que aparece en esta guía.

Si aparece un mensaje indicando que no se encuentra la historia, comprueba que estás en la raíz del repositorio. Si falla `python -m venv`, comprueba que tu instalación de Python incluya el módulo `venv`.

## Para quienes quieran verificar todo el proyecto

La instalación normal es suficiente para jugar y seguir los primeros talleres. Para ejecutar las pruebas del repositorio, instala también las dependencias de desarrollo y ejecuta, desde la raíz:

```bash
python -m pip install -r requirements-dev.txt
python tools/check_gisela.py --full
```

En Windows, sustituye `python` por `.\.venv\Scripts\python.exe` en ambos comandos.

Si necesitas más detalles, consulta la [guía de inicio rápido](../../guides/QUICK_START.md) y la [guía de GLAUQUIR](../../guides/GLAUQUIR.md).

**Próximo paso:** continúa con el [taller 01, El paraguas olvidado](01_paraguas/README.md), que incluye un relato preparado para modificarlo y comprobar sus decisiones.

**Alcance de la comprobación:** los comandos y las rutas proceden del repositorio; la instalación limpia en Windows no se ha comprobado en esta revisión.
