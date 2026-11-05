# GISELA v0.8.2: presentación declarativa

**Estado:** capacidades implementadas hasta v0.8.2f sobre el DSL 1.5.
Este documento describe el contrato actual. Los resultados y límites de cada
entrega están en los [informes v0.8.2](../operatives/RESULTADOS_V082.md) y
[v0.8.2f](../operatives/RESULTADOS_V082F.md). La
[guía práctica](../guides/workshops/WORKSHOP_PRESENTACION_V082.md) muestra ejemplos.

## Vistas, tablas y selección de acontecimientos

`presentation.views` es opcional y contiene hasta 32 vistas con identificador. Una región puede
referenciar una vista con `view`, manteniendo regiones heredadas con `source`.
Las vistas son configuraciones cerradas y los datos proceden de Observe.

- `table`: `source` admite una fuente pública (`actuation.resources`, `actuation.participants`,
  `actuation.effects`, `actors`), `columns` de 1 a 12 pares `id`/`label` y `align`.
  Transformación opcional `pivot_resources` únicamente sobre `actuation.resources`.
  Límite de 1 a 64 registros; ausencias indicadas mediante `missing`.
- `event_log`: solo `actuation.causal`, selección opcional `kinds`, filtro opcional
  por `kind` o `source`, y límite entre 1 y 64. El límite se aplica a los últimos N
  seleccionados, conservando el orden de publicación.

Validación: JSON Schema para estructura y cotas; validación semántica para fuentes,
columnas permitidas y referencias entre vistas y regiones. Proyección pura con
copias defensivas. El cliente recibe filas, encabezados y registros seleccionados.

## Ventana pública y compatibilidad

La ventana causal pública existente permanece limitada a los últimos 40 registros,
por lo que un filtro solo puede seleccionar acontecimientos presentes en esa ventana.
La agrupación utiliza la identidad causal publicada; no atribuye resultados por
proximidad ni interpreta diferencias de HP como daño. Los filtros y límites de una
vista pueden reducir todavía más esa ventana. No hay paginación del historial completo.

Los componentes existentes y paquetes sin `presentation.views` conservan sus
contratos, sin migración. No se han modificado cartas, balance ni políticas NPC.

## Agrupación causal

El contrato opcional `causal_execution_id` existe en los registros públicos confirmados.
`event_log` admite `group_by: action`, únicamente cuando el inicio de la ejecución
está presente en la ventana pública; de lo contrario permanece plano. La identidad
se conserva al guardar y restaurar. Consulte la
[descripción de identidad causal](CORRELACION_CAUSAL_V082C.md) para el alcance
de la propagación y el tratamiento de habilidades anidadas.

## Plantillas y roles de presentación

`presentation.views[].event_formats` es una lista opcional (máximo 32) admitida
exclusivamente en vistas `event_log`. Cada elemento incluye `kind` público y puede
incluir `variable` para precisar un registro `variable_changed`, `role`, `template`
y `missing`. Las combinaciones `(kind, variable)` no pueden repetirse.

Los roles son `damage`, `healing`, `buff`, `debuff`, `neutral`; la proyección publica
`semantic_role` y, cuando puede sustituir una plantilla, `display_text`. Este DTO
se calcula únicamente sobre **registros públicos confirmados** de Observe, nunca
sobre estado privado ni textos narrativos interpretados. El tema asigna los roles
a colores mediante la instancia existente de `Styler` en GLAUQUIR. Cada etiqueta
va acompañada de su equivalente textual (Daño, Curación, Beneficio, Perjuicio,
Acontecimiento); `--color never` conserva el contenido textual.

La sintaxis solo admite sustituciones `{field}` de campos públicos específicos de
cada `kind`, más `{{` y `}}` para llaves literales. Quedan prohibidos atributos,
índices, conversiones y formatos de Python. Los nombres se verifican al admitir
el paquete; los campos ausentes tienen política `omit` (volver al render anterior)
o `placeholder` (reemplazar con `-`). Máximo 1000 caracteres de plantilla,
16 sustituciones, celdas interpoladas acotadas a 160 caracteres y resultado a
1000; caracteres de control ANSI se eliminan. Los textos originales no se mutan.

**Límite semántico importante:** `role` es una *etiqueta de presentación declarada
por el autor* sobre una clase y, opcionalmente, una variable confirmada. No es
una nueva verdad del motor sobre si un decremento constituye daño o gasto de
recurso. Para certificar dicha intención causal se necesitaría metadata explícita
en la operación confirmada; no se infiere del signo del cambio. El ejemplo Tegularis
usa por ello `neutral` para los cambios numéricos y no afirma daño donde la traza
no lo prueba. La introducción de roles específicos por operación se deja para un
contrato posterior expresamente validado.

La ampliación es aditiva en el DSL 1.5 y conserva las solicitudes de Act, las
transacciones y las reglas de juego. Observe incorpora las proyecciones públicas
correspondientes sin modificar el estado lógico ni consumir números aleatorios.
Cambiar `presentation` cambia el digest del paquete: un snapshot debe restaurarse
con el mismo paquete admitido.

## Comprobación y límites

Las pruebas `test_release_v082e.py` y `test_release_v082f.py`, en
`gisela/engine/tests/`, comparan presentaciones, decisiones, estado lógico,
aleatoriedad y restauración. El verificador de la Unidad 8 compara siete variantes
con el canon, dos semillas y tres pasos por sesión. Esa cobertura no equivale a
recorrer todas las ramas del combate ni a una prueba de usabilidad con alumnos.
