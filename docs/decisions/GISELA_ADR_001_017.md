# Registro de decisiones arquitectónicas de GISELA

Versión consolidada de 29 de octubre de 2026. ADR-015 quedó autorizada para iniciar una vertical mínima en CLI mediante el encargo posterior de continuar con el MVP; la implementación parcial se documenta en la arquitectura v1.5. Las precisiones deterministas de ADR-016 y ADR-017 se han implementado como contratos técnicos, no como nuevas reglas narrativas.

# GISELA  -  Registro de decisiones y auditoría de arquitectura

**Fecha:** 29 de octubre de 2026  
**Base:** `GISELA_ALBERTO_SOFIA_Arquitectura_y_Schemas_v1(1).md`; `GISELA_Schemas_v1(1).zip`; `Central_Clasificadora_Demo_RenPy_instrucciones.txt`; `lptn.zip`.  
**Estado:** selección arquitectónica delegada por el autor. **No se han modificado los 13 JSON Schemas ni se ha comenzado a implementar el motor.** Los contratos candidatos de v1 requieren adecuación al registro.  
**Precedencia:** este diseño reemplaza la arquitectura y el código anteriores basados en barajas de acontecimientos, Croupier, Scheduler y rangos Gold/Silver/Bronze como núcleo. Los contenidos narrativos y requisitos de experiencia del demo siguen siendo referencias, pero no condicionan el núcleo general.

## Criterios aplicados

1. **Responsabilidad única:** GISELA controla sesión, ejecución, atomicidad, reglas y exportación; ALBERTO es su modelo de mundo; S.O.F.I.A. es opcional; Ren'Py/CLI son adaptadores, no motores paralelos.
2. **Apertura:** nuevas historias incorporan definiciones y reglas, no código específico; cambios del lenguaje declarativo son explícitos, tipados y versionados.
3. **Mantenibilidad:** una fuente de verdad por dato; diagnósticos precisos; semántica sin precedencias accidentales.
4. **Evolución:** separar contratos conceptuales del alcance implementado; no fijar plataformas ni sistemas de visualización en el modelo autoral.
5. **Eficiencia:** primero corrección con datos en memoria y transacciones aisladas; optimizar según pruebas; evitar planificación global y sondeos permanentes.
6. **Simplicidad:** no sumar coordinadores, Croupier, Scheduler, DSL arbitrarios ni jerarquías de plugins para casos no demostrados.

## Decisiones previamente aprobadas (ADR-001-005)

- **ADR-001 DECIDIDO:** decisiones auxiliares se solicitan antes de confirmar una transacción; no hay estados del mundo parcialmente confirmados.
- **ADR-002 DECIDIDO:** una operación voluntaria puede cancelarse íntegramente; una operación obligatoria no puede eludirse mediante cancelación. Guardar y salir sigue permitido.
- **ADR-003 DECIDIDO:** persistir el estado confirmado, la intención, su contexto, respuestas provisionales y solicitud pendiente; reconstruir determinísticamente, no serializar el borrador del ejecutor.
- **ADR-004 DECIDIDO:** como máximo una transacción pendiente por sesión; mientras dure se bloquean otras mutaciones/acciones narrativas, no las consultas de solo lectura.
- **ADR-005 DECIDIDO:** Observe y Scoresheet muestran solo el mundo confirmado; la solicitud pendiente es una proyección separada y autorizada.

## Resoluciones elegidas en la revisión integral (ADR-006-015)

### ADR-006  -  Estados de ejecución y espera  -  SELECCIONADO

Conservar únicamente `preparing`, `node`, `exploring`, `ended` como estados principales. La espera de confirmación de texto, una elección, preparación, ventana de habilidad o una transacción pendiente es información específica del cursor/solicitud, no un quinto motor de estados. `node` exige cursor válido; `exploring` exige una escena válida; `ended` exige desenlace. Los estados que no usan cursor ni desenlace no deben arrastrar datos contradictorios. Puntos de espera son estables cuando no existe ejecución parcial publicada; una transacción pendiente mantiene el estado confirmado aparte.

**Coste/condición:** escribir invariantes de transición y esquemas condicionales, no solo un enum de `status`.

### ADR-007  -  Turnos y cierre causal  -  SELECCIONADO

Un turno corresponde a una ejecución efectiva de nodo; los pasos internos y acciones de escena no crean turnos por sí solos. La preparación anterior al nodo no lo inicia. Inicio de turno y su reacción son atómicos. Al terminar, `node_completed` y `turn_ended` son sucesos del mismo cierre causal: las reglas activadas por ambos se evalúan desde el mismo estado base y sin prioridad entre ellas. Solo después de resolver y estabilizar el cierre causal se inicia el nodo siguiente o se pasa a `exploring`; el cierre de A y la entrada a B pueden confirmarse en una **única transacción atómica**, sin publicar un estado intermedio. Un final explícito conduce a `ended`. Si no hay escena y el nodo se agota sin transición ni final, hay error técnico identificable. Un error tardío no revierte las transacciones anteriores ya confirmadas del mismo nodo.

