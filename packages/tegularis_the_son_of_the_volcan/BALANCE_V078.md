# Tegularis: ajuste de balance v0.7.8

## Origen y límites

Compilado directamente sobre `09_cierre_autoral_v077.package.json` del repositorio actualizado. La nueva definición es `10_balance_v078.package.json`. No se alteró el motor, el DSL 1.5 ni los paquetes anteriores. El generador reproducible es `build_v078.py`.

## Cambios autorales

1. **Preponderancia de la leyenda** recupera **25 TP y 15 MP** (en vez de 8 TP y 8 MP). Conserva el tope de 60 TP y el tope de MP del propio personaje, la acción consumida, la protección +5 y su vencimiento original. El aumento de recursos posibilita Coletazo cuando exista otro turno de acción válido, pero no promete un ataque en todas las circunstancias.
2. **Gillius** aumenta Awareness de 5 a 6. No se cambió su Strength ni el daño base de sus cartas.
3. **Iosepus** prioriza Armadura mágica y Firesteel sobre Gillius y Parnecio antes de protegerse a sí mismo; conserva Agarraguirre y los ataques/restauración de maná. Todos los destinatarios anteriores siguen disponibles.
4. **Clarisa** deja de tener una preferencia fija por Iosepus. Curación y Regeneración seleccionan al compañero vivo y herido con menor proporción HP actual/HP máximo, por comparación exacta de productos cruzados, sin coma flotante. Regeneración no se aplica a personajes con HP completo. En empate, las prioridades de la lista favorecen Parnecio, Gillius, Clarisa e Iosepus. Los caídos siguen pudiendo recibir Fénix y se conservan las alternativas de Groupal Shield, Bless y Concentración.

Las decisiones de objetivo están expresadas como `requires` declarativos y orden de `candidates` del paquete. GISELA no reconoce ninguna regla especial de estos personajes.

## Verificación efectuada

- `python tools/check_quality.py`: conforme (700 líneas/archivo, 64 líneas/función, tres parámetros explícitos).
- 7 pruebas específicas de v0.7.8 aprobadas; 32 pruebas dirigidas de v0.7.7, desenlaces, calidad y balance aprobadas.
- Tres partidas completas por el contrato público Observe/Act, con semillas 1, 2 y 3:
  - Semilla 1, estrategia `attack`: victoria, ronda 6, 68 acciones.
  - Semilla 2, estrategia `pass`: derrota, ronda 9, 102 acciones.
  - Semilla 3, estrategia `shield`: victoria, ronda 6, 70 acciones.
- Comparación controlada, semilla 2 y estrategia `pass`: el paquete v0.7.7 daba victoria, ronda 13 y 155 acciones; v0.7.8 da derrota, ronda 9 y 102 acciones.
- En el recorrido de semilla 2, Preponderancia produjo ocho mensajes y Coletazo trece; no se observó un ciclo exclusivamente dedicado a Preponderancia.
- Restauración y Observe idénticos después de 12 acciones dirigidas.
- Regresión general: la ejecución superó aproximadamente el 60 % sin fallos visibles, pero terminó por límite de tiempo; NO está certificada.

## Ejecución local

Desde la raíz del repositorio:

```bash
python packages/tegularis_the_son_of_the_volcan/build_v078.py
python tools/check_quality.py
python -m pytest -q packages/tegularis_the_son_of_the_volcan/test_balance_v078.py
python tools/play_mvp.py --package packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --save sesion_balance_v078.json
```

`tools/tegularis_campaign_v077.py` sigue apuntando al paquete anterior por diseño; para probar masivamente v0.7.8 sin alterar las herramientas existentes puede importar `SeedRun` y pasar `admit_package_file` sobre el nuevo archivo.

## Riesgos y observaciones

