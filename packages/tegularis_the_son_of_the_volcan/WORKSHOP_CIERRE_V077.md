# Taller práctico: Tegularis v0.7.7

## Preparación

Desde la raíz de `gisela`:

```bash
python -m pip install -e . -r requirements-dev.txt
python tools/check_quality.py
python -m pytest -q tools/test_quality.py
cd gisela/packages/tegularis_the_son_of_the_volcan
python build_v077.py
cd ../../..
```

El paquete resultante es `gisela/packages/tegularis_the_son_of_the_volcan/09_cierre_autoral_v077.package.json`.

## Sesión con Parnecio controlado por el jugador

```bash
python tools/play_mvp.py \
  --package gisela/packages/tegularis_the_son_of_the_volcan/09_cierre_autoral_v077.package.json \
  --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  --save sesion_tegularis_v077.json
```

La consola ofrece las cartas admisibles de Parnecio. **Protección** aparece como una opción distinta por aliado; el resto de personajes siguen sus políticas. La presentación recoge las tiradas, puntuaciones, recursos y mensajes confirmados. Para continuar:

```bash
python tools/play_mvp.py \
  --package gisela/packages/tegularis_the_son_of_the_volcan/09_cierre_autoral_v077.package.json \
  --restore sesion_tegularis_v077.json
```

## Prácticas de comprobación

1. Usar **Protección** sobre Gillius antes de un ataque de grupo. Comprobar que Gillius no pierde HP por el impacto cubierto, Parnecio recibe un solo golpe de refilón y los compañeros no cubiertos siguen resolviendo normalmente.
2. Usar **Bless** desde Clarisa: cuesta 10 MP, da +2 al atributo principal y el efecto caduca según los turnos del beneficiario. Reaplicarlo no debe sumar +4.
3. Verificar que Groupal Shield neutraliza la explosión antes que Protección y que la explosión no causa daño después de consumido el escudo.
4. Comparar los campos `actuation.causal`, `actuation.rolls`, `actuation.contests` y los mensajes. Una tirada debe aparecer con su valor real y procedencia, no calculada por GLAUQUIR.
5. Guardar, restaurar y ejecutar exactamente los mismos comandos. Deben conservarse revisión, recursos, efectos, reloj autoral, registro causal y RNG.
6. Intentar una acción vencida o no ofrecida y confirmar que ni el estado ni las tiradas cambian.

## Tests reproducibles

```bash
python -m pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_cierre_v077.py
python -m pytest -q gisela/engine/tests/test_actuation_public_v073.py \
  gisela/engine/tests/test_actuation_roll_trace_v075.py \
  gisela/engine/tests/test_actuation_contest_trace_v076.py
python -m pytest -q
```

Para recorridos ordinarios por Observe/Act, sin editar estados:

```bash
python -m tools.tegularis_campaign_v077 --start 0 --count 1 --strategy attack
python -m tools.tegularis_campaign_v077 --start 0 --count 1 --strategy pass
python -m tools.tegularis_campaign_v077 --start 1 --count 1 --strategy shield
```

Estos recorridos pueden tardar debido a la validación completa de cada acción. No fuerzan ni garantizan el resultado. La documentación de las semillas realmente ejecutadas está en `RESULTADOS_CIERRE_V077.md`.

## Criterio para certificar el encuentro

Para cerrar definitivamente el combate todavía será necesario: observar los tres desenlaces desde partidas ordinarias; decidir el redondeo del 50 % y la semántica de condiciones secundarias del defensor; verificar impactos individuales hacia aliados si el catálogo incorpora esas cartas; y repetir la regresión general sobre la misma compilación que se distribuya.
