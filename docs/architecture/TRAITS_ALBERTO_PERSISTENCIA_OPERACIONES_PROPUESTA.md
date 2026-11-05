# TRAITS y ALBERTO: Persistencia y operaciones de asignación (PROPUESTA)

**Proyecto:** GISELA, motor general para distintos juegos.
**Estado:** contrato de diseño; la persistencia y operaciones básicas se implementaron para GISELA v1.3. Los sucesos tipados y capacidades futuras siguen propuestos. Véase `TRAITS_DICE_INTEGRACION_FASE_1.md`.
**Fecha:** 30-10-2026.
**Base examinada:** `las-personas-tienen-nombre(7).zip`, especialmente `docs/architecture/ALBERTO.md`, `gisela/contracts/{card,initial_state,session,common}.schema.json`, `gisela/engine/{initialization,world_lifecycle,world,reactions}.py` y el contrato TRAITS previo.

## 1. Problema y criterio

Las cartas y las instancias **v1.2** de ALBERTO no poseen un campo `traits`. `create_instance` inicializa los datos mínimos de la entidad sin copiar propiedades avanzadas de su carta. El esquema de sesión v1.2 impide añadir campos arbitrarios, por lo que los ejemplos siguientes **no son JSON válido en v1.2**; la nueva extensión v1.3 admite `traits`. Debemos ampliar explícitamente la admisión, inicialización, persistencia y ejecución, **sin modificar silenciosamente los contratos v1.2**.

**Decisiones de partida:** (1) el juego configura un máximo de rasgos por entidad, por defecto **5**; (2) GISELA es la única autoridad transaccional; (3) ALBERTO conserva las asignaciones de TRAITS, sin duplicarlas en un estado independiente; (4) TRAITS evalúa pertinencia y contribuciones de forma pura; (5) el resultado preparado de DICE puede necesitar congelar los rasgos que intervinieron antes de aplicar consecuencias.

## 2. Tres planos que no deben confundirse

| Plano | Contenido | Propietario lógico |
| --- | --- | --- |
| Definición de rasgo | ID, aplicabilidad, exclusiones, contribuciones y versión | Catálogo de TRAITS definido por el juego |
| Rasgos predeterminados | IDs de rasgos iniciales indicados en una **carta de entidad**; no se alteran por una partida | Definiciones del paquete de autoría |
| Rasgos actuales | Conjunto materializado de IDs que tiene una **instancia** en la sesión confirmada | Estado del mundo de ALBERTO, confirmado por GISELA |

No generar una instancia ni un ID global de ALBERTO por cada rasgo: el rasgo es una referencia a definición, no un objeto transferible. Su presencia o ausencia en una entidad forma parte del estado de esa entidad.

### 2.1. Ámbito propuesto para v1

Permitir rasgos en entidades `character`, `location` y `object` que tengan carta. Los perfiles de rasgo declaran en qué clases pueden aplicarse. No incluir de forma automática `skill` ni `effect`, que poseen sus propios contratos y ciclos de vida; cualquier ampliación será versionada.

Un mismo rasgo puede estar asignado a varias entidades. Esto no significa que comparta un estado mutable entre ellas.

## 3. Inicialización y representación efectiva

**Propuesta:** adoptar el mismo patrón general de "definición inicial inmutable / instancia mutable" que S.O.F.I.A., sin introducir un archivo de estado exclusivo de TRAITS.

1. **Carta (`cards[]`)**: puede declarar `traits: [trait_id, ...]` como valor predeterminado para futuras instancias de esa carta. Si falta, el predeterminado es `[]`.
2. **Instancia del `initial_state`**: puede declarar `traits` para **reemplazar completamente** el predeterminado de su carta; la ausencia significa "heredar de la carta", pero `[]` explícito significa "comenzar sin rasgos".
3. **Estado confirmado (`session.world`)**: para entidades compatibles, **materializar siempre** `traits` como lista sin repetidos, normalizada en orden canónico. Nunca reconstruir rasgos actuales desde la carta al restaurar el guardado.
4. **Creación durante la partida (`create_instance`)**: la entidad creada hereda los rasgos predeterminados de su carta y se valida la capacidad. En v1, `create_instance` no lleva sobreescritura adicional de rasgos; para cambiarlos se usa una operación explícita posterior en la misma transacción, si corresponde.
5. **Restauración**: el estado confirmado contiene el conjunto actual; la carta solo sirve como definición y referencia. La identidad del paquete y su versión/digest se validan, sin rehacer asignaciones desde la carta.

La lista se normaliza para serialización estable; su orden **no** representa prioridad, cronología ni ventaja. Las entradas de autoría duplicadas se **rechazan** durante la admisión (no se silencian). Una consulta sobre rasgos actuales es pura.

### Ejemplo conceptual (no válido en v1.2)

Carta:

```json
{"id":"explorer","kind":"character","title":"Explorador","traits":["curious","prudent"]}
```

