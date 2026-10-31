# DICE: Contrato declarativo de evaluación (propuesta)

**Proyecto:** GISELA, motor narrativo de propósito general
**Fecha:** 30 de octubre de 2026
**Estado de este documento histórico:** propuesta original. **Actualización E1:** los contratos `evaluate` de autoría ya están admitidos y normalizados en v1.4 (ADR-021), pero aún no se ejecutan; no hay presentación visible ni ramas aplicadas por GISELA.
**Relación:** ADR-007/008, ADR-012-014, ADR-019 (revisión 2), `DICE_CONTRATO_API_SESION_PROPUESTA.md`.

## 1. Alcance y constataciones del código

Este documento propone la **unidad declarativa de evaluación** necesaria para que un juego describa una acción incierta sin implementar lógica en Python, Ren'Py o GLAUQUIR. No incorpora decisiones particulares de *Las personas tienen nombre*.

En el contrato v1.2 actual:

- `node.schema.json` conoce los pasos `narrate`, `dialogue`, `choice`, `condition`, `effect`, `scene`, `transition`, `ending`, `prepare_hand`, `skill_window` y `random`. **No existe `evaluate`.**
- `common.schema.json` define `choice_option` y `action` con `effects` y `next`; **no existe una evaluación declarativa** en esas entradas.
- `common.schema.json#/$defs/value` ya permite constantes, variables, `stat` con `component: effective`, relaciones, propiedades, reloj y turno. Esta gramática puede servir al **adaptador de GISELA**; no obliga a DICE a conocerla.
- `runtime._run_automatic()` atraviesa efectos, condiciones y transiciones dentro de la misma operación; por eso introducir un `roll` visible entre efectos produciría confirmaciones parciales. El `roll` existente en `consequences.py` es una operación **oculta, atómica y con destino variable**.
- Las acciones de escena (`_source_scene`) y las opciones (`_source_choice`) ejecutan primero sus `effects` y luego sus transiciones. Un resultado visible exige un camino de ejecución alternativo, no interceptar `roll`.

El validador semántico, la admisión y `support.py` deben evolucionar juntos con los JSON Schemas. **Este archivo no modifica el contrato público v1.2.**

## 2. Decisión de diseño propuesta: evaluación como recurso declarativo

Una evaluación debe declarar, como mínimo:

| Campo conceptual | Responsabilidad |
|---|---|
| `id` | Identidad estable dentro de su origen. |
| `profile` | Perfil de resolución versionado definido o seleccionado por el juego. |
| `presentation` | Política: `hidden`, `visible` o `acknowledged`. |
| `inputs` | Parámetros nominales; pueden proceder de constantes, atributos u otros valores autorizados. |
| `context` | Etiquetas y entidades pertinentes para seleccionar aportaciones de TRAITS; **no es un guion de reacciones**. |
| `branches` | Correspondencia explícita entre **cada resultado posible del perfil** y las consecuencias/continuación autorizadas. |

Una evaluación **no incorpora un programa o fórmula de Python del autor**. El perfil determina los mecanismos matemáticos y la interpretación de resultados mediante un vocabulario de reglas validado y versionado.

**Separación de capas:**

1. GISELA autoriza la acción y resuelve referencias del mundo con ALBERTO y S.O.F.I.A. cuando estén presentes.
2. TRAITS (opcional) propone contribuciones aplicables al contexto declarado y su propia política de composición; GISELA valida las contribuciones y las transforma en valores de entrada neutrales.
3. DICE recibe números, identificadores de perfil, modificadores y un RNG inyectado (si procede); devuelve un resultado inmutable y trazable. **DICE no consulta directamente S.O.F.I.A., TRAITS, ALBERTO ni MARY.**
4. GISELA selecciona la rama asociada al resultado, y aplica sus operaciones y reacciones; MARY evalúa los acontecimientos pertinentes a través del ciclo causal existente.

Los atributos de S.O.F.I.A. **no determinan por sí solos** el tipo de dado, su escala o su probabilidad: esas transformaciones pertenecen al perfil del juego. TRAITS tampoco implica automáticamente una modificación numérica; su pertinencia se resuelve mediante reglas declaradas por el juego.

