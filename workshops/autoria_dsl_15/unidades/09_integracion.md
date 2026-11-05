# Unidad 9 — Integración, trazabilidad y reproducción autónoma

**Objetivo.** Construir, admitir, ejecutar y explicar un encuentro declarativo completo sin copiar mecánicamente el paquete final. El alumno no programa Python y no altera las reglas productivas de Tegularis. El trabajo combina las unidades 1–8, y utiliza la documentación oficial del repositorio como referencia normativa.

**Prerrequisitos:** unidades 1–8, sus laboratorios pequeños, una ejecución satisfactoria por Observe/Act y capacidad de explicar los resultados de TRAITS, DICE y las prioridades NPC. **Conceptos nuevos:** semilla, estado autoritativo, instantánea, revisión, determinismo, restauración, compatibilidad, evidencia de cobertura y entrega reproducible.

## 1. Intención, regla, declaración y comprobación

La tarea final no consiste en rellenar un JSON de cientos de KB. Consiste en convertir una especificación de comportamiento en declaraciones propias, comprobarlas primero sobre el encuentro mínimo acumulativo y, finalmente, reconstruir **sin cambios de balance** las declaraciones canónicas del encuentro productivo.

El laboratorio 7 sigue siendo una práctica pequeña: contiene dos personajes, una habilidad, una respuesta guionizada y dos desenlaces; **no es la batalla productiva**. El archivo `packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json` sirve de referencia para las reglas de combate; `14_presentacion_semantica_v082d.package.json` muestra la presentación declarativa. No se deben mezclar los valores entre versiones sin justificarlo con los contratos y los paquetes reales.

## 2. Trabajo autónomo A — Mecánica nueva en el encuentro mínimo

**Especificación de comportamiento:** un defensor recibe una bonificación de evasión de +2 solo si participa como `defender` y la resolución lleva la etiqueta `evasion`. La misma entidad no recibe esa bonificación si actúa como `actor` ni cuando la resolución utiliza otras etiquetas. Cree una variante autónoma de `paquetes/04_progresivo/04_laboratorio.package.json`, declarando un rasgo propio de identificador distinto de `dodge`; asígnelo a Parnecio y sustituya la asignación inicial, sin editar el archivo distribuido. Explique el significado de `id`, `entity_kinds`, `when`, `role`, `all_tags`, `slot` y `amount` a partir de las referencias del repositorio.

**Antes de ejecutar:** escriba los cuatro resultados esperados (defensor/evasión, atacante/evasión, defensor/sin evasión, defensor/evasión con una etiqueta adicional). Prediga los aportes numéricos. Admita su copia y repita las comprobaciones con los procedimientos docentes documentados. Una admisión sin evidencia de los cuatro contextos no satisface el ejercicio.

**Respuesta de referencia:** el rasgo original `dodge` en el paquete de práctica y el estudio del paquete canónico; no se entrega un JSON nuevo con el trabajo resuelto. El script `evaluacion/comprobar_puentes_04_06.py` verifica **la referencia distribuida**, no corrige por sí mismo la entrega del alumno.

## 3. Trabajo autónomo B — Prioridad NPC real

**Especificación de comportamiento:** Clarisa debe intentar primero Curación cuando sea admisible; si la guarda o los recursos no permiten jugarla, debe evaluar Concentración; si ninguna candidata procede, debe registrarse el hecho declarado en `otherwise`. Utilice como base una **copia** de `packages/tegularis_npc_prioridades_v03.package.json`, donde `play_first_skill` ya es un contrato público real. Prediga y ejecute tres situaciones: maná suficiente y heridas, maná insuficiente y guarda falsa en la primera opción; examine la rama `otherwise` con las restricciones reales del paquete.

**No confunda mecanismos:** en `paquetes/06_progresivo`, `play_skill` ejecuta una respuesta escrita en el guion. Eso no prueba elección autónoma. El ejemplo v0.3 utiliza una lista de candidatos y una operación `play_first_skill`; la versión de balance usa además `actuation.participants`. Los tres mecanismos están relacionados, pero sus estructuras no son intercambiables.

**Comprobación de referencia del instructor:** `PYTHONPATH=. python -m pytest -q engine/tests/test_npc_skill_priorities.py`. Esta prueba usa código de infraestructura existente: el alumno no tiene que programarla.