**Coste/condición:** pruebas de reentrada en nodo, saltos, intentos fallidos y reacciones al cierre.

**Precisiones aprobadas, 30-10-2026:**

- Distinguir **turno** (ejecución de nodo), **transacción causal** (unidad de confirmación), **ronda reactiva** (iteración interna) y **punto de estabilidad** (estado confirmado publicable).
- Las fases preparación, inicio, desarrollo, resolución y cierre son conceptuales; no introducen un quinto estado público. El contador `turn` aumenta una sola vez al ingresar efectivamente a un nodo; no aumenta por pasos, consultas ni rondas.
- En una transición de A a B, estabilizar `node_completed` y `turn_ended` de A antes de emitir `turn_started` de B, dentro del mismo borrador causal. Si falla la entrada de B o una reacción de su inicio, se revierte **toda la transacción del salto**, incluido el cierre provisional de A, sin revertir transacciones previas ya confirmadas durante A.
- La frontera del salto es un solo commit: no existe un estado observable ni un guardado intermedio entre cerrar A e iniciar B.
- Durante una transacción suspendida por una decisión auxiliar, el turno y el mundo confirmados no cambian; las solicitudes no publican el borrador.


### ADR-008  -  Rondas reactivas, conflictos y límites  -  SELECCIONADO

Una sola autoridad aplica las operaciones ordenadas de la acción originaria y luego resuelve, por rondas, los eventos y reglas que genera. Todas las reglas de una ronda ven el mismo estado base; escrituras iguales/idempotentes son compatibles, `add` numéricos compatibles se combinan, escrituras contradictorias fallan; ninguna prioridad oculta derivada del orden de archivo. `state_changed` requiere cambio efectivo de valor en el límite causal, no solo un `set` repetido. Las ocurrencias de hecho y señales explícitas conservan su identidad de suceso. Se detectan ciclos y se aplica un presupuesto interno finito; el exceso falla y revierte la unidad causal. Los ciclos narrativos que incluyen interacción del jugador no se bloquean por parecer repetitivos.

**Coste/condición:** fijar con pruebas el algoritmo de detección y el límite operativo, sin exponerlo como mecánica autoral.

**Precisiones aprobadas, 30-10-2026:**

- Un punto de estabilidad es una frontera de estado **confirmado** tras terminar toda la transacción causal, incluidas sus rondas reactivas. No se permite observar ni guardar borradores intermedios.
- Las reglas de una misma ronda se seleccionan y sus escrituras se planifican sobre un estado base compartido; las operaciones originarias conservan su orden declarado. El estado compartido de una ronda no se extiende automáticamente a todas las operaciones de la transacción.
- El contador `turn` y la revisión de sesión no aumentan por cada ronda. MARY puede entregar yields durante las rondas, pero la autoridad transaccional permanece en GISELA.

**Condiciones de implementación y ampliaciones pendientes:**

- Los límites actuales del código son `MAX_ROUNDS = 32` y `MAX_AUTOMATIC_STEPS = 512`; son presupuestos de implementación, no reglas narrativas universales.
- Una evaluación visible de DICE antes de sus efectos **no** equivale a publicar el borrador de una `pending_transaction` actual. El mecanismo para fijar resultado, RNG y consecuencias pendientes requiere contrato/versionado propio (véase ADR-019, en propuesta), sin romper ADR-001-005 ni ADR-012.


### ADR-009  -  Instancias y referencias  -  SELECCIONADO

IDs de definiciones únicos dentro de su categoría; IDs de instancia únicos globalmente en cada sesión. Persistir identificadores ya utilizados (incluidos retirados) y el siguiente contador de asignación, evitando reutilizaciones después de restaurar. La generación es determinista y transaccional: una operación cancelada no consume IDs. Las referencias tienen tipo esperado y contexto explícito; un referente contextual no ligado es error; una consulta singular con varios candidatos es ambigua y falla por defecto. No implementar `first_by_id` como desempate automático en v1.

**Coste/condición:** validador semántico y pruebas de creación, retirada, restauración y consultas plurales.

### ADR-010  -  Habilidades  -  SELECCIONADO (CONTRATO, NO MVP)

