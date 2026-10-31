# ADR-020: Frontera de solicitantes, confirmación y persistencia E0

**Estado:** aplicada en la implementación Python E0; **no** autoriza por sí sola una red ni `evaluate`.

## Contexto

`Act` era una petición local de un cliente confiable; ahora debe poder llegar desde cualquier software autenticado, incluida otra instancia de GISELA. Además, una tirada futura podría fijar RNG y resultado antes de consecuencias. La base anterior carecía de exclusión interna sobre una sesión, comprobantes de reintentos y validación de la proyección *antes* del commit. El modelo narrativo de ADR-007/008 y el RNG no necesitan cambiar.

## Decisiones

1. Separar solicitante autorizado, actor ALBERTO, origen causal y sesión destino. Un principal del anfitrión nunca se infiere de un `action_id` ni de datos del mundo.
2. Mantener `Act` y `Observe`. Para **clientes externos**, usar un gateway opcional que reciba identidad confiable y capacidades de acceso. El motor local conserva su API anterior cuando no se vincula gateway.
3. Serializar comandos por sesión; proyectar y validar el estado candidato **antes** de confirmarlo. No crear otro ejecutor ni una máquina de estados paralela.
4. Deduplicar `(principal, command_id)` con huella del comando; conservar estado y recibo en una unidad de persistencia si se configura `JsonCheckpointStore`. Fallos de escritura ambigua bloquean nuevas operaciones hasta reconciliación.
5. `observe_player` no es una capacidad genérica de lectura de NPC. `export_private` y `debug_private` requieren permiso explícito; los errores enviados a clientes externos no muestran mensajes internos.
6. Mantener v1.2 y v1.3 en sesiones, paquetes y `Act`; corregir **aditivamente** el conjunto de códigos de errores `Result` para cubrir errores que el ejecutor ya emitía. No se cambian estructuras ni su significado. v1.4 pertenece al futuro `evaluate`.
7. DICE define bandas unívocas; la primera cubre cualquier total por debajo de su primer umbral. Rechazar perfiles inválidos antes de consumir RNG.

## Consecuencias y alternativas rechazadas

No se implementan credenciales o canales de red dentro de ALBERTO, TRAITS o DICE; la autenticación pertenece al anfitrión. No se implementa una transacción distribuida entre dos sesiones ni se presupone intervención humana para confirmar un comando. No se incorpora un log paralelo de eventos del mundo ni se modifica el modelo de turnos. El checkpoint de archivo es un backend POSIX **local**, no un consenso multi-host. El gateway no es una frontera de sandbox contra Python no confiable que inspeccione atributos privados.

**Obligación de prueba:** cada invariante E0 tiene anclaje ejecutable en `docs/operatives/E0_INVARIANTES_TRAZABILIDAD.json`, comprobado mediante `tools/verify_e0_invariants.py` y ejecutado por `tools/check_project.py`.
