# GISELA v0.7.2 — Acontecimientos declarativos y desenlaces

## Alcance comprobado

En `actuation.event_policies` el autor define identificador, fase (`immediate` o `after_action`), predicado, operaciones DSL y ramas de consecuencias. En `actuation.outcome_policies` declara los desenlaces y su precedencia explícita. No existe código de combate ni nombres de recursos o de participantes en el intérprete.

La fase `immediate` se examina después de cada mutación genérica `set` o `add`, también cuando está anidada en una habilidad; por ello Pride se aplica antes del segundo impacto de Double Slash cuando el primer impacto deja vivo al dragón al 30 % o menos. La fase `after_action` se examina después de las consecuencias de la oportunidad y en los límites de inicio de turno. En ella se ejecuta la explosión una vez y **luego** se decide el desenlace.

La relación `clock.fired` contiene los IDs de políticas ya ejecutadas y es parte del estado guardado. Una transacción fallida descarta también tiradas, disparadores y mensajes. Las definiciones completas de políticas se comparan con el paquete admitido durante la validación de la sesión restaurada.

## Reglas del paquete Tegularis v0.7.2

- Pride: vida positiva y `10 × HP ≤ 3 × HPmax`; activa efecto persistente con +1 en STR/OPN/FOR/INT/AWA y +1 de reducción física y mágica consultada por TRAITS.
- Última llama: al caer Tegularis a 0 HP, tirada reproducible de 1d10, daño bruto `30 + INT efectivo + dado` sin Hit ni Evasion; aplica reducción mágica y defensa de cada héroe individualmente.
- Groupal Shield: una instantánea del estado antes de las ramas garantiza que el mismo escudo no permita simultáneamente la rama de impacto. Se consume una carga.
- Desenlaces: con Tegularis caído y algún héroe vivo, victoria; ambos bandos caídos, destrucción mutua; héroes caídos y Tegularis vivo, derrota.

## Límites y riesgos

La integración sigue siendo de laboratorio, no está conectada al gateway Observe/Act productivo. Esta versión tampoco completa Protección ni Bless (contratos autorales pendientes de v0.7.1). La explosión está modelada en una política declarativa, no mediante `play_skill` de la carta `ultima_llama`, que sigue catalogada sin efectos para evitar una doble ejecución. En v0.7.3 conviene unificar la procedencia visual del disparo con la instancia de carta.

No se certifica todavía el equilibrio de muchas semillas, todas las políticas tácticas de NPC, ni la regresión general completa. En particular, el orden de las ramas es una decisión autoral: la instantánea previa evita que los cambios de una rama modifiquen accidentalmente las condiciones de otra, pero el motor sigue evaluando las ramas en secuencia.

## Criterios de aceptación ejecutados

`PYTHONPATH=. pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_desenlaces_v072.py` — siete tests aprobados.

Admisión, recursos y costos v0.7.1 (selección) — cuatro tests aprobados.

Recorrido real de 30 oportunidades hasta ronda 3, con 46 mensajes y restauración en oportunidad 15 — comprobado.

Regresión combinada amplia — **no certificada**: excedió el tiempo disponible.
