# GISELA, ALBERTO y S.O.F.I.A. Arquitectura consolidada, versión 1.5

**Fecha:** 29 de octubre de 2026. **Estado:** descripción arquitectónica; prevalecen los contratos versionados y el código. **Primer caso de uso:** "Las personas tienen nombre", dentro del proyecto Central Clasificadora. El motor es general y no puede incorporar como obligaciones universales las mecánicas específicas de este demo. Para la interfaz y los campos de presentación actuales, consulte la [API de clientes](API_CLIENTES.md) y la [guía de GLAUQUIR](../guides/GLAUQUIR.md).

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

Las reglas reactivas se ejecutan por rondas. Todas las reglas activadas en una ronda observan el mismo estado base. Los cambios compatibles se combinan, mientras que las escrituras contradictorias provocan un fallo tipado y revierten la transacción causal completa. Un cambio sin diferencia efectiva no debe provocar por sí solo nuevos `state_changed`. El ejecutor aplica límites de rondas reactivas para impedir ciclos infinitos; el contrato y las pruebas del ejecutor determinan el límite efectivo.

El RNG y el asignador de IDs son parte de la misma transacción que las modificaciones del mundo y del historial. Una operación fallida no consume aleatoriedad ni identidades y no publica consecuencias parciales.

## 8. Transacciones pendientes, ADR-001 a ADR-005

Una acción originaria y la cadena causal de reacciones se confirman de manera atómica. Cuando una consecuencia requiere una decisión adicional del jugador, GISELA conserva la intención original, su contexto, las respuestas provisionales y la solicitud pendiente, mientras que el mundo confirmado permanece sin cambios. El borrador no se entrega al frontend ni se guarda como un segundo mundo.

Solo puede existir una transacción pendiente por sesión. Mientras está pendiente, no se ejecutan otras acciones narrativas ni mutaciones del mundo. Se permiten consultas autorizadas y guardar la sesión. Una transacción voluntaria puede cancelarse por completo; una operación automática obligatoria no puede cancelarse para eludir sus consecuencias. En ambos casos se mantiene la semántica de errores técnicos y de retorno al último estado confirmado.

La restauración debe reconstruir la transacción desde la intención y las respuestas provisionales, compararla con las definiciones y el estado confirmado y continuar solo si la reconstrucción es válida. La cobertura de replay depende del origen y de la versión del contrato; los casos de evaluaciones v1.4/v1.5 se documentan en E2/E3. Los schemas y el validador estático no sustituyen el replay dinámico.

## 9. Interfaces y consulta

`Observe` produce una vista coherente y autorizada, con revisión de presentación, escena, contenido activo y acciones posibles. No contiene el `world_snapshot` interno completo porque podría revelar datos ocultos. `Act` recibe identificadores opacos que estaban disponibles para la revisión correspondiente, sin aceptar operaciones arbitrarias suministradas por el frontend. Se rechazan acciones vencidas, invisibles, bloqueadas o no ofrecidas.

`GetScoresheet` es una lectura de solo consulta, cuando los personajes y permisos pertinentes existen. No cambia escena, turno, tiempo, RNG, revisiones ni historia. El frontend decide cómo dibujarla. Una vista privada del mundo de ALBERTO sigue separada de la proyección pública.

## 10. Persistencia

GISELA exporta y restaura una representación completa del estado confirmado de sesión en JSON. La escritura y lectura de archivos corresponde al anfitrión. El estado incluye cursor, turnos, reloj ficticio, instancias, ubicaciones, propiedades, hechos, ejecuciones, relaciones, conocimientos, habilidades, efectos, RNG, identidades utilizadas, revisiones y, cuando corresponda, la transacción pendiente.

Los guardados almacenan `package_digest`, un SHA-256 de 64 caracteres hexadecimales calculado sobre `GISELA-CJSON-1` con separación de dominio. El algoritmo exacto, los límites numéricos y los vectores están especificados en `docs/determinism/DIGEST_CANONICO.md`. Un cambio en las definiciones cambia el digest y la restauración contra ese paquete debe rechazarse. Las migraciones automáticas entre versiones no están permitidas.

El estado RNG usa `sha256_counter_v1`, con semilla hexadecimal de 32 bytes y contador entero. Los bloques se derivan de SHA-256 sobre semilla y contador; el muestreo por rechazo evita sesgo de módulo y la función devuelve un estado nuevo sin modificar el anterior. El contrato se detalla en `docs/determinism/RNG_SHA256_CONTADOR.md`. El ejecutor utiliza este RNG en operaciones transaccionales, incluidas evaluaciones declarativas. Las pruebas de suspensión, cancelación y conflicto protegen el RNG confirmado.

## 11. Admisión y validación

Todo paquete debe entrar a través de la puerta de admisión, que aplica lectura JSON estricta, comprobación estructural y validación semántica. Los errores técnicos bloquean; las advertencias narrativas pueden describir riesgos sin rechazar obras legítimas. Las definiciones admitidas se conservan por copia independiente, con digest calculado. La ruta de acceso al paquete no afecta el hash.

Un guardado requiere comprobaciones adicionales de formato, origen, digest, identidades, historia, cursor e invariantes de mundo. La parte estática de estas comprobaciones ya existe, pero no reemplaza la restauración dinámica. La implementación de Ren'Py tampoco podrá modificar directamente las estructuras internas del motor para eludir esta admisión.

## 12. Implementación y evolución

Este documento explica las fronteras arquitectónicas, no registra el estado de cada
hito. El comportamiento de las versiones de contrato se comprueba en
[`gisela/contracts/`](../../gisela/contracts/README.md) y en el
[ejecutor](../../gisela/engine/README.md). Los detalles de evaluaciones ocultas
v1.4 y visibles v1.5 están en [E2](E2_EVALUACIONES_OCULTAS.md) y
[E3](E3_EVALUACIONES_VISIBLES.md), respectivamente. Para rasgos persistentes
y el adaptador de DICE consulte [TRAITS](../../traits/README.md) y
[DICE](../../dice/README.md).

La secuencia H2-H5, los incrementos H3/H4 y los registros TRAITS-DICE de la
primera integración pertenecen al [changelog](../../CHANGELOG.md) y al
[historial Git](../../README.md); no deben interpretarse como limitaciones
vigentes. Para las funcionalidades pendientes, consulte el
[roadmap](../operatives/ROADMAP.md).
