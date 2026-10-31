# ALBERTO. Modelo de mundo y operaciones del motor GISELA

**Estado del documento:** registro de la etapa H3; consulte el [roadmap vigente](../operatives/ROADMAP.md) para el estado actual.

**Público:** autores de paquetes, responsables de integración y desarrolladores del motor. La especificación de datos está en `gisela/contracts/` y el seguimiento se encuentra en `docs/operatives/ROADMAP.md`.

Para comenzar a utilizar estas capacidades, consulte la presente arquitectura de ALBERTO y el [inicio rápido](../guides/QUICK_START.md). Explican por qué las operaciones de mundo siempre se confirman mediante GISELA.

## 1. Responsabilidad y frontera con GISELA

ALBERTO significa "Autonomous Layer for Beings, Environments, Relationships, Traits, and Objects". Representa instancias de personajes, lugares, objetos, habilidades, efectos, relaciones y conocimiento individual. Su responsabilidad es comprobar invariantes de mundo y aplicar operaciones a un estado de trabajo.

GISELA conserva la única autoridad de sesión. Abre una transacción, crea un borrador, ejecuta consecuencias y reacciones, y confirma o descarta ese borrador íntegramente. ALBERTO no mantiene otro historial autoritativo, no confirma cambios, no decide opciones del jugador y no serializa una segunda sesión. El RNG, el historial de hechos, los turnos y el reloj ficticio pertenecen a la autoridad transaccional de GISELA, aunque las condiciones de ALBERTO puedan consultarlos.

La frontera de operaciones es `gisela/engine/world.py`; los módulos `world_base.py`, `world_entities.py`, `world_skills.py` y `world_lifecycle.py` son detalles internos separados para disminuir el acoplamiento. No forman un servicio autónomo ni requieren otra interfaz pública.

## 2. Entidades y sus invariantes

| Entidad | Representación | Invariante principal |
| --- | --- | --- |
| Personaje | ID, carta, lugar, conocimiento y creencias | El lugar debe existir. El conocimiento no implica que el hecho se haya registrado históricamente. |
| Lugar | ID y carta | Es destino de ubicaciones, pero no equivalente a una escena visual. |
| Objeto | ID, carta, propietario o ubicación | Exactamente una forma de tenencia: personaje o lugar. |
| Habilidad | ID, carta, personaje y zona | La zona es `hand` o `reserve` y respeta capacidades. |
| Efecto | ID, carta, objetivo y datos de inicio | La estructura está admitida, pero su ejecución sigue pendiente. |
| Relación | Origen, destino, clave y valor | Relaciones dirigidas y dispersas; lectura predeterminada y escritura dinámica disponibles en H3.4a. |

Los IDs de instancia son globales en la sesión. Se conserva `identity.used_instance_ids` incluso cuando una entidad se retira. El contador `identity.next_sequence` y el registro de utilizados son parte del mismo borrador causal que la operación originaria. No se reutiliza un ID confirmado anteriormente.

Las cartas del paquete son definiciones; no se modifican al cambiar una instancia. Los datos de un personaje tampoco son idénticos a las variables narrativas de sesión ni a los hechos del historial.

## 3. Operaciones ejecutables en H3

Todas las entradas que siguen son consecuencias declarativas y requieren un paquete admitido. Las referencias de entidad deben ser explícitas, existentes y del tipo esperado. La excepción y el rechazo de una operación impiden confirmar toda la transacción causal. La validación final del estado corresponde a GISELA.

### Transferencia de objetos, `transfer`

**Entrada:** `object`, `from` y `to`, con IDs explícitos. **Precondiciones:** el objeto existe, el origen coincide exactamente con su propietario o ubicación actual y el destino es un personaje o un lugar existente. **Resultado:** se retira el campo anterior y se establece `owner` o `location`, nunca ambos. **Errores relevantes:** `INVALID_REFERENCE`, `INVALID_STATE`. **Pruebas:** `test_transfer_between_person_and_location`, `test_wrong_transfer_origin_is_atomic`, recorridos CLI de H1.

### Movimiento de personajes, `move_character`

**Entrada:** `character`, `location`. **Precondiciones:** ambos IDs existen y pertenecen a las categorías correctas. **Resultado:** actualiza `character.location`; no cambia `current_scene`. **Error:** referencia inválida. **Prueba:** `test_move_character_and_location_condition`.

### Conocimiento individual, `learn_fact`

**Entrada:** `character`, `fact`. **Resultado:** añade el hecho a `character.knowledge` si todavía no está. No escribe en `history.facts`, por lo que `has_fact` y `knows` siguen siendo consultas diferentes. **Prueba:** `test_learn_and_believe_do_not_register_new_historical_fact`.

