# TRAITS: Contrato de rasgos, pertinencia y composición (PROPUESTA)

**Proyecto:** GISELA, motor narrativo general.
**Estado:** contrato histórico. El núcleo TRAITS v1 está implementado y su persistencia en ALBERTO funciona en GISELA v1.3; las ampliaciones de reglas avanzadas siguen propuestas. Véase `TRAITS_DICE_INTEGRACION_FASE_1.md`.
**Fecha:** 30-10-2026.
**Referencias:** `docs/architecture/ALBERTO.md`, `SOFIA.md`, `GISELA_Arquitectura_Consolidada_v1_5.md`, `docs/decisions/GISELA_ADR_001_017.md` (ADR-007/008), `ADR_019_DICE_EVALUACIONES_VISIBLES_PROPUESTA.md` y `DICE_EVALUACION_DECLARATIVA_PROPUESTA.md` (si ya se aplicó el parche incremental).

## 1. Propósito y fronteras

TRAITS significa **Trait Rules and Attribute Interaction Tracking System**. Define e interpreta **rasgos cualitativos y sus aportaciones declarativas**, sin imponer un catálogo de personalidades, sistemas de alineamiento ni reglas específicas de un juego. Puede ser utilizado fuera de GISELA mediante entradas y salidas neutrales.

- **ALBERTO:** autoridad del modelo de entidades; conserva los rasgos asignados y sus cambios en el estado de trabajo de GISELA; verifica identidad, pertenencia y capacidad. No mantiene un segundo estado de rasgos.
- **S.O.F.I.A.:** capacidad opcional que ofrece atributos numéricos efectivos; `openness` corresponde a apertura, empatía y carisma; `awareness` se orienta a percepción sobrenatural. No reemplaza los rasgos ni realiza tiradas.
- **TRAITS:** admite definiciones, determina pertinencia y devuelve aportaciones puras y explicables. No consulta directamente sesiones, ejecuta acciones, decide sentimientos ni consume RNG.
- **DICE:** recibe valores y modificadores ya resueltos; calcula e interpreta una evaluación conforme a un perfil del juego. No debe importar TRAITS o S.O.F.I.A.
- **GISELA:** reúne contexto, evalúa condiciones narrativas y confirma cambios, resultados y consecuencias mediante sus transacciones; MARY puede evaluar los hechos confirmados.

**Invariante:** un rasgo no obliga a un personaje a actuar siempre de cierta manera. Una característica puede habilitar una posibilidad, alterar una evaluación o no intervenir.

## 2. Límite de rasgos por entidad: DECIDIDO

Cada juego declara su máximo de rasgos **por entidad**; si no lo declara, el máximo es **5**. Tener rasgos es opcional: **cero** es válido. Esta capacidad es una regla del juego, no un límite inmutable de TRAITS.

**Propuesta de interpretación para v1:** contar el conjunto de **rasgos asignados** a la entidad, estén o no siendo pertinentes en la evaluación actual. De otro modo, un rasgo no pertinente liberaría artificialmente un espacio. No se cuentan los efectos circunstanciales que solo alteran valores o condiciones, sin asignar un rasgo.

- Los identificadores de rasgo son únicos dentro del conjunto de una entidad: repetir el mismo ID no lo apila ni consume un segundo espacio.
- El límite se valida al admitir el paquete, al crear una entidad y en cada operación de asignación o retiro; las escrituras respetan la atomicidad de GISELA.
- La política inicial es **un único máximo por juego para todas las clases de entidad compatibles**. Capacidades por tipo de entidad quedan fuera de v1.
- El límite numérico máximo permitido por el validador y si se admite 0 como configuración global requieren un presupuesto de seguridad antes de cerrar el esquema; nunca se interpreta ausencia de límite como infinito.
- Las cartas aportan asignaciones iniciales; las instancias pueden ganar o perder rasgos posteriormente, si el juego lo permite. No se deben copiar silenciosamente propiedades avanzadas a instancias: el estado efectivo de rasgos se deriva de definiciones inmutables y del estado confirmado/delta persistido.

