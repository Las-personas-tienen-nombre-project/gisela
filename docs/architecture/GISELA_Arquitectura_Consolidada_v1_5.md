# GISELA, ALBERTO y S.O.F.I.A. Arquitectura consolidada, versión 1.5

**Fecha:** 29 de octubre de 2026. **Estado:** base arquitectónica v1.5 con secciones de avance histórico. **Primer caso de uso:** "Las personas tienen nombre", dentro del proyecto Central Clasificadora. El motor es general y no puede incorporar como obligaciones universales las mecánicas específicas de este demo. Para la interfaz y los campos de presentación actuales, consulte la [API de clientes](API_CLIENTES.md) y la [guía de GLAUQUIR](../guides/GLAUQUIR.md).

## 1. Alcance y precedencia

La fuente estructural de verdad son los schemas de `gisela/contracts/`; la validación semántica complementa las restricciones que JSON Schema no puede verificar. Una definición válida no demuestra que la historia sea jugable, que una transacción converja ni que un guardado se pueda restaurar. Cada garantía necesita su prueba independiente.

## 2. Identidad y límites de los componentes

GISELA significa "enGine for Interactive Stories through Events, Links, and Actions". Es el único motor que ejecuta la narrativa, posee una sola sesión y autoriza todas las transacciones. Sus responsabilidades incluyen el cursor de nodos, las condiciones, las acciones, el historial, el RNG, las revisiones, la persistencia lógica y la API `Observe` y `Act`.

ALBERTO significa "Autonomous Layer for Beings, Environments, Relationships, Traits, and Objects". Es un subsistema interno de GISELA, no un segundo motor. Administra las entidades y sus invariantes: personajes, lugares, objetos, ubicación y posesión exclusiva, habilidades, efectos, conocimiento, creencias, relaciones y reloj ficticio. ALBERTO no confirma transacciones ni conserva un segundo reloj.

S.O.F.I.A. significa "Strength, Openness, Fortune, Intelligence, Awareness". Es una capacidad opcional de ALBERTO. Sus cinco atributos enteros tienen escala común configurable, por defecto de 0 a 10. Cada personaje puede tener valores base y actuales; el efectivo resulta del actual más modificadores activos y puede superar la escala. No hay tiradas universales, porque el autor declara los chequeos que necesita.

Ren'Py y CLI son anfitriones. Presentan una proyección autorizada y envían identificadores de acción; no interpretan condiciones ni inventan consecuencias. Volumen, animación, recursos visuales y secuencias ANSI pertenecen al anfitrión. Los roles semánticos de color declarados por el autor pueden formar parte del estado narrativo confirmado. Ren'Py no es requisito para probar los contratos del motor.

## 3. Paquete narrativo

Un paquete contiene `manifest`, `nodes`, `cards`, `scenes`, `rules`, `initial_state`, `endings` y opcionalmente `strings`. El contenido es declarativo y no ejecuta código Python suministrado por el autor. Sus identificadores técnicos, tipos, operaciones y claves se escriben en inglés; los textos literarios conservan su idioma, en este proyecto especialmente español de Chile.

Las cartas describen tipos de entidades, habilidades y efectos. Los acontecimientos narrativos se expresan mediante nodos. Las definiciones permanecen inmutables durante una sesión; el estado de instancias se almacena por separado. Los IDs de definición son únicos dentro de su categoría, mientras que los IDs de instancia son únicos en la sesión completa y no se reutilizan después de retirar un ejemplar.

Los IDs de pasos se resuelven dentro de su nodo. Las opciones se identifican mediante nodo, paso y opción; el historial conserva al menos el paso y la opción dentro de la ejecución del nodo correspondiente. Las acciones de escenas se identifican con su propietario, que puede ser la escena o un elemento de ella. Se rechazan las referencias que exigen un elemento singular cuando encuentran varios candidatos sin selección inequívoca.

## 4. Modelo narrativo

La unidad de ejecución es el nodo. Cada nodo tiene una secuencia ordenada de `steps`, cada uno con `id` y `op`. Los pasos incluyen narración, diálogo, elección, condición, consecuencias, cambio de escena, transición, preparación excepcional de habilidades, ventana de uso, selección aleatoria y final explícito. El motor ejecuta secuencialmente salvo cuando aparece un destino tipado a un paso del mismo nodo o a otro nodo.