La carta `skill` describe requisitos y consecuencias; usarla es una acción que invoca el **mismo ejecutor de GISELA**. Una habilidad solo se juega desde mano; mano N y reserva M se administran en ALBERTO. El intento jugable confirmado consume por defecto, incluido el fracaso narrativo; un error técnico o cancelación de transacción no consume. Los posibles resultados y retornos se describen declarativamente con condiciones sin prioridades implícitas; si dos políticas de retorno incompatibles coinciden, debe rechazarse la ambigüedad o exigirse una especificación autoral inequívoca. Las decisiones de descarte usan ADR-001-005. No construir ahora un mecanismo universal de contrahechizos ni una máquina independiente para habilidades.

**Aún fuera de MVP:** codificación final del orden y estado de evaluación de resultados condicionales; pruebas de capacidades, retornos y efectos derivados. No afirmar que el schema candidato ya expresa por completo esos casos.

### ADR-011  -  Efectos y tiempo  -  SELECCIONADO (CONTRATO, NO MVP)

Un solo reloj ficticio que avanza únicamente por operaciones declarativas de GISELA. Un efecto sin vencimiento persiste; los vencimientos por tiempo, cierre de turno, nuevo hecho o condición se resuelven en la misma cadena causal que detecta el suceso, sin Scheduler autónomo. Cada suceso de expiración tiene identidad y se procesa como máximo una vez para la instancia afectada. `after_turns: 1` significa el primer cierre de un **turno posterior al turno de aplicación**; si se activa fuera de nodo, el siguiente cierre elegible. `after_minutes` compara instantes del reloj ficticio, incluidos saltos sobre umbrales. Como composición mínima, mantener vencimiento por **cualquiera** (`any`); diferir `all`, que exige persistir cuáles desencadenantes ya ocurrieron. `on_fact` observa una ocurrencia nueva desde la aplicación, no reinterpreta automáticamente hechos antiguos.

**Coste/condición:** estas precisiones son nuevas normalizaciones técnicas. Deben comprobarse cuando se implemente el sistema de efectos.

### ADR-012  -  RNG reproducible  -  SELECCIONADO (CONTRATO, NO MVP)

Fijar un RNG de contador y SHA-256 con representación byte a byte versionada para semilla/contador y muestreo uniforme sin sesgo mediante rechazo. Persistir el contador/estado junto al snapshot confirmado; los sorteos de un borrador se descartan ante fallo o cancelación. El orden de consumo se determina por la ejecución semántica del motor, no por el orden de diccionarios/archivos. No depender de las versiones de `random` de Python ni del host. Los detalles precisos de codificación se publicarán al preparar pruebas vectoriales, antes de implementar `roll`.

**Coste/condición:** hashing por extracción, irrelevante para la frecuencia típica de sorteos narrativos; se requieren vectores de compatibilidad entre plataformas.

### ADR-013  -  Sesión, historial y versionado  -  SELECCIONADO

Snapshot completo del estado **confirmado** más, opcionalmente, una sola `pending_transaction` (intención, origen voluntario/obligatorio, contexto vinculado, respuestas aceptadas, solicitud actual). El borrador reactivo no se guarda. Mantener historial autoritativo de ocurrencias y ejecuciones; índices `has_fact`, últimas ubicaciones, etc., se derivan en memoria y no se serializan como segundas fuentes de verdad. Las proyecciones tampoco se guardan como estado autoritativo. Un digest del paquete completo normalizado (catálogos no ordenados ordenados por ID; listas semánticamente secuenciales conservadas) impide restaurar contra definiciones distintas. El formato de sesión se versiona separadamente; sin migraciones silenciosas en v1.

**Coste/condición:** se pierden restauraciones entre contenidos editados hasta que haya migraciones explícitas; se gana integridad y simplicidad.

### ADR-014  -  Contrato de interfaces y validación  -  SELECCIONADO

`Observe` publica proyección autorizada y acciones con `action_id` ligado a `revision`. `Act` revalida revisión, permisos y condiciones; no acepta operaciones arbitrarias del frontend. Scoresheet es lectura pura; `world_snapshot` es interno/privilegiado. Errores técnicos tipados sin commit, advertencias narrativas no bloqueantes. Validar (1) forma con JSON Schema, (2) referencias y tipos cruzados con validador semántico, (3) invariantes y causalidad durante ejecución. Las pistas `presentation` son datos opacos: GISELA no renderiza. Las ampliaciones de operadores requieren cambio explícito de contrato/versión, no ejecución de Python autoral ni plugins sin necesidad comprobada.

**Coste/condición:** mantener fixtures positivos/negativos y pruebas que ejerciten sesiones restaurables, no solo un paquete de ejemplo.

### ADR-015  -  Frontera del primer MVP  -  APROBADO PARA LA VERTICAL CLI

