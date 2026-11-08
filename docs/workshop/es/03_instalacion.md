# 3. Instalación y requisitos

En este capítulo instalarás GISELA y ejecutarás tu primera historia. No necesitas saber programar, pero sí utilizar una terminal y escribir algunos comandos.

## Requisitos

- Python 3.10 o posterior.
- Una copia del repositorio de GISELA.
- Una terminal y conexión a internet para instalar las dependencias.

No necesitas instalar Ren'Py. Ejecuta los comandos desde la raíz del repositorio, donde se encuentra `pyproject.toml`.

## 1. Crear un entorno de Python

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

El entorno virtual mantiene las dependencias de este proyecto separadas de otros programas. En Windows, los comandos siguientes usan directamente los ejecutables del entorno para evitar tener que cambiar la política de ejecución de PowerShell.

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

Este comando revisa el paquete narrativo antes de ejecutarlo.

## 4. Problemas frecuentes

Si no se reconoce `python`, comprueba la instalación de Python. En algunas distribuciones de Linux el comando se llama `python3`; puedes utilizarlo para crear el entorno virtual.

Si no se reconoce `glauquir`, comprueba que instalaste GISELA. En Linux, también debes activar el entorno virtual. En Windows, utiliza la ruta completa que aparece en esta guía.

Si aparece un mensaje indicando que no se encuentra la historia, comprueba que estás en la raíz del repositorio.

## Para quienes quieran verificar todo el proyecto

La instalación normal es suficiente para jugar y seguir los primeros talleres. Para ejecutar las pruebas del repositorio, instala también las dependencias de desarrollo y ejecuta, desde la raíz:

```bash
python -m pip install -r requirements-dev.txt
python tools/check_gisela.py --full
```

En Windows, sustituye `python` por `.\.venv\Scripts\python.exe` en ambos comandos.

Si necesitas más detalles, consulta la [guía de inicio rápido](../../guides/QUICK_START.md) y la [guía de GLAUQUIR](../../guides/GLAUQUIR.md).

**Próximo paso:** el primer taller, *El paraguas olvidado*, comenzará con un relato preparado para modificarlo y comprobar sus decisiones.
