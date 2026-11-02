# Contrato público de clientes de GISELA

## Responsabilidades

GISELA conserva la autoridad de la sesión, la evaluación declarativa, la ejecución de acciones y las transacciones. ALBERTO administra las entidades del mundo en borradores proporcionados por GISELA. S.O.F.I.A. calcula atributos. GLAUQUIR y Ren'Py solo presentan proyecciones y envían decisiones.

La CLI no debe importar `world.py`, modificar el estado de sesión, ejecutar reglas ni reconstruir a partir de la traza causal una historia pública. `debug_query` es una excepción diagnóstica para herramientas explícitamente autorizadas, nunca una fuente para presentar datos normales del jugador.

## API Python disponible

| Operación | Resultado |
| --- | --- |
| `admit_package_file(path)` | Valida estructura y semántica, calcula digest y admite definiciones. |
| `new_session(admitted)` | Crea una sesión de GISELA. |
| `restore_session(admitted, snapshot)` | Valida el guardado y la identidad del paquete. |
| `session.observe()` | Entrega contenido, actores, elementos y acciones, más inventario, habilidades, efectos y cartas públicas. |
| `session.act(request)` | Revalida una acción ofertada mediante identificador y revisión. |
| `session.read_public(identifier)` | Entrega título y descripción de una carta actualmente conocida. |
| `session.player_status()` | Entrega únicamente el Scoresheet del protagonista cuando existe. |
| `session.read_history(limit=None)` | Entrega copias del registro narrativo confirmado. |
| `session.export()` | Exporta un snapshot JSON sin estado provisional. |
| `session.debug_query(request)` | Entrega datos de diagnóstico, solo para herramientas de desarrollo. |

`Observe` incorpora campos opcionales para conservar compatibilidad con los consumidores anteriores. Las entradas del registro se almacenan en `history.reading` dentro de la sesión, como un dato autoritativo diferente de `history.trace`. Este agregado es compatible con snapshots v1.2 anteriores, aunque dichos snapshots no contienen la historia de lectura que no se llegó a registrar.

## Contrato de Act

El cliente debe leer primero una acción de `view.actions`, comprobar que está habilitada y enviar el mismo `action_id` y `revision`:

```python
view = session.observe()
action = next(item for item in view['actions'] if item['enabled'])
answer = session.act({
    'session_id': view['session_id'],
    'revision': view['revision'],
    'action_id': action['action_id']
})
```

Ningún verbo textual autoriza operaciones por sí mismo. Si hay dos coincidencias, el cliente no escoge automáticamente. Si la acción deja de estar disponible, GISELA la rechaza. Una acción puede detenerse para pedir una decisión auxiliar sin confirmar cambios del mundo ni del RNG.

## Historia de lectura

GISELA conserva los pasajes narrativos efectivamente confirmados al entrar en una escena, alcanzar un paso visible o confirmar una decisión. El historial público contiene textos en su orden original y no vuelve a ejecutar condiciones ni reconstruye descripciones usando el mundo presente.

La lectura del historial no produce nuevos registros, no cambia revisiones ni consume aleatoriedad. Una transacción pendiente conserva exclusivamente el estado anterior y su solicitud; los pasajes provisionales no se registran.

## Información visible y oculta

`read_public` solo permite cartas visibles, conocidas o poseídas conforme a la proyección actual. El inventario pertenece al protagonista y no publica pertenencias de otros personajes. El estado público de S.O.F.I.A. pertenece al protagonista. Las propiedades y conocimientos internos del mundo siguen reservados a las consultas diagnósticas de desarrollo hasta contar con políticas de visibilidad declaradas.

## Habilidades de exploración

La escena autoriza el ofrecimiento mediante `allow_skill_play: true`. GISELA evalúa requisitos y propiedad de la habilidad, publica la acción y resuelve su uso con las mismas transacciones de las ventanas narrativas. No se configura un segundo sistema de habilidades en el cliente.

## Compatibilidad

Los cambios de esta etapa amplían los campos opcionales de los schemas `session` y `observe`, pero mantienen el formato declarado en 1.2. El nuevo paquete de ejemplo usa ese formato. Un guardado previo puede restaurarse si sigue siendo válido y coincide su digest; sin embargo, no puede recuperar retroactivamente los textos anteriores a esta ampliación.

## GLAUQUIR y presentación v1.5 vigente