### Creencias, `set_belief`

**Entrada:** `character`, `claim` y un `value` booleano. **Resultado:** asigna la creencia del personaje; no convierte la afirmación en hecho histórico y no modifica lo que saben los demás personajes. **Prueba:** `test_learn_and_believe_do_not_register_new_historical_fact`.

### Crear instancias, `create_instance`

**Entrada:** `card`, `instance_id` opcional y propietario o lugar cuando corresponda. **Precondiciones:** carta de personaje, lugar u objeto; referencias exigidas por el tipo válidas; ID no utilizado antes. **Resultado:** agrega la instancia con datos iniciales mínimos y reserva el ID en el borrador. Si falla una operación posterior, no se confirma ni la instancia ni su ID. **Límite:** no crea todavía habilidades o efectos mediante esta operación y no copia propiedades avanzadas de la carta. **Pruebas:** `test_creating_and_removing_retains_used_identity`, `test_auto_id_generated_only_on_commit`, `test_creation_then_failure_does_not_consume_id`.

### Retirar instancias, `remove_instance`

**Entrada:** `instance`. **Precondiciones:** la instancia existe y ninguna otra entidad, relación, capacidad o personaje jugador la referencia. **Resultado:** retira la instancia, pero conserva su ID en el registro de utilizados. **Errores:** `INVALID_REFERENCE`, `ENTITY_IN_USE`. **Pruebas:** `test_removing_referenced_character_is_atomic`, `test_removed_id_reuse_rolls_back_all`.

### Conceder habilidades, `grant_skill`

**Entrada:** `character`, `skill`, `overflow` opcional. **Precondiciones:** personaje y carta de habilidad válidos; capacidad disponible en mano o reserva. **Resultado:** crea una instancia de habilidad con ID nuevo. Si ambas zonas están llenas y se autoriza `require_choice`, solicita al jugador el descarte mediante la transacción pendiente de GISELA. ALBERTO solo aplica la respuesta; no crea otra sesión. **Errores:** `MISSING_CAPACITY`, `CAPACITY_EXCEEDED`, `NO_LEGAL_CHOICE`. **Pruebas:** `test_pending.py`, `test_h2_closure.py`.

### Mover o descartar habilidades, `move_skill` y `discard_skill`

**Entrada:** `character`, `skill_instance`, y `to` para el movimiento. **Precondiciones:** la habilidad pertenece al personaje; el destino tiene cupo. **Resultado:** cambia la zona o retira la instancia. Los IDs descartados siguen reservados. **Errores:** `INVALID_STATE`, `CAPACITY_EXCEEDED`. **Pruebas:** `test_move_skill_rejects_full_hand`, `test_move_and_discard_skill`. Jugar una habilidad y aplicar su política de retorno no es parte de estas operaciones.

### Variables, escena y tiempo

`set` y `add` cambian variables declaradas de ámbito `session` o `world`, propiedades y relaciones declaradas, conservando sus tipos y rechazando sumas no numéricas. `set_scene` cambia la escena presentada sin mover personajes. `advance_time` aumenta explícitamente `world_time` en minutos positivos; no activa por sí solo un Scheduler independiente. `roll` consume el RNG transaccional y escribe una variable numérica; `record_fact` agrega una ocurrencia al historial narrativo de GISELA, no al conocimiento individual. Estas operaciones se coordinan en `consequences.py` y `world.py` según su responsabilidad.

**Pruebas:** `test_advance_time_is_explicit_and_restorable`, regresiones de H1 y H2, pruebas de RNG, historial y reacciones.

## 4. Consultas puras disponibles

- `owns`: compara la propiedad de un objeto con un personaje explícito.
- `at_location`: consulta la ubicación de un personaje.
- `knows`: consulta conocimiento individual.
- `believes`: consulta el valor booleano de una creencia individual.
- `has_skill`: comprueba carta, personaje y zona `hand`, `reserve` o `either`.
- `has_fact`: consulta una ocurrencia registrada en el historial de GISELA.
- `compare`: compara expresiones admitidas del subconjunto actual.
- `all`, `any`, `not` y `constant`: composición lógica sin mutaciones.

Las condiciones no asignan conocimiento nuevo ni ejecutan acciones para obtener su respuesta. Los contextos `$actor` y otros selectores dependientes de ligaduras no implementadas se rechazan anticipadamente, sin seleccionar el primer resultado de forma implícita.

## 5. Reactividad y conflictos

