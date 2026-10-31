# DICE — Contrato de sesión e interfaz pública (propuesta)

**Proyecto:** GISELA, motor general de historias y juegos interactivos  
**Fecha:** 30 de octubre de 2026  
**Estado:** PROPUESTA DE API pública todavía no implementada. Ya existe núcleo DICE y adaptador interno TRAITS–DICE; no existe aún `pending_evaluation` ni tirada visible.
**Relación:** complemento técnico de ADR-019 (revisión 2); no sustituye ADR-001–008, 012–014 ni el contrato v1.2.

**Precisión E0/E1:** las menciones históricas al «jugador» son ejemplos, no una restricción del solicitante: pueden llamar clientes, servicios u otra instancia de GISELA, siempre a través de la autoridad confiable del anfitrión. E1 reservó v1.4 para autoría sin habilitar sesiones. Si E3 cambia un contrato de sesión ya ejecutable en E2, debe versionarlo explícitamente y no reinterpretar v1.4.

## 1. Decisiones vigentes y alcance

**DECIDIDO:** GISELA debe poder presentar los dados antes de aplicar el resultado; una tirada publicada queda fijada y, por defecto, no admite cancelación para evitar su consecuencia. El juego puede declarar retiradas o repeticiones explícitas, auditables y con reglas propias.

**DECIDIDO:** el turno corresponde a una ejecución de nodo, no a cada transacción. El cierre A y el inicio B pueden confirmarse en una sola transacción. DICE no tiene autoridad para crear turnos, modificar el mundo o persistir por su cuenta.

**PROPUESTO aquí:** definir una interfaz pública mínima, una evaluación pendiente persistente y el límite de las dos transacciones. **No** se propone aún un mecanismo matemático único, el contrato interno definitivo de TRAITS ni cambios inmediatos en código o JSON Schema.

## 2. Comprobación sobre el código del ZIP (6)

- `GiselaSession.observe()` proyecta estado confirmado; `GiselaSession.act()` autoriza por `session_id`, `revision` y una `action_id` efectivamente ofrecida.
- La sesión pública v1.2 tiene `status ∈ {preparing,node,exploring,ended}`, `revision`, `world_revision`, `turn` y `rng` con `sha256_counter_v1`.
- `pending_transaction` almacena **intención y respuestas** para reproducir un borrador. No almacena tiradas confirmadas y no debe reinterpretarse como resultado de DICE.
- El `roll` existente en `gisela/engine/consequences.py` **escribe en una variable del borrador** y cambia su RNG provisional. No permite publicar dados antes de que se confirmen las consecuencias de la misma operación.
- El validador de sesión y la proyección pública rechazan estructuras no declaradas. La propuesta exige una evolución versionada de los contratos y nuevas pruebas de restauración; **no puede implementarse agregando una clave sin actualizar los validadores**.

## 3. Frontera causal de una evaluación visible

**Restricción propuesta para la primera versión:** solo se puede preparar una evaluación visible en un **límite declarativo identificable**, antes de ejecutar cualquiera de las consecuencias que dependan de ese resultado. La fase de preparación puede consultar el estado y resolver los modificadores, pero no confirma otros efectos de la acción originaria, no inicia/cierra nodos y no ejecuta reacciones de éxito o fracaso.

Esta regla evita una trampa del diseño: no basta con interceptar el `roll` actual en medio de una lista arbitraria de efectos, porque podría haber mutaciones antes de esa operación. Para v1, el lenguaje de autoría debe señalar una **evaluación explícita** con sus ramas de consecuencia; si una historia necesita hacer algo *antes* de la evaluación, esos efectos deben pertenecer a una operación causal anterior ya confirmada.

Una vez fijada, GISELA guarda la procedencia y el resultado, sin serializar el borrador completo. Durante la aplicación, recupera las ramas declaradas y comprueba que el origen sigue siendo válido; usa el resultado ya fijado y no vuelve a consumir RNG por esa evaluación.

No se admite encadenar silenciosamente otra evaluación **visible** dentro de la transacción de aplicación: debe existir una nueva frontera explícita. **Tampoco se admite una evaluación visible dentro de las reacciones de `node_completed`, `turn_ended` o `turn_started` que forman una transición A→B**: dividiría el cierre y el inicio que ADR-007 exige confirmar conjuntamente. En v1, esos lugares solo podrán contener tiradas ocultas y atómicas; los dados visibles deben solicitarse desde un paso o acción estable anterior o posterior a la transición. Las tiradas ocultas mantienen su semántica atómica actual.

## 4. Evolución propuesta del snapshot

ADR-021 estableció **v1.4 para el paquete de autoría E1**, pero su esquema de sesión sigue siendo solo una forma reservada, **no admitida para restauración ni ejecución**. Los formatos v1.2 y v1.3 existentes se conservan; v1.3 ya incorpora TRAITS. La migración desde v1.2 solo podrá producir un nuevo snapshot sin evaluación pendiente y deberá ser explícita.

Campo opcional nuevo en sesión: `pending_evaluation`, **excluyente** con `pending_transaction`. La ausencia del campo significa que no existe una evaluación fijada pendiente de efectos.