## 4. Trabajo autónomo C — Reconstrucción de Tegularis

**Antes de empezar**, use la [secuencia de hitos, rutas y evidencias](../evaluacion/09_integracion/HITOS.md). Cada paso debe validarse sobre la ruta que usted creó; los paquetes distribuidos no sustituyen el trabajo propio.


El alumno recibe el comportamiento exigido, no una copia con huecos arbitrarios: cinco personajes y sus fichas; S.O.F.I.A.; recursos y variables; rasgos y contribuciones; habilidades y concursos; turnos, candidatos y políticas; Pride, muerte, Última llama y los desenlaces; presentación separada de las reglas. Debe justificar cada declaración indicando la intención, el identificador, su dependencia y el efecto esperado. Construya el paquete progresivamente y use la referencia productiva solo para verificar fidelidad de reglas y balance, nunca para sustituir su explicación.

**Secuencia de hitos comprobables:** (1) fichas e instancias; (2) condiciones, recursos y referencias; (3) rasgos con activación y no activación; (4) `Slash`, `Double Slash` y `Blai`; (5) actuación y políticas NPC; (6) estados, Firebreath, Pride y Última llama; (7) condiciones de cierre; (8) una presentación que no cambie el estado lógico. En cada hito se exige admisión, ejecución y una explicación de la consecuencia observada. Los ejercicios de integración de las unidades 2–8 son material de contraste, no sustituyen este recorrido autónomo.

## 5. Observe, Act, determinismo y restauración

1. Admita el paquete con `PYTHONPATH=. python -m gisela.contracts.admit_package RUTA_DEL_PAQUETE`.
2. Ejecute con `python tools/glauquir.py --package RUTA_DEL_PAQUETE --auto`. Repita con selección interactiva para cubrir alternativas, sin inventar identificadores de acción.
3. Documente las acciones ofrecidas por Observe, la `revision`, el `action_id` transmitido por Act y los acontecimientos confirmados. No deduzca causas solo de cambios de HP ni de la proximidad temporal de mensajes.
4. Con el procedimiento público de sesión documentado en `docs/architecture/API_CLIENTES.md`, compare dos sesiones iniciadas con la misma semilla y la misma secuencia de decisiones. La igualdad esperada se refiere al estado lógico y al historial confirmados.
5. Guarde una instantánea, restáurela mediante la interfaz pública existente y compare estado y observación. Repita una acción válida después de restaurar. La reproducción de una semilla por sí sola no demuestra persistencia.
6. Cambie la presentación sin modificar las declaraciones lógicas, mantenga semilla y decisiones, y verifique invariancia del estado lógico.

No se declarará reproducido todo Tegularis porque una ronda termine correctamente. La cobertura de cada desenlace y de las ramas de Última llama exige ejecuciones dirigidas independientes y sus registros.

## 6. Entrega y evaluación

Entregue: (a) paquete construido y su identificación de versión; (b) lista de referencias oficiales usadas; (c) matriz intención → regla → declaración → predicción → observación; (d) comandos, semillas y registros; (e) evidencia de las cuatro situaciones de TRAITS y las tres de NPC; (f) igualdad determinista y restauración o descripción exacta del fallo; (g) diferencias frente al canon, justificando que no se ha cambiado el balance.

**Criterios de aprobación:** declaración válida (20 %), comprensión y explicación causal (30 %), verificación en situaciones positivas y negativas (20 %), reproducción y compatibilidad con Tegularis (20 %), documentación de determinismo y restauración (10 %). La mera copia del paquete canónico no alcanza aprobación, aunque funcione. El instructor comprueba las evidencias usando la matriz en `evaluacion/09_integracion/RUBRICA.md`.

**Errores frecuentes:** equiparar JSON válido y paquete admitido; equiparar admisión y ejecución; creer que un bono equivale a éxito automático; confundir `play_skill`, `play_first_skill` y `actuation.participants`; mezclar paquetes de distintas versiones; asumir que la narración refleja causalidad; presentar una ejecución interrumpida como aprobada.

**Fuentes normativas:** `docs/guides/CREAR_PAQUETE.md`, `gisela/contracts/v1_5/`, `traits/README.md`, `dice/README.md`, `docs/architecture/API_CLIENTES.md` y los paquetes productivos del repositorio. Esta unidad no establece una especificación paralela del DSL.