**ABIERTO:** si el autor desea permitir rasgos asignados pero suspendidos, deberá diseñarse explícitamente el estado de suspensión. V1 no lo necesita: un rasgo puede estar asignado y simplemente no resultar pertinente.

## 3. Definición declarativa de rasgo: PROPUESTO

Cada rasgo tiene, como mínimo:

| Elemento | Responsabilidad |
| --- | --- |
| `id` | Identificador estable definido por el juego. |
| `label`, `description` | Presentación y documentación del autor; no definen lógica por sí solos. |
| `entity_kinds` | Categorías a las que se puede asignar el rasgo. |
| `contributions` | Reglas declarativas de aplicabilidad y aportación. Pueden estar vacías. |
| `excludes` (opcional) | Incompatibilidades explícitas de asignación; no se infieren por nombres o lenguaje natural. |
| `visibility` (opcional) | Política de exposición; los rasgos ocultos de NPC no se publican automáticamente. |

Los rasgos no requieren puntuación numérica ni una taxonomía universal. Pueden describir personajes (`honest`, `impulsive`), objetos (`fragile`) o lugares (`poor_visibility`) cuando el tipo de entidad esté admitido. El soporte inicial de asignación debe concretarse en los contratos de ALBERTO (personajes, objetos y lugares son candidatos); ninguna categoría existente se declara compatible por mera inferencia.

**No se autoriza código de autor, expresiones Python, callbacks de red ni operadores arbitrarios.** El catálogo pertenece al paquete y queda versionado; GISELA debe poder validar sus referencias antes de iniciar una sesión.

## 4. Pertinencia: no aplicar todos los rasgos siempre

Una solicitud de TRAITS recibe una **instantánea neutral del contexto ya resuelto**, con identificadores de participante y etiquetas tipadas definidas por el juego. No recibe el mundo mutable ni accede a conocimiento o relaciones por su cuenta.

Una aportación es pertinente cuando se cumplen **todas** sus condiciones declaradas:

1. La entidad porta el rasgo y el rasgo admite su clase de entidad.
2. El rol de la entidad en la evaluación coincide (`actor`, `target`, `environment` u otro rol declarado por el perfil del juego).
3. El contexto satisface los filtros explícitos; para la primera versión bastan conjuntos finitos de etiquetas requeridas y excluidas.
4. Sus referencias a ranuras de modificación son aceptadas por el perfil de evaluación y sus valores pasan los controles de tipo y rango.

Las condiciones narrativas más complejas (`knows`, `believes`, relaciones, hechos, S.O.F.I.A. efectivo, etc.) las resuelve GISELA/ALBERTO **antes** de invocar TRAITS. Si el adaptador entrega una señal contextual derivada de ellas, debe conservar su procedencia para reproducirla y auditarla. TRAITS no ejecuta el lenguaje de condiciones de GISELA de manera encubierta.

La evaluación de pertinencia es **pura**, determinista y sin consumo RNG. Las etiquetas no son poderes mágicos: deben definirse con semántica estable en el juego, sin agregar tags ad hoc para forzar un resultado.

## 5. Contribuciones admitidas en v1: PROPUESTO

Para el primer contrato implementable, TRAITS devuelve solamente:

- **Modificadores aditivos enteros** sobre una **ranura tipada** que el perfil del juego haya declarado; por ejemplo `approach_modifier` o `difficulty_modifier`. Los nombres de ranura no son universales ni se confunden con los cinco nombres S.O.F.I.A.
- **Consultas de presencia** para condiciones de elegibilidad (`has_trait`) interpretadas por el adaptador del anfitrión. La elegibilidad de una elección no es un resultado aleatorio ni una modificación directa de DICE.

No incluir inicialmente: repetir dados, sustituir una tirada, cambiar de perfil a mitad de una evaluación, alterar directamente un resultado, ejecutar efectos narrativos, ni cadenas de rasgos que se disparan mutuamente. Podrían añadirse posteriormente con contratos versionados y pruebas de terminación.

