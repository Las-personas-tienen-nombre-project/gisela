# GISELA: Arquitectura consolidada y contratos del motor narrativo

**Versión documental:** 1.3, sincronización con los contratos JSON 1.2 y la admisión semántica del 29 de octubre de 2026
**Proyecto de referencia:** *Central Clasificadora. Demo Ren'Py*; primer caso de uso: *Las personas tienen nombre*  
**Alcance:** arquitectura del motor general GISELA, subsistema ALBERTO y sistema opcional S.O.F.I.A.; auditoría y preparación de schemas.  
**Estado:** **ARQUITECTURA CONSOLIDADA / SCHEMAS 1.2 Y VALIDACIÓN SEMÁNTICA ESTÁTICA IMPLEMENTADOS / EJECUCIÓN DINÁMICA PENDIENTE / MVP PENDIENTE DE APROBACIÓN EXPRESA**. No constituye una declaración de implementación completa.

> **Regla de precedencia.** Esta revisión y las ADR-001-014 reemplazan las decisiones arquitectónicas incompatibles de los documentos antiguos y del diseño candidato del 29 de octubre. **No reemplazan el contenido narrativo ni el canon de *Blue Forever*.** El código antiguo de `lptn.zip` es una referencia histórica y funcional, no la base obligatoria del nuevo ejecutor. Los 13 schemas originales de `GISELA_Schemas_v1(1).zip` son históricos y fueron reemplazados por los contratos 1.1 y posteriormente por los schemas 1.2 con validador semántico v0.2, que incorporan correcciones estructurales, semánticas y sus pruebas. **La validación semántica estática ya existe; la conformidad de ejecución permanece pendiente**; no debe confundirse metavalidación con funcionamiento del motor.

**Nombres:** GISELA: *enGine for Interactive Stories through Events, Links, and Actions*; ALBERTO: *Autonomous Layer for Beings, Environments, Relationships, Traits, and Objects*; S.O.F.I.A.: *Strength, Openness, Fortune, Intelligence, Awareness*. Los nombres técnicos, `op`, campos y enumeraciones estarán en inglés; el texto literario permanece en el idioma del autor.

## 1. Principios, estatus y autoridad

### 1.1. Principios no negociables (DECIDIDO)

1. **Un motor, una sesión, una autoridad transaccional.** GISELA controla cursor narrativo, ejecución, validación, reglas, historial, aleatoriedad, transacciones, proyecciones y persistencia lógica. ALBERTO forma parte de GISELA, no es un segundo motor; S.O.F.I.A. es opcional y no ejecuta reglas independientemente.
2. **Autoría explícita.** El autor define contenido, sucesos, elecciones, condiciones, consecuencias y resultados. El motor no crea acontecimientos, psicología, relaciones, rutinas ni motivaciones.
3. **Separación de definición y estado.** Las definiciones del paquete son inmutables durante la sesión; el estado persistente reside en la sesión. Una carta define; una instancia representa un ejemplar o sujeto presente en el mundo.
4. **Lenguaje declarativo limitado.** Condiciones puras, operaciones tipadas y desencadenantes compartidos; ningún Python arbitrario aportado por contenidos. Ampliar vocabulario exige contrato y versión, no evaluación dinámica.
5. **Un mismo dominio para todo frontend.** CLI y Ren'Py usan `Observe` y `Act`. Ninguno calcula resultados narrativos ni conserva estado de juego oculto.
6. **Atomicidad causal y determinismo.** Cada operación originaria y sus reacciones se confirman juntas o se revierten; acciones equivalentes con la misma sesión/paquete/semilla y entradas producen resultados equivalentes.
7. **Sin mecanismos históricos obligatorios.** Croupier, Scheduler, barajas de acontecimientos y categorías Gold/Silver/Bronze no son parte del nuevo núcleo. Mecánicas de horarios, desplazamientos y oportunidades de *Las personas tienen nombre* se expresarán mediante contenido y reglas donde alcance el lenguaje general.
8. **Simplicidad verificable.** No se introduce un coordinador adicional, base de datos, sistema de plugins, DSL libre, event sourcing integral ni optimización prematura sin una necesidad demostrada.

### 1.2. Qué está decidido y qué no

- **DECIDIDO:** principios anteriores; contratos conceptuales de nodos, pasos, mundo, S.O.F.I.A. y las ADR-001-014 de esta versión (ADR-006-014 fueron seleccionadas por delegación del autor en la revisión integral).
- **PROPUESTA DE ALCANCE:** ADR-015 define el primer MVP recomendado. **No autoriza comenzar a programarlo**; necesita aceptación expresa.
- **PENDIENTE DE NORMALIZACIÓN:** validación semántica del contrato JSON 1.1, detalles de reconstrucción transaccional, formato canónico de digest, algoritmo exacto de RNG, presupuesto numérico de ejecución y semántica de algunos resultados condicionales. Son decisiones técnicas por precisar, no invitación a sustituir lo aprobado.
- **DIFERIDO:** implementación completa de habilidades, expiración avanzada, S.O.F.I.A., migraciones, contrahechizos, desplazamientos específicos del demo y todas las tareas audiovisuales.

## 2. Límites y responsabilidades

```text
                     Paquete narrativo validado
         manifest · nodes · cards · scenes · rules · initial_state
                                   │
                                   ▼
                                GISELA
                sesión / máquina narrativa / ejecutor
                condiciones / reacciones / transacciones
                historial / RNG / validación / Observe-Act
                                   │
                                 ALBERTO
                   instancias / ubicaciones / inventario
                   relaciones / memorias / tiempo / efectos
                                   │
                             S.O.F.I.A. (opcional)
                         atributos y modificadores
                                   │
                     proyecciones y acciones tipadas
                              ╱             ╲
                            CLI            Ren'Py
```

**GISELA** es propietario del ciclo de vida completo de la sesión y único punto de confirmación. Puede invocar funciones puras de ALBERTO para consultar, proponer y validar mutaciones, pero ALBERTO no hace commits, no crea transacciones, no avanza un reloj privado y no desencadena por su cuenta una segunda cadena reactiva.

