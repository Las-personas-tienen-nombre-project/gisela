# Traza pública de concursos DICE: avance incremental v0.7.6

Registro del incremento indicado en el título. Sus pendientes describen esa etapa; consulte el [roadmap](../operatives/ROADMAP.md) y la [presentación actual](PRESENTACION_DECLARATIVA_V082.md) para las capacidades posteriores.

## Base y objetivo

Base: `gisela.tar(6).gz`, entregada por el autor. Esta entrega **no** aplica directamente la implementación anterior ni cambia valores de combate. Extiende Observe/Act de DSL 1.5 con `actuation.contests`, tomando exclusivamente entradas confirmadas `contest_resolved` del historial transaccional.

## Contrato

Cada elemento publica `source`, `profile`, `winner` y las dos puntuaciones `left`/`right` con `rolls`, `die_value`, `base`, `bonus`, `total`. Se limita a los últimos 12 concursos, respetando el orden del historial. Los detalles de las contribuciones internas de TRAITS y el estado RNG no se exponen mediante este campo. Los mensajes siguen siendo independientes.

Esta es una proyección, no una segunda ejecución ni una nueva ruta de autoridad. Observe no tira dados ni muta el estado. La validación estructural está declarada en `gisela/contracts/v1_5/observe.schema.json`.

## Calidad

Se respetan los máximos de `tools/test_quality.py` / `tools/check_quality.py`: 700 líneas por archivo mantenido, 64 líneas por función (sin docstring) y 3 parámetros explícitos (salvo excepción existente de constructor de sesión).

Comprobaciones: 23 pruebas dirigidas aprobadas (`test_actuation_contest_trace_v076`, `test_actuation_public_v073`, `test_actuation_roll_trace_v075`, `test_npc_contests_v05`); `python -m tools.check_quality`: OK. Esto no certifica regresión general ni finales naturales.

## Pendientes sin resolver

- `actuation.rolls` sigue mostrando solo la operación general `roll`; `contests` representa una fuente distinta. Unificación cronológica de todas las fuentes, con identificadores y procedencia, permanece pendiente.
- Los dados de iniciativa siguen en `actuation.initiative`; la exposición de todos los Damage Roll está sujeta a que cada operación los registre.
- Protección y Bless permanecen sujetos a definiciones autorales. No se les atribuyeron reglas.
- No se ha certificado la batería completa, ni los finales naturales de derrota y destrucción mutua.