GLAUQUIR (GISELA's Lightweight Access Utility for Queries, User Interaction, and Rendering) es el cliente textual oficial. `tools/glauquir.py` y el comando instalado `glauquir` son entradas equivalentes; los alias históricos siguen disponibles. Véase la [guía de comandos y color](../guides/GLAUQUIR.md).

`Observe.actions` puede incluir ofertas deshabilitadas. GLAUQUIR las filtra en `mirar`, `acciones` y `acciones ELEMENTO`; ID, verbo y número solo seleccionan habilitadas. `--developer` añade recuentos y permite `acciones bloqueadas` y `acciones todas`, sin ampliar las acciones ejecutables. `reason` es opcional y la CLI no lo inventa.

GLAUQUIR asigna letras a las ofertas habilitadas según el orden mostrado, con las salidas primero, y aplica ese mismo orden a los números. Las letras y el historial de comandos editables son funciones locales del cliente: no forman parte de `Observe`, de la solicitud `Act` ni del snapshot de sesión. El comando `history` sigue leyendo el registro narrativo confirmado de GISELA.

Las escenas pueden declarar `role: "exit"` en acciones y `role: "portable_object"` o `"fixed_object"` en elementos. Los elementos sin rol se presentan como genéricos. Son categorías autorales, no inferencias a partir de etiquetas, verbos o propiedades privadas. La escena inicial `muelle` de Faro de Niebla no declara elementos, pero su escena `archivo` declara dos. Central Clasificadora no declara elementos en sus escenas.

Las cartas, actores y elementos v1.5 pueden declarar `presentation.color` con `default`, `red`, `yellow`, `green`, `cyan`, `blue`, `magenta` o `white`. Solo el rol llega a `Observe`; la CLI lo traduce a ANSI. Si una carta de personaje u objeto declara la propiedad `presentation_color` de tipo `string` e inicial `inherit`, una operación `set` puede cambiar el color de esa instancia. `inherit` retira esa sobrescritura. Precedencia: **instancia → actor o elemento de escena → carta → tema**. El rol explícito `default` restablece el estilo básico y también prevalece sobre la disposición en desarrollo. La presentación propia de la escena no reemplaza los colores de las entidades.

Para proteger identidades, un actor puede declarar `unknown_name`, `known_if` y `public_id`. Mientras la condición no se cumple, `Observe.actors[].name` usa el nombre desconocido y la ficha pública omite su descripción; la referencia pública puede mantenerse al cambiar el nombre. Los elementos pueden declarar `public_id` y `public_entity`; una acción exploratoria puede declarar `public_id` para el comando visible. Estos alias son opcionales: los paquetes que no los declaren conservarán sus IDs actuales. La autoría debe revisar también las etiquetas, fichas y opciones que puedan revelar una identidad. El `action_id` vigente sigue siendo el token que `Act` revalida.

La configuración opcional `manifest.disposition_display` declara `field`, `minimum`, `neutral`, `maximum` y, si se desean otros cortes, `thresholds` con cuatro números crecientes dentro de −100 a 100. La admisión exige `minimum < neutral < maximum` y valores finitos. Sin umbrales propios se usan −60, −20, 20 y 60: `hostile` para valores menores que −60; `unfriendly` desde −60 y menores que −20; `neutral` desde −20 hasta 20 inclusive; `friendly` por encima de 20 hasta 60 inclusive; `very_friendly` por encima de 60. Se clasifica el valor normalizado sin redondearlo y se satura en los extremos.

`debug_query({"kind": "disposition", "actor": REFERENCIA_PUBLICA})` acepta una persona visible y lee la relación dirigida NPC → protagonista, incluido el valor inicial declarado cuando aún no hay registro. Devuelve `value`, `scale`, `normalized`, `category`, `color` y `color_source`. Sin escala o campo relacional numérico devuelve `unknown`. `Observe` nunca contiene esa relación ni su categoría. GLAUQUIR consulta este diagnóstico únicamente con `--developer` y lo usa para colorear personas sin color explícito; `disposicion PERSONA` muestra el cálculo. `session.debug_query()` es para anfitriones locales confiables; el gateway exige `debug_private` a clientes externos. El paquete productivo declara `affinity_score` con escala −10 a 10 y neutral 0; su campo `affinity` textual no participa en este cálculo.

La plantilla productiva aún no declara una acción narrativa que cambie `presentation_color`. La prueba de cambio y restauración utiliza un paquete de integración; la configuración diagnóstica del producto no añade consecuencias narrativas por sí misma.

`--color auto` usa ANSI solo en una terminal compatible, sin `NO_COLOR` y con `TERM` distinto de `dumb`. `--color never` lo desactiva; `--color always` lo fuerza incluso con `NO_COLOR` o salida redirigida. Los escapes ANSI no forman parte de los paquetes ni de `Observe`.

## Escenas físicas e inspección en H4.5f

`scene.location` delimita un contexto físico de ALBERTO. GISELA revalida que la ubicación del protagonista coincide con dicho lugar en la admisión de entrada exploratoria y en cada guardado o confirmación. No hay movimiento implícito desde `set_scene`: una transición física requiere `move_character` y `set_scene` en la misma transacción. Una escena sin `location` representa un contexto no espacial cuya visibilidad es declarativa.

GISELA proyecta actores y elementos vinculados a entidades únicamente cuando están físicamente presentes, y no publica objetos poseídos por terceros solo por estar cerca. Se permite proyectar objetos propios del protagonista en su lugar actual. Las acciones de un elemento oculto tampoco se ofrecen ni se autorizan; los identificadores derivados de posiciones declaradas permanecen estables al cambiar la visibilidad. Los elementos sin vinculación física se gobiernan por `visible_if`.

El campo opcional `scene.elements[].description` usa `localized_text` y llega a `Observe.elements[].description`. GLAUQUIR puede leerlo mediante `mirar ELEMENTO`; cuando no existe, usa la carta pública del `entity` autorizado. Leer no ejecuta efectos. `examinar ACCIÓN`, cuando `ACCIÓN` identifica inequívocamente por ID o etiqueta una oferta visible, consulta sus anotaciones sin ejecutarla, incluso si no tiene notas. Para los demás argumentos, `examinar` busca primero una acción declarada y, si no la encuentra, una ficha o elemento público. El contrato de Act y el registro narrativo confirmado no cambian.

Véanse [semántica de escenas](ESCENAS_Y_PRESENCIA.md) y [pruebas ancladas](../operatives/INVARIANTES_H4_5F.md).

## E0: Software solicitante no humano (implementado, anfitrión confiable)

`session.act()` y `session.observe()` se mantienen para clientes **locales confiables**. Para software externo o varias fuentes concurrentes existe `ExecutionGateway` (véase [frontera autorizada](E0_FRONTERA_AUTORIZADA_Y_PERSISTENCIA.md)). El anfitrión autentica a cada solicitante y le asigna capacidades; no hay relación automática entre ese principal, el `player_character` y la entidad narrativa de una acción. Una vez asociado el gateway, se bloquea la entrada `session.act()` directa. La API externa utiliza un `command_id` adicional, fuera del JSON `Act` versionado.

La lectura externa solo publica el contenido del protagonista si se concede explícitamente `observe_player`. `export_private` y `debug_private` son permisos privilegiados. El transporte entre instancias y otras audiencias **no** son capacidades implementadas.

## Localización y anotaciones (v1.5)

`new_session(admitted, language=None)` y `restore_session(admitted, snapshot, language=None)` usan por defecto `manifest.language`. `session.observe(language=None)` es pura; `session.set_language(codigo)` modifica solo la preferencia efímera del anfitrión. El resolvedor único de `localized_text` consulta `strings[idioma][text_key]` y, si falta la traducción, vuelve a `strings[idioma_base][text_key]`. La admisión rechaza claves sin texto base. `history.reading` conserva el texto ya confirmado, sin retraducciones al cambiar idioma. El snapshot, sus revisiones y el RNG no incorporan la preferencia idiomática.

`session.observe_glauquir(language=None)` es una vista local de GLAUQUIR separada de `session.observe()`; añade información de autor de la escena, acción, nodo y paso actualmente accesibles, sin modificar `Act`, historial o estado. El gateway requiere las capacidades conjuntas `observe_player` y `observe_glauquir` para `BoundClient.observe_glauquir()`; Ren'Py no dispone de esta última. Las anotaciones no equivalen a `debug_query` ni conceden `debug_private`.

Los detalles del esquema, diagnóstico y ensamblado de catálogos están en la [guía v1.5](../guides/LOCALIZACION_Y_ANOTACIONES.md).
