# Resultados ejecutados: v0.7.3/v0.7.4

- Contrato público + restauración + gateway + invariantes: **7/7** pruebas nuevas pasaron.
- Acontecimientos y desenlaces v0.7.2: **7/7** pasaron.
- Regresión dirigida previa de CLI, NPC y TRAITS: **55/55** pasaron.
- Gateway más integración pública y desenlaces (antes de añadir dos invariantes): **36/36** pasaron; los siete tests de integración se volvieron a pasar después de añadir iniciativa a Observe.
- Partidas completas Observe/Act con elecciones automáticas de la primera acción habilitada: semilla `1` repetida 64 veces (96 acciones, victoria, ronda 8), `2` (89, victoria), `3` (120, victoria), `4` (81, victoria).
- GLAUQUIR de consola con `--auto` completó la primera partida con código de salida 0. Salida: `glauquir_full_game.txt` en carpeta de pruebas del paquete entregado.
- Regresión del motor: interrumpida por límite de ejecución, último avance visible ~57%, sin fallos visibles antes de interrumpirse. **NO aprobada**.
- Tres desenlaces naturales con diferentes estrategias y publicación detallada de todos los dados individuales: **NO demostrados**.