**ALBERTO** es propietario de las invariantes de su modelo de mundo: tipos de entidades, instancias, poseedores/ubicaciones, mano/reserva, relaciones, conocimientos, creencias, efectos y el valor del reloj ficticio. La autoridad para ejecutar cambios sigue estando en GISELA. **S.O.F.I.A.** define la interpretación opcional de cinco atributos y de sus modificadores, sin tiradas automáticas.

**Host y frontends:** suministran archivos y recursos, muestran texto, animación y menús, reciben entrada, guardan bytes físicos, y aplican políticas locales sobre assets. No interpretan condiciones, seleccionan ramas ni mutan mundo. Las claves/contraseñas compactas específicas del demo, recursos audiovisuales, derechos editoriales y publicación quedan fuera del motor general.

**Criterio de responsabilidad única:** cada dato persistente tiene un dueño y una representación autoritativa; índices, paneles y presentaciones son derivaciones. Evitar el mismo campo con dos listas diferentes que deban mantenerse sincronizadas.

## 3. Paquete narrativo, identidad y referencias

### 3.1. Modelo lógico

Un paquete válido contiene `manifest`, `nodes`, `cards`, `scenes`, `rules`, `initial_state` y `endings`; `strings` es opcional. Es una unidad lógica única aunque el host lo distribuya en varios archivos. GISELA recibe el documento ensamblado; leer ZIP y archivos es asunto del host.

- `manifest`: identidad del paquete, formato, idioma base e idiomas disponibles, entrada inicial por nodo o escena, declaraciones tipadas de variables, hechos, proposiciones y señales, configuración opcional de S.O.F.I.A.
- `nodes`: unidades narrativas ejecutables; cada una contiene `steps` ordenados y con `id` estable.
- `cards`: definiciones de tipos `character`, `location`, `object`, `skill`, `effect`. No son eventos narrativos.
- `scenes`: representación observable y acciones disponibles, sin equiparar automáticamente escena con lugar físico.
- `rules`: desencadenantes y guardas con consecuencias declarativas compartidas.
- `initial_state`: instancias, ubicaciones, posesión, capacidades, reloj, valores, conocimientos, relaciones y hechos iniciales.
- `endings`: desenlaces definidos por el autor. `strings`: textos localizados opcionales.

### 3.2. Identificadores (ADR-009, DECIDIDO)

Los IDs de definición son únicos en su categoría; los de instancia son únicos en **toda** la sesión, incluso entre clases. Un ID retirado nunca se reutiliza. Los pasos se identifican por `(node_id, step_id)` y las opciones por `(node_id, step_id, option_id)`; no se utilizan posiciones de listas como identidades persistentes.

La sesión guarda un conjunto/registro de IDs ya utilizados, incluido el de los retirados, y un contador de asignación determinista. Las asignaciones dentro de una transacción provisional no consumen números ni identidades al cancelar o fallar. El estado inicial y el historial deben ser coherentes con ese registro. Las definiciones no cambian durante la sesión.

### 3.3. Referencias y contexto

Se permiten referencias explícitas y contextuales (`$actor`, `$target`, `$selected_object`, etc.) cuando existe un contexto que las liga. El motor/validador conoce el **tipo esperado** de cada posición. Una referencia ausente, inexistente o incompatible es error; no se interpreta silenciosamente como `false` ni como una entidad inventada.

Las consultas múltiples son explícitas. Una operación que necesita una sola entidad no acepta un resultado plural. Ante varios candidatos para selección singular: **error de ambigüedad**, sin seleccionar accidentalmente el primero de un archivo; `first_by_id` del schema candidato queda fuera de v1. La existencia de una consulta sin resultados puede producir `false` solamente cuando la semántica del predicado lo declara (`exists`), no al resolver una referencia singular obligatoria.

### 3.4. Localización y compatibilidad

El contenido es libre de expresarse en español u otro idioma; los tokens técnicos siguen en inglés. La resolución de `text_key` debe exigir texto en el idioma base del paquete y ofrecer una política explícita de fallback. Un digest de **contenido semántico completo** enlaza una sesión con las definiciones exactas. El algoritmo/canon de serialización se documentará antes de implementar restauración semántica: listas donde importa el orden se conservan; catálogos no ordenados pueden normalizarse por ID. Ninguna migración implícita altera un guardado de v1.

## 4. Máquina narrativa y estados (ADR-006-007, DECIDIDO)

### 4.1. Estados principales

| Estado | Significado | Invariantes |
|---|---|---|
| `preparing` | Ventana opcional de preparación previa a ejecutar un nodo. | Debe existir el nodo que se va a iniciar; no se ha iniciado su turno. |
| `node` | Nodo ya iniciado con ejecución activa. | Cursor y ejecución activos y coherentes; `step_id` pertenece al nodo. |
| `exploring` | No hay nodo activo; se observan/interactúan elementos de una escena. | Escena válida; no existe cursor de nodo activo. |
| `ended` | Desenlace autoral confirmado. | `ending_id` válido; no se ofrecen nuevas acciones narrativas. |

Confirmar texto, elegir, preparar, ofrecer habilidades o esperar una **transacción pendiente** son situaciones subordinadas, no nuevos estados principales. Los datos de espera deben tener un tipo explícito y ser compatibles con el estado. Una sesión `exploring` no debe exigir una `pending_choice`; `ended` no puede carecer de desenlace, ni `node` carecer de cursor. Una entrada inicial por nodo puede no tener aún escena; antes de entrar a `exploring` debe haber una escena válida o se informa error técnico, no se fabrica una escena.

### 4.2. Unidad narrativa y turnos

Un **turno** es una ejecución efectiva de nodo. Entrar al nodo genera una identidad de ejecución nueva y avanza el contador una sola vez. Un salto interno al mismo nodo, confirmar texto, consultar Scoresheet o interactuar con una escena sin iniciar nodo **no** crea turno. Se puede volver a ejecutar un mismo nodo más adelante: cada visita es un turno nuevo y no revierte ejecuciones anteriores.

