# Verificación independiente de GISELA

Para preparar y publicar una nueva versión, siga el procedimiento de
[versionado y publicaciones](../../README.md#versioning-and-releases). Incluye
la comprobación de la wheel y de los comandos instalados fuera del repositorio.

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

El modo normal ejecuta 12 grupos: pruebas de motor (incluida la práctica Tegularis) y herramientas, Ruff lint y
formato, Radon, Bandit, calidad estructural, enlaces locales Markdown e
invariantes E0, E1, E2 y E3. `--full` ejecuta 18 grupos y
agrega rutas completas y verificaciones de restauración de Faro de Niebla y
Central Clasificadora. Los grupos muestran tiempo y código de salida; si uno
falla, el resultado global es distinto de cero. `--timeout N` limita cada
grupo y un agotamiento se informa con `exit=124`; no convierte fallos en éxito.

Pytest usa `--import-mode=importlib` y el complemento local
`tools.pytest_canonical` para cargar primero los paquetes mantenidos bajo
`gisela/`. Esto evita que las copias `engine/` y `contracts/` de la raíz
sustituyan módulos durante la colección. El complemento comprueba la ruta
de los paquetes cargados y falla explícitamente si corresponde a otra copia.
La configuración también incluye la ruta del simulador para sus imports
históricos; se aplica tanto al kit como a las pruebas individuales.

## Política estática

Ruff aplica los códigos fijados en `pyproject.toml` y comprueba formato sin
reescribir archivos. Cualquier incidencia bloquea. Radon analiza complejidad
ciclomática en GISELA, MARY, DICE, TRAITS y narrative_conditions: grados D, E y F
bloquean; A, B y C se permiten. El índice de mantenibilidad (MI) se muestra sin
umbral: un módulo C puede reflejar volumen y no demuestra por sí solo un defecto.

Bandit analiza todos los archivos Python mantenidos de los cinco árboles;
excluye `.venv`, `.git` y `__pycache__`, también cuando están anidados.
El análisis y la comprobación de cobertura usan el mismo inventario.
Cualquier hallazgo en código de producción y cualquier Medium o High bloquea.
Las advertencias Low de pruebas revisadas en `tools/bandit_low_baseline.json` se muestran como informativas: incluyen
asserts de pruebas, simulaciones con semillas fijas, subprocess sin shell para
pruebas de integración y un dato sintético que no es una credencial.
El simulador de combate usa una excepción local documentada `B311` en su
fábrica de RNG: necesita reproducibilidad y no genera secretos. Una advertencia Low nueva en pruebas bloquea hasta
su revisión y registro; el kit no la presume inocua. Errores de análisis o
herramientas ausentes también bloquean.

Para reproducir un diagnóstico por separado:

```bash
python -m ruff check gisela mary dice traits narrative_conditions tools
python -m ruff format --check gisela mary dice traits narrative_conditions tools
python -m radon cc gisela mary dice traits narrative_conditions -s -a
python -m radon mi gisela mary dice traits narrative_conditions -s
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

## API de duración del laboratorio

La declaración de duración agrupa sus datos en `ActuationDuration`; no cambia
los contratos Act/Observe ni los snapshots:

```python
from gisela.engine.actuation import ActuationDuration

session.actuation_add_duration(
    session.export()["revision"],
    ActuationDuration("escudo_de_prueba", "gillius", 2),
)
```

Los constructores de Tegularis se verifican en un directorio temporal: deben
reproducir el contenido, digest canónico y formato compacto de los paquetes
v0.7.1, v0.7.2 y v0.7.7. La compactación de los JSON conserva sus rutas y referencias.
El constructor v0.7.7 rechaza una explosión final mal formada también con
`python -O`.

## Campañas Tegularis y reproducción de fallos

Desde la raíz y con el entorno de desarrollo instalado:

```bash
python tools/tegularis_campaign_v077.py --start 0 --count 4 --strategy attack
python tools/tegularis_campaign_v077.py --replay /ruta/campaign-XXXX/SEMILLA_COMPLETA
```

Las estrategias disponibles son `pass`, `attack` y `shield`. Cada semilla
crea una sesión independiente y puede ejecutar hasta 600 acciones. Todos los
desenlaces del juego, incluidos `derrota` y `destruccion_mutua`, cuentan como
partidas válidas. Los errores técnicos individuales se registran y la campaña
continúa; errores de configuración, importación, memoria o E/S la interrumpen.

Stdout contiene únicamente JSONL compacto: un resultado por semilla y el
resumen final. Las semillas se identifican con sus 64 dígitos hexadecimales.
La campaña devuelve `0` si todas terminan válidamente, `1` si alguna falla por
un error técnico individual y `2` si se interrumpe por un error global.

Cada ejecución crea un directorio privado bajo `.local/tegularis-campaigns/`,
ignorado por Git. `--output-dir RUTA` permite elegir otra ubicación; quien
la elija debe mantenerla fuera de commits y de servicios de sincronización
si contienen información privada. Los diagnósticos incluyen el guion y el
estado interno completo: son archivos locales para autores, no vistas públicas
del jugador. Los directorios nuevos tienen permisos 0700 y los archivos 0600.

`summary.json` conserva resultados, conteos, desenlaces, errores y semillas
pendientes. Se actualiza después de cada resultado y al terminar. Cada semilla
fallida tiene su propio directorio con:

- `snapshot.json`: estado confirmado anterior a la operación fallida, incluido
  el RNG. Un fallo de inicialización sin sesión se representa con `null`.
- `error.json`: excepción, traceback, fase, acción, respuesta, revisión,
  estrategia y contexto del entorno ejecutado.
- `events.jsonl`: hechos y trazas confirmados hasta el snapshot, ordenados por
  su secuencia; no se limita a la ventana pública de Observe.
- `package.json`: copia del paquete admitido para la reproducción independiente.
- `manifest.json`: hashes de los cuatro archivos para comprobar su integridad.

Los archivos se escriben en temporales del mismo volumen con `fsync` y
reemplazo atómico. El directorio de fallo se publica completo mediante rename;
un fallo de escritura impide continuar la campaña. Si tampoco puede guardarse
el resumen, se informa por stderr y el proceso devuelve `2`. Un corte abrupto
puede dejar temporales ocultos, pero no un directorio de semilla publicado a
medias; el resumen anterior conserva su estado `running`.

Replay utiliza los archivos del diagnóstico, sin consultar el paquete original
ni otras semillas. Requiere el mismo código y entorno: verifica la huella de
fuentes y contratos, versiones de dependencias, Python y optimizaciones. Para
Act restaura el snapshot y repite la solicitud; las fases de inicialización,
exportación, restauración y límite de acciones se repiten desde la semilla y
estrategia originales. Si falla exportar, el snapshot disponible es el último
capturado correctamente, identificado por la fase `export`.

En modo `--replay`, el código `0` significa que se reprodujo el mismo fallo;
`1`, que el comportamiento cambió; y `2`, que los archivos o el entorno impiden
la reproducción. El comando no modifica los diagnósticos originales. Las
opciones de campaña y `--replay` son excluyentes.
