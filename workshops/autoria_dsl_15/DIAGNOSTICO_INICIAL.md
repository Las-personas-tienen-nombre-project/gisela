# Diagnóstico inicial del workshop de autoría GISELA DSL 1.5

## Alcance verificado

Repositorio de entrada: `gisela.tar.gz` (fuente del proyecto), versión `0.1.21` según `pyproject.toml`; DSL declarado `1.5` en los paquetes y contratos. El análisis distingue el paquete inicial, el cierre autoral v0.7.7, el balance v0.7.8 y el paquete de presentación semántica v0.8.2d.

**Canon de reglas para reproducción:** `packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json`. **Ejemplo más completo de presentación declarativa:** `14_presentacion_semantica_v082d.package.json`. Las variantes 11–14 contienen vistas y proyecciones; no deben suponerse versiones de balance nuevas.

## Inventario de mecanismos observados

| Mecanismo | Ubicación comprobada | Relevancia |
|---|---|---|
| Manifiesto, definiciones y estado | `manifest`, `cards`, `initial_state` | Identidad, fichas, condiciones y datos iniciales |
| S.O.F.I.A. | Cartas `kind: character`, propiedad `sofia` | Atributos asignados |
| Rasgos contextuales | `traits.traits`, `contributions` | Bonificaciones y penalizaciones en resoluciones |
| Habilidades | `cards`, `initial_state.skills` | Definición frente a instancia asignada |
| Dados y concursos | `dice_profiles` y efectos de las cartas | Resolución reproducible |
| Actuación | `actuation.participants`, `setup`, `event_policies`, `outcome_policies` | Iniciativa, candidatos, NPC y desenlaces |
| Recursos y trazas | `actuation.public_resources`, `public_trace_variables` | Estado observable y rastros autorizados |
| Presentación | `presentation.views`, `regions`, `action_targets` | Tablas, acciones y crónica sin decidir reglas |
| Persistencia | `gisela.engine.runtime` | Exportación y restauración con digest |

El paquete de presentación v0.8.2d contiene **cinco personajes**, **ocho rasgos definidos**, **89 cartas** y **53 instancias iniciales de habilidades**. Estos conteos describen ese archivo y no la cantidad de unidades didácticas necesarias.

## Personajes del paquete examinado

- `parnecio`: Parnecio Esparcales. S.O.F.I.A. `{'strength': 8, 'openness': 5, 'fortune': 6, 'intelligence': 4, 'awareness': 6}`; rasgos iniciales `['dodge']`.
- `gillius`: Gillius Cabezadeencina. S.O.F.I.A. `{'strength': 10, 'openness': 4, 'fortune': 5, 'intelligence': 4, 'awareness': 6}`; rasgos iniciales `['dodge']`.
- `clarisa`: Clarisa de la Hojarasca. S.O.F.I.A. `{'strength': 4, 'openness': 7, 'fortune': 9, 'intelligence': 7, 'awareness': 7}`; rasgos iniciales `['magic_redux']`.
- `iosepus`: Iosepus Knechti. S.O.F.I.A. `{'strength': 4, 'openness': 5, 'fortune': 6, 'intelligence': 9, 'awareness': 8}`; rasgos iniciales `['magic_redux']`.
- `tegularis`: Tegularis, el Hijo del Volcán. S.O.F.I.A. `{'strength': 15, 'openness': 7, 'fortune': 5, 'intelligence': 9, 'awareness': 7}`; rasgos iniciales `['enorme', 'escamas']`.

## Rasgos comprobados

