# 10. Catálogo de capacidades de GISELA

Esta guía permite decidir qué recursos usar al escribir una historia. Reúne las capacidades comprobables en el repositorio actual y sus límites. No sustituye la [referencia DSL 1.5](../../reference/dsl_1_5/README.md), que detalla los campos admitidos y sus reglas.

## Cómo leer el catálogo

- **Disponible:** existe una implementación en el motor y un ejemplo o prueba que muestra su uso. Puede requerir declaraciones concretas en el paquete.
- **Laboratorio:** existe una implementación y una vía de ejecución, pero la experiencia no está incorporada al recorrido narrativo habitual de GLAUQUIR.
- **Limitado:** la capacidad existe, pero no incluye todas las funciones que podría sugerir su nombre. Se indica el límite concreto.
- **No confirmado:** no se encontró una implementación general que permita prometer esa función como parte del curso.

**Importante:** que un archivo JSON supere la validación de estructura no demuestra que todas sus operaciones puedan ejecutarse. El validador semántico, el motor y las pruebas determinan el alcance efectivo. Una historia puede combinar sistemas disponibles sin que GISELA ofrezca una mecánica universal para esa combinación.

## Narración y decisiones

| Capacidad | Estado | Alcance y límites | Para comenzar |
| --- | --- | --- | --- |
| Escenas, nodos y finales | Disponible | Organizan la progresión del relato; un cambio de nodo no implica necesariamente un desplazamiento físico. | [Taller 01](01_paraguas/README.md) |
| Opciones y acciones | Disponible | El cliente solo puede enviar acciones ofrecidas por la observación vigente. | [Taller 01](01_paraguas/README.md) |
| Diálogos con personajes | Disponible | Se declaran intervenciones y elecciones. No implica una conversación generada libremente por inteligencia artificial. | [Taller 04](04_dialogos_decisiones/README.md) |
| Hechos, variables y condiciones | Disponible | Permiten recordar decisiones y condicionar escenas o resultados posteriores. | [Taller 02](02_faro/README.md) |
| Reglas que reaccionan a eventos | Disponible | Se ejecutan cuando coinciden los disparadores y condiciones declarados. Están sujetas a control de conflictos y límites de ejecución. | [Taller 09](09_reglas_relaciones/README.md) |
| Exploración de escenas | Disponible | Puede mostrar personajes, elementos y acciones según ubicación, presencia y visibilidad; la escena no sustituye el estado del mundo. | [Referencia de escenas](../../reference/dsl_1_5/scene.md) |

## Mundo, personajes y objetos: ALBERTO

| Capacidad | Estado | Alcance y límites | Para comenzar |
| --- | --- | --- | --- |
| Personajes y lugares | Disponible | Las fichas definen tipos; `initial_state` crea las instancias de la historia. | [Taller 03](03_personajes/README.md) |
| Objetos y propietarios | Disponible | Se pueden declarar, transferir y consultar pertenencias. No existe por ello un inventario gráfico universal. | [Taller 05](05_objetos_equipo/README.md) |
| Desplazamientos | Disponible | `move_character` modifica la ubicación; las transiciones de escenas deben mantener coherencia con ella. | [Relaciones del DSL](../../reference/dsl_1_5/03_RELATIONSHIPS.md) |
| Relaciones entre personajes | Disponible | Son campos declarados por el autor, con dirección y valores que pueden cambiar. No representan automáticamente sentimientos recíprocos. | [Taller 09](09_reglas_relaciones/README.md) |
| Conocimientos y creencias | Disponible | Permiten distinguir lo que un personaje sabe o cree del estado general del mundo. | [ALBERTO](../../architecture/ALBERTO.md) |
| Tiempo, efectos y rasgos | Disponible | El motor aplica las operaciones declaradas y admitidas; no simula un mundo autónomo sin reglas del autor. | [ALBERTO](../../architecture/ALBERTO.md) |

## Atributos, habilidades y evaluaciones

| Capacidad | Estado | Alcance y límites | Para comenzar |
| --- | --- | --- | --- |
| S.O.F.I.A. | Disponible, opcional | Cinco atributos declarables: `strength`, `openness`, `fortune`, `intelligence` y `awareness`. No impone pruebas universales ni valores implícitos a todos los personajes. | [S.O.F.I.A.](../../architecture/SOFIA.md) |
| Habilidades activas | Disponible | Se usan en ventanas autorizadas y producen los efectos declarados; no pueden activarse en cualquier momento por defecto. | [Taller 06](06_habilidades_activas/README.md) |
| Habilidades pasivas | Disponible | Pueden aportar rasgos sin una acción de activación. La existencia del rasgo y sus modificadores contextuales son conceptos distintos. | [Taller 07](07_habilidades_pasivas/README.md) |
| TRAITS | Disponible, contextual | Sus aportes dependen de roles, etiquetas y otras condiciones de la evaluación. Tener un rasgo no garantiza una bonificación en toda tirada. | [Taller 07](07_habilidades_pasivas/README.md) |
| DICE | Disponible | Admite cálculos aleatorios reproducibles con semilla. El autor declara entradas y consecuencias; DICE no cambia el mundo directamente. | [Evaluaciones](../../reference/dsl_1_5/02_SEMANTICS.md) |
| Evaluaciones ocultas o visibles | Disponible | Las visibles pueden detener la acción hasta su confirmación; la continuación reutiliza el resultado ya calculado, sin volver a tirar. | [Ejecución](../../reference/dsl_1_5/04_EXECUTION.md) |