CLI primero, usando el mismo contrato Observe/Act previsto para Ren'Py. Un paquete de prueba no canónico con uno o dos nodos, narración, diálogo, decisión visible/bloqueada, condición, consecuencia de ALBERTO (propiedad de casete), registro de hecho, una regla reactiva simple que produzca un cambio verificable, salida de escena o final, exportación/restauración y reproducción determinista. Pruebas de rollback ante conflicto, repetición de nodo y opción inhabilitada. Ren'Py se conecta después, sin lógica narrativa propia. Fuera de esta vertical: mano/reserva, efectos temporales, Scoresheet de S.O.F.I.A., calendario recurrente, contrarreacciones, aleatoriedad si no es imprescindible y desplazamiento especializado del demo.

**Estado de ejecución:** primera vertical de CLI implementada y probada. Todavía no verifica ADR-001 a ADR-005 en sus decisiones auxiliares, ni la integración con Ren'Py. Las demás capacidades permanecen como contratos del diseño y no se declaran terminadas.

## Problemas concretos constatados en los schemas candidatos

Ejecutado: `python schemas/verify_contracts.py` entonces `PASS: 13 schema definitions; package + API contracts; unknown operation rejected.` Esta verificación no ejercita `session.schema.json` en sus invariantes entre estados.

Pruebas adicionales sobre `session.schema.json`:

- Una sesión `exploring` sin `pending_choice` es **rechazada**, aunque puede ser válida conceptualmente, porque `narrative.pending_choice` es obligatorio.
- Una sesión `exploring` con `pending_choice.kind: overflow`, un paso arbitrario y candidatos vacíos es **aceptada** estructuralmente.
- Una sesión `node` sin `cursor` es **aceptada**.
- Una sesión `ended` sin `ending` es **aceptada**.

La `pending_choice` candidata guarda `kind/step/candidates`; no representa ADR-001-005. Falta una `pending_transaction` opcional y tipada, separada de una elección narrativa normal. También falta persistencia del registro de IDs usados/contador, y es confusa la duplicación `narrative.facts` frente a `history.facts` y `narrative.executions` frente a `history.trace`.

## Próxima secuencia documental  -  SIN CÓDIGO DE MOTOR

1. Ajustar el documento consolidado con estas ADR, sin atribuir a decisiones antiguas las normalizaciones nuevas.
2. Revisar primero `session`, `observe`, `result`, `act`, `node` y `common`; luego `initial_state`, `package` y los contratos de ALBERTO.
3. Construir fixtures positivos y negativos por estado y por transacción; verificar con JSON Schema y con una matriz de validaciones semánticas pendientes.
4. Ejecutar la vertical aprobada, mantener pruebas de regresión y exigir nuevas verificaciones antes de ampliar funcionalidades.

## Temas pospuestos, no contradicciones sin resolver del núcleo

Contratos detallados de `outcomes` y `return_policy` de habilidades; composición `all` de expiraciones; mecanismos de respuesta/contrahechizos; migraciones entre paquetes; zonas horarias históricas especializadas; límite cuantitativo de rondas; assets y empaquetado; decisiones audiovisuales y guion canónico del demo. Se documentarán cuando tengan un caso de uso y pruebas concretas.


# Normalizaciones técnicas para el determinismo

**ADR-016. Digest canónico. Estado: DECIDIDO por ejecución de la sugerencia solicitada.** Se establece el perfil `GISELA-CJSON-1`, con objetos ordenados por clave Unicode, listas en su orden original, decimales normalizados y SHA-256 con prefijo de separación de dominio. El resultado se guarda como 64 caracteres hexadecimales. La documentación normativa está en `docs/determinism/DIGEST_CANONICO.md`.

**Motivo:** los guardados deben detectar cambios en las definiciones sin depender del orden de claves, espacios o saltos de línea. Se evita la complejidad de decidir qué colecciones del paquete podrían reordenarse, por lo que todas las listas conservan su orden. Los recursos externos al JSON quedan fuera del hash y esa limitación se declara expresamente.

**ADR-017. RNG de contador. Estado: DECIDIDO por ejecución de la sugerencia solicitada.** Se fija `sha256_counter_v1` con semilla de 32 bytes, contador serializable, bloques SHA-256, codificación big endian y extracción uniforme por rechazo. La documentación normativa se encuentra en `docs/determinism/RNG_SHA256_CONTADOR.md`.

**Motivo:** la reproducción no debe depender de `random` de Python ni del anfitrión. El módulo independiente entrega nuevo estado sin mutar el anterior, lo que facilita su integración posterior en la semántica transaccional. La prueba de rollback real sigue pendiente porque no existe el ejecutor.

Ambas ADR precisan campos que ya existían en los schemas 1.2; no cambian las enumeraciones ni la forma estructural. Por esa razón no se publica un schema 1.3 artificial. La versión normativa de la arquitectura pasa a 1.4, y los tests añaden vectores para comprobar que el perfil documentado y su implementación coinciden.
