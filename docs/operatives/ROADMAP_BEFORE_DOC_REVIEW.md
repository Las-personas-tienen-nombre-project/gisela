# Roadmap operativo. Las personas tienen nombre y GISELA

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**H4.6.0: MARY v1, implementado y verificado por baterías independientes.** Condiciones comunes, misiones opcionales, objetivos persistentes/reversibles y yields transaccionales. Evidencia: [cierre MARY](MARY_REVISION_Y_CIERRE.md). La adaptación narrativa H4.6 y la integración Ren'Py siguen pendientes.

**Actualización inicial:** 29 de octubre de 2026.

**Última revisión técnica:** 30 de octubre de 2026. H2, H3.4a a H3.4d, H4, H4.5 y H4.5f tienen pruebas y documentación. H4.6 (autoría canónica) precede a H5.

**Base verificada:** GISELA MVP v0.1, schemas 1.2, arquitectura consolidada disponible en `docs/architecture/GISELA_Arquitectura_Consolidada_v1_5.md`.

**Propósito:** mantener en un solo lugar el avance técnico, los criterios de aceptación y el orden de trabajo del motor y de su primer anfitrión Ren'Py. Este documento no sustituye las decisiones arquitectónicas ni establece acontecimientos de la novela.

## 1. Cómo utilizar este documento

Los hitos se clasifican como TERMINADO, EN CURSO, PENDIENTE o BLOQUEADO. Se considera TERMINADO un hito únicamente cuando existe su implementación o documento comprometido, se han satisfecho los criterios de aceptación y queda indicada la comprobación realizada. Un contrato redactado no equivale a una función implementada; un archivo Ren'Py presente no equivale a una demo jugable.

Al actualizar el roadmap se debe registrar la fecha, el alcance efectivo, las pruebas ejecutadas y cualquier limitación que permanezca abierta. Si cambia una decisión de arquitectura, primero debe actualizarse el registro de ADR correspondiente. Los detalles narrativos y editoriales se revisan por separado y solo con autorización del autor.

## 2. Resumen de hitos

| Hito | Área | Estado | Dependencia principal |
| --- | --- | --- | --- |
| H0 | Arquitectura, schemas y determinismo | TERMINADO para la base actual | Ninguna |
| H1 | Ejecutor mínimo y CLI | TERMINADO para el MVP v0.1 | H0 |
| H2 | Transacciones interactivas pendientes para el subconjunto ejecutable | TERMINADO | H1 |
| H3 | ALBERTO ampliado y mecánicas de azar futuras | EN CURSO: H3.1 a H3.3 implementadas | H2 para las operaciones con decisiones auxiliares |
| H4 | Exploración, interacción, consultas y CLI de referencia | TERMINADO para el subconjunto ejecutable | H2 y H3 |
| H4.5 | GLAUQUIR: juego, consulta, historial y autoría | TERMINADO para el subconjunto ejecutable | H4 |
| H4.5f | Endurecimiento de escenas, presencia e inspección | TERMINADO | H4.5 |
| H4.6.0 | MARY v1: progresión, objetivos y misiones declarativas | TERMINADO | H4.5f |
| H4.6 | Primera jornada canónica y pruebas de estrés en GLAUQUIR | PENDIENTE | H4.6.0 |
| H5 | Adaptador y pruebas con Ren'Py | PENDIENTE | H4.6 y API estable |
| H6 | Vertical narrativa de la novela visual | PENDIENTE | H4 y H5 |
| H7 | Verificación integral y preparación de entrega | PENDIENTE | H6 |

La secuencia propuesta admite trabajo preparatorio en paralelo, pero no se deben declarar completas capacidades que dependan de operaciones todavía inexistentes. La prioridad actual es H4.6: adaptar el guion oficial y probarlo en GLAUQUIR antes de integrar Ren'Py. H3.1 a H3.3 ya están implementados y cuentan con pruebas.

## 3. H0. Arquitectura, contratos y determinismo

**Estado: TERMINADO para los contratos actuales.**

