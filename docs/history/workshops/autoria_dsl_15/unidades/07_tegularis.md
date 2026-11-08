# Unidad 7: Construcción del encuentro completo de Tegularis

**Objetivo:** integrar habilidades, rasgos, estados, políticas de acontecimientos y desenlaces en un único paquete productivo, explicando sus dependencias causales y comprobando el comportamiento sin modificar el motor.

**Prerrequisitos:** unidades 1 a 6. **Conceptos nuevos:** alcance de los ataques de área, efectos temporales y sus disparadores, umbral de Pride, fases de política, captura de estado previo, explosión posterior a la muerte, evaluación de desenlaces.

**Referencia canónica del taller:** `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`. Su presentación no debe confundirse con las reglas de combate; para comparar balance, consulte también `10_balance_v078.package.json` y `BALANCE_V078.md`.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 7](../paquetes/07_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. Mapa de dependencias

Las dependencias principales del encuentro son las siguientes:

1. Las fichas de personaje (`cards`) y sus instancias (`initial_state`) definen a los participantes.
2. Los rasgos y las variables declaran sus contribuciones y recursos, incluidos HP, MP y TP.
3. Las habilidades (`play.effects`) producen consecuencias y pueden aplicar estados (`cards` con `kind: "effect"`).
4. La actuación selecciona participantes y candidatos. Los estados responden a `on_apply`, `on_actor_turn_start` y `on_expire`.
5. Las resoluciones y los cambios confirmados pueden activar `event_policies` en las fases `immediate` o `after_action`. Pride comprueba su umbral y aplica `ef_pride_volcan`; Última llama captura el escudo, realiza una tirada y elige una rama de daño.
6. Las políticas `outcome_policies` determinan `victoria`, `derrota` o `destruccion_mutua`.
7. Observe publica la información que GLAUQUIR presenta al jugador.

Esta lista explica dependencias; para conocer el orden exacto de ejecución, consulte las fases y las pruebas originales.

## 2. Ataque de área: Firebreath y Wingblast

**Intención autoral.** Que Tegularis ataque a varios integrantes del equipo sin convertir el encuentro en cuatro habilidades independientes.

**Regla.** `firebreath` comienza con una operación `add` sobre `mp_tegularis` por `-50`, calcula un valor común mediante tirada y atributo, y después utiliza valores de ataque/evasión por participante. `wingblast` también comienza consumiendo 50 MP y mantiene resoluciones propias para sus objetivos.

**Declaración real, fragmento de Firebreath:**

```json
{"op":"add","target":{"var":{"scope":"session","key":"mp_tegularis"}},"value":{"literal":-50}}
```

No interprete la primera operación como garantía de daño: debe recorrer el resto de `play.effects` y explicar cuáles operaciones almacenan resultados, cuáles evalúan condiciones y cuáles modifican HP o aplican efectos. En la práctica se restaura el costo canónico, no se rebalancea el combate.

**Predicción y comprobación.** Si se cambia solo `-50` por `-40`, la admisión puede seguir funcionando, pero la regla autoral es otra: el consumo previsto de MP deja de coincidir con la referencia. Compare ambos fragmentos y registre, en una ejecución controlada en que Firebreath sea seleccionado, MP antes y después; no presente un caso donde el ataque no ocurrió como prueba del costo.

## 3. Estados temporales: parálisis y regeneración

La carta `ef_paralizado_parnecio` contiene propiedades reales:

```json
{"id":"ef_paralizado_parnecio","kind":"effect","title":{"text":"ef_paralizado_parnecio"},"stacking":"unique_per_target","on_reapply":"refresh","actuation_turns":1,"actuation_blocks_actions":true}
```

`actuation_turns` se refiere al ciclo de actuación administrado por GISELA y no a minutos de la ficción. El bloqueo de acciones es parte de este efecto; no es una regla que deba escribirse por separado en GLAUQUIR.

`ef_regen_parnecio` declara tres turnos, una captura de atributo al aplicar el efecto (`on_apply`), operaciones en el inicio del turno del actor (`on_actor_turn_start`) y limpieza de la captura (`on_expire`). La duración no describe por sí sola la cantidad efectiva de curación: esta depende de activaciones y condiciones concretas. **Predicción:** acortar `actuation_turns` de 3 a 2 modifica oportunidades de activación; la admisión, por sí sola, no demuestra cuántos pulsos de curación ocurrieron.

## 4. Pride: condición, efecto y rasgo concedido

La política `pride_of_the_volcan_son` tiene fase `immediate`. Su condición usa dos comparaciones: Tegularis conserva HP positivo y `hp_tegularis * 10 <= max_hp_tegularis * 3`. La segunda expresa un umbral del 30 %, sin división y sin redondeos.

Al cumplirse, una de las operaciones aplica `ef_pride_volcan`. Esta carta de efecto incorpora modificadores de +1 a los cinco atributos S.O.F.I.A. y concede `pride_redux` mediante `granted_traits`. No confunda: **la condición detecta el umbral, el efecto modifica la ficha efectiva, y el rasgo contribuye solo en las resoluciones cuyas etiquetas lo activan**.

**Caso límite:** exactamente el 30 % cumple la segunda comparación, mientras que cero HP no cumple la primera. Cambiar el multiplicador derecho de 3 a 4 elevaría el umbral al 40 %; puede pasar la admisión pero deja de ser Tegularis canónico.

## 5. Muerte de Tegularis, Última llama y desenlace

`ultima_llama` figura como carta catalogada con `play.effects` vacío; **la explosión productiva se implementa en `actuation.event_policies`**, en una política con el mismo identificador y fase `after_action`. No atribuya a la carta vacía el trabajo que ejecuta la política.

La guarda de la política exige `hp_tegularis <= 0`. La primera operación copia `group_shield` a `burst_shield_snapshot`. La segunda genera un dado de diez caras y guarda su resultado en `burst_die`; las demás calculan `burst_raw` y emiten información. Las ramas `outcomes` examinan ese valor capturado, escudos individuales y reducciones mágicas; por ello es incorrecto determinar daño solo por cercanía entre dos acontecimientos.

**Importante:** el caso de escudo grupal, la protección individual y los casos sin protección tienen condiciones diferentes. Recorra las ramas de la declaración real antes de asegurar qué personaje recibe daño. No asuma que bajar la vida de Tegularis a cero implica victoria inmediata.

Los desenlaces declarados son `destruccion_mutua`, `victoria` y `derrota`. Las tres condiciones consideran tanto el estado de Tegularis como la supervivencia de los cuatro aliados. La evaluación debe realizarse con el estado confirmado **después** de los acontecimientos pertinentes, incluida Última llama. El orden de la lista del paquete canónico se conserva; modificarlo en una práctica obliga a justificar si el motor preserva o no la prioridad, no a suponer equivalencia.

## 6. Recorrido guiado: seis restauraciones de reglas

Los archivos de `ejercicios/07_tegularis/` son paquetes completos **admitidos, pero intencionalmente alterados**. Cada paquete cambia una sola propiedad con respecto al canon. Su tarea no es inventar valores equilibrados, sino explicar qué cambia y restaurar exactamente la declaración de referencia. Los solucionarios `soluciones/07_tegularis/` son copias íntegras del paquete canónico.

| Archivo | Alteración de práctica | Restauración canónica | Predicción que debe explicar |
|---|---|---|---|
| `01_firebreath_area` | Firebreath cuesta 40 MP | cuesta 50 MP | cambia el consumo si se ejecuta |
| `02_paralisis` | `ef_paralizado_parnecio` dura 2 turnos | 1 turno | cambia el bloqueo potencial |
| `03_regeneracion` | `ef_regen_parnecio` dura 2 turnos | 3 turnos | cambia el horizonte de regeneración |
| `04_pride` | umbral 40 % | 30 % | Pride se activaría antes |
| `05_ultima_llama` | explosión tira `1d8` | `1d10` | cambia el dominio del azar |
| `06_desenlaces` | orden de las políticas invertido | orden canónico | investigar precedencia efectiva |

**Procedimiento para cada práctica:** (1) localice el cambio y exprese la intención; (2) encuentre las declaraciones a las que afecta; (3) haga una predicción comprobable; (4) restablezca el valor/orden canónico; (5) valide el paquete entero; (6) ejecute un escenario que alcance la rama; (7) observe el estado y la traza; (8) compare el resultado con la predicción. La validación del JSON no sustituye los pasos 6 a 8.

**Error deliberado:** `07_error_efecto.package.json` declara `habilidad_inexistente` como candidato NPC de Tegularis. Debe rechazarse en admisión semántica. Corrija la referencia usando `firebreath_01`. Este caso enseña la diferencia entre un identificador bien formado y una referencia existente.

## 7. Recorrido autónomo

Sin consultar los solucionarios, reconstruya un paquete canónico a partir de estas especificaciones de comportamiento: el dragón posee dos habilidades de área que consumen 50 MP; la parálisis de Parnecio tiene duración de un turno; la regeneración tiene tres turnos y actúa en los inicios de turno; Pride entra cuando Tegularis está vivo y queda a lo sumo un 30 % de HP; al llegar a cero HP se dispara el proceso de Última llama, que lee el escudo capturado y tira un dado de diez caras; el encuentro distingue victoria, derrota y destrucción mutua. Explique qué declaraciones contienen cada regla y cuándo se evalúan.

La meta es la **identidad estructural con el paquete canónico**, no conseguir un resultado favorable en una partida aleatoria. Use el manual, esquemas y referencias del repositorio, pero no los solucionarios para realizar la primera reconstrucción.

## 8. Comprobaciones, errores y aprobación

Desde la raíz del repositorio:

```bash
python -m json.tool docs/history/workshops/autoria_dsl_15/ejercicios/07_tegularis/01_firebreath_area.package.json > /dev/null
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_07.py
```

El segundo comando es una herramienta de evaluación del repositorio, no un requisito de programación para alumnos. Comprueba admisión de paquetes, rechazo de la referencia inválida, restauraciones estructurales y pruebas puntuales de las reglas declaradas. Para **ejecución efectiva** debe utilizar la interfaz pública de GLAUQUIR y registrar turno, acción habilitada, revisión, acontecimientos y valores observados antes/después. La selección de una semilla sin ejecutar la rama no certifica la mecánica.

**Errores frecuentes:** confundir efecto con habilidad; asumir que un objetivo de área recibe daño sin resolución; leer `actuation_turns` como tiempo real; omitir el requisito de HP positivo de Pride; dar por terminada la batalla antes de Última llama; tratar la presentación como fuente de verdad; mezclar variantes de balance.

**Criterio de aprobación:** reconstruir sin consultar la solución las seis reglas, explicar al menos una cadena causal completa (acción, cambio de estado, activación de una política, acontecimiento y desenlace), superar la admisión y acreditar al menos una observación real de las ramas estudiadas. Si aún no hay ejecución dirigida, marque esa evidencia como pendiente, no como aprobada.