## 3. Tres orígenes, un contrato compartido

Se propone **un solo objeto `evaluation`** con tres lugares de uso, sin crear tres motores distintos:

| Origen | Forma candidata | Semántica |
|---|---|---|
| Paso de nodo | `step.op = "evaluate"` y `step.evaluation` | **Paso observable**; `Observe` ofrece la acción de evaluar. No se ejecuta automáticamente al pasar sobre él. |
| Opción de elección | `choice_option.evaluation` | Al elegir la opción se prepara la evaluación, en lugar de aplicar `effects` o `next` inmediatamente. |
| Acción de escena | `action.evaluation` | Al interactuar se prepara la evaluación, en lugar de aplicar `effects` o `next` inmediatamente. |

La evaluación autónoma como paso observable permite resolver pruebas obligatorias sin saltarse las fronteras causales. El motor actual deberá tratar `evaluate` como un nuevo tipo de paso observable y ofrecer su acción mediante `Observe`.

**Restricción v1 propuesta:** cada origen declara **`evaluation` O BIEN `effects`/`next` inmediatos**, nunca ambos. Las ramas de `evaluation` contienen sus propios efectos y destinos. Si se necesitan hechos previos a la tirada, deben producirse en una transacción anterior, ya confirmada. En un origen de evaluación no se registra de forma anticipada ni siquiera el historial de elección o interacción: el registro causal correspondiente se realiza cuando se aplican las consecuencias, no durante la preparación de dados.

Esto impide ejecutar efectos antes de mostrar una tirada visible y evita que una sesión quede con hechos narrativos confirmados a medias.

En v1 no se admiten evaluaciones visibles en `node_completed`, `turn_ended` o `turn_started` durante una transición A→B; tampoco en `on_apply`/`on_expire`, efectos automáticos o el cuerpo de una reacción. Los resultados ocultos podrán seguir resolviéndose en una única transacción, sujetos al contrato de su mecanismo. Más adelante se puede estudiar el uso de evaluaciones por habilidades sin cambiar la interfaz neutral de DICE.

## 4. Resultado y ramificación

- Cada perfil expone un conjunto finito de **identificadores de resultado**. No exige categorías universales `success`/`failure` ni una escala de afecto.
- La evaluación debe contemplar **exactamente una rama por identificador alcanzable**, sin ambigüedades ni prioridades ocultas. Se rechazan ramas duplicadas y resultados sin rama.
- Cada rama puede tener `effects` (posiblemente vacío) y `next` (opcional, según el origen). Las condiciones que decidan aplicar efectos adicionales se evalúan conforme a la causalidad de GISELA, no mediante tiradas secretas adicionales.
- Las ramas pueden registrar hechos o cambios en ALBERTO y activar MARY como cualquier operación de GISELA. La definición de DICE no almacena progreso de misión.
- Si el perfil es determinista, `dice` puede estar vacío y no se consume RNG. La política de presentación sigue pudiendo mostrar el **resultado de una evaluación** sin representar dados inexistentes.

### Ejemplo de autoría (JSON **ilustrativo, no válido en v1.2**)

El ejemplo describe una reparación técnica y utiliza una constante para no hacer depender DICE de S.O.F.I.A. ni de TRAITS:

```json
{
  "id": "check_repair",
  "op": "evaluate",
  "evaluation": {
    "id": "repair_machine",
    "profile": "two_dice_test.v1",
    "presentation": "acknowledged",
    "inputs": {"base": {"literal": 3}},
    "context": {"tags": ["technical", "repair"]},
    "branches": [
      {"outcome": "complete", "effects": [{"op": "record_fact", "fact": "repair_completed"}]},
      {"outcome": "limited", "effects": [{"op": "record_fact", "fact": "repair_partial"}]},
      {"outcome": "blocked", "effects": []}
    ]
  }
}
```

Las categorías `complete`, `limited`, `blocked` y el perfil `two_dice_test.v1` son **ejemplos inventados**; no se han registrado en ningún perfil real. En un paquete ejecutable, los hechos deben declararse en el vocabulario del juego y el perfil debe existir y haber pasado validación.