Al iniciar, el contador y el suceso `turn_started` se resuelven dentro de una sola operación causal. El cierre de un nodo genera `node_completed` y `turn_ended` como **sucesos de un mismo límite causal**; sus reglas observan el mismo estado base de ronda, sin prioridad accidental entre esos sucesos. Confirmado el cierre, GISELA transfiere control al siguiente nodo, o a la escena `exploring`, o a `ended` si existe un `ending` explícito. Cada inicio/cierre tiene semántica exact-once.

**Límite transaccional:** una operación falla sin deshacer otras operaciones ya confirmadas del mismo nodo. No se promete rollback del turno completo; se promete rollback de la operación originaria y de su cascada causal. Una transición que requiera cierre y comienzo de otro nodo no puede publicar un estado intermedio incoherente. La codificación exacta de ambos límites deberá explicitarse en el ejecutor y sus pruebas.

### 4.3. Pasos y destinos

Las operaciones narrativas del candidato son `narrate`, `dialogue`, `choice`, `condition`, `effect`, `scene`, `transition`, `prepare_hand`, `skill_window`, `random`, `ending`. No todas son necesarias para MVP. Cada paso lleva `id` y `op`; si no existe destino explícito, se continúa con el paso siguiente cuando corresponda. Un destino tipado `{ "step": "..." }` pertenece al nodo actual; `{ "node": "..." }` inicia otra ejecución después de cerrar la actual.

- `narrate` y `dialogue` exponen texto y esperan confirmación. `dialogue` atribuye la intervención a una instancia de personaje válida.
- `choice` expone opciones con `visible_if` y `enabled_if` independientes; las consecuencias de la opción seleccionada se ejecutan antes de continuar; se revalidan permisos al recibir la acción.
- `condition` evalúa su prueba pura en el estado confirmado disponible al alcanzarla y selecciona `then` o `else`; rama ausente equivale a continuidad secuencial.
- `effect` ejecuta operaciones declarativas ordenadas en una sola unidad causal; `scene` cambia la presentación sin mover personajes; `transition` altera el flujo.
- `prepare_hand` y `skill_window` abren las ventanas permitidas por el autor; `random` selecciona rama con RNG transaccional; `ending` marca un final explícito.

Si una cadena de pasos automáticos salta indefinidamente sin llegar a una espera ni cierre, el motor debe detenerse con error y rollback de la **unidad causal actual**; no debe congelar la interfaz. Los bucles que contienen una decisión real del jugador no son automáticamente errores.

## 5. ALBERTO: mundo, instancias y memoria

**Clases de cartas:** `character`, `location`, `object`, `skill`, `effect`. Un personaje instanciado guarda lugar, propiedades, memoria individual y eventualmente atributos; un lugar instanciado guarda propiedades; un objeto guarda exactamente **un** propietario o **un** lugar válido, nunca ambos. Habilidades instanciadas pertenecen a una mano o reserva de un personaje; efectos instanciados permanecen vinculados a un objetivo mientras estén activos.

`transfer` y `move_character` son operaciones diferentes de `set_scene`. Cambiar de escena no mueve automáticamente a nadie. Retirar una instancia requiere verificar vínculos que quedarían colgantes: no puede abandonar objetos, habilidades, efectos o relaciones en estados inválidos. Ningún actor del mundo ejecuta autonomías inventadas por el motor: sus reglas y oportunidades están declaradas por el autor.

**Tres conceptos separados:**

- **Hecho narrativo persistente:** una ocurrencia registrada por `record_fact`, con identidad, secuencia y origen. Se conserva aunque el mundo cambie.
- **Conocimiento:** proposiciones/hechos que una instancia de personaje conoce, modificados mediante `learn_fact`; no se distribuyen automáticamente a terceros.
- **Creencia:** valor afirmado o negado de una proposición individual, modificado mediante `set_belief`; puede diferir del hecho histórico y de las creencias de otro personaje.

**Autoridad del historial:** un registro persistente de ocurrencias es la verdad de hechos narrativos. `has_fact`, recuentos y accesos por clave se resuelven mediante índices reconstruidos en memoria. No se guardarán simultáneamente `narrative.facts` y `history.facts` como fuentes de verdad independientes. La traza y las ejecuciones de nodo deben tener responsabilidades no superpuestas; ver §9.

### 5.1. Tiempo ficticio

Un único `world_time`, administrado como dato del mundo por ALBERTO bajo control transaccional de GISELA, solo avanza por `advance_time` u operación explícita equivalente. No depende del reloj del equipo; los clics, las consultas y los turnos no adelantan el tiempo automáticamente. Los umbrales cruzados se detectan incluso cuando un salto pasa por encima de ellos. Las recurrencias son una extensión declarativa, no un Scheduler separado. La convención exacta de instantes/husos históricos queda fuera del primer MVP.

## 6. S.O.F.I.A.: sistema opcional

Atributos fijos: `strength`, `openness`, `fortune`, `intelligence`, `awareness`. Escala entera común configurable, 0-10 por defecto. Cada atributo conserva `base` y `current`; el valor `effective` **se calcula**, no se almacena como segundo estado mutable: `current + suma(modificadores activos)` por defecto. El efectivo puede exceder la escala; `base` y `current` permanecen dentro de ella. No existen tiradas universales ni consumo automático de atributos. El autor declara umbrales y comprobaciones.

`GetScoresheet` consulta, en cualquier punto estable, los atributos, modificadores y efectos activos de un personaje autorizado. No crea turno, no cambia escena, mundo, historial, RNG ni revisión. No da acceso a estadísticas privadas de otros personajes salvo autorización explícita. La forma de dibujarlo pertenece al frontend. **S.O.F.I.A. y Scoresheet no forman parte de la vertical inicial propuesta.**

## 7. Habilidades y efectos (ADR-010-011, DECIDIDO EN CONTRATO; DIFERIDO EN MVP)

### 7.1. Habilidades