Se consolidaron las responsabilidades de GISELA, ALBERTO y S.O.F.I.A.; se registraron las ADR-001 a ADR-017; se actualizaron 13 JSON Schemas a la versión 1.2 y se incorporó una puerta de admisión que exige JSON válido, estructura correcta y coherencia semántica. También se implementaron el digest canónico `GISELA-CJSON-1` y el generador `sha256_counter_v1`, ambos con vectores de prueba.

**Evidencia:** `gisela/contracts/verify_contracts.py`, `gisela/contracts/test_*.py`, `docs/determinism/VECTORES.json` y `python tools/check_project.py`.

**Límite:** los contratos describen más operaciones de las que ejecuta el MVP. El RNG está probado por separado e integrado en H2 mediante `roll`, con pruebas de cancelación, restauración y rollback.

## 4. H1. MVP de ejecución narrativa por consola

**Estado: TERMINADO para el alcance reducido aprobado.**

Se implementó la API `new_session`, `restore_session`, `observe`, `act` y `export`. El motor ejecuta narración, diálogo, elecciones, condiciones, efectos básicos, cambios de escena, transiciones y finales. Puede transferir un objeto, registrar un hecho persistente, modificar variables y ejecutar una reacción declarativa sobre la misma transacción.

El paquete `gisela/packages/mvp_casete.package.json` ofrece dos recorridos: prestar el casete y guardarlo. Las pruebas comprueban la diferencia de consecuencias, el rechazo de acciones ajenas a la proyección, la consistencia del guardado, la restauración, los conflictos de reglas, la detección de ciclos y la ausencia de cambios parciales cuando una acción falla.

**Evidencia de la base recibida:** 148 pruebas de contratos y 21 del ejecutor, más dos recorridos automáticos. Se repiten mediante `python tools/check_project.py`.

**Cierre limitado:** la vertical permite comprobar la autoridad narrativa única, pero no demuestra todavía todas las garantías de ADR-001 a ADR-005. El anfitrión Ren'Py no participa de esas pruebas.

## 5. H2. Transacciones interactivas pendientes

**Estado: TERMINADO para los orígenes y operaciones ejecutables en H2.**

**Objetivo:** permitir que una acción o cadena reactiva solicite decisiones adicionales antes de confirmar consecuencias, sin publicar ni guardar un mundo provisional como si fuera definitivo.

Trabajo previsto:

1. Representar una única transacción pendiente por sesión, con origen, intención, contexto y respuestas ya entregadas.
2. Presentar la solicitud auxiliar mediante `Observe`, sin exponer modificaciones del mundo todavía no confirmadas.
3. Restringir `Act` durante la espera a las respuestas pertinentes y a la cancelación autorizada por el origen voluntario de la operación.
4. Guardar el estado confirmado junto con la intención pendiente y reconstruir la operación determinísticamente al restaurar.
5. Confirmar exactamente una vez al completar todas las respuestas; rechazar los errores sin cambios parciales.
6. Probar respuestas inválidas, cancelación, restauración intermedia, conflictos, ciclos y decisiones automáticas obligatorias que no pueden eludirse.

**Criterio de aceptación:** una misma secuencia de respuestas debe producir el mismo estado final antes y después de guardar y restaurar; cancelar una operación voluntaria debe dejar intactos mundo, historial y RNG; ninguna acción ajena a la solicitud pendiente puede intercalarse.

**Avance comprobado en H2:** el ejecutor implementa solicitudes `select_one` para `grant_skill` con `overflow: require_choice`, cuando mano y reserva están llenas. Guarda solo el estado confirmado junto con la fuente de la operación y sus respuestas; reconstruye y verifica las solicitudes al restaurar. Admite la cancelación de operaciones voluntarias, impide cancelar un avance automático obligatorio y rechaza acciones no ofrecidas. Las pruebas cubren solicitudes consecutivas y conflictos posteriores a una respuesta, sin alteración del estado confirmado.

**Evidencia:** `gisela/engine/pending.py`, `gisela/engine/tests/test_pending.py`, `gisela/packages/h2_descarte.package.json`, `tools/play_mvp.py --package gisela/packages/h2_descarte.package.json`.