- Se ensayaron tres semillas, por lo que los resultados no representan una distribución estadística de balance.
- Todavía no se ha demostrado destrucción mutua en una partida natural con este ajuste.
- La prioridad defensiva de Iosepus es heurística y puede modificarse según feedback de las partidas. No reemplaza la elección táctica consciente del jugador.
- Un personaje realmente más herido puede seguir recibiendo más curaciones; eso es intencional. El cambio elimina la prioridad arbitraria del nombre Iosepus, no impone una cuota por personaje.
- No se agregaron aserciones a código de construcción: los contratos del compilador se comprueban con `ValueError` explícitos.

## Ajuste posterior: habilidades inalcanzables de Tegularis

### Problema

`actuation` ejecuta la primera candidata cuyas guardas y requisitos se cumplan. La lista anterior era Firebreath, Wingblast, Coletazo, Zarpa, Dentellada, Preponderancia, sin guardas. Wingblast cuesta 50 MP, como Firebreath, y está detrás; Zarpa cuesta 20 TP, como Coletazo, y Dentellada (30 TP) también queda detrás de Coletazo. Las tres eran inalcanzables mientras Coletazo y Firebreath siguieran en la mano. En 60 partidas (semillas 1–20 × `attack`, `pass`, `shield`) Tegularis jugó Wingblast, Zarpa y Dentellada cero veces. Wingblast es la única fuente de `ef_paralizado_*`, de modo que la parálisis tampoco ocurría en juego normal.

### Cambio

Solo se modifica `actuation.participants[tegularis].candidates` (función `tune_tegularis` de `build_v078.py`). No cambian cartas, costos, daños, variables ni el motor.

| Orden | Candidata | Guarda |
|---|---|---|
| 1 | Firebreath | `hp_tegularis × 2 > max_hp_tegularis` (sano) |
| 2 | Wingblast | — (se alcanza cuando Tegularis está herido) |
| 3 | Dentellada | `hp_parnecio × 2 ≤ max_hp_parnecio` |
| 4 | Zarpa | `hp_parnecio × 2 ≤ max_hp_parnecio` |
| 5 | Coletazo | — |
| 6 | Preponderancia | — |

Firebreath conserva el primer lugar, de modo que los ejercicios `05_guarda` y `06_referencia_invalida` de la Unidad 6 siguen apuntando a la misma candidata.

El cambio se aplicó directamente a los paquetes 10–14 y a todas sus copias del workshop `autoria_dsl_15`. En la versión anterior, `build_v078.py` no reproducía el paquete 10: faltaban `presentation`, `public_resources` y `public_trace_variables`. Ahora `v078_public_view.json` es la fuente de estos campos, y el generador reproduce el paquete 10 byte por byte. Se comprobó que `tune_tegularis` produce exactamente la misma lista que contienen los datos. Las instantáneas históricas 07–09 no se modificaron.

### Verificación

- `python -m pytest -q`: 720 aprobadas, 1 omitida (igual que antes del cambio).
- `test_balance_v078.py`, `test_cierre_v077.py` y `test_build_packages.py`: 16 aprobadas.
- `comprobar_unidad_04` a `08` y `comprobar_puentes_04_06`: conformes.
- `tools/check_quality.py`: conforme.
- 60 partidas por paquete con `SeedRun`, semillas 1–20:

| Estrategia | Antes V/D/DM | Después V/D/DM | Rondas promedio |
|---|---|---|---|
| `attack` | 16/1/3 | 17/2/1 | 7,0 → 6,9 |
| `pass` | 6/12/2 | 8/9/3 | 11,0 → 11,9 |
| `shield` | 20/0/0 | 19/1/0 | 7,35 → 7,65 |

| Habilidad de Tegularis (60 partidas) | Antes | Después |
|---|---|---|
| Firebreath | 213 | 139 |
| Wingblast | 0 | 75 |
| Coletazo | 676 | 541 |
| Dentellada | 0 | 76 |
| Zarpa | 0 | 57 |
| Preponderancia | 444 | 467 |
| Mensajes de parálisis | 0 | 25 |

Con 20 semillas por estrategia, diferencias de uno a tres desenlaces están dentro del ruido: el ajuste no demuestra que el encuentro sea más fácil ni más difícil, solo que las tres habilidades ya participan.