Una ficha S.O.F.I.A. podría sustituir `{"literal": 3}` por una referencia de `value` como `{"stat": {"character": "technician", "name": "intelligence", "component": "effective"}}`. Esta referencia la interpreta el adaptador de GISELA. No se transmite a DICE como referencia de personaje.

## 5. Preparación, presentación y aplicación

**Preparación:** el `Act` autorizado sobre el origen valida que el perfil existe y que los parámetros exigidos están disponibles y dentro de rango; determina las contribuciones aplicables, evalúa DICE y fija el resultado junto al RNG. No ejecuta las ramas, no avanza el tiempo ni abre/cierra otro turno.

**Presentación:** en `visible` y `acknowledged`, `Observe` proyecta únicamente los datos autorizados del resultado inmutable. El cliente presenta dados, números y resultado sin ejecutarlos. En `hidden` GISELA prepara y aplica en la **misma transacción**, sin publicar un pendiente.

**Aplicación:** una continuación autorizada usa el resultado fijado y la rama prevalidada; se registran entonces la elección/interacción, hechos, eventos, reacciones y progresión de MARY. Si falla la transacción, la evaluación pendiente permanece fijada y sus efectos no se aplican parcialmente.

**Principio esencial:** durante la preparación de una evaluación visible solo cambian el **estado interno de evaluación, el contador RNG y la revisión de sesión**. No se publican selecciones ni trazas narrativas antes de aplicar. Esta precisión complementa ADR-019 y evita que la fase de preparación anticipe consecuencias.

## 6. Visibilidad, seguridad y restauración

- Los valores individuales de los dados seleccionados para presentación son públicos; no se filtra por accidente la puntuación efectiva de un NPC, su lista de rasgos, condiciones ocultas, semillas o huellas privadas.
- Un `total` calculado sobre datos secretos no puede publicarse automáticamente si permite deducirlos. La política de exposición del perfil debe declarar qué sumandos y qué resultado agregado son públicos.
- Las entradas efectivas y contribuciones que decidieron la evaluación se conservan internamente en forma validable; no se recalculan desde un estado cambiado después de publicar los dados.
- La solicitud se asocia a la versión del paquete y del perfil; no se reinterpreta con reglas nuevas durante una restauración.
- Se debe impedir un segundo pendiente y rechazar acciones causales ajenas mientras exista una evaluación visible sin aplicar. `cancel_pending` no elimina una tirada fijada.
- Una repetición autorizada constituye una operación nueva, trazable y enlazada al resultado original. Una restauración o un reintento técnico nunca es una nueva tirada.

## 7. Reglas de admisión semántica (propuestas)

1. Perfil y versión existen, están soportados y sus parámetros tienen tipos/rangos adecuados.
2. Entradas referenciadas existen, son resolubles por el anfitrión y compatibles con el perfil; se rechaza la ausencia de S.O.F.I.A./TRAITS si una entrada **concreta** los exige, pero DICE funciona sin esos subsistemas cuando no los necesita.
3. Los identificadores de resultado del perfil y las ramas declaradas coinciden exactamente.
4. Las operaciones de las ramas cumplen el contrato causal y los destinos existen, con validación de referencias cruzadas.
5. Ningún origen contiene simultáneamente `evaluation` y efectos/transición inmediatos; tampoco los introduce indirectamente mediante automatismos ejecutados en el mismo `Act` de preparación.
6. El paso `evaluate` está disponible solo como paso observable, no se ejecuta dentro de `_run_automatic`.
7. Se rechazan evaluaciones visibles en reacciones automáticas y en fronteras de cierre/inicio atómicas de nodos.
8. El número máximo de dados, modificadores y ramificaciones es finito y se valida como presupuesto de contrato antes de ejecutar, sin fijar todavía aquí sus límites numéricos.
9. La configuración del perfil y las aportaciones de TRAITS se componen de modo determinista y sin depender del orden físico de archivos o diccionarios.

## 8. Matriz de pruebas de aceptación pendiente