**Cierre de H2:** `new_session` puede suspender el primer turno en una solicitud obligatoria; el origen `session_start` se conserva en el guardado. Si falta escena inicial, el estado confirmado utiliza `preparing` y `preparing_for`, sin inventar una escena. Al restaurar se repiten el inicio y todas las respuestas desde el estado confirmado. `roll` escribe una variable numérica y consume el generador solamente al confirmar. Las pruebas cubren cancelación, restauración, conflictos después de un sorteo, errores de respuesta y el orden estable de reglas con RNG. El paquete `h2_inicio_azar.package.json` sirve como caso reproducible.

**Fuera del cierre de H2:** en aquel momento faltaban exploración, habilidades y Scoresheet. Las habilidades y Scoresheet se incorporaron después, en H3.4d y H3.4b respectivamente. Las acciones exploratorias se incorporaron después en H4. Las capacidades todavía no ejecutables se rechazan de forma explícita. No se ha probado aún la integración con Ren'Py.

**Referencias:** ADR-001 a ADR-005 y schemas `session`, `observe`, `act` y `result`.

## 6. H3. Operaciones de ALBERTO y aleatoriedad integrada

**Estado: EN CURSO. H3.1 a H3.3, H3.4a y H3.4b terminadas; H3.4c y H3.4d terminadas para el subconjunto ejecutable.**

**Objetivo:** ampliar las operaciones de mundo sin duplicar la autoridad transaccional de GISELA. El trabajo se organiza por capacidades necesarias y no por cantidad de clases o subsistemas nuevos.

**H3.1, responsabilidades:** se separaron consulta de instancias e identidades, operaciones de entidades, habilidades y ciclo de vida. El ejecutor separó proyección, recepción de acciones e inicialización. El validador semántico ahora distribuye sus reglas en módulos más pequeños, conservando su interfaz. Estado: TERMINADO PARA ESTA ETAPA.

**H3.2, operaciones de mundo:** se implementaron `move_character`, `learn_fact`, `set_belief`, `create_instance`, `remove_instance`, `move_skill`, `discard_skill` y `advance_time`. Se amplió `transfer` para permitir posesión por personajes o ubicación en lugares. Se añadieron las condiciones puras `knows`, `believes` y `has_skill`. Estado: TERMINADO PARA ESTA ETAPA.

**H3.3, garantías:** el registro transaccional de identidades impide reutilizar IDs retirados; las capacidades de habilidades y las referencias vivas se comprueban antes de modificar el borrador. Los errores revierten toda la operación. Se agregaron pruebas de rollback, restauración y conflictos. Se incorporó la regla automática de hasta 500 líneas por archivo técnico mantenido y 30 líneas por función Python, sin contar el docstring inicial. Estado: TERMINADO PARA ESTA ETAPA.

**H3.4a, TERMINADO:** propiedades y relaciones dirigidas con valores iniciales, operaciones `set`, `add` y `compare`, combinación de escrituras y rollback. **H3.4b, TERMINADO:** atributos base y actuales, efectivos calculados, modificadores de efectos activos, condiciones y Scoresheet. **H3.4c, TERMINADO:** aplicación, acumulación y vencimiento de efectos con consecuencias y restauración. **H3.4d, TERMINADO:** habilidades en ventanas de nodo, requisitos, resultados, retornos, consumo confirmado, cancelación y restauración. La vinculación de referencias contextuales debe tratarse cuando exista una fuente de contexto estable. Las acciones exploratorias corresponden a H4. No se declara terminado H3 global por tener un subconjunto de operaciones ejecutables.

**Criterio de aceptación para cerrar H3:** cada mecanismo efectivamente incorporado debe tener un caso jugable reproducible, pruebas positivas y negativas, garantías de rollback y restauración, documentación de precondiciones y rechazo anticipado de formatos no soportados.

**Evidencia:** `gisela/engine/tests/test_h3_world.py`, `tools/check_quality.py`, `tools/test_quality.py`, `python tools/check_project.py`, [referencia técnica de ALBERTO](../architecture/ALBERTO.md) y [catálogo de hallazgos H3](H3_REVISION_PLAN_IMPLEMENTACION.md).

