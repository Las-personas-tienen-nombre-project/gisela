# Workshop — Cartas del encuentro v0.7.1

**Alcance comprobable:** paquete `07_cartas_v071.package.json`, DSL 1.5, sobre la base más reciente suministrada de GISELA. El guion de combate se compila con `build_v071.py`; el motor desconoce nombres, daño, HP, MP y estrategias del dragón.

## 1. Preparación

Desde la raíz del repositorio:

```bash
python gisela/packages/tegularis_the_son_of_the_volcan/build_v071.py
python -m gisela.cli.glauquir --actuation --rounds 3 --auto --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --package gisela/packages/tegularis_the_son_of_the_volcan/07_cartas_v071.package.json
pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_cartas_v071.py
```

El paquete tiene un **nodo de entrada separado de la práctica histórica**. No combina la variable didáctica `dano_tegularis` con `hp_tegularis`. Las tiradas iniciales de HP/MP son operaciones autorales de `actuation.setup`, ejecutadas una vez antes de la iniciativa.

## 2. Comprobaciones funcionales

1. **Cartas ofensivas:** Slash, Blai, Double Slash, Hachazo, Eviscerate, los Bastonazos, Dentellada, Zarpa, Coletazo, Firebreath, Wingblast y Magic Blast consultan S.O.F.I.A., TRAITS y el RNG. Double Slash dispone de dos tiradas de Hit, dos de Evasion y dos de Damage independientes.
2. **Recursos:** las cartas que requieren TP/MP consumen el recurso en la misma operación autorizada. Una carta sin recursos no puede ejecutarse. Concentración recupera 30 MP hasta el máximo.
3. **Mitigación:** Escamas, Dodge, Magic Redux, Firesteel, Grito de guerra, Armadura mágica y Preponderancia participan en la fórmula; Groupal Shield bloquea un ataque de área y consume una carga.
4. **Efectos:** Armadura mágica y Firesteel duran dos turnos del beneficiario; Regeneración tres, con INT del lanzador guardada al aplicar; Agarraguirre resta 2 AWA durante dos turnos del dragón; Wingblast puede aplicar Paralizado si falla la resistencia. Preponderancia desaparece al **comienzo** del siguiente turno propio.
5. **Destinatarios:** las variantes `curacion_*`, `fenix_*`, `regeneracion_*`, `armadura_magica_*` y `firesteel_*` son cartas concretas generadas por el autor. `play_first_skill` las selecciona sin decisiones del jugador sobre NPC; el motor no elige objetivos ocultamente.
6. **Mensajes:** `emit_message` genera avisos en el historial confirmado, con valores calculados y destinatarios correctos. Una acción rechazada conserva estado y RNG intactos.
7. **Persistencia:** guarde a mitad de las rondas, restaure y compare recursos, iniciativa, orden, efecto activo, RNG y mensajes después de continuar con las mismas acciones.

## 3. Contratos aún abiertos

**No se declara completa la v0.7.1.** `Protección` permanece deshabilitada porque no está acordado si la mitigación se calcula antes o después de redirigir el daño a Parnecio. `Bless` permanece deshabilitada porque el costo de maná no está fijado. Las cuatro pasivas están catalogadas; la habilidad disparada `ultima_llama` se reserva para los acontecimientos y desenlaces de v0.7.2.

La política de Magic Blast emplea **x=10 como elección explícita del guion de laboratorio**; el valor puede cambiar en los candidatos. El tratamiento de Wingblast como daño mágico a efectos de Magic Redux es una interpretación provisional: debe confirmarse con el autor. La selección completa de Parnecio, los acontecimientos de 30 % HP, la explosión, los finales y Observe/Act productivo corresponden a los hitos siguientes.

## 4. Pruebas

```bash
pytest -q \
  gisela/engine/tests/test_npc_skill_arguments_v04.py \
  gisela/engine/tests/test_npc_traits_v06.py \
  gisela/engine/tests/test_scripted_npc_skills.py \
  gisela/engine/tests/test_npc_contests_v05.py \
  gisela/engine/tests/test_traits_dice_bridge.py \
  gisela/engine/tests/test_npc_skill_priorities.py \
  gisela/packages/tegularis_the_son_of_the_volcan/test_actuacion_nativa_v07.py \
  gisela/packages/tegularis_the_son_of_the_volcan/test_cartas_v071.py \
  gisela/packages/tegularis_the_son_of_the_volcan/test_practica_nativa.py
```

Las pruebas dirigidas no sustituyen la regresión general ni las partidas integrales pendientes. No interpretar la salida de laboratorio como una victoria/derrota certificada.