Las reglas disparadas en una misma ronda se evalúan contra un estado base común. Antes de aplicar sus consecuencias se comprueban las colisiones de escritura conocidas mediante `writable_key`. Por ejemplo, dos reglas que intenten mover al mismo personaje, o una que retire una instancia utilizada por otra, generan `REACTION_CONFLICT`, con rollback de la acción completa. La implementación conserva el orden estable de reglas establecido en H2 y el límite de rondas reactivas.

La resolución de conflictos es conservadora: se prefiere rechazar dos escrituras que puedan interferir antes que hacer depender el resultado del orden físico del paquete. Este mecanismo no constituye un sistema general de planificación de dependencias ni demuestra ausencia de conflictos semánticos en operaciones futuras.

## 6. Persistencia, errores y pruebas

La sesión guarda exclusivamente cambios confirmados. Si se solicita una decisión auxiliar, la intención pendiente y las respuestas se serializan por separado; el borrador no se publica. Restaurar exige reconstruir la solicitud contra el mismo paquete y las mismas definiciones. La asignación de identidades, las relaciones y las variables participan del mismo rollback que el historial y el RNG.

Para repetir las pruebas de ALBERTO y la verificación integral:

```bash
python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q
python tools/check_gisela.py --full
```

Los errores de dominio se expresan mediante códigos estables como `INVALID_REFERENCE`, `INVALID_STATE`, `INSTANCE_COLLISION`, `ENTITY_IN_USE`, `CAPACITY_EXCEEDED` y `REACTION_CONFLICT`. Los casos exactos dependen de las precondiciones de cada operación. La API externa devuelve errores de ejecución tipados; el anfitrión no debe intentar reparar directamente el estado.

## 7. Límites y siguientes pasos

H3.4a incorporó propiedades y relaciones mutables, lecturas predeterminadas y escrituras compatibles. H3.4c incorpora aplicación y vencimiento de efectos. Los atributos efectivos y Scoresheet están disponibles desde H3.4b. Quedan pendientes la ejecución de cartas de habilidad y sus políticas de retorno. También faltan acciones desde escenas o elementos y ligaduras de referencias contextuales, correspondientes a la evolución del motor y a H4.

La admisión estática conoce algunas de estas estructuras, pero el ejecutor todavía las rechaza. La planificación y el inventario de hallazgos están en [H3. Revisión, hallazgos y plan](../operatives/H3_REVISION_PLAN_IMPLEMENTACION.md). No se debe marcar H3 completo antes de verificar las capacidades pendientes y sus consecuencias para la persistencia.

## 8. Propiedades y relaciones en H3.4a

Las propiedades se definen en cada carta de personaje, lugar u objeto. Las relaciones se declaran mediante `manifest.relationship_fields` y son dirigidas. Una lectura de una propiedad o relación ausente devuelve su valor inicial, sin materializarla. `set` y `add` escriben el borrador, comprueban tipos y límites y generan `state_changed` solo si cambia el valor.

Las reglas de una ronda usan un estado base común. GISELA combina las operaciones `add` y consolida los `set` iguales; las asignaciones contradictorias y la mezcla `set` con `add` se rechazan. Consulte la [guía ejecutable](../architecture/ALBERTO.md) y el [registro de H3.4a](../operatives/H3_4A_CIERRE.md).

## H3.4b. Datos de S.O.F.I.A. implementados

ALBERTO resuelve los atributos opcionales de las cartas y las instancias. `base` es inmutable, `current` es transaccional y `effective` se calcula desde los modificadores de los efectos activos. La consulta Scoresheet lee únicamente el estado confirmado; no mantiene un segundo registro de atributos. Consulte [la especificación de S.O.F.I.A.](SOFIA.md) y [su guía ejecutable](../architecture/SOFIA.md).

## H3.4d. Habilidades ejecutables

GISELA autoriza y ejecuta las habilidades de ventanas de nodo. ALBERTO mantiene únicamente instancias, zonas, capacidad e identidad. Los destinos `discard`, `hand` y `reserve` se aplican transaccionalmente. Consulte [HABILIDADES.md](../architecture/ALBERTO.md). Las acciones de exploración permanecen fuera del alcance actual.

## Integración opcional TRAITS (formato GISELA v1.3)

Las instancias `character`, `location` y `object` del nuevo formato admiten rasgos actuales, derivados inicialmente de su carta salvo sustitución explícita. ALBERTO ejecuta `assign_trait`, `remove_trait` y `has_trait` mediante `world_traits.py`; las validaciones de capacidad, exclusiones y pertinencia corresponden al núcleo independiente TRAITS. El guardado conserva las asignaciones actuales, no una segunda ficha separada. GISELA sigue siendo la única autoridad de commit. Los paquetes v1.2 no cambian. Véase [integración fase 1](TRAITS_DICE_INTEGRACION_FASE_1.md).