Cada personaje puede tener mano de capacidad N y reserva M, configuradas por autor. Una habilidad se juega **solo** desde mano y solo en una ventana autorizada por el contenido. Preparar/intercambiar mano y reserva tampoco crea turno salvo que inicie un nodo. Una habilidad consumible se consume por defecto al producirse el **intento jugable confirmado**, aunque su resultado narrativo fracase. Error técnico o cancelación restauran la habilidad y todo consumo provisional.

El uso invoca el mismo ejecutor de operaciones de GISELA. `effects`, `outcomes` y `return_policy` permanecen como conceptos; el contrato JSON final debe fijar cuándo se evalúan las condiciones de resultado y de devolución, y cómo se detecta coincidencia incompatible, **sin asignar prioridad implícita por orden**. Si la concesión/retorno excede capacidades, se solicitan descartes mediante ADR-001-005, no se elige arbitrariamente ni se hace commit parcial. No hay contrahechizos universales ni segundo intérprete de habilidades.

### 7.2. Efectos

Los efectos pueden aplicar modificadores y consecuencias `on_apply`/`on_expire`, con acumulación aditiva por defecto y restricciones explícitas como `unique_per_target`. Sin expiración autoral permanecen activos. Un vencimiento válido se procesa **como máximo una vez por instancia**, dentro de la misma transacción causal que lo descubre; sus `on_expire` y reacciones se incluyen en el commit o rollback.

Normalización técnica seleccionada: `after_turns: 1` vence en el primer cierre de **un turno posterior** al turno de aplicación; si se aplica entre nodos, en el próximo cierre elegible. `after_minutes` compara tiempo ficticio acumulado y detecta cruces de umbral. `on_fact` observa una ocurrencia **nueva** desde la aplicación. La composición inicial de varias cláusulas es `any`; `all` queda diferido porque exige memoria adicional de disparos satisfechos. Estos contratos requieren pruebas antes de implementarse.

## 8. Ejecutor declarativo, reacciones y transacciones

### 8.1. Tres mecanismos compartidos

- **Desencadenantes:** `state_changed`, `fact_recorded`, `turn_started`, `turn_ended`, `world_time_crossed`, `signal`, `effect_expired`, `node_completed` como repertorio candidato.
- **Condiciones puras:** combinadores booleanos, comparaciones tipadas, hechos, conocimiento, creencias, posesión, ubicación, habilidades, efectos y existencia de instancias.
- **Consecuencias tipadas:** `set`, `add`, `transfer`, `move_character`, `create_instance`, `remove_instance`, `record_fact`, `learn_fact`, `set_belief`, `set_scene`, `advance_time`, operaciones de habilidades/efectos, `roll` y `emit_signal` conforme al catálogo candidato.

Los nodos, cartas y reglas comparten el vocabulario; **tener un operador declarado no implica que deba implementarse completo en MVP**. No existen acciones de movimiento de puertas ni reglas de romance integradas al motor; el autor compone consecuencias generales.

### 8.2. Unidad causal y rondas (ADR-008)

1. GISELA valida la acción ofrecida, su revisión, referencias y precondiciones evidentes.
2. Evalúa la operación originaria **en aislamiento**, junto con sus operaciones ordenadas y su RNG provisional, y obtiene un conjunto de sucesos.
3. Por rondas, todas las reglas activadas por los sucesos de la ronda evalúan sus guardas **sobre el mismo estado base de esa ronda**.
4. Se combinan operaciones compatibles; dos `set` incompatibles sobre el mismo destino, `set` concurrente con `add`, destinos distintos del mismo objeto, retiro y modificación simultánea incompatible y situaciones similares generan error. Dos `add` numéricos compatibles pueden sumarse; sets idénticos se tratan como idempotentes si no ocultan otro conflicto.
5. Una mutación efectiva genera sucesos para la ronda siguiente; una operación `set` que deja idéntico el valor observable no genera por sí sola un `state_changed`. Las señales y hechos explícitos sí son ocurrencias con identidad.
6. Al converger, confirma en una sola operación el mundo, cursor, historial, RNG, IDs y revisiones; al fallar, no confirma ninguna parte de la unidad causal actual.

El orden de archivos o diccionarios nunca decide un conflicto. Se fija un presupuesto interno de pasos automáticos, reacciones y profundidad de evaluación; su exceso devuelve `BUDGET_EXCEEDED`/`REACTION_CYCLE` según la causa. La detección de ciclos debe considerar progreso o repetición de estados causales, no prohibir bucles narrativos elegidos por el jugador.

**Endurecimiento recomendado, todavía no codificado:** especificar si `state_changed` resume los cambios netos de una ronda (recomendación por simplicidad) y cómo interactúan escrituras concurrentes a relaciones y colecciones. No asumir que JSON Schema puede comprobar esas semánticas.

### 8.3. Transacciones que necesitan al jugador (ADR-001-005, DECIDIDO)

Una operación puede descubrir una elección auxiliar (por ejemplo, descartar una habilidad por capacidad). **No se confirma nada** hasta completar todas las decisiones de esa operación y de su cadena causal. Existe a lo sumo **una transacción pendiente por sesión**; no se intercalan otras mutaciones ni avances narrativos. Se permiten consultas puras y exportación/restauración.

- **Origen voluntario:** el jugador puede cancelar; la operación entera se abandona, incluidos hechos, RNG e IDs provisionales. Vuelve a estar disponible la decisión original, sujeta a las condiciones vigentes.
- **Origen obligatorio:** la cancelación no puede saltarse la consecuencia. Puede guardarse/salirse; si no hay resolución válida, hay error técnico verificable.
- **Persistencia:** se guarda solamente el último estado confirmado más la intención original, su procedencia y contexto vinculado, las respuestas provisionales y la solicitud actual. No se persiste el borrador interno de la ejecución.
- **Restauración:** GISELA reconstruye/revalida determinísticamente desde el estado confirmado y las respuestas guardadas. Una reproducción que ya no corresponda al contrato o digest debe rechazarse, no repararse silenciosamente.
- **Proyección:** Observe/Scoresheet muestran exclusivamente el mundo confirmado. La solicitud pendiente puede mostrar los **datos mínimos necesarios** de la decisión futura, identificados como propuesta, no como cambio ya ocurrido.
- **Confirmación:** ocurre exactamente una vez, sin dobles concesiones, eventos, consumo RNG o cambios de cursor.

