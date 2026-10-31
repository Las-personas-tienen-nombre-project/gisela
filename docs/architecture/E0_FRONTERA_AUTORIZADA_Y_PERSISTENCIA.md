# GISELA E0: Frontera de ejecución y recuperación

**Estado:** implementado en la base Python; `evaluate`/ADR-019 continúa pendiente. Esta etapa **no** agrega `evaluate`, `pending_evaluation`, red ni un protocolo entre instancias. Las cartas y los snapshots 1.2/1.3 conservan sus esquemas y sus turnos. Se corrige aditivamente el catálogo de códigos de error devueltos en `result.schema.json`.

## Actores y autoridades

1. **Solicitante externo (`Principal`)**: identidad autenticada por el *anfitrión*, que concede capacidades. No se infiere de un personaje ni de `request['principal']`. Un cliente puede ser GLAUQUIR, Ren'Py, un servicio, una persona o **otra GISELA**.
2. **Sesión destinataria**: una instancia de `GiselaSession` con su propio estado, revisión y RNG. La sesión es la única autoridad transaccional para su mundo.
3. **Actor narrativo**: personaje, objeto o lugar ALBERTO declarado por el juego. Nunca se deriva automáticamente del identificador del solicitante.
4. **Fuente causal**: nodo, opción, acción de escena o regla declarativa. La autoriza la oferta de `Observe` vigente y las condiciones del ejecutor.

Un mensaje desde otra instancia GISELA no entra directamente en ALBERTO, TRAITS, DICE ni en un borrador. Su adaptador remoto deberá autenticarlo y pasar un comando por esta misma puerta. **No existen commits distribuidos ni transporte entre procesos en E0.**

## API del anfitrión autorizado

`gisela.engine.authorized_gateway.ExecutionGateway(session, principals, store=None)` encapsula la sesión y expone `bind(principal_id)` **solo al anfitrión que ya autenticó al llamante**. `Principal(identifier, frozenset(capabilities))` pertenece a la configuración confiable del anfitrión, no a un documento del cliente. Ni el constructor, ni `bind`, ni los objetos Python internos constituyen un mecanismo de autenticación para código Python arbitrario ejecutándose en el mismo proceso.

Capacidades E0:

| Capacidad | Alcance |
|---|---|
| `act` | Ejecutar una oferta validada con `command_id` independiente del `action_id`. |
| `observe_player` | Obtener la proyección **del jugador declarado**. No implica acceso a datos privados. |
| `export_private` | Acceso privilegiado a snapshot completo, RNG incluido. Nunca conceder automáticamente a un cliente externo. |
| `debug_private` | Consultas diagnósticas privilegiadas; no se usan como proyección. |

Un escritor sin `observe_player` recibe de `act` solo estado/revisión y código seguro, **no** el campo `view`. Los mensajes internos detallados de error se sustituyen por texto genérico en la frontera del gateway. Las autorizaciones se verifican de nuevo en cada solicitud y también al devolver un recibo anterior; cambiar o revocar capacidades invalida las fachadas antiguas. El anfitrión debe impedir que un cliente remoto invoque directamente `session.act`, `session.export` o la fachada de configuración. Al enlazar un gateway, `session.act` local queda deshabilitado; los lectores locales restantes son responsabilidad del código confiable del anfitrión.

La política de audiencia E0 **solo** implementa `observe_player`. Otras audiencias (un NPC, varios jugadores, clientes automatizados con vistas parciales) requieren contratos explícitos, **no** un permiso implícito por ser un software. El acceso a acciones ofertadas continúa sujeto a revisión y sesión; conocer un `action_id` no equivale a una autorización.

## Garantía transaccional local

Toda ejecución `session.act` se serializa mediante `RLock` por sesión; también se protege `observe`, exportación y consultas públicas del ejecutor. No hay bloqueo global de todas las partidas. El gateway ejecuta un `Act` a la vez por sesión; la revisión impide aplicar dos comandos diferentes construidos sobre una misma proyección. La protección es **local al proceso**.

En `_commit`, `_publish_pending`, `_cancel` y el arranque: primero se construye y valida la proyección del candidato **contra su versión 1.2/1.3**; después se sustituye el puntero al estado confirmado. Una proyección ausente, mal formada o que falle durante su construcción produce rechazo/aborto sin medio commit. `Observe` por sí solo sigue siendo una lectura sin efectos.

## Identidad, idempotencia y guardado

