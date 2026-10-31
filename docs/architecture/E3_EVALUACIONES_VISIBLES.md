# E3 — Evaluaciones visibles DICE: contrato ejecutable v1.5

## E3.1: decisiones de alcance

Se implementan `hidden`, `visible` y `acknowledged` con un único índice `EvaluationRoutes`, una fuente RNG `sha256_counter_v1`, el mismo ejecutor de consecuencias y la misma frontera de autorización. Los resultados visibles se fijan sin consecuencias y se continúan por `Act`. Las modalidades visibles difieren solo en la política de presentación/confirmación del anfitrión. No hay reintentos de tirada ni retiradas posteriores.

## E3.2: extensión de contratos

Los trece esquemas de `gisela/contracts/v1_5/` conservan las estructuras anteriores, salvo el nuevo campo privado `pending_evaluation` del snapshot y el nuevo contenido/acción de `Observe`. `Act` conserva `{session_id,revision,action_id}`: para continuar se ofrece `action_id="continue_evaluation"`, sin parámetros. Si se necesita una opción auxiliar tras el resultado se ofrecen acciones `resolve_<id>` de clase `resolve_evaluation_auxiliary`; se conserva la oferta pública de opciones legales y la validación de replay.

`pending_evaluation` contiene `evaluation_id`, `prepared_revision`, `origin`, `source`, `initiated_revision`, `rng_initial`, `fixed[]`, `answers[]` y opcionalmente `auxiliary_request`. Cada entrada de `fixed[]` contiene `key`, `presentation`, `result`, `rng_before` y `rng_after` y está protegida por verificación de replay. El snapshot confirma el RNG tras el último resultado visible, pero nunca confirma estado narrativo provisional. `pending_transaction` y `pending_evaluation` no pueden coexistir.

Una entrada visible en el inicio de sesión utiliza `status=preparing` más `preparing_for`; no crea un turno hasta el commit final. Las evaluaciones de pasos, opciones, acciones exploratorias y elementos comparten ruta de ejecución. Se permiten tiradas ocultas entre visibles sin confundir su orden, y varias tiradas visibles en la misma intención se verifican con una cinta ordenada (no varias transacciones abiertas).

## E3.3: preparación

`EvaluationRoutes.execute` utiliza `traits_dice_bridge.resolve` para obtener un resultado y un RNG propuesto desde el estado efectivo. `EvaluationReplay` registra una suspensión si corresponde; `GiselaSession` publica solo el resultado y el RNG. No se modifica el resto del estado confirmado.

## E3.4: aplicación

`continue_evaluation` revalida la acción, reconstruye el borrador, verifica resultados fijos y aplica ramas por `_operations`, incluyendo reacciones y MARY. La confirmación recorre `_commit` y respeta ADR-007. Las solicitudes auxiliares usan `DecisionReplay` dentro del mismo pendiente.

## E3.5: restauración e idempotencia

`restore_session` realiza validación estructural y semántica, seguida por reproducción hasta el resultado fijado o la solicitud auxiliar. El checkpoint del `ExecutionGateway` incluye estado y recibos de comandos en una operación atómica. La idempotencia por principal/comando y la expiración de revisión no se redefinen.

## E3.6: auditoría

Las pruebas nuevas verifican los tres orígenes, dos presentaciones visibles, efecto previo, cadenas visibles/ocultas, RNG, decisiones auxiliares, MARY, rollback, transición A→B, privacidad, restauración y gateway no humano. Ejecutar `python tools/check_project.py` para la comprobación integral, junto con `tools/verify_e3_invariants.py`.

## Límites

No se introducen animaciones, reglas de repetición, retirada ni total público. Los clientes deben representar los datos de `Observe`; el motor no depende de Ren'Py. Los paquetes viejos deben permanecer en sus contratos originales.