**Precisión de mantenibilidad:** una `choice` narrativa que espera respuesta es distinta de `pending_transaction`: la primera aún no inició la operación causal de una opción; la segunda conserva una operación ya intentada cuya confirmación requiere decisiones auxiliares. No deben almacenarse ambas bajo un único campo ambiguo `pending_choice`. Al guardar, toda respuesta provisional debe tener identificación estable y contexto; al responder, la revisión de la proyección y el token de decisión siguen siendo obligatorios.

## 9. Estado de sesión, historial, revisiones y RNG

### 9.1. Fuentes de verdad

El estado confirmado incluye identificadores de paquete/sesión y digest, formato de sesión, estado y cursor narrativo, escena, turno/identidad de ejecución, reloj ficticio, instancias ALBERTO, valores persistentes, capacidades, relaciones, conocimientos, creencias, hechos y ejecuciones confirmadas, RNG, asignador de IDs y revisiones. Opcionalmente se serializa **una** operación pendiente según §8.3.

- **Hechos:** historial autoritativo de ocurrencias. `has_fact` y sus índices son derivados.
- **Ejecuciones:** cada entrada a nodo tiene identidad y turno; el historial de ejecuciones no se reconstruye suponiendo que cada nodo ocurrió una sola vez.
- **Traza:** sucesos/acciones confirmados con procedencia para diagnóstico y reproducción. Se exige relación clara con el historial de ejecuciones, sin conservar una segunda lista mutable de los mismos hechos.
- **Proyecciones:** `Observe`, Scoresheet y snapshots privados son lecturas, no estados persistidos.
- **RNG:** generador determinista de contador y SHA-256, independiente del `random` del host. Su representación exacta, muestreo uniforme sin sesgo y vectores de prueba se fijarán antes de desarrollar `roll` (ADR-012); el contador del borrador se revierte ante cancelación/error.

### 9.2. Revisiones, acciones y errores

`revision` cambia cuando cambia la proyección autorizada (avance de cursor, nueva espera, confirmación/cancelación pertinente). `world_revision` cambia cuando cambia el estado persistente del mundo. Una lectura pura no cambia ninguna de las dos. La relación entre revisionado de una espera pendiente y el estado confirmado debe ser explícita: las esperas afectan la proyección, no publican mutaciones del mundo.

`Observe` devuelve una vista coherente con acciones y opciones identificadas por `action_id` opaco y ligadas a `revision`; una opción bloqueada puede ser visible pero **no ejecutable**. `Act` recibe `session_id`, `revision` y `action_id`, y únicamente parámetros tipados que la acción ofrecida haya declarado. El motor vuelve a verificar su autorización y sus condiciones. Una acción antigua, inventada o prohibida se rechaza sin commit.

`GetScoresheet` es lectura privilegiada en función del personaje permitido. `world_snapshot` es interno/privilegiado y no puede filtrarse por `Observe` a un usuario común. `export_session`/`restore_session` no leen ni escriben archivos físicos; el host maneja bytes. Un guardado exige snapshot estable, formato y digest compatibles. No se realizan migraciones automáticas entre paquetes ni se finge que passwords compactos del demo equivalen a snapshots completos.

### 9.3. Resistencia a fallos y seguridad de contenido

El estado restaurado es entrada no confiable hasta pasar validación estructural, semántica y de invariantes (incluidas referencias, IDs, enum de estado, cursor, posesión exclusiva, capacidad, revisión y contexto de transacción pendiente). GISELA rechaza datos inválidos sin modificarlos. Los mensajes de error identifican operación, nodo/paso/regla y causa; **no** muestran información secreta en una proyección pública.

**Endurecimiento propuesto:** límites explícitos de tamaño de paquete, cantidad de instancias, longitud de texto, profundidad de condiciones y presupuesto de pasos; validación de las referencias a assets por el host y prohibición de efectos externos dentro de operaciones provisionales. Esto no añade mecánicas ni subsistemas; previene entradas patológicas y evita acciones irreversibles antes del commit.

## 10. Auditoría crítica: defectos demostrados y riesgos

### 10.1. Defectos históricos comprobados en el conjunto candidato 1.0

El comprobador incluido en el ZIP **original 1.0** ejecutaba satisfactoriamente la verificación estructural de 13 schemas y el fixture, pero dejaba pasar los defectos siguientes. Esta tabla conserva el diagnóstico de origen; el nuevo paquete 1.1 aplica sus correcciones estructurales y agrega regresiones. **Su conformidad semántica sigue pendiente.**

| Severidad | Evidencia | Corrección exigida |
|---|---|---|
| **Bloqueante** | `session.schema.json` rechaza `exploring` sin `narrative.pending_choice`, aunque puede ser un estado válido. | Esperas opcionales y compatibles con el estado principal. |
| **Bloqueante** | Acepta `node` sin `cursor` y `ended` sin desenlace. | Restricciones condicionales por `status`; validación semántica en restauración. |
| **Alta** | Acepta `exploring` con `pending_choice.kind: overflow`, incluso con candidatos vacíos. | Separar `choice` de transacción pendiente y validar vinculación/contexto. |
| **Bloqueante** | La `pending_choice` actual solo tiene `kind/step/candidates`: no guarda la intención, respuestas provisionales ni contexto de ADR-001-005. | Introducir una `pending_transaction` estable; no serializar el borrador. |
| **Alta** | `node.schema.json` acepta `choice` sin `prompt` (incluida la fixture), mientras `observe.schema.json` requiere `prompt` para esa misma elección. | Hacer opcional el `prompt` de la proyección o establecer una fuente y fallback inequívocos. **Recomendación: proyección sin prompt obligatorio.** |
| **Alta** | El snapshot candidato duplica `narrative.facts` con `history.facts`; `narrative.executions` no tiene frontera clara con `history.trace`. | Un solo historial autoritativo y vistas/índices derivados. |
| **Alta** | No consta un registro persistido de IDs retirados ni siguiente contador de asignación. | Incorporar el asignador de ADR-009 a `session`. |
| **Media** | El schema valida objetos con propietario o ubicación por `oneOf`, pero no puede garantizar que las referencias existan ni sean del tipo correcto. | Preservar `oneOf` y añadir validación semántica, sin duplicar reglas de JSON Schema. |

