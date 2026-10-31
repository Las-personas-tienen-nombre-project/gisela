# E2 — Auditoría diferencial y riesgos residuales

## Inconsistencias de la base antes de corregir

1. E1 aceptaba v1.4 pero el runtime rechazaba todos los paquetes y guardados v1.4; esto era deliberado y documentado. Se activó únicamente el alcance oculto de E2.
2. El puente TRAITS–DICE era puro, pero aún no hacía comprobación de rangos *efectivos* antes del RNG. Se añadió preflight numérico de componentes neutrales y presupuesto nominal del contador.
3. Los pasos `evaluate` no tenían despachador, y opciones/acciones ignoraban sus ramas. Se añadió `EvaluationRoutes` compartido, sin segunda autoridad.
4. Dos tests e invariantes E1 exigían la suspensión histórica del runtime v1.4. Se actualizaron al estado E2 y se conservó el registro de transición en ADR-021.

## Fallos corregidos y garantías verificadas

- Un fallo de rama o al entrar a un nodo posterior descarta RNG, hechos, selección, historial y transición; probado en E2-08/E2-21.
- La decisión auxiliar reconstruye la misma tirada tras guardar/restaurar y permite cancelación antes de confirmar; E2-17/E2-18.
- La cifra privada y el resultado DICE no aparecen en `Observe`; E2-02/E2-23.
- MARY se actualiza dentro de `settle` y no duplica hechos en restauración; E2-19.
- Los perfiles funcionan sin TRAITS ni SOFIA, con SOFIA solamente, y con ambos; E2-01/09/14.

## Riesgos y limitaciones no resueltas

1. **Evaluaciones visibles:** `visible`/`acknowledged` no son ejecutables en E2; siguen reservadas para E3. El contrato público v1.4 no contiene un estado `pending_evaluation`.
2. **Muestreo por rechazo:** el presupuesto previo del contador considera el número nominal de dados, no un máximo teórico finito de sorteos SHA-256. Si un bloque adicional agotara el contador, la evaluación falla sin commit, conservando la garantía transaccional.
3. **Persistencia externa:** el checkpoint JSON local garantiza el protocolo E0 dentro de sus condiciones, no consenso distribuido entre anfitriones.
4. **Semántica de evaluación en autoría:** v1.4 todavía permite declarar evaluaciones `visible` y `acknowledged` aunque sean futuras; la puerta dinámica E2 las rechaza explícitamente y no las ejecuta silenciosamente.
5. **Alcance de auditoría:** la batería prueba rutas representativas y regresiones, pero no es una demostración formal exhaustiva de todas las posibles cadenas de reacciones ni de todos los estados del mundo.

Las decisiones arquitectónicas existentes permanecen bajo ADR-007/008/019/020/021; ADR-022 especifica lo efectivamente implementado.