La ausencia de destino significa continuar con el paso siguiente cuando corresponda. Una elección puede tener condiciones diferentes de visibilidad y disponibilidad. El frontend no tiene autoridad para ejecutar opciones que el motor haya ocultado o bloqueado. Toda selección se revalida cuando llega a GISELA.

Un turno corresponde a la ejecución efectiva de un nodo, no a cada clic ni a una consulta de estadísticas. La transición a otro nodo cierra primero la ejecución anterior y abre un turno nuevo. Un nodo sin transición final puede dejar la sesión en la escena explorable. El desenlace de la historia se declara de manera explícita, no por el mero agotamiento de pasos.

## 5. Máquina de sesión

Los estados principales son `preparing`, `node`, `exploring` y `ended`. Las esperas particulares son datos del estado, no nuevas máquinas independientes. `node` exige cursor válido y una ejecución correspondiente; `ended` exige un final declarado; `exploring` no tiene nodo activo y conserva una escena válida. Una sesión puede encontrarse en un punto estable de espera dentro de un nodo, siempre que no exista una transacción a medio confirmar.

El cierre del nodo debe declarar una frontera causal única para los sucesos de finalización; la evaluación de reglas no puede depender de un orden accidental de almacenamiento. Las consultas y los guardados no aumentan el turno ni hacen avanzar el reloj ficticio. Los pasos que avanzan el reloj lo hacen expresamente.

## 6. Mundo ALBERTO

Los objetos físicos pertenecen exactamente a un personaje o se encuentran en un lugar; nunca simultáneamente en ambos. `transfer` mueve un objeto comprobando su origen. `move_character` cambia la ubicación de un personaje; `set_scene` cambia solamente la presentación. Las escenas y los lugares no son equivalentes: un lugar puede presentarse mediante varias escenas y una escena puede conservarse al cerrar un nodo.

Los hechos narrativos persistentes se registran mediante `record_fact`. El conocimiento individual se obtiene mediante `learn_fact`, y las creencias mediante `set_belief`. Una persona no aprende automáticamente lo que otra sabe. Los cambios posteriores del mundo no eliminan hechos históricos. El historial es la autoridad para registrar ocurrencias; las consultas rápidas pueden reconstruirse como índices derivados, evitando mantener dos fuentes persistentes de verdad.

Las habilidades se almacenan en una mano de capacidad N y una reserva de capacidad M, distintas del inventario físico. Se juegan desde la mano en ventanas permitidas por el autor. El consumo por intento confirmado es predeterminado, incluso ante fracaso jugable; un error técnico o una cancelación de la operación revierte el intento. Las capacidades y políticas especializadas quedan fuera de la primera vertical implementada.

Los efectos pueden aplicar modificadores y consecuencias y expirar por turnos, tiempo ficticio, condiciones, hechos o retiro explícito. La v1.2 expresa composición de vencimientos mediante `any`; la semántica avanzada de `all` se pospone. Las reglas de temporización no constituyen un Scheduler autónomo.

## 7. Condiciones, consecuencias y reacciones

Las condiciones son consultas puras y tipadas. Pueden usar referencias explícitas o contextuales como `$actor` y `$target`, siempre que exista una ligadura válida. Los nodos, las cartas y las reglas ALBERTO comparten el mismo vocabulario declarativo de consultas y consecuencias. No hay un segundo lenguaje de acciones exclusivo de una interfaz.

Las reglas reactivas se ejecutan por rondas. Todas las reglas activadas en una ronda observan el mismo estado base. Los cambios compatibles se combinan, mientras que las escrituras contradictorias provocan un fallo tipado y revierten la transacción causal completa. Un cambio sin diferencia efectiva no debe provocar por sí solo nuevos `state_changed`. El ejecutor necesitará límites y detección de ciclos para impedir reacciones infinitas; aún no se ha fijado el presupuesto numérico.

El RNG y el asignador de IDs son parte de la misma transacción que las modificaciones del mundo y del historial. Una operación fallida no consume aleatoriedad ni identidades y no publica consecuencias parciales.

## 8. Transacciones pendientes, ADR-001 a ADR-005

Una acción originaria y la cadena causal de reacciones se confirman de manera atómica. Cuando una consecuencia requiere una decisión adicional del jugador, GISELA conserva la intención original, su contexto, las respuestas provisionales y la solicitud pendiente, mientras que el mundo confirmado permanece sin cambios. El borrador no se entrega al frontend ni se guarda como un segundo mundo.

