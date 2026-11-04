# Seguimiento incremental — trazabilidad de tiradas confirmadas

Base: paquete GISELA v0.7.3/v0.7.4 entregado.

## Cambios

- La operación genérica `roll` registra `dice_roll` dentro del borrador transaccional de historial: caras, resultado, variable declarada y procedencia.
- Observe de DSL 1.5 proyecta las últimas 12 tiradas confirmadas como `actuation.rolls`.
- El esquema público valida los campos, sin publicar el estado interno del RNG.
- La consola muestra las últimas tres tiradas conocidas.
- No se cambian fórmulas de daño, políticas del encuentro ni decisiones pendientes.

## Garantías comprobadas

Comando: `PYTHONPATH=. pytest -q gisela/engine/tests/test_actuation_roll_trace_v075.py gisela/engine/tests/test_actuation_public_v073.py gisela/packages/tegularis_the_son_of_the_volcan/test_desenlaces_v072.py`

Resultado: **17 aprobadas**. Incluye pureza de Observe, no filtración por acciones rechazadas y restauración.

## Límites

- Solo incluye la operación general `roll`; otras fuentes de dados (`contest`, cálculos DICE y la propia iniciativa) tienen canales diferentes. La iniciativa ya se publica separadamente.
- No certifica todos los dados de Hit/Evasion/Damage ni reemplaza la futura auditoría completa de resultados.
- Bless carece de costo de maná confirmado y Protección mantiene una decisión autoral de mitigación pendiente. No se inventaron valores.
- Derrota y destrucción mutua siguen sin estar demostradas mediante partidas ordinarias.
- La regresión más amplia se interrumpió por tiempo de ejecución. No está aprobada.

## Siguiente etapa

Unificar las fuentes de dados en eventos estructurados transaccionales, cerrar los contratos autorales pendientes y ejecutar regresión por particiones y búsqueda de finales naturales.