Instancia inicial (omite `traits`, por lo tanto hereda):

```json
{"id":"explorer_1","card":"explorer","location":"camp"}
```

Instancia guardada después de aprender una característica y dejar atrás otra:

```json
{"id":"explorer_1","card":"explorer","location":"camp","traits":["curious","resolute"]}
```

El ejemplo utiliza IDs genéricos. Los rasgos solo serán válidos cuando estén declarados en el catálogo del juego, y los demás campos exigidos por los esquemas vigentes se mantendrán según corresponda.

### 3.1. ¿Cómo distinguir lo inicial de lo adquirido?

La **configuración inicial efectiva** de una instancia preexistente se obtiene de `initial_state`, con su regla de herencia; para una instancia creada durante la partida, de su carta en el instante de creación. El **conjunto actual** está en la sesión. La comparación de ambos puede informar de diferencias, pero **no reconstruye el orden de los acontecimientos**. Una entidad podría perder un rasgo y recuperarlo después y mostrar el mismo conjunto final.

Si un juego necesita saber **cuándo, por qué o cuántas veces** cambió un rasgo, debe registrar hechos/eventos narrativos explícitos mediante GISELA o un registro histórico versionado específico. No inferir retrospectivamente una cronología del conjunto actual. Las asignaciones de partida no obligan a registrar un hecho histórico universal.

## 4. Operaciones declarativas de ALBERTO (candidatas)

| Operación | Entrada | Resultado | Notas |
| --- | --- | --- | --- |
| `assign_trait` | `entity`, `trait` | Añade el rasgo si falta | Verifica existencia, clase compatible, límite y exclusiones |
| `remove_trait` | `entity`, `trait` | Retira el rasgo si está asignado | No modifica la definición de la carta |
| Condición `has_trait` | `entity`, `trait` | Booleano sin mutación | No consume RNG ni crea un turno |

**Idempotencia propuesta:** repetir `assign_trait` sobre un rasgo ya presente y `remove_trait` sobre uno ya ausente son operaciones válidas sin cambio efectivo, sin liberar/consumir capacidad adicional y sin disparar nuevos eventos de cambio. Aunque sea idempotente, una referencia a un rasgo o entidad **inexistentes** sigue siendo un error, no una operación silenciosamente aceptada. `has_trait` exige una entidad y un rasgo conocidos, aun cuando el resultado sea falso.

**Orden de validación:** referencias, clase de entidad, definición y exclusiones, capacidad, modificación del borrador y sucesos de cambio efectivo. La validación previa al cambio impide escribir un estado transitoriamente inválido para "arreglarlo después".

**Límite:** `max_traits_per_entity`, predeterminado en **5** en el manifiesto o perfil de TRAITS del juego. Contar *todos* los rasgos asignados, sean pertinentes o no. Los rasgos circunstanciales que no son asignaciones no ocupan cupo. Valor 0 podría deshabilitar asignaciones si el contrato final lo admite; el techo numérico de seguridad queda por acordar.

**Exclusiones:** si A declara que excluye B, no pueden coexistir en una instancia aunque B no declare su exclusión de A. Ni los nombres ni las contribuciones opuestas implican incompatibilidad.

### 4.1. Cambiar rasgos con capacidad completa

Si una entidad tiene sus cinco espacios ocupados y el autor desea sustituir un rasgo, la secuencia explícita `remove_trait(A)` y luego `assign_trait(B)` **dentro de una misma transacción** resulta válida si cada operación satisface sus precondiciones; si la segunda falla, se revierte también el retiro. No introducir una operación implícita "reemplazar el peor rasgo".

### 4.2. Sucesos y reacciones

Una modificación efectiva podría emitir los sucesos tipados `trait_assigned(entity, trait)` y `trait_removed(entity, trait)`. **Estos nombres son una propuesta**, no eventos que el ejecutor reconozca hoy; deben versionarse en `common.schema.json` y `_matches()` antes de habilitar reglas que los escuchen. No reutilizar silenciosamente `state_changed` sin ampliar su definición de destino.

Si distintas reglas reactivas intentan modificar el conjunto de rasgos de **la misma entidad en una ronda**, v1 debería rechazarlas conservadoramente como `REACTION_CONFLICT` hasta disponer de un planificador de conjuntos que componga altas/bajas sobre la misma instantánea. No dar prioridad al orden físico de las reglas. Las operaciones consecutivas de una **misma acción causal** conservan su orden declarado, sujetas a rollback atómico.

## 5. Invariantes y responsabilidades

