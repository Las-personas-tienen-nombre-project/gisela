# 11. Cómo consultar la referencia DSL 1.5

Esta guía te ayuda a encontrar las reglas de escritura de un paquete GISELA. No es otra versión de la especificación: los campos, sus tipos y restricciones están en la [referencia oficial del DSL 1.5](../../reference/dsl_1_5/README.md).

Un **campo** es una propiedad del archivo JSON, como `id` o `title`; una **operación** indica algo que debe hacer el motor, como narrar o registrar un hecho. La **admisión** es la comprobación de que un paquete respeta las reglas aceptadas por GISELA.

Puedes seguir los talleres sin leer toda la referencia. Consúltala cuando necesites añadir una operación, comprobar un campo o entender por qué un paquete no se admite.

## Por dónde empezar

1. Busca un ejemplo cercano a lo que quieres escribir en los [talleres](README.md) o en los [ejemplos de la referencia](../../reference/dsl_1_5/05_EXAMPLES.md).
2. Consulta la sección correspondiente de la tabla siguiente.
3. En el inventario, busca el nombre del campo que vas a cambiar y comprueba qué valor admite. Si la explicación incluye otros campos que todavía no conoces, empieza por el ejemplo del taller correspondiente.
4. Valida el paquete y ejecuta el recorrido afectado. La validación de estructura no demuestra por sí sola que una operación se ejecute correctamente.

## Buscar por tarea

| Quiero... | Consultar primero | Campos y estructuras |
| --- | --- | --- |
| Empezar un paquete narrativo | [Sintaxis](../../reference/dsl_1_5/01_SYNTAX.md) | [Paquete](../../reference/dsl_1_5/package.md), [datos comunes](../../reference/dsl_1_5/common.md) |
| Crear escenas, decisiones y finales | [Lenguaje narrativo](../../architecture/NARRATIVE_LANGUAGE.md), [semántica](../../reference/dsl_1_5/02_SEMANTICS.md) | [Nodos](../../reference/dsl_1_5/node.md), [acciones](../../reference/dsl_1_5/act.md), [resultados](../../reference/dsl_1_5/result.md) |
| Recordar una decisión o evaluar una condición | [Semántica](../../reference/dsl_1_5/02_SEMANTICS.md), [ejecución](../../reference/dsl_1_5/04_EXECUTION.md) | [Reglas](../../reference/dsl_1_5/rule.md), [estado inicial](../../reference/dsl_1_5/initial_state.md) |
| Crear personajes, objetos y ubicaciones | [Relaciones](../../reference/dsl_1_5/03_RELATIONSHIPS.md) | [Fichas](../../reference/dsl_1_5/card.md), [estado inicial](../../reference/dsl_1_5/initial_state.md), [escenas](../../reference/dsl_1_5/scene.md) |
| Crear habilidades o aplicar rasgos | [Semántica](../../reference/dsl_1_5/02_SEMANTICS.md), [relaciones](../../reference/dsl_1_5/03_RELATIONSHIPS.md) | [Fichas](../../reference/dsl_1_5/card.md), [estado inicial](../../reference/dsl_1_5/initial_state.md) |
| Resolver evaluaciones y comprobar sus resultados | [Ejecución](../../reference/dsl_1_5/04_EXECUTION.md), [determinismo](../../reference/dsl_1_5/07_DETERMINISM.md) | [Resultados](../../reference/dsl_1_5/result.md) |
| Mostrar información al lector | [Presentación](../../reference/dsl_1_5/09_PRESENTATION.md), [Observe y Act](../../reference/dsl_1_5/08_OBSERVE_ACT.md) | [Observaciones](../../reference/dsl_1_5/observe.md), [escenas](../../reference/dsl_1_5/scene.md), [hojas de puntuación](../../reference/dsl_1_5/scoresheet.md) |
| Comprender el estado de una sesión | [Observe y Act](../../reference/dsl_1_5/08_OBSERVE_ACT.md), [determinismo](../../reference/dsl_1_5/07_DETERMINISM.md) | [Sesiones](../../reference/dsl_1_5/session.md), [estado del mundo](../../reference/dsl_1_5/world_snapshot.md) |
| Corregir un paquete rechazado | [Errores](../../reference/dsl_1_5/06_ERRORS.md), [validación](../../reference/dsl_1_5/12_VALIDATION.md) | [Inventario completo](../../reference/dsl_1_5/README.md) |
| Estudiar un encuentro por turnos | [Tegularis](../../reference/dsl_1_5/10_TEGULARIS.md), [ejecución](../../reference/dsl_1_5/04_EXECUTION.md) | [Taller 08](08_combate/README.md) |

## Qué documento tiene la última palabra

Los [esquemas versionados](../../../gisela/contracts/v1_5/) describen la estructura aceptada y la admisión semántica comprueba reglas que no se reducen a la forma del JSON. Juntas definen qué declaraciones son válidas. El motor y sus pruebas muestran qué comportamiento está implementado. Los manuales, talleres y ejemplos sirven para aprender, pero no sustituyen esas fuentes.

Si un esquema acepta un campo, eso no garantiza por sí solo que cualquier combinación de operaciones tenga un efecto visible. Revisa el [catálogo de capacidades](10_capacidades.md) para conocer los límites y las funciones de laboratorio.

## Cuando una explicación no coincide con el resultado

Consulta primero [errores](../../reference/dsl_1_5/06_ERRORS.md) y [validación](../../reference/dsl_1_5/12_VALIDATION.md). Si un archivo no se admite, comienza por el mensaje de error y vuelve al ejemplo mínimo del taller. Para diferencias entre lo documentado y lo comprobado, la referencia mantiene una [lista de discrepancias](../../reference/dsl_1_5/DISCREPANCIES.md) y un [informe de verificación](../../reference/dsl_1_5/VERIFICATION.md).

Este capítulo cierra el recorrido introductorio. Para seguir practicando, vuelve al [índice de talleres](README.md) y trabaja sobre una copia de los paquetes de ejemplo.
