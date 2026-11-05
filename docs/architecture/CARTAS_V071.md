# Integración v0.7.1: Contratos genéricos, no motor de combate

Registro del incremento indicado en el título. Sus pendientes describen esa etapa; consulte el [roadmap](../operatives/ROADMAP.md) y la [presentación actual](PRESENTACION_DECLARATIVA_V082.md) para las capacidades posteriores.

## Cambios a la base

- `actuation.setup`: lista optativa de operaciones ya autorizadas por el DSL; se ejecuta durante la creación de sesión, una sola vez y antes de la iniciativa. Permite aleatorizar recursos de manera reproducible sin añadir reglas de HP/MP a GISELA. La sesión no llega a publicarse si alguna operación de preparación falla.
- `expire_on_actor_turn_start`: bandera optativa de una carta de efecto. Termina el efecto enlazado al comienzo del turno autoral del beneficiario, ejecutando el `on_expire` normal y sin modificar el turno narrativo.
- Validación dinámica de `on_actor_turn_start`, además de `on_apply`/`on_expire`.
- Ningún nombre de personaje, habilidad, categoría de daño, recurso o atributo específico del encuentro se añadió al ejecutor general.

## Alcance compilado

Se conservan las **32 cartas originales del diseño** y se generan **15 variantes de destinatario** (47 cartas de habilidad en total). De las 27 cartas originales que requieren actuación (26 activas más una postura), 25 tienen ejecución conectada; `Protección` y `Bless` permanecen explícitamente inhabilitadas. Las cuatro pasivas siguen actuando a través de TRAITS; `ultima_llama` no se ejecuta sin los acontecimientos de v0.7.2.

Las acciones NPC se eligen contra el estado confirmado tras cada operación y se ejecutan sobre el borrador de sesión. Los efectos cuentan turnos del beneficiario y no las acciones individuales.

## Riesgos conocidos / no certificados

- El módulo `actuation` sigue siendo una vía de **laboratorio** de `GiselaSession`, no una nueva acción pública autenticada del gateway Observe/Act.
- No hay todavía finalización del encuentro: después de que un bando queda fuera de combate, el reloj no produce por sí solo un desenlace. Eso exige la política de acontecimientos de v0.7.2.
- `Protección`: falta acordar la secuencia entre Hit/Evasion, mitigación y redirección.
- `Bless`: falta el costo de MP.
- Las políticas de NPC son reglas ordenadas declaradas y evaluadas; aún no se han comparado con todas las decisiones tácticas del documento de diseño.
- La magnitud de Wingblast se trata como daño mágico para Magic Redux; falta confirmar esta clasificación con el autor.
- Las pruebas dirigidas no equivalen a la regresión global.
