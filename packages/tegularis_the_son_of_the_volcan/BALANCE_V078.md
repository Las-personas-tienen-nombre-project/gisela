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
