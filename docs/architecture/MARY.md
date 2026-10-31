# MARY: diseño e integración v1

MARY significa **Mission Assignment, Resolution and Yield**. Es una biblioteca opcional para asignar, evaluar y resolver objetivos declarativos y misiones. Está diseñada para funcionar dentro o fuera de GISELA.

## 1. Responsabilidades

- El **autor** define objetivos, misiones, visibilidad, umbrales y resultados.
- El **anfitrión** aporta hechos y valores mediante un contexto neutral. En nuestra integración, ese anfitrión es GISELA.
- **MARY** verifica requisitos, calcula el progreso propuesto y devuelve las transiciones y sus `yields`.
- **GISELA** valida y ejecuta los efectos derivados en el mismo borrador de su transacción. Solo GISELA confirma.
- **ALBERTO** conserva la autoridad sobre entidades y mundo; S.O.F.I.A. calcula atributos. No importan MARY ni tienen que saber qué es una misión.
- **GLAUQUIR** y Ren'Py presentan únicamente la proyección pública. La consola permite `misiones` y `quests`.

MARY no importa GISELA, ALBERTO, S.O.F.I.A. ni sus contratos. El lenguaje lógico `narrative_conditions` tampoco depende de ninguno de ellos.

## 2. Acontecimiento, objetivo y misión

Un **acontecimiento** es un hecho ocurrido: `inspecciono_radio`, `conocio_gisela`, etc. No tiene que pertenecer a ninguna misión.

Un **objetivo** define qué debe cumplirse: registrar un hecho, reconocer al menos dos experiencias distintas o alcanzar un umbral ponderado. Puede permanecer oculto.

Una **misión** agrupa uno o más objetivos mediante `all` o `any`. Su ciclo v1 es `inactive`, `active`, `completed` o `failed`. Se reserva `abandoned` para interoperabilidad con futuros anfitriones; v1 no implementa un comando para abandonar misiones.

Una historia puede omitir completamente MARY. Un objetivo oculto no debe convertirse en una tarea visible para el jugador.

## 3. Dos modelos de progreso: qué hacen y por qué existen

### `mode: milestone`: hito persistente

Una vez que su requisito se cumple, el objetivo conserva `true`, incluso si el mundo cambia después. Representa una experiencia vivida o una tarea terminada, no la condición momentánea del inventario. Puede emitir un `yield` una sola vez.

Ejemplo: Alberto ha tenido dos experiencias significativas diferentes con Gisela. Una conversación posterior no borra esas experiencias.

### `mode: current`: condición reversible

MARY recalcula `true` o `false` a partir del contexto actual. No concede `yield`, porque una condición reversible no debe repetir recompensas cada vez que oscila.

Ejemplo: Alberto tiene una linterna. Si la entrega, deja de cumplirse ese requisito. Puede contribuir al cumplimiento de una misión, pero no es en sí mismo un recuerdo permanente.

**Importante:** una misión que llega a `completed` permanece completada aunque uno de sus objetivos `current` deje de cumplirse después. Para representar una obligación continua, el autor debe usar condiciones consultables y no tratar una misión terminal como un monitor permanente.

## 4. Formas de completar un objetivo

- `condition`: un predicado puro (`has_fact`, comparación de un valor publicado, `constant`, `all`, `any`, `not`).
- `distinct`: al menos N hechos distintos de una lista. Registrar dos veces el mismo hecho cuenta una sola vez.
- `weighted`: suma de pesos de hechos distintos. La repetición de un hecho no vuelve a sumar.

Estos dos últimos son una generalización limitada del «alambique» usado por Aureus Gaj en *Roadwarden*: distintos aportes pueden llegar a un mismo resultado sin multiplicar ramas argumentales. Los umbrales no pueden superar el máximo declarable y se validan al compilar.

## 5. Ejemplo declarativo

```json
{
  "objectives": [
    {
      "id": "reconocimiento_gisela",
      "mode": "milestone",
      "visibility": "hidden",
      "criterion": {
        "kind": "distinct",
        "facts": ["experiencia_pasillo", "experiencia_puesto_b", "experiencia_ascensor"],
        "minimum": 2
      },
      "yield": {"fact": "rostro_gisela_reconocido"}
    }
  ],
  "missions": []
}
```

Esta definición es un **ejemplo de capacidad**, no el catálogo narrativo aprobado para la demo. Los hechos y el `yield` deben estar declarados en el manifiesto de GISELA cuando se integre en un paquete. La biblioteca independiente no conoce ese manifiesto.

El schema es `mary/schemas/definitions.schema.json`; el paquete GISELA admite la sección opcional `mary`. No se modifica la semántica de los paquetes v1.2 que la omitan.

