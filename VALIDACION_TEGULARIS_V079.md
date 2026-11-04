# GISELA — validación local v0.7.9

## Alcance

Esta revisión parte del repositorio `gisela.tar(9).gz` y conserva los datos de balance v0.7.8. No incorpora generador ni informe automático de equilibrio. La campaña únicamente emite registros JSONL operativos por semilla y un `summary.json` de ejecución, necesarios para reproducir fallos.

## Cambios técnicos

- `tools/tegularis_campaign_v077.py` utiliza **por defecto** `packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json`. Se conserva el nombre del script para no romper integraciones existentes.
- Permite `--package RUTA` para seleccionar explícitamente otra definición. Replay es excluyente con la selección de paquete; al reproducir se usa el paquete persistido en el diagnóstico.
- La ejecución como archivo Python desde una extracción sin instalar el proyecto incorpora la raíz del repositorio a `sys.path`.
- `SeedRun` comprueba serialización/Observe y **continúa desde la sesión restaurada** en las acciones 13 y 37. Son comprobaciones internas, no acciones de juego adicionales.
- Se agregan pruebas de versión por defecto, selección de paquete y exclusión con replay.

## Ejecución local

Desde la raíz del repositorio:

```bash
python tools/check_quality.py
python -m pytest -q tools/test_tegularis_campaign.py tools/test_quality.py
python tools/tegularis_campaign_v077.py --count 3 --strategy attack
python tools/tegularis_campaign_v077.py --count 3 --strategy pass
python tools/tegularis_campaign_v077.py --count 3 --strategy shield
python -m pytest -q
```

Para validar una definición concreta, añada `--package packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json`.

Para repetir una semilla fallida, utilice `--replay /ruta/al/directorio-de-diagnostico`. Los diagnósticos permanecen en `.local/tegularis-campaigns`; no deben compartirse automáticamente.

## Criterios de interpretación

- Victoria, derrota y destrucción mutua son resultados válidos del encuentro y no deben registrarse como errores técnicos.
- Una semilla que falla por excepción debe conservar artefactos de diagnóstico y provocar código de salida no nulo al terminar la campaña.
- La muestra pequeña de semillas no permite inferir una probabilidad de victoria ni un balance definitivo. El límite operacional obliga a completar la campaña extensa en la máquina local antes de certificar v0.7.9.
- La restauración probada compara snapshot y observación en los checkpoints. Para una prueba diferencial más fuerte, conviene comparar también toda la traza final de una corrida ininterrumpida con una restaurada, misma semilla/estrategia.

## Pendientes de cierre

- Campaña extendida de 100 semillas por las estrategias propuestas.
- Revisión manual de selección de objetivos y acciones desperdiciadas (sin generar informe automático todavía).
- Ejecución completa sin interrupciones de la batería general en la máquina local.
- Observación de destrucción mutua en partida ordinaria; no se debe inventar un resultado para cumplir el criterio.

## Resultados ejecutados en esta revisión

- Regresión general: **661 passed, 1 skipped, 120 subtests passed** (65,56 s).
- Pruebas de campaña tras el ajuste final: **36 passed**.
- Calidad y balance dirigidos: **18 passed**.
- `tools/check_quality.py`: conforme.
- Campañas ordinarias completadas (semillas 0 y 1 por estrategia):
  - `attack`: victoria en rondas 5 y 6.
  - `pass`: victoria en ronda 10 y derrota en ronda 10.
  - `shield`: victoria en rondas 7 y 8.
- La campaña conjunta solicitó nueve partidas, pero el entorno interrumpió el lote después de seis resultados. No se presentan las tres partidas restantes como realizadas.
- No se obtuvo destrucción mutua en las seis partidas terminadas. No se certifica su alcanzabilidad natural.
- No se generó un informe automático de equilibrio, conforme a la decisión autoral de reservarlo para el cierre final.

## Advertencia sobre la validez estadística

Seis partidas completadas son suficientes para una comprobación funcional inicial, no para establecer tasas de éxito confiables. La campaña de 100 semillas y la revisión de comportamientos NPC continúan como trabajo de validación local, sin alterar datos ni reglas en esta revisión.