Solo puede existir una transacción pendiente por sesión. Mientras está pendiente, no se ejecutan otras acciones narrativas ni mutaciones del mundo. Se permiten consultas autorizadas y guardar la sesión. Una transacción voluntaria puede cancelarse por completo; una operación automática obligatoria no puede cancelarse para eludir sus consecuencias. En ambos casos se mantiene la semántica de errores técnicos y de retorno al último estado confirmado.

La restauración debe reconstruir la transacción desde la intención y las respuestas provisionales, compararla con las definiciones y el estado confirmado y continuar solo si la reconstrucción es válida. H2 implementa ese replay para avances de paso y opciones de elección que suspenden por `grant_skill`; los demás orígenes siguen pendientes. Los schemas y el validador estático comprueban parcialmente la procedencia, pero no sustituyen el replay dinámico.

## 9. Interfaces y consulta

`Observe` produce una vista coherente y autorizada, con revisión de presentación, escena, contenido activo y acciones posibles. No contiene el `world_snapshot` interno completo porque podría revelar datos ocultos. `Act` recibe identificadores opacos que estaban disponibles para la revisión correspondiente, sin aceptar operaciones arbitrarias suministradas por el frontend. Se rechazan acciones vencidas, invisibles, bloqueadas o no ofrecidas.

`GetScoresheet` es una lectura de solo consulta, cuando los personajes y permisos pertinentes existen. No cambia escena, turno, tiempo, RNG, revisiones ni historia. El frontend decide cómo dibujarla. Una vista privada del mundo de ALBERTO sigue separada de la proyección pública.

## 10. Persistencia

GISELA exporta y restaura una representación completa del estado confirmado de sesión en JSON. La escritura y lectura de archivos corresponde al anfitrión. El estado incluye cursor, turnos, reloj ficticio, instancias, ubicaciones, propiedades, hechos, ejecuciones, relaciones, conocimientos, habilidades, efectos, RNG, identidades utilizadas, revisiones y, cuando corresponda, la transacción pendiente.

Los guardados almacenan `package_digest`, un SHA-256 de 64 caracteres hexadecimales calculado sobre `GISELA-CJSON-1` con separación de dominio. El algoritmo exacto, los límites numéricos y los vectores están especificados en `docs/determinism/DIGEST_CANONICO.md`. Un cambio en las definiciones cambia el digest y la restauración contra ese paquete debe rechazarse. Las migraciones automáticas entre versiones no están permitidas.

El estado RNG usa `sha256_counter_v1`, con semilla hexadecimal de 32 bytes y contador entero. Los bloques se derivan de SHA-256 sobre semilla y contador; el muestreo por rechazo evita sesgo de módulo y la función devuelve un estado nuevo sin modificar el anterior. El contrato se detalla en `docs/determinism/RNG_SHA256_CONTADOR.md`. El perfil está probado como módulo aislado y el subconjunto `roll` se ha integrado al ejecutor. Las pruebas H2 comprueban que una suspensión, cancelación o conflicto no consume el RNG confirmado.

## 11. Admisión y validación

Todo paquete debe entrar a través de la puerta de admisión, que aplica lectura JSON estricta, comprobación estructural y validación semántica. Los errores técnicos bloquean; las advertencias narrativas pueden describir riesgos sin rechazar obras legítimas. Las definiciones admitidas se conservan por copia independiente, con digest calculado. La ruta de acceso al paquete no afecta el hash.

Un guardado requiere comprobaciones adicionales de formato, origen, digest, identidades, historia, cursor e invariantes de mundo. La parte estática de estas comprobaciones ya existe, pero no reemplaza la restauración dinámica. La implementación de Ren'Py tampoco podrá modificar directamente las estructuras internas del motor para eludir esta admisión.

## 12. Frontera de implementación en la etapa H2 (registro histórico)

Están implementados la validación estática, los dos contratos deterministas y un ejecutor narrativo H2 reducido. Se restauran sesiones confirmadas y pendientes de descarte dentro de ese alcance. Ren'Py todavía no consume `Observe` y `Act`; su árbol es un anfitrión de preproducción. El código antiguo permanece aislado en `archive/`.