## 6. API independiente

```python
from mary import compile_plan, initial_progress, evaluate, public_quests

plan = compile_plan(definitions)
progress = initial_progress(plan)
result = evaluate(plan, {"facts": ["experiencia_pasillo"], "values": {}}, progress)
progress_propuesto = result["progress"]
transiciones = result["transitions"]
resultados_propuestos = result["yields"]
```

`compile_plan` valida y copia la definición. `evaluate` no modifica `definitions`, `context` ni `progress`; devuelve nuevas estructuras JSON serializables. `public_quests` excluye los objetivos ocultos. Otro motor puede suministrar su propio contexto y decidir si confirma los resultados.

El anfitrión debe conservar el progreso que **decida confirmar**; MARY nunca lo guarda por su cuenta. Un guardado GISELA contiene `mary` dentro de la sesión confirmada y está vinculado al digest del paquete.

## 7. Conexión con GISELA y las reacciones

El adaptador `gisela/engine/mary_bridge.py` transforma hechos de `history.facts` y variables `session.*` y `world.*` en el contexto neutral de MARY. No entrega referencias mutables a ALBERTO.

En el ciclo `settle`, GISELA evalúa MARY después de los efectos de las reglas de la ronda; luego convierte únicamente `yield: {"fact": "..."}` en `record_fact` dentro del **mismo borrador**. Los hechos producidos pueden alimentar la siguiente ronda de reacciones. La confirmación, el límite de 32 rondas, el rechazo de conflictos y el rollback siguen siendo responsabilidad exclusiva de GISELA.

Un yield es una **propuesta de resultado**, no una orden ejecutada por MARY. Si el anfitrión rechaza la transacción, no se conserva ni el progreso ni el yield. Un hecho ya registrado no vuelve a publicarse por el adaptador.

La admisión comprueba las referencias a hechos y a variables del anfitrión. GISELA no acepta accesos arbitrarios a propiedades o relaciones mediante MARY v1; de ser necesarios, deberán exponerse mediante un contrato de lectura explícito y autorizado.

## 8. Visibilidad

Un objetivo o misión sin `visibility: public` es oculto. `Observe.quests` enumera solo misiones públicas y, dentro de estas, solo objetivos públicos. Los IDs y títulos de objetivos ocultos nunca se envían por esa proyección. Un estado de misión pública puede revelar indirectamente que se cumplió algo oculto; el autor debe elegirlo conscientemente.

Mientras existe una transacción pendiente, `Observe` no publica la lista de misiones para evitar representar resultados provisionales.

## 9. Alcance y límites v1

- `scope: session` o `campaign` se conserva como intención de autoría, pero todavía **no existe** un reinicio selectivo por jornada ni una transferencia por password. No debe suponerse que estén implementados.
- La biblioteca no calcula por sí sola si queda alguna ruta futura para completar una misión. El autor usa condiciones de activación o fracaso cuando corresponda.
- Una misión terminada no se reabre en v1. `abandoned` es interoperabilidad prevista, no una acción jugable disponible.
- El evaluador recorre los objetivos declarados al llegar a cada frontera causal; el límite de 256 objetivos y 128 misiones es explícito. Un índice incremental de dependencias solo se justificará con medidas de rendimiento.
- El progreso guardado tiene validación de estructura y de IDs; como los demás guardados JSON de GISELA, no incorpora una firma criptográfica antimanipulación.
- Solo se ofrecen yields de hechos declarados. Recompensas de inventario, escenas u otras operaciones requerirán una capacidad futura, con validación y resolución de conflictos explícitas.

## 10. Referencias de diseño

- Aureus Gaj, *Deep Dive: How to Design for Impact and Narrative Variance with Roadwarden*, Game Developer: acumulación, variación y coste de las dependencias cruzadas.
- Evennia, sistema de quests y comandos extensibles: misiones opcionales, etapas y persistencia.
- Yarn Spinner, separación de runtime, variables y presentadores: independencia de los clientes.

Las referencias informan el diseño; los formatos, los comportamientos y los límites anteriores son decisiones propias de GISELA/MARY.

## 11. Integridad de un repositorio ya instalado

Después de aplicar MARY sobre H4.5f, ejecutar `python tools/update_manifest.py` antes de verificar el manifiesto. La utilidad conserva todas las rutas que ya existen en el manifiesto del proyecto, vuelve a calcular sus hashes y añade solo las rutas nuevas de MARY. Se detiene si falta un archivo o encuentra rutas duplicadas. No es un actualizador genérico ni elimina archivos ajenos al hito.