No se han ejecutado pruebas de comportamiento del motor nuevo ni de restauración real; estas observaciones proceden del schema y del validador, no de un ejecutor implementado.

### 10.2. Riesgos de diseño que todavía requieren especificación

| Riesgo | Impacto | Resolución / estado |
|---|---|---|
| Semántica de cambios netos por ronda | Disparos repetidos o perdidos en escrituras consecutivas | **PENDIENTE TÉCNICO**: preferir evento de cambio neto por campo y ronda. |
| Cadena automática de nodos sin espera | Bucle infinito o ejecución muy larga | **DERIVADO DE ADR-008**: presupuesto y error tipado, distinto de ciclos interactivos. |
| Repetición de evaluación de operación pendiente | Concesiones dobles, RNG/IDs consumidos, exposición de borradores | **CUBIERTO CONCEPTUALMENTE POR ADR-001-005**: re-ejecutar desde estado confirmado y commit exact-once; faltan tests. |
| Posible discrepancia entre validación estructural y proyección | Paquete válido que no puede mostrarse | **PENDIENTE**: fixtures de ida y vuelta autoría → Observe/Act. |
| Colisiones o ciclos de referencias contextuales | Cambios al objetivo equivocado | **ADR-009**: resolución tipada y ámbitos vinculados. |
| Expiraciones por `all` y recurrencias | Estado adicional y reglas difíciles de reconstruir | **DIFERIDO**: no complejizar v1 sin caso de uso. |
| Cambios de definiciones entre guardado/restauración | Sesión irreproducible | **ADR-013**: digest estricto, sin migraciones silenciosas. |
| `presentation` demasiado amplio | Acoplar interfaz con lógica o pasar instrucciones ejecutables | **LÍMITE DECIDIDO**: metadatos opacos, interpretados por el host de forma permitida. |
| Parámetros externos arbitrarios en Act | Inyección de destinos/operaciones | **ADR-014**: lista de parámetros permitidos ligada a acción emitida y revisión. |

### 10.3. Simplificaciones aceptadas en la revisión

1. No introducir un quinto estado principal para la transacción pendiente.
2. No guardar un segundo mundo provisional ni una segunda lista de hechos.
3. No ordenar reglas reactivas por prioridad implícita; detectar conflictos en un solo ejecutor.
4. No convertir acciones de movimiento del demo en subsistemas generales.
5. No hacer del sistema de habilidades el ejecutor central del motor.
6. No permitir selección arbitraria del primer resultado de una consulta ambigua.
7. No implementar `all` de expiraciones ni migraciones de sesión antes de que exista una necesidad concreta.
8. No acoplar la compatibilidad del motor nuevo al viejo Croupier ni a schemas históricos.

## 11. Contratos de validación y plan de endurecimiento

**Tres capas, una autoridad:**

1. **JSON Schema:** forma, requeridos, enums, discriminación de variantes, exclusividad de campos, restricciones de tipos y formatos.
2. **Validación semántica del paquete y snapshot:** IDs únicos, correspondencia de categorías y referencias, ligaduras contextuales, destinos válidos, definiciones de variables, tipos comparables, propiedad/ubicación exclusiva, S.O.F.I.A., capacidades, sucesos, digest y estados consistentes.
3. **Invariantes de ejecución:** autorización de Act, transacciones y rollback, conflictos/reactividad, revalidación de condiciones, consumos RNG/IDs, integridad de pendientes y convergencia.

**Pruebas mínimas a incorporar en la revisión de schemas:**

- Cuatro estados principales válidos y variantes inválidas (falta de cursor, fin sin desenlace, espera incongruente).
- Elección con y sin `prompt` y proyección correspondiente; opción oculta, visible-bloqueada, habilitada y rechazo de ID falsificado.
- Registro/restauración de transacción voluntaria cancelada y obligatoria no cancelable, con respuestas acumuladas; sin borradores públicos, IDs/RNG ni hechos duplicados.
- Dos `add` compatibles, dos `set` contradictorios, no-op sin disparo, regla cíclica y salto automático sin punto de espera.
- Instancia creada/eliminada/restaurada sin reutilización de identidad; objeto con un único poseedor o lugar.
- Final de nodo sin transición con escena, y error explícito si no hay escena; transición a otro nodo sin doble cierre de turno.
- Digest diferente en restauración, formato no soportado y rechazo de snapshot inconsistente.
- Reproducción determinista en dos frontends, cuando exista el adaptador Ren'Py.

**Criterios de cierre:** los schemas revisados pasan metavalidación y fixtures positivos/negativos; el validador semántico documenta las invariantes que JSON Schema no alcanza; cada ADR implementada cuenta con al menos una prueba observable. No se declarará completo el motor solo por el éxito de `verify_contracts.py`.

## 12. ADR: Registro integrado y precedencia

