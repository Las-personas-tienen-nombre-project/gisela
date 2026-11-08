# Guía del instructor: Workshop de autoría GISELA DSL 1.5

## Principio de evaluación

Se califica la **comprensión causal** y no la copia de una solución. El alumno debe explicar qué quiere expresar, cómo lo declara, cómo admite y ejecuta el paquete, qué observa y qué cambia al introducir una variación. No se exige escribir Python ni tocar el motor.

## Criterios aplicables a cada unidad

1. **Interpretación:** nombra correctamente entidades, referencias, condiciones y resultados que corresponden al contrato.
2. **Predicción:** anticipa una activación y al menos una no activación, antes de ejecutar.
3. **Autoría:** modifica el DSL admitido sin introducir nuevas capacidades del motor.
4. **Comprobación:** distingue un rechazo sintáctico, admisión semántica y comportamiento observado.
5. **Transferencia:** puede resolver una variación diferente sin copiar el solucionario.

No se aprueba una unidad únicamente porque el JSON sea correcto. La corrección del instructor debe solicitar una explicación independiente.

## Recorridos

- **Guiado:** se entrega paquete mínimo, pregunta y cambio localizado; se pide registrar la predicción antes de ver la salida.
- **Autónomo:** se entrega intención y resultados observables; el estudiante selecciona declaraciones y explica su validez.
- **Integración:** se consulta el paquete canónico de Tegularis sin alterar sus reglas para la evaluación final.

## Evidencia y límites

Los verificadores `evaluacion/comprobar_unidad_*.py` son herramientas del instructor. Sus resultados anteriores no certifican el taller completo ni todas las ramas. Consulte `evaluacion/RESULTADOS_UNIDAD_*.md` para límites declarados. La ausencia de una prueba no se debe interpretar como prueba aprobada.

## Riesgos didácticos identificados

Las unidades 1 a 8 disponen de laboratorios reducidos. Cada unidad comienza con ese laboratorio y continúa con los paquetes productivos como ejercicio de **integración**. La Unidad 9 reúne la reconstrucción autónoma y su rúbrica. Estos materiales están disponibles; la certificación pedagógica y las pruebas con alumnos reales siguen pendientes.

## Fuentes de autoridad externas al workshop

La descripción de campos y restricciones pertenece a [contratos v1.5](../../../../gisela/contracts/README.md), [documentación oficial](../../../README.md), [TRAITS](../../../../traits/README.md) y [DICE](../../../../dice/README.md). No mantener un glosario ni una referencia DSL paralela aquí.

## Secuencia de laboratorios reducidos (1 a 8)

Compruebe primero que el alumno puede explicar las referencias entre declaraciones. En la Unidad 4, solicite el contexto exacto de la contribución, no solo una tirada afortunada. En la 5, compare jugar y omitir una carta. En la 6, exija distinguir la respuesta guionizada de una política NPC autónoma. En la 7, compruebe la conjunción de hechos. En la 8, compare la presentación con el estado lógico y las decisiones autorizadas. Los casos productivos siguen siendo el paso de integración y no deben cambiar de balance.

## Evaluación integradora

Use la [rúbrica de Unidad 9](evaluacion/09_integracion/RUBRICA.md); no dé por aprobado un ejercicio que solo supera admisión. Para las pruebas dirigidas de los puentes 04 y 06, consulte [evidencias reproducibles](evaluacion/RESULTADOS_PUENTES_04_06_Y_UNIDAD_09.md). No atribuya a la respuesta guionizada del laboratorio 6 las capacidades de selección de `play_first_skill` o `actuation.participants`.

El script `comprobar_puentes_04_06.py` comprueba las contribuciones del paquete de referencia de la Unidad 4; no ejecuta pruebas NPC ni evalúa una entrega del alumno. Además de las interfaces públicas de sesión, consulta las definiciones internas de la sesión para llamar a `contribution_total`. Las pruebas NPC se ejecutan por separado con `python -m pytest -q gisela/engine/tests/test_npc_skill_priorities.py`.
