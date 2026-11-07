# C6-A — Advertencias conservadoras de candidatas NPC

Ejecute desde la raíz:

```bash
python tools/candidate_shadow_report.py packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json
```

`POTENTIAL_CANDIDATE_SHADOW` aparece si dos candidatas usan cartas que tienen `play.requires` **estructuralmente iguales**, los `arguments` coinciden, ambas están inicialmente en `hand` y ninguna tiene `when`. La anterior se evalúa primero. El diagnóstico es **una advertencia, no un rechazo ni una demostración de inalcanzabilidad**. Las cartas pueden dejar de estar disponibles o cambiar de zona durante la partida. No se deducen equivalencias matemáticas entre predicados diferentes.

No cambia la ejecución, no consume RNG y no se expone en el estado público del jugador. Este primer analizador no cubre costos inferiores con requisitos diferentes, variaciones dinámicas de zona ni explicaciones durante la selección; esos trabajos pertenecen a C6-B/C6-C.
