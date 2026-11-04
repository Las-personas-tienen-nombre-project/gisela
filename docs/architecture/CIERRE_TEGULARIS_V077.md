# GISELA — cierre integrado del taller de Tegularis (v0.7.7)

Estado: **integración comprobada; certificación de desenlaces naturales incompleta**.

## Alcance y autoridad

La compilación autoral es `gisela/packages/tegularis_the_son_of_the_volcan/build_v077.py` y produce `09_cierre_autoral_v077.package.json` desde la base v0.7.2. No se reescribieron las reglas originales de S.O.F.I.A., TRAITS, DICE o los relojes narrativos. El encuentro sigue utilizando Observe/Act, la sesión transaccional y el gateway. El motor no contiene identificadores de Tegularis ni fórmulas especiales para combate.

## Decisiones autorales incorporadas

- **Bless** cuesta exactamente **10 MP**, aplica **+2 al atributo principal del beneficiario durante tres turnos del beneficiario**, renueva al reaplicar y no acumula el modificador. Las variantes atienden a Parnecio, Gillius, Clarisa e Iosepus.
- **Protección** permite a Parnecio elegir a Gillius, Clarisa o Iosepus. Dura hasta el inicio del siguiente turno de Parnecio; una nueva elección no se permite mientras otra protección siga activa. El destinatario protegido no recibe el impacto interceptado.
- En **ataques grupales**, el defensor recibe **un único impacto desviado**, aunque él también sea un objetivo del ataque original. Los demás aliados siguen resolviendo sus ataques con sus propias tiradas.
- Primero se aplican **las defensas y reducciones del defensor**, y luego se aplica **el 50 % del daño restante**. La compilación usa división entera hacia abajo para resultados impares, una decisión de redondeo técnica que no estaba especificada expresamente.
- **Groupal Shield** tiene prioridad frente a la redirección de la explosión final y bloquea el daño de todo el grupo. **Wingblast** no paraliza al aliado cuyo impacto fue interceptado. La redirección no transmite automáticamente la condición de parálisis al defensor; la protección establecida solo sustituye el daño.
- La **explosión final** respeta esa redirección y se resuelve antes de la evaluación del desenlace.

## Historial causal

El registro transaccional conserva una secuencia auditada de `initiative`, `skill_started`, `dice_roll`, `contest_resolved`, `variable_changed`, `author_message`, `skill_played`, `event_triggered` y `encounter_completed`. Todos los elementos comparten el contador `sequence` del historial confirmado, y conservan `source` para relacionarlos con la habilidad o el acontecimiento que los originó.

Observe publica `actuation.causal`, una ventana de las últimas **40 entradas autorizadas**. Las variables numéricas se incluyen solo si figuran en `actuation.public_trace_variables`; el paquete autoriza 72 variables de salud, maná, TP, defensas y cálculos de combate. Las tiradas y concursos continúan publicándose también en sus campos de compatibilidad `rolls` y `contests`. La vista no consulta directamente el estado RNG ni reejecuta las tiradas.

El cliente textual de GLAUQUIR presenta esa secuencia mediante Observe y la muestra sin interpretar cadenas narrativas para deducir daño o resultados. Los acontecimientos confirmados son visibles tras Act; las operaciones rechazadas son descartadas íntegramente.

## Riesgos y límites

1. La protección de ataques individuales dirigidos a otros aliados no se demuestra en este encuentro porque las cartas individuales del dragón apuntan a Parnecio; las rutas de grupo y explosión sí tienen pruebas específicas.
2. El criterio de redondeo de la mitad se fijó provisionalmente en **piso** para permitir cifras enteras; debe confirmarse como regla autoral.
3. El historial expuesto es una **ventana de 40 hechos**, no una descarga pública íntegra de toda la transcripción. La sesión persistida retiene el registro completo.
4. Los finales `derrota` y `destruccion_mutua` tienen pruebas de disparadores con estados preparados, pero **no** se verificaron todavía en recorridos ordinarios sin modificaciones de estado. No se retocó el balance ni se forzaron pérdidas para fingir su alcanzabilidad.
5. `Protección` redirige daño y anula la incapacidad del objetivo cubierto en Wingblast; no se ha generalizado a redirección automática de cualquier efecto secundario arbitrario.

## Calidad

Se respeta la política de `tools/test_quality.py`/`tools/check_quality.py`: 700 líneas por archivo, 64 por función y tres parámetros explícitos. No se relajaron límites ni se agregaron excepciones de calidad.
