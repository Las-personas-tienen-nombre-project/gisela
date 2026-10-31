# Laboratorio H4.6 — El faro de niebla

## Naturaleza del contenido

**Ficción original de diagnóstico, no canónica**, creada para GISELA y jugable desde GLAUQUIR. No adapta *Blue Forever*, no utiliza sus personajes y no impone reglas narrativas nuevas al motor. El proyecto Ren'Py continúa siendo un trabajo separado.

Lara llega a un faro costero cuando una tormenta amenaza a dos barcos. El guardafaros Elio necesita reparar la campana de auxilio, recuperar el prisma y reunir información antes de que suba la marea. La persona que juega puede buscar recursos, ayudar a Elio, usar una habilidad, arriesgar una reparación o intentar enviar la señal inmediatamente. El desenlace depende de la preparación, la estrategia y los dados, no de una variable de «afinidad romántica».

## Jugar

Desde la raíz del repositorio (con `jsonschema` y `referencing` instalados):

```bash
python gisela/contracts/admit_package.py gisela/packages/h46_faro_de_niebla.package.json
python tools/glauquir.py --package gisela/packages/h46_faro_de_niebla.package.json
```

GLAUQUIR acepta los identificadores de acción que ofrece el motor o el número correspondiente en `acciones`. Primero use `escuchar_aviso`; después responda a Elio. Los lugares disponibles son `muelle`, `archivo`, `taller` y `cupula`. Comandos de lectura: `mirar`, `acciones`, `misiones`, `inventario`, `habilidades`, `estado` e `history`. `guardar partida.json` exporta un snapshot; `cargar partida.json` restaura el mismo paquete. También puede iniciar la consola con `--restore partida.json`.

## Recorridos verificables

Para reproducir los tres desenlaces con la misma semilla y decisiones diferentes:

```bash
python tools/h46_walkthrough.py --route completa --seed $(printf '0%.0s' {1..64}) --verify-restores
python tools/h46_walkthrough.py --route parcial --seed $(printf '0%.0s' {1..64}) --verify-restores
python tools/h46_walkthrough.py --route sin_preparacion --seed $(printf '0%.0s' {1..64}) --verify-restores
```

| Recorrido | Final esperado (semilla de 64 ceros) | Característica |
| --- | --- | --- |
| `completa` | `faro_encendido` | Recupera el prisma, conoce el faro, ayuda y repara antes de emitir |
| `parcial` | `luz_intermitente` | Lee el registro, pero no consigue suficientes preparativos |
| `sin_preparacion` | `noche_cerrada` | Omite los preparativos y utiliza el perfil arriesgado |

La herramienta `h46_walkthrough.py` **no es un segundo ejecutor**: reproduce una lista de acciones ya ofrecidas por `Observe` y las envía por `Act`; nunca modifica el estado directamente ni interpreta condiciones. Se utiliza solamente para automatizar pruebas. Una partida interactiva puede seguir otro orden y obtener otros resultados, incluido un final de fracaso tras preparar todo.

## Matriz de cobertura

| Subsistema | Ejercicio del paquete | Evidencia automatizada |
| --- | --- | --- |
| GISELA — escenas/nodos | Exploración, narración, diálogo, decisiones, transiciones y tres finales | `test_02_three_real_endings` |
| Autorización `Act` | Acciones ofrecidas, rechazadas y revisiones obsoletas | `test_09_stale_action_and_unoffered_do_not_mutate` |
| ALBERTO | Transferencia, desplazamiento, conocimiento, creencia y relación dirigida | `test_03_relationships_inventory_and_knowledge` |
| S.O.F.I.A. | Estadística efectiva, aumento de inteligencia y efecto de fuerza temporal | `test_05_skill_traits_and_effect_expiration` |
| TRAITS | Rasgo inicial `meticulosa` y asignación de `audaz` por una decisión | `test_05`, `test_06` |
| DICE E2 | Verificación oculta determinista en el primer nodo | `test_08_hidden_does_not_consume_random` |
| DICE E3 | Evaluación visible de escena, reconocida de elección y visible automática de paso | `test_02`, `test_07`, `test_14` |
| RNG y restauración | Snapshot tras cada acción y suspensión de tirada | `test_02`, `test_07`, `test_12` |
| MARY | Objetivos de hito y actuales, misión pública, yield una vez | `test_04_mary_milestone_yields_once` |
| Reacciones | Dos hechos encadenados, relación observada, vencimiento temporal y marea | `test_03`, `test_05`, `test_13` |
| Frontera de autoridad | Solicitante no humano, recibos idempotentes y rechazo de intruso | `test_10_gateway_nonhuman_exactly_once` |
| Rollback | Rama inválida después de resultado DICE fijado, sin efectos parciales | `test_11_rollback_of_invalid_evaluation_branch` |
| GLAUQUIR | Representación de los dados desde la proyección pública | `test_15_glauquir_prints_public_dice` |

La evaluación visible de una acción de escena y la reconocida en una elección tienen ramas, mientras que el segundo pulso es una evaluación visible de paso. Todas utilizan el mismo pipeline del motor. La tirada fija se confirma antes de las consecuencias; la continuación no puede volver a elegir un resultado.

## Qué no prueba este laboratorio

No equivale a cobertura exhaustiva de todas las combinaciones ni a una certificación del motor. Quedan fuera, entre otros, el descarte auxiliar con mano llena, ciclos reactivos patológicos, operaciones no soportadas aunque existan en schemas, validación de bibliotecas externas bajo carga y el adaptador real Ren'Py. Las baterías E0–E3/H2–H4 existentes siguen siendo obligatorias. El objetivo de este paquete es **integración narrativa y causal**, no reemplazarlas.

El tiempo ficticio avanza cuatro minutos por traslado. Si la partida se prolonga hasta las 19:40 y se inicia una nueva ejecución narrativa, una reacción registra `marea_alta`, lo que impide el mejor desenlace. La regla se expresa en datos; no se implementa en Python. Los límites de tiempo y el orden de acciones deben verificarse siempre en una sesión con la misma semilla.

## Verificar y aplicar

```bash
python -m unittest gisela.engine.tests.test_h46_adventure -q
python tools/check_project.py
sha256sum -c MANIFEST.sha256
```

El estado de la adaptación canónica H4.6 del roadmap **no cambia** por la entrega de este laboratorio: la adaptación de la primera jornada literaria requiere selección y aprobación editorial independientes.
