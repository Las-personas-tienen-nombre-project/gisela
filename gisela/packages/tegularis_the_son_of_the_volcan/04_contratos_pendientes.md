# Contratos generales pendientes para ejecutar el combate completo en GISELA

**Alcance histórico:** este documento registra una etapa incremental de
Tegularis. Sus pendientes corresponden a esa etapa; consulte el
[taller de cierre v0.7.7](WORKSHOP_CIERRE_V077.md) para el combate completo.

**Referencia:** GISELA 0.1.21; DSL 1.5. **No se ha aplicado ningún cambio al motor.**

Este documento es una lista de aceptación para ampliar el DSL sin incorporar las reglas de combate como primitivas del motor.

## A. `play(skill)` invocable por reglas del guion

Propuesta conceptual, NO sintaxis GISELA actual:

```text
when: actor_ready(iosepus)
try:
    play(skill=agarraguirre, instance=agarraguirre_01, target=tegularis)
else if not_executable:
    play(skill=concentracion_iosepus, instance=concentracion_iosepus_01)
```

Requisitos: la carta debe pertenecer al actor, estar disponible y satisfacer `requires`; el guion tiene autoridad para invocar, el cliente no puede invocar cartas ajenas, y ambos orígenes reutilizan exactamente una misma transacción de ejecución. Un rechazo no descuenta costos ni acciones; un impacto fallido sí puede gastar recursos si la ejecución se confirmó.

**Prueba obligatoria:** intentar ejecutar una carta de Tegularis mediante una petición del jugador debe producir `INVALID_ACTION` sin alterar el estado, incluso después de habilitar la ruta declarativa de NPC.

## B. Parámetros tipados de invocación

`Magic Blast` requiere `x` entero no negativo y una elección de objetivo. La carta valida que el costo `1+x` no supere el maná actual. La misma `x` debe consumirse para costo, precisión, daño e historial, sin poder variar durante una transacción.

**Pruebas:** x negativo/decimal se rechaza; x superior al maná se rechaza sin gasto; x=0 es legal con 1 MP; una restauración reproduce exactamente la misma elección y tirada.

## C. Expresiones matemáticas compuestas

Aritmética pura y tipada (`+`, `-`, `*`, `floor`, `min/max`, porcentaje y comparación) sobre valores de S.O.F.I.A., variables y resultados DICE, sin ejecución de código de autor. No debe ser posible abrir una ventana de código Python/Rust desde el paquete.

**Pruebas:** iniciativa STR+AWA+FOR+1d10; evasión floor((STR+AWA)/2); costo MP 1+x; HP máximo 150+STR+1d20; Fénix ceil(HPmax/2); condición de Pride HP<=0.30*HPmax.

## D. Acontecimientos declarados por el autor

El motor proporciona emisión, condiciones, procedencia y orden causal; el autor define `turno_inicio`, `turno_fin`, `ataque_resuelto` y otros nombres de su mundo. Los eventos no deben asumir que existe un combate.

**Pruebas:** Regeneración se ejecuta una vez por turno del beneficiario, aunque posea tres acciones; una reacción no crea un ciclo infinito ni se reejecuta al restaurar.

## E. Enlace entre carta, efecto y TRAIT

Una carta pasiva como Dodge puede otorgar una contribución TRAITS mientras permanezca vigente. Una postura como Stance Aggressive activa una contribución temporal y puede retirarla sin borrar TRAITS similares de otras fuentes. Reaplicar Bless renueva su duración sin duplicar su bonificación; Bless, Grito de guerra y Armadura mágica sí coexisten.

**Pruebas:** identidades de origen independientes, exact-once de on_apply/on_expire, restore, modificación de atributos efectivos y soporte de contribuciones por contexto (`hit`, `evasion`, `magic_damage`, etc.).

## F. Prioridades declarativas y oportunidades de actuación

La cantidad de acciones del actor la define el autor (base 1; más acciones según atributo principal + TRAITS). La política de un NPC intenta alternativas en orden y debe tener un límite causal. No introducir un planificador de combate dentro de GISELA.

**Pruebas:** múltiples acciones de Gillius, una sola activación de Regeneración por turno, parálisis que impide todas las acciones del siguiente turno y termina sin afectar a otros.

## G. Efectos disparados antes del desenlace

Al caer Tegularis a cero, la carta "Si vas a perder asegurate de que no ganan por mucho" se resuelve **antes del final**; omite Hit y Evasion Roll por decisión del autor, aplica reducciones, y solo después se decide victoria, derrota o destrucción mutua. Pride se activa al llegar vivo a 30 % o menos, antes de resolver un segundo impacto de Double Slash.

**Pruebas:** evento de muerte repetido no duplica explosión; si Groupal Shield está activo, la bloquea una sola vez; destrucción mutua cuando todos caen; el final no se confirma anticipadamente; guardado y restauración mantienen la misma traza.

## Criterio de cierre

La ampliación se considera general solo si los mismos mecanismos se pueden usar en un laboratorio, una escena social o una investigación: habilidades con requisitos/costos, acciones solicitadas por reglas, eventos arbitrarios y efectos con identidad y vencimiento declarados. Ninguna operación debe estar codificada en función de nombres como `dragon`, `hit`, `combat_turn`, `mana` o `hp`.