## Objetivos, progreso y consecuencias: MARY

**Disponible, con límites.** MARY evalúa objetivos y misiones declarados y propone avances y hechos resultantes; GISELA decide si los confirma junto con la acción que los originó. Puede ocultar objetivos al lector.

No ofrece todavía reinicio selectivo de una jornada ni transferencia de progreso por contraseña. Sus resultados automáticos admitidos se limitan a hechos declarados: no debe suponerse que conceda directamente objetos u otras recompensas arbitrarias. Tampoco determina por sí sola si una misión será imposible de completar en el futuro.

Consulta la [descripción de MARY](../../architecture/MARY.md) y sus ejemplos antes de incorporar misiones a un paquete.

## Encuentros y combate

**Laboratorio.** El motor incluye un reloj de actuación con participantes, iniciativa, oportunidades por turno, habilidades y políticas de resultado. GLAUQUIR lo ejecuta con `--actuation`; **no es todavía una pantalla de combate integrada al flujo habitual**. El [taller 08](08_combate/README.md) enseña un encuentro de dos personajes mediante esta modalidad.

La resistencia del taller es una variable elegida por el autor. GISELA no impone puntos de vida, daño, armadura ni condiciones universales de victoria. Las reglas del intruso se declaran en el paquete: no equivalen a una inteligencia táctica general. Las políticas que cierran el reloj tampoco crean por sí mismas un final narrativo.

**No confirmado como sistema general:** combate completo con equipamiento, estados y una interfaz de juego unificada, sin configuración específica del autor ni herramientas de laboratorio.

## Presentación y clientes

| Capacidad | Estado | Alcance y límites | Fuente |
| --- | --- | --- | --- |
| GLAUQUIR, cliente de texto | Disponible | Muestra texto y acciones públicas. No decide ni confirma por su cuenta los cambios del mundo. | [Guía de GLAUQUIR](../../guides/GLAUQUIR.md) |
| Tablas y vistas declarativas | Disponible, limitada | Pueden proyectar información pública, participantes, recursos y eventos con filtros y plantillas restringidas. No añaden reglas de juego. | [Presentación DSL 1.5](../../reference/dsl_1_5/09_PRESENTATION.md) |
| Roles visuales de eventos | Disponible, descriptiva | Etiquetas como `damage` o `healing` son clasificaciones visuales del autor; no prueban la causa mecánica del cambio. | [Presentación DSL 1.5](../../reference/dsl_1_5/09_PRESENTATION.md) |
| Integración con Ren'Py | Externa, aceptación pendiente | El adaptador pertenece a otro repositorio. No se incluye aquí una integración gráfica lista para distribuir. | [Roadmap](../../operatives/ROADMAP.md) |
| Interfaz visual universal para escribir paquetes | No confirmada | Este curso enseña a modificar archivos JSON y no presupone un editor visual integrado. | [Instalación](03_instalacion.md) |

## Guardado, validación y reproducibilidad

**Disponibles.** GISELA admite paquetes, crea sesiones, ofrece acciones mediante `Observe` y confirma cambios mediante `Act`. Puede exportar y restaurar una sesión, incluidas decisiones o evaluaciones pendientes que el contrato permite reconstruir. Una petición inválida no debe dejar cambios parciales confirmados.

Los guardados están vinculados al contenido admitido del paquete. Si cambias las definiciones del relato, no debes suponer que un guardado antiguo seguirá siendo compatible. El estado exportado puede contener información privada y no debe mostrarse al lector como si fuera la observación pública. La reproducibilidad requiere repetir el estado inicial, las entradas y la semilla pertinente.

Consulta [Observe y Act](../../reference/dsl_1_5/08_OBSERVE_ACT.md), [determinismo](../../reference/dsl_1_5/07_DETERMINISM.md) y [validación](../../reference/dsl_1_5/12_VALIDATION.md).

## Dónde consultar una capacidad no enseñada en los talleres

Primero revisa la [referencia DSL 1.5](../../reference/dsl_1_5/README.md), luego un paquete existente y, si necesitas confirmar un comportamiento específico, sus pruebas. Los [ejemplos históricos de Tegularis](../../history/workshops/autoria_dsl_15/README.md) muestran combinaciones más extensas, pero no todas representan interfaces disponibles para un autor principiante.

Este catálogo no promete que todas las combinaciones de operaciones funcionen en cualquier contexto. Cuando una mecánica no esté demostrada por un ejemplo ejecutable, conviene construir un paquete pequeño, validarlo y comprobar sus resultados antes de incorporarla a una historia mayor.
