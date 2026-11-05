# Documentación de GISELA

GISELA es un motor narrativo independiente. Este repositorio contiene su implementación, contratos, bibliotecas y cliente textual GLAUQUIR. La integración gráfica con Ren'Py pertenece a otro proyecto y **no es necesaria** para usar el motor.

## Lectura recomendada

1. [Inicio rápido](guides/QUICK_START.md): instalación, ejecución y pruebas. La [guía de GLAUQUIR](guides/GLAUQUIR.md) explica comandos, diagnóstico y color. [Crea tu primer paquete](guides/CREAR_PAQUETE.md) enseña a escribir un relato pequeño.
2. [Lenguaje narrativo](architecture/NARRATIVE_LANGUAGE.md): conceptos del DSL y su ejecución (en inglés). La [base arquitectónica v1.5](architecture/GISELA_Arquitectura_Consolidada_v1_5.md) desarrolla el modelo y conserva secciones históricas señaladas.
3. [API de clientes](architecture/API_CLIENTES.md) y [ejecutor](../gisela/engine/README.md): observación, acciones, errores y persistencia.
4. [Contratos](../gisela/contracts/README.md): paquetes, esquemas y admisión.
5. [ALBERTO](architecture/ALBERTO.md), [S.O.F.I.A.](architecture/SOFIA.md), [MARY](architecture/MARY.md), [TRAITS](../traits/README.md) y [DICE](../dice/README.md): responsabilidades específicas.
6. [Decisiones ADR](decisions/GISELA_ADR_001_017.md) y [ADR-020](decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md): decisiones de diseño.
7. [Roadmap actual](operatives/ROADMAP.md) y [cierre técnico PA-001](operatives/PA001_CIERRE_2026_10_31.md): estado y límites verificados.

Para ejecutar los controles del repositorio independiente, consulte la
[guía del verificador GISELA](guides/VERIFICACION_GISELA.md).

## Official DSL 1.5 reference

The [DSL 1.5 reference index](reference/dsl_1_5/README.md) records versioned schema fields, constraints, source hierarchy and traceability. It complements the existing architecture documents and does not redefine the execution contract.

## Talleres y ejemplos

- [Taller de autoría DSL 1.5](../workshops/autoria_dsl_15/README.md): nueve unidades, laboratorios reducidos, ejercicios y evaluación final.
- [Presentación por regiones](guides/workshops/WORKSHOP_PRESENTACION_V080.md): composición básica y publicación de recursos.
- [Tres disposiciones de Tegularis](guides/workshops/WORKSHOP_PRESENTACION_V081.md): participantes, decisiones y crónica.
- [Tablas, causalidad y plantillas](guides/workshops/WORKSHOP_PRESENTACION_V082.md): vistas de presentación y sus límites.
- [Manuales en español](manuals/es/README.md): diseño de una historia y sus sistemas. Los paquetes por etapas de *El paraguas olvidado* aún no se incluyen; la guía [Crea tu primer paquete](guides/CREAR_PAQUETE.md) utiliza un archivo completo disponible.

## Informes y evidencias

El [índice de informes operativos](operatives/README.md) distingue las guías de
estado actual, los cierres de implementación y los antecedentes de cada intervención.
Sus [evidencias](operatives/evidence/) incluyen registros, resúmenes y snapshots;
no son observaciones públicas del jugador ni instrucciones para iniciar una partida.
La [revisión documental de noviembre de 2026](operatives/REVISION_DOCUMENTAL_2026_11_04.md)
registra los traslados, las comprobaciones actuales y sus límites.

## Cómo leer el archivo documental

`docs/architecture` contiene contratos de arquitectura y también propuestas anteriores; no toda propuesta está implementada. `docs/decisions` conserva decisiones aprobadas y antecedentes. `docs/operatives` reúne informes de implementación, verificación y auditoría. `docs/history` preserva material de etapas anteriores; sus referencias al repositorio original no son instrucciones vigentes.

Los números de los incrementos, como v0.8.2, identifican hitos de desarrollo.
Son distintos de la versión del formato narrativo, como DSL 1.5, y de la versión
del paquete Python declarada en `pyproject.toml`.

Para desarrollar nuevas capacidades, contraste el documento pertinente con el código, los esquemas y las pruebas actuales. Los ejemplos narrativos incluidos tienen condiciones de derechos distintas de la licencia del software.