**Composición de modificadores:** se agrupan por ranura y se suman. El perfil decide cómo incorpora cada total y define límites antes de consultar a DICE. TRAITS no interpreta probabilidades, no aplica un clamp implícito y no modifica directamente S.O.F.I.A.

## 6. Exclusiones, compatibilidad y conflictos

Conviene separar **conflictos de asignación** de **conflictos de aportación**:

- **Asignación:** dos rasgos declarados incompatibles por `excludes` no pueden coexistir en una misma entidad. La exclusión es simétrica al validarse; si A excluye a B, se rechaza A+B incluso cuando B no declare la exclusión de vuelta. Deben detectarse inconsistencias y referencias inexistentes al cargar el catálogo.
- **Aportación:** dos modificadores aditivos para la misma ranura son compatibles y se suman, incluso cuando tienen signos opuestos. No se deduce incompatibilidad porque los nombres sean semánticamente contrarios.
- **Aportaciones no aditivas:** si se incorporan en versiones posteriores, no se define prioridad implícita por orden de catálogo o ID. Una colisión no resuelta mediante una regla explícita del juego falla con diagnóstico identificable.
- **Duplicidad:** la misma regla de aportación, identificada por entidad/rasgo/regla/evaluación, se considera una sola vez; repetir consultas o restaurar una partida no vuelve a sumar el efecto.

Ejemplo de principio: `brave` y `prudent` pueden coexistir. Una acción arriesgada y una planificación cuidadosa no son situaciones equivalentes. El autor decide qué aportación es pertinente a cada contexto; TRAITS no concluye que uno cancela al otro ni modela por sí mismo la voluntad del personaje.

**Determinismo:** ordenar para producir diagnósticos o trazas estables es válido; ordenar para escoger silenciosamente qué contribución "gana" es incorrecto. La composición debe producir el mismo resultado sin importar el orden físico de las cartas o asignaciones.

## 7. Contrato neutral y ciclo causal

### Entrada lógica del evaluador TRAITS

- Catálogo de definiciones y versión.
- Conjunto de rasgos asignados, ya validado por el anfitrión, con rol y clase de entidad.
- Contexto cerrado y tipado de la evaluación: etiquetas, ranuras aceptadas y valores/resoluciones pertinentes.

### Salida lógica de TRAITS

- Lista canónica de aportaciones individuales con `source_trait`, `source_entity`, `rule_id`, `slot`, `amount` y motivación de aplicabilidad.
- Totales por ranura, más diagnósticos tipados para entradas inválidas o incompatibles.
- Ningún hecho, cambio de estado, elección, acción ni RNG consumido.

El adaptador de GISELA valida la salida de TRAITS contra el perfil, resuelve los atributos opcionales de S.O.F.I.A. y construye la solicitud neutral de DICE. Cuando la tirada es visible, todas las entradas y aportaciones **quedan fijadas durante la preparación**; no se recalculan contra un mundo cambiado al momento de confirmar efectos. Las trazas internas deben permitir auditoría sin revelar rasgos secretos al cliente `Observe`.

Asignar o retirar rasgos en juego sería una operación declarativa de ALBERTO/GISELA que modifica el borrador y se confirma de forma atómica. Una simple consulta TRAITS **no** crea turno, transacción ni actualización de revisión.

## 8. Ejemplo neutral ilustrativo (no ejecutable en v1.2)

Un juego de exploración define `fragile` para objetos y un perfil de evaluación que admite la ranura `handling_difficulty`. Un objeto porta el rasgo. Cuando el contexto de una acción contiene las etiquetas `physical` y `handling`, TRAITS aporta `+2` a esa ranura; cuando el objeto se inspecciona sin manipularlo, el rasgo no modifica la evaluación. El perfil del juego decide qué significa una dificultad dos puntos mayor.

Otro juego podría definir un rasgo `methodical` que contribuya a una prueba técnica, sin depender de los nombres de S.O.F.I.A. ni de las reglas del primer juego. Es el autor, no TRAITS, quien decide qué comportamiento resulta narrativamente apropiado.