ADR-015 autoriza una vertical funcional de CLI con narración, diálogo, elección, condición, transferencia de objeto, hecho histórico y al menos una reacción causal. Se excluyen, en esta primera etapa, las habilidades avanzadas, los efectos temporales compuestos, S.O.F.I.A., los mecanismos de contrahechizos y las rutinas específicas del demo. El encargo de continuar con el MVP autorizó iniciar esta implementación limitada.

## 13. Puntos pendientes en la etapa H2 (registro histórico)

Se implementaron parcialmente el ejecutor, el cierre de turnos, el rollback ante conflictos y el replay de decisiones auxiliares de descarte. Siguen pendientes los orígenes asociados a operaciones aún no implementadas, como acciones de exploración y uso de habilidades, las conversiones de contenido del demo anterior, la integración con Ren'Py y la política de migración futura de sesiones. El ejecutor H2 aplica límites operativos de 32 rondas reactivas y 512 pasos automáticos; no son una decisión narrativa general. Estas tareas se deben resolver dentro de GISELA, no mediante otro motor.

Las decisiones de producción, derechos y publicación siguen separadas. La existencia de un ZIP integrado no equivale a una demo terminada ni a un acuerdo contractual con terceros.


## 14. Implementación verificada de la vertical CLI 0.1 (registro histórico)

El código nuevo se ubica en `gisela/engine/`, sin reutilizar el sistema histórico de acontecimientos. Se conserva la distinción arquitectónica entre GISELA como ejecutor y autoridad de transacciones, ALBERTO como gestor de operaciones sobre instancias y las capacidades opcionales de S.O.F.I.A. como datos y cálculos de H3.4b. El anfitrión de consola solo muestra proyecciones y remite acciones, utilizando la misma frontera Observe y Act prevista para Ren'Py.

El paquete `gisela/packages/mvp_casete.package.json` muestra narración, diálogo, elección, condición, transferencia de objeto, un hecho histórico y una reacción automática. El motor puede iniciar sesiones, recorrer ambos caminos, cerrar nodos, exportar snapshots completos del estado confirmado y restaurarlos al comprobar que corresponden al mismo paquete admitido. El historial mantiene una ejecución por turno y registra la procedencia de hechos y selecciones. Las respuestas de Act se comprueban contra la proyección vigente, por lo que una revisión antigua, una opción inhabilitada o una acción inventada no modifican el estado.

Las operaciones se aplican primero sobre una copia de sesión. Las reglas reactivas se seleccionan por rondas a partir del mismo estado base de cada ronda, sin prioridades implícitas. Si dos reglas escriben el mismo destino, o una cadena reactiva no converge dentro del presupuesto, el motor devuelve un error y conserva el estado confirmado. El primer perfil operativo utiliza un máximo de 32 rondas reactivas y 512 pasos automáticos por acción; estos límites son controles del ejecutor y no decisiones autorales narrativas.

Solo está implementado un subconjunto verificable de pasos, condiciones, operaciones y disparadores. El ejecutor rechaza los demás con un error de formato no soportado, aunque sean estructuralmente válidos bajo el schema general. Esta distinción es obligatoria: el validador estático comprueba definiciones generales y el control de capacidad del ejecutor verifica lo que efectivamente puede correr.

La exportación y restauración están comprobadas para sesiones confirmadas. H2 añade reconstrucción de intención y respuestas provisionales para el descarte provocado por `grant_skill`, incluso con dos solicitudes sucesivas, tanto en la apertura de sesión como en avances y elecciones. `roll` consume RNG en el borrador transaccional y las pruebas comprueban su rollback. Todavía no se han implementado el uso de habilidades, los efectos temporales ni las acciones de exploración. Ren'Py sigue sin comprobación con su SDK. Los límites efectivos se detallan en `gisela/engine/README.md` y `docs/validation/PLAN_DE_VERIFICACION.md`.

La referencia de [ALBERTO](ALBERTO.md) desarrolla las entidades e invariantes del mundo, y la de [S.O.F.I.A.](SOFIA.md) describe sus atributos opcionales, cálculos de atributos y efectos implementados.

## 14. Estado técnico actualizado en H3

La arquitectura de autoridad única sigue vigente. H3 no introduce una segunda sesión ni un nuevo formato de guardado. La primera etapa implementada amplía ALBERTO con movimiento de personajes, conocimiento, creencias, creación y retiro de entidades, habilidades de inventario y transferencia de objetos entre personas y lugares. El reloj ficticio puede avanzar mediante la operación explícita `advance_time`, coordinada por GISELA. Las condiciones `knows`, `believes` y `has_skill` se evalúan sin mutaciones.