| ADR | Estado | Resolución |
|---|---|---|
| 001 | **DECIDIDO** | Solicitar decisiones auxiliares antes de confirmar la transacción. |
| 002 | **DECIDIDO** | Cancelación íntegra solo si la operación originaria es voluntaria. |
| 003 | **DECIDIDO** | Guardar estado confirmado + intención/contexto/respuestas y reconstruir; no el borrador. |
| 004 | **DECIDIDO** | Máximo una transacción pendiente; no intercalar mutaciones. |
| 005 | **DECIDIDO** | Observe/Scoresheet muestran mundo confirmado; solicitud pendiente separada. |
| 006 | **DECIDIDO por selección delegada** | `preparing`/`node`/`exploring`/`ended` y esperas subordinadas. |
| 007 | **DECIDIDO por selección delegada** | Turno por ejecución de nodo; cierre causal común para `node_completed`/`turn_ended`. |
| 008 | **DECIDIDO por selección delegada** | Rondas simultáneas, conflictos explícitos y presupuesto de seguridad. |
| 009 | **DECIDIDO por selección delegada** | IDs de instancia no reutilizables y referencias tipadas sin desempate implícito. |
| 010 | **DECIDIDO por selección delegada** | Habilidades declarativas usan ejecutor único; implementación fuera de MVP. |
| 011 | **DECIDIDO por selección delegada** | Tiempo explícito y expiración simple; `all` diferido. |
| 012 | **DECIDIDO por selección delegada** | RNG SHA-256 con contador; byteado y vectores aún por formalizar. |
| 013 | **DECIDIDO por selección delegada** | Snapshot confirmado autoritativo, historia no duplicada, digest estricto. |
| 014 | **DECIDIDO por selección delegada** | Observe/Act tipados; validación estructural, semántica y ejecución. |
| 015 | **PROPUESTA PARA APROBACIÓN** | CLI primero y vertical narrativa mínima con una reacción causal. **Sin autorización de código.** |

Este registro integrado se convierte en la referencia de precedencia del diseño actual. El registro separado del 29 de octubre conserva la argumentación histórica de cada elección; no es una segunda fuente del contrato ejecutable. Una modificación posterior requerirá ADR nueva con justificación y pruebas, no edición silenciosa del historial.

## 13. MVP recomendado (ADR-015, todavía NO aprobado)

La primera vertical debería demostrar el núcleo mediante un paquete de prueba **no canónico**: Alberto, Gisela y un casete; uno o dos nodos; narración, diálogo, condición, elección con visibilidad/disponibilidad, transferencia de objeto, registro de hecho, una reacción compatible, salida a una escena o desenlace, exportación/restauración y reproducción determinista. No pretende reconstruir la cronología ni escribir el guion definitivo de *Blue Forever*.

**Interfaz:** CLI inicial que consume `Observe/Act`; conexión mínima posterior de Ren'Py al mismo contrato. **Fuera del primer hito:** mano/reserva, consumo de habilidad, expiraciones avanzadas, S.O.F.I.A./Scoresheet, generación aleatoria si no es indispensable, scheduler de rutinas, contrahechizos y navegación propia del demo.

**Criterios de aceptación:** una opción oculta/bloqueada no es ejecutable; la elección válida realiza exactamente sus consecuencias; el hecho persiste y es consultable; un conflicto reactivo revierte la unidad; una sesión restaurada conserva cursor y mundo; mismo paquete y entradas producen el mismo resultado. La operación pendiente interactiva de ADR-001-005 requiere un hito de integración propio, no una simulación incompleta dentro del MVP.

**Puerta de entrada a programación:** aprobación expresa del alcance y de los contratos mínimos revisados. Hasta entonces, solo documentación, pruebas de schemas y validadores/fixtures preparatorios, no implementación del engine.

## 14. Estado de los 13 JSON Schemas y migración documental

| Archivo | Estado de corrección estructural 1.1 | Pendiente de ejecución/semántica |
|---|---|---|
| `common.schema.json` | Consultas singulares sin `first_by_id`, expiración `any`, sin recurrencia implícita; literales escalares. | Referencias tipadas, condiciones y disparos reales. |
| `node.schema.json` | Pasos y `choice.prompt` opcional conservados como fuente autoral. | Integridad de destinos, turnos y cierres. |
| `scene.schema.json` | Estructura existente conserva acciones, actores y elementos declarativos. | Visibilidad y autorización de acciones. |
| `rule.schema.json` | Estructura existente de desencadenante/guarda/consecuencia. | Conflictos y rondas compartidas. |
| `card.schema.json` | Estructura existente de entidades, habilidades y efectos; `any` en expiraciones. | Resultados y retornos condicionales. |
| `initial_state.schema.json` | Estructura existente, con propietario o ubicación exclusivos por objeto. | Referencias, capacidades e identidad global. |
| `package.schema.json` | `format_version: 1.1`; referencias locales a `/v1.1/`. | Digest canónico y catálogos cruzados. |
| `session.schema.json` | Estados restringidos, `pending_transaction`, historia única, RNG y asignador. | Replay, rollback, IDs e historial coherentes. |
| `observe.schema.json` | `status`, acciones tipadas únicas, elección sin prompt obligatorio, vista de espera restringida. | Coherencia y confidencialidad de la proyección. |
| `act.schema.json` | Parámetros estructuralmente escalares y acotados. | Autorización por acción y revisión. |
| `result.schema.json` | Resultado tipado, vista coherente y detalles de error escalares. | Control de errores y no filtración de datos. |
| `scoresheet.schema.json` | Se mantiene contrato de lectura estructural. | Permisos y cálculo derivado correcto. |
| `world_snapshot.schema.json` | Se mantiene contrato privilegiado de lectura. | Acceso restringido y revisión coherente. |

**Recomendación documental:** retirar el apéndice de más de 3.900 líneas con los schemas candidatos del documento arquitectónico normativo. Los JSON versionados viven en su paquete y tienen pruebas propias; reproducirlos dentro del Markdown fomenta divergencias. Esta revisión mantiene los schemas fuera del Markdown: **los archivos ya se corrigieron y se distribuyen en `GISELA_Schemas_v1_1_ADR_001_014.zip`**, con `verify_contracts.py`, `test_contracts.py`, fixtures y una matriz de validación semántica pendiente. El ZIP 1.0 queda archivado como candidato no conforme, no como contrato vigente.

## 15. Próximos hitos y condiciones de cierre

