# Evidencia v0.8.0f: Observe, Act y presentación de Tegularis

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](../../CHANGELOG.md).

## Base y alcance

Se trabajó sobre la entrega parcial v0.8.0 basada en `gisela.tar.gz` adjunto;
se conservaron los dos árboles de código de la distribución y se sincronizaron
los módulos modificados. El paquete productivo integrado es
`packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json`.
No se cambiaron cartas, probabilidades, políticas NPC ni resultados de reglas.

## Pruebas que finalizaron

- Comprobación inicial: `python tools/check_quality.py`, resultado OK; `python -m pytest -q tools/test_quality.py`, 11 pruebas aprobadas.
- Tras el incremento: `python tools/check_quality.py`: OK (700/64/3).
- `engine/tests/test_author_presentation_v080.py`: 8 aprobadas.
- `engine/tests/test_actuation_public_v073.py`: 7 aprobadas.
- `engine/tests/test_public_presentation_v080f.py`: 6 aprobadas, incluidas
  los cinco participantes, quince recursos, objetivos publicables, restauración,
  rechazo de recursos privados, rechazo de destino inexistente, autorización,
  revisión vencida y ausencia de mutación ante el rechazo.
- `tools/test_quality.py`: 11 aprobadas.

## Partida real por interfaz pública

Comando completado con salida `0`:

```sh
PYTHONPATH=<raiz-padre-del-paquete> python -m gisela.cli.glauquir \
  --auto --color never \
  --package packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json \
  --seed <64-ceros-hex> --save <snapshot.json>
```

Resultado: **victoria**, ronda **6**, **816** entradas en el historial de
trazabilidad del snapshot. El registro incluye `ultima_llama`, consecuencias
de daño y `encounter_completed` con desenlace `victoria` (secuencia 816).
El snapshot final fue restaurado con el mismo paquete admitido y su Observe
confirmó `ended / victoria`, ronda 6 y 15 recursos públicos.

Una segunda integración mediante `new_session`/`observe`/`act` terminó con
**59 acciones**, en ronda 5, victoria y 733 registros causales, con restauración
idéntica comprobada después de las acciones 11 y 31 (la tercera condición de
restauración a 61 no se alcanzó). Son dos ejecuciones de prueba, no datos
estadísticos de balance.

## Límites y pendientes

- El selector de destinatario es declarativo para instancias autorales ya
  diferenciadas. No habilita parámetros dinámicos arbitrarios dentro de Act.
- `actuation.causal` expone una ventana ordenada de 40 eventos confirmados;
  el historial íntegro se conserva en la sesión, pero no se pagina en la UI.
- La regresión conjunta fue interrumpida al agotar su límite de ejecución.
  Una campaña adicional de dos semillas tampoco terminó en el límite del
  comando: **no se certifican** sus resultados.
- No se ejecutó Bandit ni la regresión general del repositorio completo.
- No se emite certificación de v0.8.0 final; se entrega un incremento funcional
  con un recorrido completo confirmado.
