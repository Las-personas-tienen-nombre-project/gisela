# Documentación de GISELA

GISELA es un motor narrativo independiente. Este repositorio contiene su implementación, contratos, bibliotecas y cliente textual GLAUQUIR. La integración gráfica con Ren'Py pertenece a otro proyecto y **no es necesaria** para usar el motor.

## Lectura recomendada

1. [Inicio rápido](guides/QUICK_START.md): instalación, ejecución y pruebas. La [guía de GLAUQUIR](guides/GLAUQUIR.md) explica comandos, diagnóstico y color. [Crea tu primer paquete](guides/CREAR_PAQUETE.md) enseña a escribir un relato pequeño.
2. [Lenguaje narrativo](architecture/NARRATIVE_LANGUAGE.md): conceptos del DSL y su ejecución (en inglés). La [base arquitectónica v1.5](architecture/GISELA_Arquitectura_Consolidada_v1_5.md) desarrolla el modelo y conserva secciones históricas señaladas.
3. [API de clientes](architecture/API_CLIENTES.md) y [ejecutor](../gisela/engine/README.md): observación, acciones, errores y persistencia.
4. [Contratos](../gisela/contracts/README.md): paquetes, schemas y admisión.
5. [ALBERTO](architecture/ALBERTO.md), [S.O.F.I.A.](architecture/SOFIA.md), [MARY](architecture/MARY.md), [TRAITS](../traits/README.md) y [DICE](../dice/README.md): responsabilidades específicas.
6. [Decisiones ADR](decisions/GISELA_ADR_001_017.md) y [ADR-020](decisions/ADR_020_E0_FRONTERA_AUTORIDAD_Y_COMPROMISO.md): decisiones de diseño.
7. [Roadmap actual](operatives/ROADMAP.md) y [cierre técnico PA-001](operatives/PA001_CIERRE_2026_10_31.md): estado y límites verificados.

Para ejecutar los controles del repositorio independiente, consulte la
[guía del verificador GISELA](guides/VERIFICACION_GISELA.md).

## Cómo leer el archivo documental

`docs/architecture` contiene contratos de arquitectura y también propuestas anteriores; no toda propuesta está implementada. `docs/decisions` conserva decisiones aprobadas y antecedentes. `docs/operatives` reúne informes de implementación, verificación y auditoría. `docs/history` preserva material de etapas anteriores; sus referencias al repositorio original no son instrucciones vigentes.

Para desarrollar nuevas capacidades, contrastar siempre el documento pertinente con el código, schemas y pruebas actuales. Los ejemplos narrativos incluidos tienen condiciones de derechos distintas de la licencia del software.
