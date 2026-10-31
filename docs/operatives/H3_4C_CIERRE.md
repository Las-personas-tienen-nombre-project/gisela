# H3.4c. Registro técnico de aplicación y vencimiento de efectos

**Estado:** TERMINADO para los contratos v1.2 que ejecuta el motor CLI.

**Fecha:** 30 de octubre de 2026.

## Responsabilidades

ALBERTO crea y retira instancias de efecto, comprueba su destino y aplica la política de acumulación. El cálculo de modificadores de S.O.F.I.A. continúa siendo una lectura pura del mundo confirmado. GISELA interpreta `on_apply` y `on_expire`, resuelve vencimientos y reacciones, y conserva la única autoridad de confirmación.

No se agregaron atributos efectivos persistentes ni un servicio programador de tiempo. Tampoco se modificaron los schemas v1.2.

## Implementación

- `gisela/engine/world_effects.py`: comprobación de carta y destino, acumulación e identidad, alta y retiro de instancias.
- `gisela/engine/expiration.py`: evaluación de las cuatro cláusulas de vencimiento sobre el estado causal.
- `gisela/engine/consequences.py`: interpretación de `apply_effect`, `end_effect`, `on_apply`, `on_expire` y avance del reloj.
- `gisela/engine/reaction_nested.py`: rechazo de escrituras anidadas entre reglas que dependan de un orden oculto.
- `gisela/engine/reactions.py`: resolución del evento `effect_expired` y vencimientos después de las operaciones de cada ronda.
- `gisela/engine/conditions.py`: consulta `has_effect`.
- `gisela/engine/support.py`: rechazo anticipado de condiciones no implementadas y ciclos directos de aplicación.

El estado del efecto contiene únicamente `id`, `card`, `target`, `started_turn` y `started_at`. La identidad sigue siendo propiedad de la sesión. La expiración retira la instancia antes de ejecutar `on_expire` y genera `effect_expired` una vez por retiro.

## Decisiones de semántica

La política `unique_per_target` rechaza un duplicado activo; no reemplaza la instancia anterior. `additive` permite instancias repetidas y sus modificadores se suman. La ausencia de `stacking` equivale a `additive`.

`after_turns` se evalúa en `turn_ended` y no puede vencer en el mismo turno de aplicación. `after_minutes` se evalúa cuando `advance_time` mueve el reloj. `on_fact` atiende un nuevo registro de hecho. `when` se evalúa en las fronteras causales, sin observación asíncrona. Una carta sin cláusulas de expiración solo termina por `end_effect`.

La evaluación de efectos y consecuencias se realiza en el borrador transaccional. El estado confirmado permanece intacto durante una espera, y restaurar una espera exige repetir la operación desde ese estado. Las cartas con un ciclo directo de `on_apply` se rechazan al crear la sesión.

## Evidencia y criterios comprobados

El paquete `gisela/packages/h3_efectos.package.json` recorre aplicación, restauración y vencimiento. `docs/guides/examples/ejemplo_efectos.py` verifica los valores efectivos y la ejecución única de los hechos declarados. `gisela/engine/tests/test_h34c_effects.py` comprueba acumulación, unicidad, terminación explícita, las cuatro causas de vencimiento, reacciones a `effect_expired`, restauración, suspensión y rollback.

El verificador principal incorpora el nuevo ejemplo. Conserva las pruebas de H1, H2, H3.1 a H3.3, H3.4a y H3.4b, además de la política de 500 líneas por archivo, 30 líneas por función sin docstring y tres parámetros explícitos.

## Límites pendientes

H3.4d incorporó la ejecución de habilidades, sus requisitos, ventanas, resultados y retorno. H4 debe incorporar acciones de exploración y autorización de consultas. Ren'Py sigue sin conectar al ejecutor. No se implementa un programador de vencimientos independiente ni un reloj que avance fuera de las operaciones declarativas.

La documentación de uso se encuentra en [la guía de efectos](../architecture/ALBERTO.md) y el estado general en [ROADMAP](ROADMAP.md).