Ejemplo de **esquema conceptual**, sujeto a aprobación antes de producir JSON Schemas:

```json
{
  "trait": "fragile",
  "entity_kinds": ["object"],
  "contributions": [
    {
      "id": "handling",
      "when": {"role": "target", "all_tags": ["physical", "handling"]},
      "add": {"slot": "handling_difficulty", "amount": 2}
    }
  ]
}
```

Este objeto **no es válido para los esquemas actuales**; nombres como `all_tags`, `role` y `add.slot` son candidatos de contrato y no interfaces implementadas.

## 9. Matriz de pruebas propuesta

| ID | Caso | Resultado esperado |
| --- | --- | --- |
| T01 | Juego sin configuración de límite | Capacidad predeterminada de 5. |
| T02 | Entidad con cero rasgos | Válida; ninguna contribución. |
| T03 | Entidad con cinco asignados y otro no pertinente | No admite un sexto; la pertinencia no libera capacidad. |
| T04 | Nueva asignación excede capacidad | Rechazo atómico; estado y revisión sin cambios. |
| T05 | Mismo ID duplicado | No se apila ni aumenta el número de rasgos; política de operación explícita. |
| T06 | Rasgos A y B con exclusión unilateral declarada | Rechazo simétrico al asignar el segundo. |
| T07 | Rasgos `brave` y `prudent` sin exclusión | Pueden coexistir; aportaciones según contexto. |
| T08 | Dos aportaciones de +2 y -1 a una misma ranura | Total +1; independiente del orden de datos. |
| T09 | Rasgo pertinente solo para `handling` | No modifica una evaluación de `inspection`. |
| T10 | Evaluación repetida del mismo contexto | Mismo total, sin cambios de estado ni RNG. |
| T11 | Personaje sin S.O.F.I.A. con rasgos | TRAITS funciona con valores neutrales. |
| T12 | Restauración con rasgo ganado o retirado | Asignación reconstruida sin pérdida o reaparición incorrecta. |
| T13 | Resultado de NPC con rasgos privados | Se usa internamente; `Observe` no los revela. |
| T14 | Evaluación visible fijada y confirmada después | No se recalculan aportaciones al aplicar consecuencias. |
| T15 | Perfil que no admite la ranura modificada | Error de contrato; sin modificación tácita. |
| T16 | Asignación y otra operación posterior que falla | Rollback total; no persiste el rasgo ni su coste de capacidad. |

Estas pruebas son **requisitos propuestos**, no pruebas ejecutables añadidas en este documento.

## 10. Decisiones y asuntos abiertos

**DECIDIDO:** GISELA es un motor general; los subsistemas deben ser reutilizables; cada juego puede fijar el máximo de rasgos por entidad, con valor predeterminado **5**; GISELA conserva la autoridad transaccional; los resultados visibles de DICE pueden fijarse antes de sus efectos.

**PROPUESTO:** rasgos cualitativos declarativos; almacenamiento de asignaciones por ALBERTO; conteo de asignados independientemente de pertinencia; v1 de aportaciones aditivas y consultas de presencia; exclusiones explícitas, simétricas y sin prioridades ocultas; evaluador TRAITS puro; entradas resueltas antes de DICE.

**ABIERTO:** capacidades compatibles por clase de entidad; representación exacta de deltas de asignación en snapshots; campo definitivo del manifiesto; límite superior técnico de capacidad; rasgos suspendidos; presupuesto de reglas/etiquetas; operador `has_trait` y operaciones de asignación/retiro; políticas públicas de exposición; convenciones de errores; versionado de esquemas.

**Siguiente etapa recomendada:** revisar el modelo de almacenamiento de rasgos en ALBERTO y aprobar las reglas de composición antes de fijar los JSON Schemas. Solo después implementar un evaluador TRAITS independiente, probarlo con ejemplos neutrales y utilizarlo como proveedor del adaptador de DICE.