- `action_id` identifica una oferta narrativa para la revisión actual; `command_id` identifica un **intento lógico de un solicitante**. No confundir con el futuro `evaluation_id`.
- La identidad del recibo es `(principal_id, command_id)`, ligada al hash canónico del JSON de `Act`. Reintentar el mismo par recupera su respuesta sin ejecutar la operación. Reutilizar el mismo ID con otra petición es error.
- El recibo se conserva en memoria. Con `JsonCheckpointStore(path)` se escribe un único documento que contiene **snapshot y recibos**, en un reemplazo atómico del archivo (archivo temporal + `fsync` + `os.replace` + `fsync` de directorio). Un bloqueo POSIX exclusivo mantenido hasta `close()` evita dos propietarios sobre el mismo archivo local.
- Si falla la escritura **antes** del reemplazo, el gateway revierte el estado en memoria y no registra el recibo; si el reemplazo pudo ocurrir y falla después, entra en estado **incierto y bloqueado** hasta que el anfitrión reabra y concilie el checkpoint. Nunca confirma otro comando ciegamente.
- Al restaurar se comprueban digest y sesión, validez estructural del recibo y `restore_session`, incluido el replay determinista de pendientes. Un recibo reconocido puede devolver la misma respuesta incluso si la revisión actual es posterior; una nueva orden con ID distinto debe superar la revisión actual.
- El máximo E0 es **10 000 recibos por sesión** y el archivo no excederá **64 MiB**. El motor no los elimina automáticamente: se requiere política de cierre/archivo externo si se alcanza el límite. La reescritura íntegra del checkpoint tiene coste creciente; reemplazarla por almacenamiento transaccional indexado es una mejora futura.

**Alcance exacto:** con el archivo y su bloqueo en un mismo anfitrión Linux/POSIX, la combinación de estado y comprobante puede recuperarse tras reinicio. Sin `store`, la idempotencia es únicamente de la vida del gateway actual. La resistencia a modificación hostil del checkpoint, el cifrado en reposo, la replicación entre anfitriones, recuperación frente a fallo de disco y la entrega exactamente una vez de efectos externos **no están prometidos**. El directorio de almacenamiento debe ser confiable, protegido con permisos y respaldado por el anfitrión. No aceptar snapshots o archivos de recibos de orígenes no confiables.

## DICE y adaptadores

El contrato matemático DICE mantiene `dice.profile.v1`. `bands[].min` está ordenado y es único, al igual que `bands[].id`. El **primer resultado actúa como reserva inferior**: ningún total entero válido queda sin categoría, incluso si es menor a `bands[0].min`. `evaluate()` valida también un perfil enviado directamente, antes de llamar al RNG inyectado. La fuente aleatoria y su commit siguen siendo de GISELA; DICE no importa a los demás subsistemas.

`traits_dice_bridge.resolve()` actualmente acepta una **especificación interna**, no el JSON autoral de `evaluate`: `participants`, `tags`, `base`, `difficulty`, `stat` opcional y `profile` materializado. Retorna `{dice, traits, rng_after}` sin mutar el estado. La conversión entre el contrato autoral propuesto y esa forma interna se especifica en `DICE_EVALUACION_DECLARATIVA_PROPUESTA.md`; implementarla pertenece a **E1/v1.4**, no a E0.

## Límites y riesgos residuales

- La sesión local sigue siendo una API Python **confiable**; el gateway impone permisos solo si el anfitrión no entrega objetos internos a código adversario ejecutándose en el mismo intérprete.
- `observe_player` todavía presupone un protagonista: no habilitar acceso a terceros sin ese permiso explícito.
- La identidad de un par GISELA remoto debe validarse en su protocolo de transporte futuro; no existe deduplicación ni orden de mensajes entre procesos remotos aquí.
- La persistencia es de archivo local y su integridad no está autenticada criptográficamente; archivos alterados por el propio anfitrión fuera de GISELA pueden reintroducir estados antiguos.
- Los eventos universales `trait_assigned` y `trait_removed`, y las tiradas visibles `pending_evaluation`, continúan sin implementación.
- El contrato público v1.4 queda reservado a `evaluate`; no se han introducido campos nuevos en sesiones 1.2/1.3.

Ver [ADR-020](../decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md), [matriz de invariantes](../operatives/E0_INVARIANTES_TRAZABILIDAD.json) y [plan de pruebas](../operatives/E0_CIERRE_Y_RIESGOS.md).