Los módulos internos se han separado por responsabilidad, manteniendo la fachada pública `new_session`, `restore_session`, `observe`, `act` y `export`. La validación semántica conserva su interfaz, pero distribuye sus comprobaciones entre archivos especializados. Los 13 schemas JSON se han reformateado sin cambiar sus contratos ni la versión 1.2. La verificación de los límites de código y documentación forma parte del procedimiento general de pruebas.

Estas incorporaciones no completan todavía H3: políticas de uso y retorno de habilidades y las referencias contextuales siguen fuera del subconjunto dinámico. Las decisiones y comprobaciones se mantienen en `docs/operatives/H3_REVISION_PLAN_IMPLEMENTACION.md` y el estado real en `docs/operatives/ROADMAP.md`.

## Actualización de contratos de ejecución en H3.4a

H3.4a se incorporó al ejecutor sin alterar los schemas v1.2. GISELA pasa un índice de definiciones del paquete admitido a las condiciones, consecuencias y rondas reactivas. ALBERTO consulta propiedades de cartas y relaciones del manifiesto, materializando entradas solo al escribir. La atomicidad, restauración y digest del paquete conservan su autoridad original.

Las reglas activadas simultáneamente usan los mismos operandos de base. `add` compatibles se suman, `set` iguales se consolidan y las escrituras contradictorias revierten toda la operación. Los atributos S.O.F.I.A. están implementados en H3.4b; efectos dinámicos están implementados en H3.4c; las habilidades en ventanas de nodo están implementadas en H3.4d. Ver [registro H3.4a](../operatives/H3_4A_CIERRE.md).


## Actualización de ejecución. H3.4b

El ejecutor ahora resuelve los atributos opcionales de S.O.F.I.A., su valor actual y sus modificadores, sin duplicar el estado derivado. El método público `sesion.scoresheet(character)` consulta exclusivamente el mundo confirmado y no modifica turnos ni revisiones. Los destinos de escritura siguen restringidos al componente `current`, y los modificadores de efectos inicialmente presentes se calculan sin ejecutar todavía un ciclo automático de aplicación y expiración. Consulte [la guía de atributos](SOFIA.md) y el [cierre del hito](../operatives/H3_4B_CIERRE.md).

El código mantenido debe respetar tres límites automáticos: 700 líneas por archivo, 64 líneas por función excluyendo el docstring y tres parámetros explícitos por función. La firma de un método puede incluir `self` o `cls` como receptor implícito. Estos límites no justifican crear sistemas adicionales; se prefieren módulos pequeños, funciones claras y contextos que agrupen datos realmente relacionados.

## Registro de implementación H4. 30 de octubre de 2026

El ejecutor admite entrada directa a escenas, acciones declarativas de escenas y elementos, transiciones a nodos y estado `exploring` con actores y elementos visibles. La procedencia se conserva en la intención y en la traza confirmada. `Observe` se construye solo desde estado confirmado y `Act` revalida cada acción antes de ejecutar consecuencias.

La CLI permite navegación, guardado, restauración y diagnóstico de datos de ALBERTO y S.O.F.I.A. El método `debug_query` es exclusivo de desarrollo y no constituye una autorización para mostrar información privada de personajes. Las consultas autorizadas para jugadores siguen siendo parte del contenido y de las acciones declaradas.

Los contratos JSON v1.2 no requirieron cambios. Persisten restricciones de soporte para referencias contextuales no vinculadas, juego de habilidades fuera de ventanas de nodo y preparación de mano en escenas. El detalle verificable está en [H4_REVISION_Y_CIERRE.md](../operatives/H4_REVISION_Y_CIERRE.md).

## Evolución posterior: TRAITS y DICE (formato v1.3)

Se añade una familia **separada y optativa** de esquemas v1.3 para rasgos persistentes y operaciones transaccionales de ALBERTO. Se mantienen los contratos v1.2 para compatibilidad; no hay migración implícita. El núcleo TRAITS independiente y el núcleo DICE independiente se integran mediante un adaptador de GISELA que no confirma estado ni publica dados. El protocolo de tiradas visibles de ADR-019 permanece pendiente. Esta sección complementa el registro histórico de v1.5, sin reinterpretar sus afirmaciones de cierre. Véase [estado y límites](TRAITS_DICE_INTEGRACION_FASE_1.md).