## 7. H4. Exploración y consultas

**Estado: TERMINADO para el subconjunto ejecutable.**

El hito se desarrolló en cuatro etapas, todas respaldadas por pruebas y por un paquete narrativo ejecutable.

1. H4.1, exploración básica. Entrada a escenas, actores, elementos, acciones, visibilidad y procedencia exacta.
2. H4.2, interacción con el mundo. Examinar, transferir, desplazarse y conversar, con consecuencias declarativas, revalidación, transacciones pendientes y rollback.
3. H4.3, consultas de ALBERTO y S.O.F.I.A. Propiedades, relaciones, conocimiento, habilidades, hechos y Scoresheet mediante una API diagnóstica de solo lectura. El modo de desarrollo no sustituye las autorizaciones de Observe.
4. H4.4, CLI de referencia. Navegación, inspección, guardado, restauración, errores y recorrido completo de una historia breve.

**Evidencia:** `gisela/engine/tests/test_h4_exploration.py`, `gisela/packages/h4_exploracion.package.json`, `docs/guides/examples/ejemplo_exploracion.py`, `docs/guides/EXPLORACION_CLI.md` y [registro de revisión y cierre](H4_REVISION_Y_CIERRE.md).

**Límites históricos de H4:** la CLI no planificaba rutas automáticamente, las consultas de desarrollo podían revelar información oculta y las habilidades solo se ejecutaban en ventanas de nodos. H4.5 amplió este último punto con autorización explícita por escena. No se incorporaron referencias contextuales no vinculadas ni preparación exploratoria de mano.

## 7.5. H4.5. GLAUQUIR, cliente textual para jugar y escribir

**Estado: TERMINADO para las capacidades declaradas.**

H4.5.0 completó las proyecciones públicas y el registro de lectura persistente. H4.5a desarrolló la presentación de escenas, diálogos y menús. H4.5b agregó inventario, fichas y comandos contextuales. H4.5c incorporó habilidades autorizadas desde exploración. H4.5d completó `history`, guardado, restauración y depuración bajo demanda. H4.5e verificó un recorrido integral por CLI y las regresiones.

**Evidencia:** `gisela/engine/tests/test_h45_cli.py`, `gisela/packages/h45_cli.package.json`, `docs/guides/CLI_TEXTUAL.md`, `docs/operatives/INVARIANTES_H4_5.md` y [registro de revisión](H4_5_REVISION_Y_CIERRE.md).

GLAUQUIR significa GISELA's Lightweight Access Utility for Queries, User Interaction, and Rendering. No incorpora un parser de lenguaje natural ni un servidor MUD. Las decisiones siguen siendo acciones autorizadas por GISELA. Ren'Py permanece pendiente para H5.

## 7.6. H4.5f. Escenas y proyecciones endurecidas

**Estado: TERMINADO.** Se formalizó `scene.location` como vínculo opcional con un lugar físico de ALBERTO, se validó la co-ubicación del protagonista en entradas y confirmaciones, se filtraron actores y elementos vinculados por presencia, se agregaron descripciones públicas opcionales y se protegió la identidad de acciones ante cambios de visibilidad. GLAUQUIR es el nombre oficial del cliente textual y `tools/glauquir.py` su entrada preferida.

**Evidencia:** `gisela/engine/tests/test_h45f_scene.py`, [escenas y presencia](../architecture/ESCENAS_Y_PRESENCIA.md), [invariantes](INVARIANTES_H4_5F.md) y [revisión de cierre](H4_5F_REVISION_Y_CIERRE.md).

## 7.7. H4.6. Guion canónico y estrés desde GLAUQUIR

**Estado: PENDIENTE.** Adaptar la primera jornada de *Las personas tienen nombre* al paquete declarativo GISELA, distinguiendo los hechos aprobados de las decisiones interactivas por autorizar. Recorrer escenas y acciones reales desde GLAUQUIR y comprobar restauración, transacciones, historial, continuidad de ubicaciones, propiedad de objetos y determinismo. No añadir ramas narrativas no aprobadas ni lógica exclusiva de cliente.

