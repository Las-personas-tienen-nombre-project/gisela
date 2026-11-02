# GISELA v1.5: localización y anotaciones de autor

## Alcance del contrato

Ambas funciones son **opcionales**, están disponibles en los paquetes v1.5 y no modifican las reglas narrativas, ALBERTO, TRAITS, DICE, el RNG ni el calendario. Los paquetes v1.2–v1.5 existentes con literales `{"text":"..."}` continúan funcionando. Las nuevas anotaciones se declaran exclusivamente en v1.5.

## Localización durante la autoría

En un paquete v1.5 se declara el idioma original y el conjunto de idiomas:

```json
"manifest": {"id":"ejemplo", "format_version":"1.5", "language":"es_cl", "languages":["es_cl","en"], "entry":{"node":"inicio"}}
```

`es_cl` se conserva deliberadamente como identificador válido del español de Chile. El formato `localized_text` admite tanto `{"text":"¿Cómo te llamái?"}` como `{"text_key":"dialogo.gisela.pregunta_nombre"}`. Una misma clave puede utilizarse en diálogos, títulos, descripciones, ofertas, elementos, cartas, finales y anotaciones. No se introdujo otro sistema de identificadores de texto.

Durante la autoría, prepare un archivo por idioma:

```text
locales/
  es_cl.json
  en.json
```

`locales/es_cl.json`:

```json
{"dialogo.gisela.pregunta_nombre":"¿Cómo te llamái?"}
```

`locales/en.json`:

```json
{"dialogo.gisela.pregunta_nombre":"What's your name?"}
```

Ensamble el paquete desde la raíz de GISELA:

```bash
python -m gisela.contracts.catalogs guion_fuente.json locales/ guion.package.json
python -m gisela.contracts.admit_package guion.package.json
```

El ensamblador usa lectura JSON estricta, rechaza claves duplicadas y colisiones con catálogos ya embebidos, y escribe JSON canónico. La admisión valida el resultado. El paquete exportado contiene `strings.es_cl`, `strings.en`, etc. El runtime **no** lee `locales/` después de la admisión: los textos forman parte del digest del paquete. Cambiar un catálogo admitido cambia el digest y requiere nueva admisión; snapshots del digest anterior no se restauran automáticamente contra el nuevo paquete.

Un `text_key` sin definición en el idioma base es **error**; un idioma declarado sin catálogo o un catálogo no declarado también es **error**. Una traducción ausente en un idioma secundario es **advertencia** y usa exactamente el texto de la clave base; los campos literales permanecen literales para todos los idiomas. La admisión comprueba diferencias entre marcadores simples `{identificador}` del original y de una traducción, pero **no** sustituye ni evalúa esos marcadores en esta versión; los catálogos actuales deben contener textos completos, sin parámetros dinámicos. No hay traducción automática, flexión gramatical ni ejecución de expresiones en las cadenas.

La validación de claves duplicadas solo se puede realizar sobre archivos JSON sin pérdida de información: los diccionarios Python ya construidos no conservan duplicados. Para ello, utilice el ensamblador o el lector estricto de GISELA.

## Idioma de observación e historial

```python
session = new_session(admitted, language="en")
view = session.observe()                 # idioma elegido para este anfitrión
es = session.observe(language="es_cl")  # consulta puntual, pura
session.set_language("es_cl")           # preferencia local, sin nueva revisión
```

`new_session` y `restore_session` aceptan un `language` opcional. Si no se indica, eligen `manifest.language`. La selección **no se serializa** como parte del mundo ni forma parte de `Act`; cada anfitrión puede elegir su idioma nuevamente después de restaurar. El `language` puntual de una observación no altera la selección estable de la sesión. Es inválido solicitar un idioma no declarado.

`history.reading` sigue guardando el **texto resuelto en el momento de su confirmación**, no una clave que se resolverá posteriormente: al crear la sesión y al ejecutar acciones se usa el idioma estable de ese anfitrión. Cambiarlo no reescribe registros pasados; los nuevos registros se confirman en el idioma seleccionado a partir de ese momento. Cuando distintos observadores comparten **una misma** sesión autoritativa por gateway y solicitan idiomas diferentes solo para consultar, el historial queda en el idioma estable del escritor. No es posible afirmar que ambos hayan leído una traducción determinada; el historial sigue siendo una fuente única, estable y sin reconstrucción retrospectiva.

`Observe` y `Act` mantienen la misma revisión, el mismo identificador de acción y la misma autoridad. La selección de idioma no consume RNG ni invalida ofertas ya emitidas. En Ren'Py, `h5_bridge.observe` y `apply` pueden recibir `language=` desde el anfitrión, sin duplicar los textos del guion en Ren'Py; el motor confirma los pasajes nuevos en ese idioma.

## Anotaciones exclusivas de GLAUQUIR

Las escenas, acciones (incluidas acciones de elementos), nodos y sus pasos observables pueden declarar:

```json
"annotations": [
  {"audience":"glauquir", "text":{"text_key":"porteria.ronda.instrucciones"}}
]
```

El contrato v1.5 exige una lista no vacía de objetos `{"audience":"glauquir","text": localized_text}` sin campos adicionales. La anotación **no** es un paso, efecto, conocimiento de ALBERTO ni entrada de `history.reading`. `audience` no es un sistema de permisos arbitrarios y solo admite `glauquir`.

El `session.observe()` **habitual no cambia**. `session.observe_glauquir(language=None)` añade `annotations` únicamente de la escena activa, de las acciones visibles ofertadas y del nodo/paso realmente alcanzado. No consulta escenas futuras, fuentes ocultas ni acciones excluidas por `visible_if`. No se presenta información sobre un borrador pendiente. Las notas se entregan como `{scope, source, text}` y, para acciones, también `action_id`; estos datos no son comandos ejecutables. Si un cliente debe atravesar `ExecutionGateway`, el anfitrión debe conceder **ambas** capacidades `observe_player` y `observe_glauquir`; Ren'Py solo recibe `observe_player`. `debug_private` permanece independiente.

GLAUQUIR presenta las notas bajo el encabezado `INFORMACIÓN`; `mirar` vuelve a mostrarlas por solicitud del usuario, y `examinar ACCIÓN` permite leer la información correspondiente a una acción ya visible. No registra artificialmente lecturas ni controla cuándo el usuario decide volver a inspeccionar. `--color auto|always|never` y `NO_COLOR` conservan su comportamiento.

```bash
glauquir --package guion.package.json --language en --color never
```

**Política editorial:** use las anotaciones para explicar convenciones, intenciones de diseño y ayudas no narrativas que puedan conocer quienes recorren GLAUQUIR. No ponga secretos de historias futuras en notas de escenas o acciones actualmente visibles: GISELA protege por alcance y visibilidad declarativa, no interpreta el significado de la prosa.