### Campos internos mínimos (nombres provisionales)

| Campo | Significado |
|---|---|
| `evaluation_id` | Identidad estable de la evaluación en esa línea de sesión. |
| `source` | Procedencia autorizada: nodo/paso/opción, acción de escena o habilidad, según las capacidades del contrato. |
| `resolution_ref` | Referencia declarativa a las ramas de consecuencias aprobadas en el paquete. |
| `profile_id`, `profile_version` | Reglas de resolución utilizadas; la versión impide reinterpretación al restaurar. |
| `inputs_digest` | Huella canónica de entradas resueltas, incluyendo contribuciones efectivas y versión de sus reglas. |
| `context_digest` | Huella de los datos pertinentes para validar la continuidad, sin copiar todo el mundo. |
| `dice` | Resultados individuales en orden de consumo y tipo/caras de cada dado. |
| `modifiers`, `outcome` | Modificadores efectivamente utilizados y resultado clasificado. |
| `presentation_mode` | `visible` o `acknowledged`; `hidden` nunca crea este pendiente. |
| `prepared_revision` | Revisión de sesión confirmada al publicar la evaluación. |
| `rng_counter_before`, `rng_counter_after` | Evidencia del consumo comprometido; el RNG autorizado sigue siendo el de `session.rng`. |

El esquema debe fijar tipos, rangos, límites de tamaño, identidad del origen, exclusión mutua y combinación con `status`/`cursor`. La información del pendiente es interna y **no se copia literalmente a `Observe`**.

**Reglas de estado:** preparar aumenta `revision` y compromete `rng`; no aumenta `turn`, `world_revision` ni `world_time` y no aplica aún hechos, cambios de ALBERTO o progreso de MARY. Aplicar aumenta `revision` y cambia `world_revision` solo si se produce un cambio real según el contrato causal existente. La aplicación exitosa retira `pending_evaluation` y registra la identidad/resolución necesaria para garantizar aplicación a lo sumo una vez dentro de la línea de sesión.

No se fija aún una política universal de historial ilimitado. Las repeticiones explícitas sí deben conservar la cadena mínima de evaluación original y sustituta.

## 5. API pública propuesta: reutilizar `Act` y `Observe`

**No** crear un endpoint `roll()` que acepte parámetros arbitrarios del cliente. El inicio de una tirada visible ocurre cuando el jugador ejecuta una acción del juego ya ofrecida por `Observe` (`choose`, `interact`, uso de habilidad, etc.) y esa acción invoca una evaluación declarativa.

### Preparación

- La acción llega mediante el `Act` normal con `session_id`, `revision`, `action_id`.
- GISELA autoriza la acción; compone entradas; llama a DICE con RNG inyectado; fija los dados y `pending_evaluation` en una transacción.
- La respuesta `Act.status = ok` devuelve una nueva proyección `Observe` con `content.kind = evaluation_result` (nombre provisional).

### Observación pública

La proyección contiene **solo lo autorizado para el jugador**: `evaluation_id`, `dice` visibles, `total` si corresponde, `outcome` cuando el perfil permita revelarlo, y `presentation_mode`. No expone semilla, contador RNG, atributos secretos de entidades, condiciones internas, huellas ni ramas ocultas. Un juego que quiera mostrar todos los modificadores debe declararlos publicables; el resultado matemático no puede inventarse en la interfaz.

La misma proyección se devuelve sin cambios al observar repetidamente o tras restaurar un snapshot compatible. Ni GLAUQUIR ni Ren'Py generan ni interpretan dados.

### Continuación

La proyección debe ofrecer **solo acciones válidas para el pendiente**:

| Modo | `action.kind` propuesto | Quién lo solicita |
|---|---|---|
| `visible` | `continue_evaluation` | El cliente, después de presentar el resultado; puede ser automático. |
| `acknowledged` | `acknowledge_evaluation` | El jugador confirma desde la interfaz. |
| Retirada explícita | `withdraw_evaluation` | Solo si las reglas del juego ofrecen esa rama. |
| Repetición explícita | `reroll_evaluation` | Solo si el perfil autoriza una nueva tirada y sus requisitos/coste. |

Cada acción tiene `action_id` asociado a la **revisión presente**, conforme a ADR-014. `Act` sigue rechazando acciones ajenas a `Observe` y revisiones caducadas. La distinción entre continuación automática y confirmación humana es un contrato de comportamiento del cliente; el motor valida el tipo de acción, pero no puede demostrar por sí mismo qué vio físicamente una persona.

`cancel_pending` **no** sirve para descartar `pending_evaluation`. Mientras exista este último, se permiten consultas/guardado y únicamente las continuaciones declaradas; se bloquean otras mutaciones de sesión.

## 6. Ejemplo ilustrativo de `Observe` (NO schema definitivo)

```json
{
  "status": "node",
  "revision": 18,
  "content": {
    "kind": "evaluation_result",
    "evaluation_id": "eval_000006",
    "presentation_mode": "acknowledged",
    "dice": [{"sides": 6, "value": 4}, {"sides": 6, "value": 2}],
    "total": 6,
    "outcome": "partial"
  },
  "actions": [
    {
      "kind": "acknowledge_evaluation",
      "action_id": "acknowledge_evaluation",
      "id": "continue",
      "label": "Continuar",
      "enabled": true
    }
  ]
}
```