**Criterio:** aventura canónica completa, legible y comprobable sin Ren'Py, con mapa de eventos, cobertura de caminos y pruebas de estrés documentadas.

## 8. H5. Integración con Ren'Py

**Estado: PENDIENTE.**

**Objetivo:** conectar una versión compatible del SDK Ren'Py con la API de GISELA, conservando la separación entre presentación y ejecución narrativa.

Trabajo previsto:

1. Seleccionar y registrar la versión de Ren'Py con la que se hará la integración.
2. Resolver el empaquetado y carga de las dependencias Python compatibles con esa versión.
3. Implementar un adaptador que convierta la proyección `Observe` en componentes visuales y envíe solicitudes `Act` sin reinterpretarlas.
4. Separar las preferencias visuales y de audio del estado narrativo.
5. Probar creación de sesión, elecciones, errores, guardado, restauración y paridad con los recorridos CLI.

**Criterio de aceptación:** ambos anfitriones deben obtener el mismo estado confirmado al ejecutar la misma secuencia de decisiones. La apertura del proyecto en el SDK, por sí sola, no constituye aceptación.

## 9. H6. Vertical narrativa de Las personas tienen nombre

**Estado: PENDIENTE.**

**Objetivo:** preparar un recorrido jugable representativo de la historia con contenido aprobado, utilizando el motor general y sin incrustar excepciones narrativas dentro de GISELA.

Trabajo previsto:

1. Delimitar las escenas y decisiones de la primera jornada jugable, con aprobación de su alcance narrativo.
2. Transformar el contenido elegido en nodos, escenas, cartas, reglas y estado inicial del paquete de autoría.
3. Comprobar continuidad de personajes, tiempos, objetos y conocimiento, con revisión editorial independiente.
4. Incorporar recursos visuales y sonoros únicamente cuando existan y su uso esté autorizado.
5. Verificar claridad, accesibilidad básica, guardado y continuidad del recorrido.

**Criterio de aceptación:** la vertical debe jugarse íntegramente en Ren'Py, desde el inicio hasta un cierre definido, con reglas ejecutadas por GISELA y pruebas de regresión para sus decisiones principales.

El paquete del casete es una prueba de contratos y no constituye una adaptación canónica definitiva.

## 10. H7. Verificación integral y entrega

**Estado: PENDIENTE.**

**Objetivo:** preparar una entrega repetible y comprobable del proyecto, diferenciando la calidad técnica de las aprobaciones editoriales y de derechos.

Trabajo previsto:

1. Ejecutar la batería completa de contratos, semántica, motor y pruebas de Ren'Py.
2. Comprobar restauraciones, revisiones antiguas, guardados incompatibles, fallos recuperables y ausencia de estados parciales.
3. Verificar que los recursos empaquetados correspondan a los autorizados y que los archivos de consulta no se distribuyan por accidente.
4. Revisar instrucciones de instalación, reproducibilidad y documentación operativa.
5. Registrar las versiones de Python, Ren'Py, schemas, motor y paquetes utilizadas en la entrega.

**Criterio de aceptación:** debe existir una compilación reproducible con un recorrido completo verificado en el SDK de destino, documentación acorde con la implementación y un inventario de restricciones conocidas.

## 11. Deudas y riesgos transversales

- **Compatibilidad de guardados:** cualquier cambio del paquete modifica su digest. No se deben migrar sesiones por inferencia ni ignorar diferencias de versión.
- **Contratos más amplios que el ejecutor:** un JSON semánticamente válido puede contener operaciones todavía no disponibles, en particular habilidades, referencias contextuales y acciones exploratorias. La comprobación de soporte debe permanecer separada de la admisión.
- **Determinismo:** la operación `roll` y la asignación de IDs ya usan el borrador transaccional. Las ampliaciones futuras deben conservar esa garantía.
- **Cadenas reactivas:** los conflictos y los ciclos deben continuar produciendo errores sin confirmaciones parciales.
- **Integración Python y Ren'Py:** la compatibilidad efectiva se comprobará contra un SDK determinado; no se debe presumir a partir de las pruebas offline.
- **Documentación:** las referencias de arquitectura, ALBERTO, operación y roadmap deben actualizarse con cada cambio. El registro de hallazgos H3 documenta qué se implementó y qué permanece fuera del ejecutor.
- **Material narrativo y derechos:** las referencias literarias, ilustraciones y música no están autorizadas para distribución por el solo hecho de encontrarse en el repositorio.

