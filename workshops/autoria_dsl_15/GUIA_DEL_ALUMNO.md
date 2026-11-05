# Guía del alumno: Workshop de autoría DSL 1.5

## Propósito

Este taller enseña a convertir una intención narrativa en datos declarativos que GISELA pueda validar y ejecutar. No se requiere saber programar ni escribir Python; sí es necesario editar texto JSON, ejecutar comandos preparados y leer sus resultados.

## Cómo trabajar

1. Lea el objetivo y la intención autoral de la unidad.
2. Abra primero el **paquete mínimo** indicado. Compruebe su admisión y recorra las opciones disponibles antes de modificarlo. Cuando el ejercicio declare dos caminos, compruebe ambos.
3. Prediga por escrito qué ocurrirá si cambia una declaración.
4. Edite exclusivamente una copia del archivo JSON. Nunca altere los paquetes canónicos de Tegularis.
5. Valide el paquete. Si es rechazado, lea y corrija el diagnóstico; no confunda JSON bien escrito con paquete admitido.
6. Ejecute y observe. Compare el resultado con su predicción.
7. Pase al ejercicio de integración de Tegularis solo cuando pueda explicar la declaración sin leer su solucionario.

## Tres niveles para cada mecanismo

- **Descubrimiento:** experimentar con un paquete completo y pequeño.
- **Construcción:** expresar una regla o decisión propia, y comprobarla.
- **Integración:** localizar el mecanismo dentro de Tegularis, conservando las reglas productivas.

La primera etapa mínima está en [Unidad 1: laboratorio](paquetes/01_fundamentos/README.md). Los laboratorios pequeños están disponibles en las unidades **1 a 8**. La Unidad 9 reúne la integración y la evaluación por hitos; las pruebas de aprendizaje con personas reales aún están pendientes.

## Documentación oficial; no duplicarla

- [Crear un paquete](../../docs/guides/CREAR_PAQUETE.md)
- [Inicio rápido](../../docs/guides/QUICK_START.md)
- [Contratos y esquemas](../../gisela/contracts/README.md)
- [Lenguaje narrativo](../../docs/architecture/NARRATIVE_LANGUAGE.md)
- [S.O.F.I.A.](../../docs/architecture/SOFIA.md)
- [TRAITS](../../traits/README.md) y [DICE](../../dice/README.md)
- [Observe/Act](../../docs/architecture/API_CLIENTES.md)

**Orden de autoridad:** esquemas y validadores vigentes, interfaces públicas, pruebas, paquetes productivos y documentación verificada. Las propuestas históricas no sustituyen contratos actuales.

## Cómo entregar un ejercicio

Entregue el JSON modificado, comando y resultado de admisión, registro de ejecución, predicción inicial, comparación con el resultado y una explicación de las referencias entre declaraciones. Un ejercicio que solo pasa admisión todavía no está aprobado.

## Laboratorios reducidos de las unidades 1 a 8

Comience por `paquetes/01_fundamentos/` y siga `paquetes/02_progresivo/` a `paquetes/08_progresivo/`. Cada README especifica predicción, modificación y prueba. Los ejercicios productivos no se eliminan. La Unidad 6 reducida presenta una respuesta **guionizada**, expresamente distinta de una política NPC autónoma.

## Evaluación final

Tras la Unidad 8, complete [Unidad 9](unidades/09_integracion.md) y prepare las evidencias que se solicitan en cada hito. La [rúbrica](evaluacion/09_integracion/RUBRICA.md) distingue admisión, comprensión, ejecución y fidelidad al canon. La solución no consiste en copiar el JSON productivo.

## Convención de entrega (obligatoria)

Todos los ejercicios se trabajan desde la raíz del repositorio, en `mi_trabajo/u01.package.json` hasta `mi_trabajo/u08.package.json` (directorio local que debe excluirse del control de versiones mediante su configuración Git local). Los comandos de validación y ejecución apuntan a **esa copia**, no a las plantillas. Si hay otro archivo, sustituya la ruta explícitamente. No edite el canon.

Vea [cómo observar errores, acciones y desenlaces](COMO_COMPROBAR.md), y [los hitos evaluables de la Unidad 9](evaluacion/09_integracion/HITOS.md).