Se omiten aquí deliberadamente otros campos obligatorios de `Observe` para concentrarse en la ampliación. Es un fragmento conceptual, **no** un objeto válido de v1.2 ni una especificación aprobada.

## 7. Restauración, errores y reintentos

1. Validar estructuralmente la versión de sesión y semánticamente la identidad de origen, el digest del paquete, las reglas/perfil, la exclusión de pendientes, el cursor y el consumo RNG registrado.
2. No reconstruir mediante una nueva tirada, ni siquiera para validar el snapshot.
3. Si falla la aplicación, conservar el pendiente exactamente como estaba antes del intento; no consumir RNG adicional ni registrar efectos parciales.
4. Una confirmación duplicada con una revisión antigua se rechaza por `STALE_PROJECTION`; una referencia de evaluación equivocada se rechaza sin mutar estado. El nombre del error específico queda abierto.
5. Un guardado deliberadamente anterior a la tirada no queda protegido por este contrato; rollback narrativo y resistencia a manipulación de guardados son políticas de producto separadas.
6. La evaluación confirmada puede invalidarse solo mediante un mecanismo explícito y auditable, nunca borrarse silenciosamente para volver a tirar.

## 8. Pruebas obligatorias antes de implementación completa

| ID | Prueba | Resultado |
|---|---|---|
| A01 | Preparar desde acción ofrecida | Datos y RNG confirmados; mundo/MARY/turn sin cambios. |
| A02 | Consultar y guardar repetidamente | Proyección y tirada inmutables, sin nuevos sorteos. |
| A03 | Restaurar con evaluación pendiente | Dados idénticos; resultado utilizable una sola vez. |
| A04 | Intentar acción ajena mientras hay pendiente | Rechazo sin mutaciones. |
| A05 | Aplicar y repetir `Act` antiguo | Un solo efecto; segundo intento rechazado. |
| A06 | Error durante ejecución de consecuencias | Roll fijo; rollback íntegro de la aplicación. |
| A07 | Cambiar paquete/perfil u origen en el snapshot | Restauración rechazada. |
| A08 | Cancelar por `cancel_pending` | No descarta tirada fijada. |
| A09 | `visible` frente a `acknowledged` | Acciones ofrecidas según modo; misma tirada. |
| A10 | Evaluación sin S.O.F.I.A., TRAITS o MARY | Funciona mediante contrato neutral. |
| A11 | Acción con efectos *antes* de evaluación visible | Rechazo en validación del paquete v1; sin efectos parciales. |
| A12 | Evaluación visible declarada en una reacción de cierre/inicio A→B | Paquete rechazado; no divide el cierre/inicio atómico de ADR-007. |
| A13 | Dos tipos de dados con consumo variable por rechazo | Se conserva contador RNG real y orden de resultados. |
| A14 | Ficha NPC con modificadores secretos | `Observe` no filtra datos ocultos. |

## 9. Orden de implementación posterior a la aprobación

1. Definir la operación declarativa de evaluación y el validador que garantice la frontera causal (sin ejecución parcial antes del dado).
2. Definir el contrato neutral de salida DICE y el adaptador que obtiene atributos/rasgos sin acoplar subsistemas.
3. Versionar esquemas de sesión/Observe/Act/result y validar fixtures positivos/negativos.
4. Incorporar la persistencia y las proyecciones del pendiente; probarlas sin motor de dados nuevo.
5. Integrar DICE con el RNG de GISELA; autorizar aplicación y rollback.
6. Ejecutar las pruebas aisladas y de integración; recién después utilizar U05 del demo como aceptación narrativa.

## 10. Puntos que permanecen abiertos

- Número definitivo de la nueva versión de sesión y política explícita de migración desde v1.2.
- Sintaxis declarativa concreta de la evaluación y sus ramas.
- Forma canónica del `context_digest` y nivel de trazabilidad histórica.
- Tratamiento de repeticiones y retiradas como operaciones de una futura versión si encarecen indebidamente v1.
- Alcance de la visibilidad de cada componente del cálculo, sin quebrar la transparencia de los dados que el autor decidió mostrar.

**Recomendación:** aprobar primero la **frontera causal de la evaluación** y el **uso de Act/Observe**, antes de alterar esquemas o el ejecutor.

## Estado después de E0 (30-10-2026)

La frontera de solicitantes, concurrencia, proyección previa a commit, recibos y almacenamiento local de E0 **ya está implementada** en Python (`authorized_gateway.py`, `checkpoint_store.py`). Este documento sigue siendo una **propuesta para v1.4**: `pending_evaluation`, tres políticas de presentación, operaciones de continuación, perfiles de paquete y evaluaciones visibles NO están implementados. La autenticación real pertenece al anfitrión, y la lectura pública E0 solo contempla la audiencia `observe_player`; no se debe deducir de este documento una autorización genérica para servicios remotos.