## 12. Registro de avance

| Fecha | Hito | Cambio comprobado | Evidencia |
| --- | --- | --- | --- |
| 29-10-2026 | H0 | Contratos 1.2, admisión semántica y perfiles de determinismo disponibles | Pruebas de `gisela/contracts/` |
| 29-10-2026 | H1 | MVP CLI v0.1 con dos recorridos y restauración de estados confirmados | `python tools/check_project.py` |
| 29-10-2026 | Documentación | README del proyecto, README de GISELA y roadmap reunidos en un parche | Verificación de aplicación del parche |
| 29-10-2026 | H2 | Espera al inicio de sesión, RNG transaccional y reproducción de solicitudes | `test_h2_closure.py`, `h2_inicio_azar.package.json` y `python tools/check_project.py` |
| 29-10-2026 | H2 | Decisión auxiliar, replay, cancelación y pruebas de atomicidad en la vertical de descarte | `gisela/engine/tests/test_pending.py` y `python tools/check_project.py` |
| 29-10-2026 | H3 | Primera etapa: operaciones de mundo, separación modular, pruebas de rollback y control de tamaño | `test_h3_world.py`, `tools/check_quality.py`, `python tools/check_project.py` |
| 30-10-2026 | Documentación | Guía rápida y README de entrada de ALBERTO y S.O.F.I.A.; ejemplos integrados al verificador | `python tools/check_project.py`, cuatro módulos de `docs.guides.examples` |
| 30-10-2026 | H3.4a | Propiedades, relaciones dirigidas dispersas y combinación de escrituras compatibles | `test_h34a_values.py`, `h3_relaciones.package.json` y `H3_4A_CIERRE.md` |

Para anotar un avance nuevo, agregue una fila con su fecha real y cambie el estado del hito únicamente después de comprobar sus criterios de aceptación. Si una tarea se suspende o descarta, registre la decisión y el motivo, en vez de borrarla del historial.

## 13. Incorporación de programadores

**Estado: TERMINADO para la guía inicial.** El documento `docs/guides/INICIO_RAPIDO.md` explica GISELA, ALBERTO y S.O.F.I.A. con ejemplos Python ejecutables. Sus entradas se enlazan desde el README principal, el de GISELA y los README de ALBERTO y S.O.F.I.A. La guía distingue las operaciones existentes de los contratos todavía pendientes.

**Evidencia:** `python -m docs.guides.examples.ejemplo_gisela`, `ejemplo_alberto`, `ejemplo_pendientes` y `ejemplo_sofia`. Los ejemplos se ejecutan también mediante `python tools/check_project.py`.

**H3.4a:** TERMINADO. Las decisiones de relaciones dirigidas y dispersas, más la combinación de escrituras compatibles, se implementaron y probaron. Véanse guía de propiedades y relaciones (guía histórica no incluida en este repositorio) y [registro de cierre H3.4a](H3_4A_CIERRE.md).

**H3.4d:** TERMINADO para ventanas de nodo. Véanse HABILIDADES.md (guía histórica no incluida en este repositorio) y [H3_4D_CIERRE.md](H3_4D_CIERRE.md).

**H3.4c:** TERMINADO. La guía EFECTOS.md (guía histórica no incluida en este repositorio) muestra el ciclo de vida, la restauración y el vencimiento reproducibles. El cierre técnico se registra en [H3_4C_CIERRE.md](H3_4C_CIERRE.md).

## 14. Próxima acción recomendada

Continuar con H4.6: adaptar el guion oficial y estresar el recorrido en GLAUQUIR. Después iniciar H5 sobre Observe y Act, usando los mismos recorridos y pruebas. Mantener las garantías de H2 y H3.4 sin introducir otro ejecutor.