- **Admisión de paquete:** validar IDs de rasgos, referencias de cartas y de instancias iniciales, clases admitidas, incompatibilidades, ausencia de duplicados y capacidad final **antes** de ejecutar.
- **Inicialización:** materializar el conjunto actual de rasgos, sin reemplazar ni editar las definiciones originales.
- **Ejecución:** `assign_trait`/`remove_trait` operan solo sobre el borrador de GISELA; un error de cualquiera de ellas invalida toda la operación causal.
- **Creación y retiro:** `create_instance` aplica rasgos por defecto; `remove_instance` retira la entidad junto con sus rasgos actuales; ningún rasgo mantiene referencias colgantes a una entidad inexistente.
- **Persistencia:** rasgos actuales en el estado confirmado de la entidad; no mantener un `traits_state` separado en la sesión.
- **Presentación y privacidad:** las consultas internas a `has_trait` no autorizan publicar rasgos secretos. `Observe` proyecta únicamente la información expresamente permitida para ese cliente.
- **Integración DICE:** las aportaciones de TRAITS son puras. En evaluaciones visibles, el contexto y las aportaciones que ya contribuyeron a la tirada quedan fijados antes de la presentación, sin reconsultar rasgos sobre un estado posterior.
- **Integración MARY:** una asignación no satisface por sí misma un objetivo genérico de MARY; el autor debe definir el acontecimiento/condición que corresponda, para evitar misiones implícitas del motor.

## 6. Versionado y compatibilidad

Los esquemas actuales se identifican como `v1.2` y tienen `additionalProperties:false`. Por ello no basta con insertar campos en un guardado v1.2; deberán versionarse `card`, `initial_state`, `session`, `common`, paquete/manifiesto y validadores semánticos con una política de compatibilidad explícita. **No presentar esta propuesta como modificación ejecutable.**

Un paquete sin catálogo TRAITS debe seguir funcionando sin añadir rasgos ni exigir un estado adicional. Guardados antiguos se leen conforme al contrato de su versión; cualquier migración futura debe ser explícita y probada. No rehidratar rasgos ausentes de un guardado viejo inventando que siempre estuvieron asignados.

## 7. Matriz de aceptación propuesta

| ID | Escenario | Resultado esperado |
| --- | --- | --- |
| A01 | Carta sin `traits`; instancia sin `traits` | Estado materializado `[]` |
| A02 | Carta con dos rasgos; instancia omite `traits` | Hereda exactamente los dos |
| A03 | Carta con dos rasgos; instancia inicial declara `[]` | Inicia vacía, no hereda |
| A04 | Carta con dos rasgos; instancia inicial declara otros dos | Reemplaza, no mezcla |
| A05 | Duplicado o rasgo inexistente en el paquete | Rechazo de admisión |
| A06 | Cinco asignados y un sexto intento | `CAPACITY_EXCEEDED`, rollback |
| A07 | Exclusión unilateral A/B | Rechazo de asignación conjunta |
| A08 | Asignación repetida | No-op, sin suceso y sin duplicación |
| A09 | Retiro repetido | No-op, sin suceso |
| A10 | Retiro y alta en una misma transacción, con segunda operación fallida | Ambos cambios revertidos |
| A11 | Entidad creada durante el juego | Hereda rasgos de su carta |
| A12 | Entidad retirada | Sus rasgos dejan de existir con la instancia |
| A13 | Guardar y restaurar tras perder rasgo inicial | No reaparece desde la carta |
| A14 | Guardar y restaurar tras adquirir rasgo | Se conserva |
| A15 | Dos reglas reactivas modifican los rasgos de la misma entidad | Conflicto, no prioridad por orden |
| A16 | `has_trait` por consulta | Sin escritura, RNG ni turno |
| A17 | Rasgo privado consultado internamente | No aparece automáticamente en `Observe` |
| A18 | TRAITS evalúa un conjunto sin S.O.F.I.A. | Funciona normalmente |
| A19 | Se preparó DICE visible, cambió el mundo y se intenta aplicar | Se respeta el contrato de evaluación fijada y bloqueo de contexto |
| A20 | Paquete sin TRAITS | Conserva funcionamiento heredado |

## 8. Estado y secuencia de trabajo

**DECIDIDO:** arquitectura de propósito general; máximo por entidad configurable con predeterminado 5; única autoridad transaccional de GISELA.

**PROPUESTO:** `traits` predeterminados en cartas, sobreescritura explícita de instancias iniciales, conjunto materializado en instancia de sesión, herencia en `create_instance`, operaciones `assign_trait`/`remove_trait`, condición `has_trait`, conflictos conservadores y sucesos tipados.

**ABIERTO:** aprobación de herencia/sobreescritura; clases de entidad soportadas en v1; evento de cambio y su tratamiento reactivo; configuración exacta del manifiesto; migración de snapshots; techo operativo de capacidad; política de visibilidad de rasgos; trazabilidad histórica opcional.

**Siguiente paso técnico, después de aprobación autoral:** fijar los esquemas versionados y pruebas de admisión/estado; implementar la inicialización, operaciones y consultas puras; comprobar rollback y reacciones; integrar el evaluador TRAITS sin acoplarlo a DICE. No escribir reglas del demo en el motor.
