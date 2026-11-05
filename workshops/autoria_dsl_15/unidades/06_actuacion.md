# Unidad 6: Turnos, actuación y políticas NPC

**Objetivo.** Interpretar y modificar las reglas declarativas del turno de Tegularis; explicar cómo se pasa de una observación pública a una acción autorizada y cómo los candidatos NPC se relacionan con las habilidades. La actividad se realiza sin programar en Python.

**Prerrequisitos:** unidades 1 a 5. **Conceptos nuevos:** iniciativa, atributo principal, umbral de acciones, participante, candidato NPC, guarda `when`, selección de acciones, Observe/Act, revisión de sesión, política de acontecimiento, condición de desenlace y rechazo de acciones no autorizadas.

**Referencia ejecutable:** `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`. Los ejercicios son copias completas y no modifican el canon. Los campos mostrados son fragmentos reales, no paquetes independientes.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 6](../paquetes/06_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. Intención, regla y ejecución

Queremos que Gillius actúe como combatiente, Clarisa como apoyo, Iosepus como mago y Tegularis como antagonista, pero **no** escribiremos un programa diferente para cada uno. Declararemos qué participantes existen, qué atributo influye en sus acciones y qué instancias de habilidad puede considerar el sistema. El motor mantiene el estado, calcula turnos y comprueba requisitos; el presentador GLAUQUIR muestra acciones disponibles y transmite decisiones por la interfaz pública.

La distinción es crucial: **un candidato no garantiza una acción ejecutada**. Su instancia debe existir, estar permitida por sus requisitos y corresponder al turno; también puede tener una guarda adicional. Una lista de candidatos tampoco debe interpretarse automáticamente como un árbol de decisiones que el autor programó en Python.

## 2. Iniciativa y número de acciones

En el paquete productivo se declara:

```json
"actuation": {
  "initiative_die": 10,
  "base_actions": 1,
  "thresholds": [
    {"at": 7, "actions": 2},
    {"at": 10, "actions": 3}
  ]
}
```

Este fragmento omite otras propiedades de `actuation`. `initiative_die` configura el dado de iniciativa. `base_actions` establece la base; `thresholds` describe umbrales a partir de los cuales pueden obtenerse dos y tres acciones. El atributo principal de cada participante y sus contribuciones de TRAITS intervienen en el cálculo correspondiente. **No confunda el dado de iniciativa con el dado de una tirada de ataque ni el umbral con un costo de TP.**

La iniciativa y el número de acciones resultantes los calcula el motor: no son valores que el autor deba asignar manualmente tras cada tirada. Para observar el resultado real, consulte `observe()` y su sección `actuation`; no intente deducirlo solamente de la ficha JSON.

## 3. Los cinco participantes

La declaración canónica separa al personaje controlado de los participantes con candidatos:

```json
{"character": "parnecio", "main_stat": "strength", "allow_pass": true}
```

Parnecio no tiene lista de `candidates` en su declaración. Una selección concreta debe proceder de las acciones ofrecidas al jugador. En cambio, Gillius tiene:

```json
{
  "character": "gillius",
  "main_stat": "strength",
  "candidates": [
    {"skill_instance": "stance_aggressive_01"},
    {"skill_instance": "grito_de_guerra_01"},
    {"skill_instance": "eviscerate_01"},
    {"skill_instance": "hachazo_01"}
  ],
  "allow_pass": true
}
```

Clarisa usa `openness` y 19 candidatos; Iosepus usa `intelligence` y 12; Tegularis usa `strength` y 6. `allow_pass` permite considerar pasar dentro de las reglas del contrato, pero no obliga a hacerlo. La referencia completa de habilidades está en `initial_state.skills` y `cards`; no se crean habilidades simplemente escribiendo un nombre en `candidates`.

Observe dos responsabilidades distintas: la **definición de la habilidad** describe requisitos y consecuencias (Unidad 5); la **participación** decide qué habilidades pueden entrar en la selección NPC. Cambiar el orden de dos candidatos modifica una regla declarativa de selección, pero el resultado concreto depende también del estado y de los requisitos.

## 4. Guardas, prioridades y candidatos

Un candidato puede incluir una condición `when`, utilizando el mismo DSL de condiciones estudiado en la Unidad 3:

```json
{"skill_instance": "firebreath_01", "when": {"constant": false}}
```

En un ejercicio, este ejemplo añade una guarda siempre falsa a una copia de Tegularis. No se pretende equilibrar el combate: se busca aprender por qué un candidato declarado puede no estar disponible. Retire la guarda añadida para restaurar el comportamiento original. Una guarda falsa no borra ni invalida la habilidad en su definición; solamente impide seleccionar ese candidato por esa vía.

No reduzca las políticas NPC al orden de una lista. La admisibilidad de una acción depende asimismo del estado, sus requisitos, las instancias disponibles y la autorización del motor. Para practicar una **prioridad condicional explícita** con alternativas y `otherwise`, examine el contrato real `play_first_skill` del paquete `packages/tegularis_npc_prioridades_v03.package.json` y la prueba `gisela/engine/tests/test_npc_skill_priorities.py`. Este ejemplo utiliza un guion con nodos y no debe confundirse con el bloque `actuation.participants` del encuentro completo.

## 5. Acontecimientos y desenlaces: políticas diferentes

El paquete tiene `actuation.event_policies`, con `id`, `phase`, `when` y `effects`, y `actuation.outcome_policies`, con condiciones de término. `pride_of_the_volcan_son` tiene fase `immediate`: su condición puede conceder el efecto `ef_pride_volcan`. `ultima_llama` utiliza `after_action`, con acciones y desenlaces propios. Las condiciones de victoria, derrota y destrucción mutua son políticas de desenlace. **No son listas de habilidades a elegir por un NPC**: son reglas del ciclo de vida que reaccionan a un estado confirmado.

## 6. Observe y Act: quién decide y quién confirma

1. **Observe:** el cliente pide la vista pública de sesión. Allí encuentra `session_id`, `revision`, `actions` y `actuation` (entre otros datos). Observe no altera el estado.
2. **Elección:** el cliente selecciona un `action_id` que haya sido ofrecido y esté habilitado. No está autorizado a escribir arbitrariamente un ataque o manipular HP.
3. **Act:** envía `session_id`, `revision` y `action_id` de esa vista. GISELA confirma la acción y aumenta la revisión cuando corresponde.
4. **Nueva observación:** el cliente vuelve a consultar el estado y los acontecimientos confirmados. Si una acción se rechazó, no debe presentarse como ejecutada.

**Ejemplo conceptual, no sintaxis JSON de paquete:** "si aparece Slash entre las acciones habilitadas, transmitir su `action_id` con la revisión actual". El formato preciso de la solicitud se estudia en el esquema público `gisela/contracts/v1_5/act.schema.json` y en `gisela/engine/tests/test_actuation_public_v073.py`. Un identificador inventado o una revisión caducada se rechazan sin mutar el estado; esta garantía se comprueba en las pruebas del repositorio.

## 7. Ejercicios guiados y predicciones

Los cinco primeros archivos `ejercicios/06_actuacion/*.package.json` son **paquetes completos válidos con una alteración para investigar**. Cada solucionario restaura exactamente el paquete productivo. Antes de consultar la respuesta, escriba: intención, propiedad modificada, efecto esperado, validación, observación y explicación causal.

1. **`01_iniciativa`:** `initiative_die` vale 8 en lugar de 10. Localice el parámetro, restáurelo a 10 y explique qué tirada cambia y cuáles (ataque y daño) no están definidas por este campo. No prometa un orden fijo sin ejecución.
2. **`02_umbrales`:** el primer umbral subió de 7 a 8. Restáurelo. Prediga la diferencia para un valor efectivo de 7 y explique por qué el segundo umbral permanece en 10.
3. **`03_atributo`:** Clarisa tiene `main_stat: strength` en lugar de `openness`. Restáurelo y explique qué responsabilidad tiene este atributo frente a los requisitos de sus cartas.
4. **`04_candidatos`:** Gillius tiene intercambiados los dos primeros candidatos. Localice la diferencia, restituya el orden productivo y explique por qué, aunque el orden importe, no hay garantía de que la primera habilidad sea ejecutable en cualquier estado.
5. **`05_guarda`:** `firebreath_01` de Tegularis tiene una guarda falsa añadida. Elimine exclusivamente la guarda y justifique la diferencia entre una habilidad inexistente y una habilidad temporalmente excluida de la selección.
6. **`06_referencia_invalida`:** la primera candidata de Tegularis apunta a `habilidad_inexistente`. El paquete está diseñado para ser rechazado por admisión; localice la referencia y restáurela a `firebreath_01`, sin eliminar el candidato.

**Ejercicio de integración adicional (sin solución predigerida):** abra el paquete de prioridades v0.3, encuentre `play_first_skill` en `respuesta_npc` y explique qué cambia entre una alternativa disponible, una descartada por `when` y la rama `otherwise`. Use el caso de Clarisa y maná insuficiente como contraste. No traslade literalmente ese bloque a `actuation.participants`: son contratos situados en estructuras diferentes.

## 8. Recorrido autónomo

Sin abrir los solucionarios, reciba esta especificación: "El dado de iniciativa tiene diez caras; un resultado efectivo de 7 habilita dos acciones y uno de 10, tres. Clarisa usa Openness, Gillius da preferencia a Stance Aggressive antes de Grito de guerra y Tegularis puede considerar Firebreath. Ninguna acción NPC puede referenciar una instancia inexistente". Reconstruya los cinco valores canónicos, repare el error de referencia y entregue una tabla de intención, campo, predicción, admisión y resultado observado. Añada una explicación de por qué `Act` no acepta un `action_id` inventado.

## 9. Comprobación y errores frecuentes

Desde la raíz del repositorio, valide cualquier ejercicio corregido:

```bash
PYTHONPATH=. python -c "from pathlib import Path; from gisela.contracts.admit_package import admit_package_file; print(admit_package_file(Path('workshops/autoria_dsl_15/ejercicios/06_actuacion/01_iniciativa.package.json')).digest)"
```

Ejecute una ronda por la interfaz de GLAUQUIR:

```bash
python -m gisela.cli.glauquir --auto --actuation --rounds 1 --package workshops/autoria_dsl_15/ejercicios/06_actuacion/01_iniciativa.package.json
```

La comprobación de instructor, **no requerida al alumno**, es `PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_unidad_06.py`. Para observar el rechazo de acciones indebidas y la restauración de sesión hay pruebas específicas en `gisela/engine/tests/test_actuation_public_v073.py`.

**Errores frecuentes:** inferir que `candidates` ejecuta todos los ataques; creer que el primer candidato siempre se puede usar; confundir `initiative_die` con un modificador de ataque; alterar una ficha cuando el cambio corresponde a `main_stat`; confundir `event_policies` con la política NPC; inventar nombres de instancias; tomar mensajes de interfaz por cambios confirmados; intentar ejecutar `Act` con revisiones caducadas.

**Criterios de aprobación:** el alumno explica las cinco declaraciones, repara los seis ejercicios, anticipa los casos límite de umbrales, diferencia una guarda de un requisito de habilidad, distingue acción ofrecida de resultado confirmado, valida sus paquetes y describe por qué Observe no muta estado ni Act permite acciones no ofrecidas. Una ronda genérica no certifica por sí sola que todas las alternativas NPC se hayan ejecutado; las pruebas dirigidas complementan esa evidencia.
