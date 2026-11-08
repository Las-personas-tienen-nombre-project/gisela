# Taller de presentación: tablas, causalidad y plantillas v0.8.2

Esta guía reúne las capacidades implementadas hasta v0.8.2f en el DSL 1.5:
tablas, selección de acontecimientos, agrupación causal y plantillas restringidas.
Los resultados de cada entrega y sus límites se conservan en los
[informes v0.8.2](../../../../CHANGELOG.md) y
[v0.8.2f](../../../../CHANGELOG.md). Ejecute los comandos desde la raíz
del repositorio. La presencia de una capacidad no certifica todas las rutas del encuentro.

Dentro de `presentation`, añadir `views` y declarar regiones con `view`:

```json
{
  "id": "presentacion_demo",
  "views": [
    {
      "id": "estado", "component": "table",
      "source": "actuation.resources", "transform": "pivot_resources",
      "columns": [
        {"id": "entity", "label": "PERSONA"},
        {"id": "hp", "label": "HP", "align": "right"},
        {"id": "mp", "label": "MP", "align": "right"},
        {"id": "tp", "label": "TP", "align": "right"}
      ]
    },
    {
      "id": "hechos", "component": "event_log",
      "source": "actuation.causal", "kinds": ["skill_started", "variable_changed"],
      "limit": 8
    }
  ],
  "regions": [
    {"id": "tabla", "component": "table", "label": "Estado", "view": "estado"},
    {"id": "registro", "component": "event_log", "label": "Hechos", "view": "hechos"},
    {"id": "actuar", "component": "choice_list", "source": "actions"}
  ]
}
```

La tabla no interpreta HP/MP/TP, solamente los ids publicados. Un paquete no
bélico puede usar la misma fuente de recursos con nombres diferentes o una tabla
sobre `actuation.effects` con columnas `beneficiary` y `remaining`.
Sin `group_by`, la crónica es plana. No presuponga que acontecimientos consecutivos
provienen de la misma acción. Las decisiones se siguen enviando mediante Act.

## v0.8.2c: Agrupar acontecimientos de una acción

En una vista de tipo `event_log` con fuente `actuation.causal` agregue:

```json
{
  "id": "cronica_causal",
  "component": "event_log",
  "source": "actuation.causal",
  "group_by": "action",
  "kinds": ["skill_started", "dice_roll", "contest_resolved", "variable_changed", "author_message", "skill_played"],
  "limit": 40
}
```

Luego cree una región `event_log` cuyo `view` sea `cronica_causal`.
Consulte el paquete reproducible
`packages/tegularis_the_son_of_the_volcan/13_tablas_causal_v082c.package.json`.
No es necesario editar código Python. El motor vincula exclusivamente registros
con el mismo `causal_execution_id` público y cuyo inicio aparece en la ventana.
Si se omite `group_by`, la lista sigue siendo plana. No presuponga que `limit`
representa todo el historial: Observe publica un máximo de 40 entradas.

## v0.8.2c y v0.8.2d: causalidad, formatos y roles

Una vista `event_log` puede añadir `group_by: "action"` si desea agrupar por la
identidad de ejecución publicada, y un catálogo de formatos autorales seguros:

```json
{
  "id": "hechos", "component": "event_log", "source": "actuation.causal",
  "group_by": "action", "limit": 20,
  "event_formats": [
    {"kind": "skill_started", "role": "neutral", "template": "{actor} ejecuta {card}"},
    {"kind": "dice_roll", "role": "neutral", "template": "Dado d{sides}: {result}"},
    {"kind": "variable_changed", "role": "neutral", "template": "{variable}: {before} -> {after}"},
    {"kind": "author_message", "role": "neutral", "template": "{text}"}
  ]
}
```

Copie la vista anterior en `presentation.views` de un paquete y mantenga una región
`{"id":"cronica","component":"event_log","view":"hechos"}`. No hace falta
modificar Python. Ejemplo completo admitido:
`packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`.

Una segunda experiencia no bélica puede publicar `event_triggered` y
`author_message` y declarar respectivamente `"Inspección: {event}"` y `"{text}"`.
Ambas usan la misma primitiva. El código no consulta el significado del nombre
de la experiencia ni de sus variables.

Para una categoría específica puede declararse `role: "buff"`, `"debuff"`,
`"damage"` o `"healing"`, pero solo cuando la clasificación autoral sea válida
para **todos** los registros que satisfacen el selector. Usar el filtro opcional
`variable` no prueba que una disminución sea daño: no atribuya semántica causal
que la operación confirmada no haya expresado. En caso de duda, `neutral`.

Para valores ausentes, `"missing":"omit"` deja el texto heredado o
`"missing":"placeholder"` produce `-`. Las llaves literales se escriben `{{` y
`}}`; rutas privadas, expresiones, índices y formatos ejecutables son rechazados.
GLAUQUIR mantiene etiquetas legibles con `--color never`.

## Verificación de entrega v0.8.2f

Para comprobar que la presentación no afecta al motor, ejecute las pruebas
`gisela/engine/tests/test_release_v082e.py` y `test_release_v082f.py`.
La nueva suite contrasta dos semillas, decisiones autorizadas, snapshots,
RNG y restauración. Para una tabla no bélica, las pruebas muestran la fuente
pública `actuation.effects`, con columnas autorales `beneficiary` y `remaining`,
y un registro `actuation.causal` con plantillas validadas. La tabla y las
plantillas se proyectan sin modificar Observe ni las reglas.

Para verificar distribución, construya la wheel e instálela con dependencias
en un entorno virtual nuevo. Ejecute ambas CLI desde un directorio ajeno al
repositorio; no basta con hacer `pip install --no-deps` o incorporar las
dependencias del entorno de desarrollo.