- `dodge` — Evasión pasiva +2; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["evasion"]}, "add": {"slot": "bonus", "amount": 2}}]`.
- `magic_redux` — Reducción de daño mágico 3; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["magic_damage_reduction"]}, "add": {"slot": "bonus", "amount": 3}}]`.
- `enorme` — Penalización de evasión -5; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["evasion"]}, "add": {"slot": "bonus", "amount": -5}}]`.
- `escamas` — Reducción del daño físico 5; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["physical_damage_reduction"]}, "add": {"slot": "bonus", "amount": 5}}]`.
- `stance_aggressive` — Golpe más certero +2; contribuciones: `[{"id": "contribucion", "when": {"role": "actor", "all_tags": ["hit"]}, "add": {"slot": "bonus", "amount": 2}}, {"id": "evasion_penalty", "when": {"role": "defender", "all_tags": ["evasion"]}, "add": {"slot": "bonus", "amount": -2}}]`.
- `stance_aggressive_evasion` — Evasión -2 en postura agresiva; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["evasion"]}, "add": {"slot": "bonus", "amount": -2}}]`.
- `protegido` — Reducción general del daño 5; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["damage_reduction"]}, "add": {"slot": "bonus", "amount": 5}}]`.
- `pride_redux` — Reducción general del daño 1; contribuciones: `[{"id": "contribucion", "when": {"role": "defender", "all_tags": ["damage_reduction"]}, "add": {"slot": "bonus", "amount": 1}}, {"id": "contrib_physical_damage_reduction", "when": {"role": "defender", "all_tags": ["physical_damage_reduction"]}, "add": {"slot": "bonus", "amount": 1}}, {"id": "contrib_magic_damage_reduction", "when": {"role": "defender", "all_tags": ["magic_damage_reduction"]}, "add": {"slot": "bonus", "amount": 1}}]`.

## Dependencias pedagógicas

JSON válido → manifiesto e identificadores → cartas de personajes → instancias/estado → variables y condiciones → rasgos y contribuciones → habilidades, costos y consecuencias → dados/concursos → turnos y NPC → encounter completo → Observe/Act → presentación → semillas y restauración.

La unidad de rasgos debe preceder a los ejercicios de combate cuya resolución dependa de `dodge`, `escamas`, `magic_redux` y `pride_redux`; esto corrige el riesgo de enseñar resultados numéricos como si fueran atributos intrínsecos de la carta.

## Ajustes al programa

1. Incluir explícitamente **definición frente a instancia** en la unidad 2 y revisitarlo en la 5.
2. Enseñar **observabilidad y privacidad** antes de la presentación, ya desde condiciones y estado.
3. Mantener la **presentación v0.8.2** como extensión del DSL 1.5, sin confundir sus números de versión.
4. Enseñar qué significa una admisión sin presentarla como una simulación de combate completa.
5. Conservar dos recorridos: guiado sobre copias pequeñas admitidas y autónomo mediante especificaciones y criterios observables.

## Comprobaciones realizadas

- `admit_package_file(Path(...))` confirmó **ADMITTED** para `01_cartas_gisela_v15.package.json` (digest `96feff888e787114684bde93a34d89cc864a8f4d96b4a7dc57ede581c71c6fbb`).
- `admit_package_file(Path(...))` confirmó **ADMITTED** para `14_presentacion_semantica_v082d.package.json` (digest `6f334a54c0f2eef9ad0d88efcf7c27496637bc39786d4b1081395c719d330d56`).
- Se inició `python tools/check_gisela.py`, pero su ejecución se interrumpió antes de concluir; **no se certifica la regresión**.
- **No se ha certificado todavía** la reproducción completa del combate, la equivalencia lógica de los paquetes progresivos ni la restauración de los ejercicios nuevos.

## Plan de implementación y aceptación

1. Construir una práctica mínima con un cambio por ejercicio y verificar admisión.
2. Añadir fichas, recursos, condiciones y rasgos de manera acumulativa.
3. Incorporar cada habilidad a partir de sus declaraciones reales, con pruebas de efecto y trazas.
4. Configurar turnos y políticas sin Python autoral.
5. Reconstruir Tegularis conservando datos originales y verificar desenlaces con semillas fijas.
6. Añadir dos presentaciones sobre el mismo encuentro; comprobar equivalencia de estado y RNG.
7. Ejecutar regresión completa, trazabilidad y guardado/restauración; solo después declarar el workshop concluido.

**Estado de entrega:** diagnóstico e inicio del workshop; el conjunto de nueve unidades y la prueba final siguen pendientes y no se presentan como terminados.
