# ADR-019 — Evaluaciones visibles y resultados preparados de DICE

**Fecha:** 30 de octubre de 2026

**Revisión:** 2 — propuesta de políticas de continuación, retirada y persistencia.

**Estado:** PROPUESTA, NO APROBADA EN SU TOTALIDAD

**Base:** ADR-001–008, ADR-012, determinismo `sha256_counter_v1` y precisión aprobada de ADR-007/008 del 30-10-2026.

## 1. Motivación y alcance

**DECIDIDO por el autor:** GISELA debe permitir obtener y mostrar los dados y su resultado **antes de aplicar sus consecuencias**. El juego debe poder ocultar la tirada, mostrarla o exigir que el jugador confirme haber visto el resultado. El requisito pertenece al motor y no a Ren'Py ni a una aventura concreta.

**PROPUESTA de implementación:** establecer una frontera confirmada entre la evaluación y sus efectos, sin cambiar el concepto de turno (ejecución efectiva de un nodo), sin mantener transacciones abiertas a través de interfaces gráficas y sin crear un RNG propio de DICE dentro de GISELA.

## 2. Contratos y separación de responsabilidades

- **DICE** recibe un perfil de resolución, entradas numéricas ya resueltas, modificadores, contexto autorizado y una fuente aleatoria inyectada; devuelve dados, resultado interpretado y trazabilidad. No modifica el mundo ni conoce la sesión de GISELA.
- **GISELA** autoriza la intención, fija el resultado cuando corresponda, lo persiste, lo proyecta a clientes y aplica las consecuencias en una transacción posterior y atómica.
- **ALBERTO** administra hechos, relaciones y propiedades que cambian después de la aplicación; **MARY** evalúa las consecuencias confirmadas; **TRAITS** y **S.O.F.I.A.** suministran datos antes de construir la solicitud neutral.
- **Clientes** como GLAUQUIR o Ren'Py no tiran dados por su cuenta ni determinan qué consecuencias aplicar. La animación presenta un resultado ya fijado por el motor.

## 3. Dos vías de ejecución

### 3.1. Tirada oculta: una transacción

`Act` autoriza la evaluación → DICE evalúa en el borrador → GISELA aplica las consecuencias y reacciones → commit único de estado/RNG o rollback íntegro.

Se conserva la semántica transaccional de `roll` actual mientras no se introduzca un contrato de evaluación pública.

### 3.2. Tirada visible: dos transacciones

**A. Preparar y fijar la evaluación:**

1. Validar intención, contexto, permisos, perfil y valores utilizados.
2. Evaluar DICE usando la copia del RNG confirmado del anfitrión.
3. Confirmar **únicamente** el resultado inmutable de la evaluación, el avance del RNG, el registro asociado y la revisión de sesión.
4. Publicar una proyección autorizada del resultado; no aplicar todavía el efecto narrativo ni disparar acontecimientos de éxito o fracaso.

**B. Aplicar el resultado:**

1. Recibir `Act` autorizado para continuar, sin sortear de nuevo.
2. Validar la identidad, vigencia del contexto relevante y la no aplicación anterior del resultado.
3. Ejecutar consecuencias y reacciones, incluida MARY, sobre un borrador.
4. Confirmar atómicamente mundo, historia y progreso, o conservar la evaluación fijada si falla la fase de efectos.

Las dos transacciones pertenecen al **mismo turno narrativo** cuando se originan dentro de un nodo. El contador `turn` no aumenta por separar la evaluación de sus efectos. Tampoco se modifica `world_time` sin una operación autoral explícita.

## 4. Estado persistente y exclusión de pendientes

**PROPUESTO:** ampliar el esquema versionado de sesión con una evaluación fijada pendiente de aplicación, distinta de la `pending_transaction` auxiliar de ADR-001–005.

Datos mínimos de la evaluación: identificador de operación, procedencia e intención, perfil y versión, digest de entradas/contexto, valores individuales de dados, modificadores aplicados, resultado categórico, estado RNG anterior y posterior o prueba equivalente de consumo, política de presentación, estado de continuación y revisión de preparación (sin agregar un estado público de sesión).

Requisitos:

- La evaluación preparada es **inmutable** respecto de dados y resultado, aunque cambie su estado de aplicación.
- Máximo **un proceso causal pendiente** por sesión: no deben coexistir `pending_transaction` y evaluación visible en espera.
- Las consultas y exportaciones de solo lectura pueden mostrar el resultado autorizado, pero no consumir RNG ni aplicar efectos.
- Una restauración debe recuperar exactamente el mismo resultado. La versión del perfil y el paquete admitido deben validarse antes de aplicarlo.
- Un intento de doble confirmación debe ser rechazado o idempotente según un contrato explícito; nunca ejecutar efectos dos veces.
- No se permite ejecutar acciones mutantes ajenas mientras la evaluación bloquee una continuación obligatoria.

**No aprobado:** nombres definitivos de campos, estructura JSON, estados exactos ni política de persistencia histórica de evaluaciones aplicadas. No modificar `session.schema.json` antes de cerrar estas decisiones.

## 5. Política de presentación

- `hidden`: no se publica antes; resolución y efectos en un commit.
- `visible`: se presenta el resultado fijado y el cliente continúa siguiendo su política de presentación.
- `acknowledged`: se presenta el resultado fijado y se exige un acto explícito del jugador para aplicar efectos.

**PROPUESTO:** cada juego puede definir la política por perfil o evaluación. Una tirada visible nunca debe depender de la finalización de una animación para ser considerada ya fijada.

## 6. Políticas de continuación y abandono (PROPUESTAS, NO APROBADAS)

### 6.1. Compromiso antes de obtener un resultado

- Antes de ejecutar DICE, una intención voluntaria puede descartarse sin resultado ni consumo del RNG. Se conserva `cancel_pending` para las decisiones auxiliares que todavía no fijaron dados.
- Una vez fijada y publicada una evaluación, **por defecto no se permite cancelar la acción** para ignorar una tirada desfavorable. Cerrar el cliente o guardar no equivale a cancelarla.
- Si un juego admite retirarse **después** de ver los dados, debe declarar esa opción como **resultado alternativo con sus propias consecuencias**, no como una anulación silenciosa. Los dados originales permanecen consumidos y registrados.
- Las intenciones obligatorias deben resolverse; no ofrecen retirada salvo regla explícita que la autorice. No se crea una cancelación universal por utilizar DICE.

### 6.2. Nuevas tiradas y modificaciones posteriores

- Una repetición es una **nueva evaluación autorizada** por una regla del juego, con una causa identificable, coste y límite cuando corresponda. No es un reinicio de la primera evaluación.
- Repetir o modificar un resultado se realiza **antes** de aplicar las consecuencias finales y mediante otra transacción de GISELA. El consumo de recursos y el avance RNG de esa operación se confirman atómicamente.
- El resultado original se conserva como evaluación sustituida o antecedente; la evaluación vigente queda identificada sin ambigüedad.
- DICE calcula resultados y no decide si existe derecho a repetir. GISELA autoriza la regla del juego y registra la transición.
- El diseño predeterminado de DICE no obliga a ningún juego a incorporar repeticiones ni recursos.

### 6.3. Resultado pendiente y contexto de aplicación

- Después del commit de preparación, el resultado visible permanece **fijado y pendiente de aplicación**. `Observe` puede mostrarlo repetidamente sin consumir RNG.
- Mientras esté pendiente, GISELA bloquea otras mutaciones de la misma sesión que puedan alterar su contexto; solo se permiten las acciones de continuación o alternativas declaradas por el perfil, además de consultas y exportación.
- La continuación comprueba identificador de evaluación, revisión de sesión, paquete admitido y que la evaluación siga pendiente. Si algo no coincide, falla explícitamente y no vuelve a lanzar dados.
- Si una causa externa invalidara el contexto, la evaluación queda inmovilizada para resolución administrativa o una política declarada; **no** debe descartarse y reintentarse silenciosamente.
- Si aplicar las consecuencias falla técnicamente, mundo, MARY, historial causal y demás cambios de la fase de aplicación se revierten; el resultado fijado sigue pendiente y no se consume RNG adicional.

### 6.4. Confirmación exactamente una vez

- La aplicación de un `evaluation_id` solo puede confirmarse **una vez**. Una solicitud duplicada o con revisión caducada se rechaza con error identificable y jamás vuelve a ejecutar consecuencias.
- Esto ofrece la garantía **a lo sumo una aplicación** dentro de la sesión. Un cliente que pierda la respuesta puede consultar `Observe` para conocer el estado confirmado, en lugar de volver a tirar.
- No se requiere inicialmente un registro histórico ilimitado; sí un identificador estable y evidencia suficiente para impedir confirmar de nuevo la misma evaluación.

### 6.5. Presentación y continuación