## Registro de H3.4b. 30 de octubre de 2026

Se incorporó la lectura de los atributos opcionales de S.O.F.I.A., la escritura transaccional de `current`, la suma pura de modificadores de efectos activos y la proyección `scoresheet(character)`. Los valores `base` y `effective` no son destinos de escritura, y los personajes sin S.O.F.I.A. no reciben atributos inventados.

La autorización de lectura de Scoresheet para anfitriones queda pendiente de H4. La admisión semántica rechaza definiciones incompatibles, y las regresiones cubren límites, tipos, conflictos de reglas, rollback, restauración y consultas durante una transacción pendiente. La guía de S.O.F.I.A. (guía histórica no incluida en este repositorio) y el [registro de cierre](H3_4B_CIERRE.md) detallan el contrato ejecutable.

La política de ingeniería agrega un máximo de tres parámetros explícitos por función, sin contar `self` ni `cls`, conforme a los criterios de legibilidad, claridad y simplicidad del Zen de Python. El verificador general incorpora pruebas de esta regla. H3.4d y H4 se incorporaron posteriormente, con pruebas independientes.

## Registro de H3.4c. 30 de octubre de 2026

Se implementaron `apply_effect`, `end_effect`, `has_effect` y el disparador `effect_expired`. Las instancias admiten acumulación aditiva o unicidad por destinatario, y terminan mediante una operación explícita o por turno, tiempo ficticio, hecho o condición. La aplicación y el vencimiento ejecutan las consecuencias declaradas en el borrador de GISELA.

Se añadió una comprobación de escrituras reactivas anidadas y se amplió la huella para detectar ciclos, incluyendo reloj y RNG. Las pruebas cubren efectos iniciales, restauración, suspensiones, vencimiento único, conflictos y rollback. El alcance y los límites están en [H3_4C_CIERRE.md](H3_4C_CIERRE.md).

H3.4d está implementada para ventanas de nodo. Ren'Py todavía no está conectado.

## H3.4d. Registro de cierre

**30-10-2026.** Se incorporó el uso de habilidades en `skill_window`, requisitos, resultados, retornos y persistencia de intentos confirmados, sin introducir otro estado autoritativo. Evidencia: `test_h34d_skills.py`, `ejemplo_habilidades.py`, `H3_4D_CIERRE.md`. El hito H3 se considera terminado solo para el subconjunto ejecutable; H4 y H5 permanecen pendientes.

## H4. Registro de cierre. 30 de octubre de 2026

Se completaron H4.1, H4.2, H4.3 y H4.4 para el subconjunto ejecutable. El paquete de exploración utiliza acciones declaradas y la CLI permite recorrer la historia hasta un final sin lógica de autor en Python. Se verifican conflictos, autorizaciones, pendientes, restauración y consultas no destructivas. Las instrucciones de uso y las debilidades pendientes están en [H4_REVISION_Y_CIERRE.md](H4_REVISION_Y_CIERRE.md).

## Registro H4.5f. 30 de octubre de 2026

Se completó el endurecimiento de escenas físicas, presencia de entidades, inspección pública y autorización. La prueba de regresión incorpora el caso de identificadores estables de acciones cuando un elemento deja de ser visible. Se oficializa GLAUQUIR (GISELA's Lightweight Access Utility for Queries, User Interaction, and Rendering). Evidencia: `H4_5F_REVISION_Y_CIERRE.md` e `INVARIANTES_H4_5F.md`. La siguiente tarea es H4.6 antes de Ren'Py.

## Laboratorio técnico H4.6: Aventura independiente

Se incorporó `gisela/packages/h46_faro_de_niebla.package.json` para probar en GLAUQUIR un recorrido original con decisiones, tres desenlaces, guardado/restauración, DICE oculto y visible, TRAITS, S.O.F.I.A., ALBERTO y MARY. Su documentación y matriz de cobertura están en [H46_FARO_DE_NIEBLA.md](H46_FARO_DE_NIEBLA.md). **No cierra el hito de adaptación de la primera jornada de la novela**, que continúa pendiente de aprobación narrativa.