| ID | Caso | Resultado esperado |
|---|---|---|
| E01 | Paso `evaluate` observable | `Observe` ofrece evaluación; no se lanza automáticamente. |
| E02 | Elección o acción de escena con `evaluation` | No confirma elección ni traza antes de aplicar. |
| E03 | Origen con `evaluation` y `effects`/`next` | Paquete rechazado en admisión. |
| E04 | Efectos automáticos antes de preparar tirada visible | No existe commit parcial previo dentro de la misma acción. |
| E05 | Perfil con tres resultados y solo dos ramas | Paquete rechazado. |
| E06 | Perfil con resultados repetidos | Paquete rechazado. |
| E07 | Perfil determinista y política visible | Sin consumo RNG y proyección válida sin dados. |
| E08 | Perfil aleatorio oculto | Un solo commit de efectos y RNG, rollback completo ante error. |
| E09 | Perfil visible y restauración | Mismos dados y misma rama; sin volver a ejecutar DICE. |
| E10 | S.O.F.I.A./TRAITS ausentes, entradas literales | Evaluación válida y reutilizable en otros juegos. |
| E11 | Atributos o rasgos privados de NPC | Se utilizan internamente sin filtrarse en `Observe`. |
| E12 | Evaluación visible en `turn_ended` | Paquete rechazado; se conserva transición A→B atómica. |
| E13 | Aplicación duplicada | Se registra y ejecuta una sola vez. |
| E14 | Falla al ejecutar una rama | Rollback de efectos, pendiente fijado disponible para reintento técnico. |

## 9. Aprobaciones y pendientes

**DECIDIDO previamente:** motor general, submódulos desacoplados, GISELA como autoridad de confirmación, RNG reproducible, tiradas visibles antes de efectos, resultado revelado comprometido por defecto, y transición atómica de nodos.

**IMPLEMENTADO en E1/ADR-021 (admisión, no ejecución):** objeto `evaluation` único, tres orígenes declarativos, sintaxis v1.4, exclusión de efectos inmediatos, ramificaciones exhaustivas y normalización de perfiles. **PENDIENTE en E2-E4:** ejecución de pasos observables y efectos, historial causal y tiradas visibles.

**ABIERTO:** forma final y versionado del perfil matemático, sintaxis definitiva, presupuesto de complejidad, contratos específicos de aportaciones TRAITS, ajustes a habilidades, forma de migración de sesiones y granularidad exacta de los datos públicos de cada evaluación.

**Actualización:** `node.schema.json` y `common.schema.json` v1.4 ya incluyen este contrato. El ejemplo sigue siendo ilustrativo e incompleto como paquete; el motor permanece cerrado a v1.4 hasta E2.

## Reconciliación E0 con el adaptador TRAITS-DICE (diseño de E1/v1.4)

La muestra original `inputs.ability` fue sustituida por `inputs.base` en E1. El normalizador implementado en `evaluation_plan.py` realiza esta transformación estática sin leer estado:

| Autoría (propuesta) | Entrada neutral interna del puente existente |
|---|---|
| `evaluation.profile` por ID | `spec.profile` materializado desde el catálogo admitido, compilado por DICE |
| `evaluation.inputs.base` | `spec.base` entero literal o `spec.stat` como referencia de S.O.F.I.A. a resolver en E2 |
| `evaluation.context.tags` | `spec.tags` ordenado y validado |
| Actor narrativo / objetivo expresamente declarados | `spec.participants` con `entity` + `role`; jamás deducidos del solicitante de `Act` |
| Dificultad del autor y entrada S.O.F.I.A. opcional | `spec.difficulty` y `spec.stat` para lectura efectiva; alternativas sin S.O.F.I.A. deben seguir válidas |
| `evaluation.branches` | Interpretación y efectos en GISELA **después** de obtener `dice.outcome`; no pertenece a DICE |

E1 verifica perfiles, límites autorales, IDs y ramas en admisión; la lectura de atributos efectivos y los presupuestos de la suma compuesta se comprobarán en E2 antes del sorteo. `traits_dice_bridge.resolve()` no cambia en E1 y mantiene la autoría de GISELA sobre el RNG. Véase ADR-021.