- `hidden`: no crea espera pública; resolución y efectos en una transacción.
- `visible`: el motor publica un estado observable con los dados fijados; el cliente puede continuar automáticamente **después de presentar ese estado**. El avance se solicita mediante una acción pública, nunca desde una animación que genere otra tirada.
- `acknowledged`: se requiere una confirmación explícita del jugador. El cliente no puede sustituirla por un avance automático.
- Ren'Py, GLAUQUIR u otro cliente presentan la misma proyección autorizada. Ni la animación ni la interfaz calculan o modifican el resultado.

### 6.6. Guardado, restauración y compatibilidad

- El estado preparado se exporta en el snapshot confirmado y se restaura **con idénticos valores de dados, modificadores, resultado y consumo RNG**. No se hace replay de la tirada al restaurar.
- El esquema de sesión deberá evolucionar de forma versionada (la versión exacta aún se decidirá). El nuevo contrato será distinto de `pending_transaction` y garantizará exclusión mutua con él.
- Antes de continuar, `restore_session` y la validación semántica verificarán paquete/digest, versión del perfil, origen, identidad y consistencia del pendiente; incompatibilidad significa **rechazo explícito**, nunca nueva tirada.
- La migración de sesiones antiguas sin evaluaciones preparadas se diseñará por separado. No se alterará retroactivamente el significado de la sesión v1.2.
- Esta garantía opera dentro de una línea de sesión. Cargar deliberadamente un guardado **anterior** a la tirada, editar el archivo o recurrir al rollback narrativo requiere una política de producto o de juego aparte; no puede impedirlo por sí solo un RNG determinista local.

### 6.7. Publicación y estado mínimo a persistir

Se propone una estructura futura `pending_evaluation` (nombre provisional), con identificador estable, procedencia, perfil y versión, entradas efectivas o huella validable, dados individuales, modificadores, resultado, prueba del consumo RNG, revisión de preparación y modo de presentación. La fase de aplicación se deduce de la existencia del pendiente más el registro de confirmación; no es necesario convertir cada fase conceptual en un estado público nuevo.

Solo habrá **un proceso causal pendiente** por sesión. La decisión de retener un historial de todas las tiradas se pospone: la primera versión requiere trazabilidad suficiente para la evaluación actual y para las sustituciones autorizadas.

## 7. Pruebas de aceptación propuestas

- **D01:** `hidden` conserva atomicidad y rollback actual.
- **D02:** preparar una tirada visible confirma RNG y resultado, pero no modifica mundo, MARY ni hechos derivados.
- **D03:** `Observe`, exportación y restauración mantienen dados idénticos sin consumir RNG.
- **D04:** aplicar una evaluación confirmada produce consecuencias exactamente una vez y no aumenta `turn` por separado.
- **D05:** el error durante aplicación mantiene evaluación fijada y mundo sin cambios parciales.
- **D06:** mientras existe una evaluación visible obligatoria, otras acciones mutantes quedan bloqueadas.
- **D07:** una evaluación con perfil/versionado incompatible se rechaza de manera explícita.
- **D08:** DICE funciona sin S.O.F.I.A., TRAITS, MARY ni entidades del demo.
- **D09:** cancelar antes de tirar no consume RNG; después de publicar, `cancel_pending` no puede descartar los dados.
- **D10:** guardar, salir, restaurar o observar repetidamente no modifica el resultado preparado.
- **D11:** una aplicación duplicada o con revisión caducada no repite efectos.
- **D12:** una retirada posterior permitida produce sus consecuencias declaradas y conserva la trazabilidad de la tirada original.
- **D13:** una repetición expresamente autorizada registra original, nueva evaluación, coste y RNG en una operación atómica.
- **D14:** una evaluación preparada bloquea acciones mutantes no autorizadas de su contexto.
- **D15:** un snapshot o perfil incompatible se rechaza sin nueva tirada.

**Alcance de implementación actual:** ninguno de D02–D07 está implementado por el ejecutor del ZIP. `roll` solo funciona dentro del borrador de la transacción normal.

## 8. Condiciones para aprobar e implementar

La presente revisión propone reglas concretas para cancelación tras revelar dados, idempotencia, repetición e invalidación de contexto. **Todas continúan pendientes de aprobación autoral.** Antes de implementar, deben fijarse la versión de sesión, los esquemas y las acciones/proyecciones públicas. La implementación se hará después de validar las pruebas de frontera de ADR-007/008. No debe introducirse un motor de turnos paralelo ni una segunda fuente de aleatoriedad.
