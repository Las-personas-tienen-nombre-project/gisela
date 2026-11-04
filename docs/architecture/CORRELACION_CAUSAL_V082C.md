# GISELA v0.8.2c — Identidad de ejecución causal

## Decisión y alcance

Se conserva el historial transaccional existente. Una habilidad iniciada bajo
`actuation` añade `causal_execution_id` público y opcional a los registros que
pertenecen de manera comprobable a la ejecución. La identidad se deriva de la
secuencia del `skill_started` confirmado (`action_00000073`); no se introduce
un generador de UUID, contador paralelo, RNG ni estado de presentación.

Los registros `skill_started`, `skill_played`, `dice_roll`, `contest_resolved`,
`variable_changed` y `author_message` llevan esa identidad cuando son generados
por las operaciones de la habilidad. Se propaga el contexto de operaciones a
subefectos de aplicación y finalización. Las habilidades anidadas abren su
propia identidad de ejecución; la presente fase **no** publica relaciones
padre-hijo de una acción anidada. Las reacciones y políticas disparadas por
otros procesos conservan sus propios registros sin identidad cuando no existe
una relación explícita comprobable. No se agrupa por distancia, `source`,
`card`, texto ni diferencia de HP.

## Contrato público aditivo

- `history.trace[]`: propiedad opcional `causal_execution_id`, formato
  `action_[0-9]{8,}`, máximo 96 caracteres.
- `Observe.actuation.causal[]`: publica el mismo campo opcional, respetando
  el límite preexistente de 40 entradas. No se revelan variables privadas.
- `presentation.views[]`: las vistas `component: event_log` aceptan
  `group_by: action` de forma opcional. No se aceptan otros operadores.
- La proyección de esa vista mantiene `items` planos y añade `blocks`: cada
  bloque de clase `action` reúne los registros con la misma identidad que
  tengan un `skill_started` dentro de la ventana seleccionada. Los demás
  permanecen como bloques individuales `event`.

Las presentaciones sin `group_by`, los paquetes antiguos y las trazas
históricas sin identidad conservan su salida plana. No se modifica DSL 1.5.

## Ventanas y límites

Primero se aplican filtros y ventana de la vista sobre Observe. Una acción cuyo
inicio queda fuera de esa selección no se convierte en un grupo ficticio. Su
continuación se muestra individualmente. Las agrupaciones son una proyección
pura del DTO público, no cambian el historial, el RNG ni la autorización Act.

## Persistencia y seguridad

La identidad vive en el historial confirmado y se serializa en el snapshot
ya existente. El commit atómico decide su publicación; una acción rechazada
no publica nuevos IDs. La restauración acepta trazas anteriores sin esta
propiedad y rechaza valores malformados. Se conservan los límites de profundidad,
archivo y longitud anteriores.

## Límites de esta fase

No hay paginación histórica, garantía de reconstruir una acción completa si
Observe recorta su inicio, ni semántica de daño/curación, plantillas o colores.
Esta capacidad de correlación no constituye todavía certificación v0.8.2.