1. **Arquitectura:** cerrada en sus principios y ADR-001-014; los detalles de ejecución y validación pendientes continúan identificados.
2. **Schemas:** revisión estructural 1.1 aplicada sobre los 13 archivos, con 41 pruebas de regresión y siete fixtures adicionales. Pendiente: validador semántico, digest canónico y pruebas del ejecutor.
3. **Validación semántica:** definir matriz de errores reproducibles y pruebas de integridad cruzada, separando diagnósticos técnicos bloqueantes de advertencias de calidad narrativa.
4. **MVP:** aprobar explícitamente ADR-015 y su criterio de aceptación, antes de comenzar la implementación del motor.
5. **Ren'Py:** integrar únicamente después de tener un núcleo ejecutable desde CLI que entregue las mismas proyecciones y acepte las mismas acciones.

### Fuentes contrastadas

- `GISELA_ALBERTO_SOFIA_Arquitectura_y_Schemas_v1(1).md` (29-10-2026): candidato conceptual y transcripción de 13 schemas; **reemplazado en arquitectura por este documento**.
- `GISELA_Schemas_v1(1).zip`: conjunto de 13 schemas originales, ahora **histórico**, sustituido por el paquete versionado 1.1.
- `GISELA_registro_de_decisiones_arquitectonicas_2026-10-29.md`: razonamiento de ADR-001-015 y selección delegada.
- `Central_Clasificadora_Demo_RenPy_instrucciones.txt`, `Blue_Forever.md`, `lptn.zip`: restricciones originales del demo, obra y arquitectura histórica. Los dos últimos no se convierten en decisiones nuevas del motor por simple inclusión como fuente.

**Conclusión de revisión:** el endurecimiento principal no consiste en sumar componentes, sino en hacer **inexpresables o rechazables** las sesiones inconsistentes, representar correctamente las transacciones pendientes, eliminar fuentes duplicadas de verdad y preservar el límite estricto entre definiciones, sesión e interfaz. No se ha implementado código de GISELA; los schemas corregidos son una nueva entrega 1.1 y no una modificación retrospectiva del ZIP original.


## 16. Sincronización documental con schemas 1.1 (29-10-2026)

**Artefacto vigente para la forma de datos:** `GISELA_Schemas_v1_1_ADR_001_014.zip`, compuesto por los 13 schemas JSON Schema Draft 2020-12, `example.package.json`, siete fixtures de sesión/proyección, pruebas de regresión y documentación de invariantes semánticas. Su `manifest.format_version` y `session.schema_version` valen `1.1`; los `$id` y `$ref` usan el espacio `/v1.1/`. Los archivos 1.0 no se migran automáticamente.

La nueva `session` separa `history.facts` / `history.executions` / `history.trace`, incorpora `identity` y `rng`, y añade `pending_transaction` opcional con intención identificada, origen, contexto, respuestas y solicitud. No guarda un mundo de borrador. Los estados narrativos exigen cursor, escena, preparación o desenlace según corresponda. La nueva proyección `observe` conserva una sola lista `actions`, permite `choice` sin `prompt` y restringe las acciones mientras exista una operación pendiente. Los resultados narrativos que todavía no se ejecutan continúan definidos solo como contrato autoral.

**Resultado de pruebas del paquete:** 13/13 schemas válidos, siete fixtures válidos y 41/41 pruebas de regresión estructural. **Resultado no obtenido:** demostración de la semántica del ejecutor, integridad referencial completa, rollback, reanudación determinista, autorización real de `Act` y vectores reproducibles de RNG. Estas obligaciones están listadas en `SEMANTIC_VALIDATION.md` dentro del ZIP. No se ha autorizado el MVP ni implementado el motor nuevo.


## 17. Enmienda contractual: schemas 1.2 y puerta de admisión (29-10-2026)

**Artefacto vigente de contratos:** `GISELA_Schemas_v1_2_Admisor_Semantico_v0_2.zip`. Esta enmienda sustituye a la sección 16 **para determinar cuál es el paquete actual**; aquella conserva valor histórico de la transición 1.0→1.1. Los 13 JSON Schema llevan identificadores `/v1.2/`, `manifest.format_version` y `session.schema_version` son `1.2`. No existe migración automática.

**Historial de opciones:** cada `history.executions[].selected_options` conserva pares `{step_id, option_id}`, cuya interpretación se realiza dentro del nodo al que corresponde la ejecución. No se exige unicidad de ese par en toda una ejecución, pues un ciclo autoral puede volver a ofrecer un paso. `history.trace` registra diagnóstico causal, no sustituye la procedencia normalizada de elecciones. Los registros 1.1 con un solo `option_id` no son restaurables por inferencia cuando existen opciones homónimas.

**Acciones de escena y elemento:** `pending_transaction.source` con `kind: scene_action` lleva siempre `scene` y `action`; añade `element` cuando la acción está declarada en `scene.elements[].actions`. La omisión de `element` identifica exclusivamente una acción en `scene.actions`. Los IDs de acciones son únicos por propietario y pueden repetirse en otros elementos de la misma escena. GISELA conserva la responsabilidad de construir fuentes precisas; el frontend solo envía `action_id` opacos autorizados.

**Admisión:** el anfitrión que cargue paquetes para GISELA debe pasar por una única puerta de validación antes de iniciar una sesión: JSON estricto (incluido rechazo de claves duplicadas y constantes no JSON) → JSON Schema → comprobación semántica estática → paquete admitido. Los errores bloquean; las advertencias se publican y, por defecto, no bloquean. El módulo `admit_package.py` implementa ya esa puerta **offline**. El ejecutor aún no existe y, por tanto, no se afirma que la integración runtime esté implementada. Esta puerta no añade una autoridad sobre las transacciones: GISELA conserva la única autoridad de ejecución.

**Pruebas y límites:** regresiones de formatos antiguos, opciones ambiguas, acciones por elemento, error de referencia, claves duplicadas y formatos JSON inválidos. Validar un paquete no demuestra reproducibilidad de RNG, atomicidad, secreto de las proyecciones, reanudación de pendientes ni digest canónico; siguen siendo obligaciones independientes para el futuro ejecutor. ADR-015 permanece sin aprobación expresa.
