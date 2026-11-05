# Guía del instructor — Workshop de autoría GISELA DSL 1.5

## Principio de evaluación

Se califica la **comprensión causal** y no la copia de una solución. El alumno debe explicar intención → declaración → admisión → ejecución → evidencia → variación. No se exige escribir Python ni tocar el motor.

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

Las unidades 2–8 utilizan, en numerosos ejercicios, paquetes productivos grandes. Son válidos como **integración**, pero deben complementarse con descubrimiento y construcción en paquetes reducidos. La Unidad 1 ya tiene un laboratorio mínimo verificado; el resto del itinerario mínimo y la Unidad 9 siguen pendientes.

## Fuentes de autoridad externas al workshop

La descripción de campos y restricciones pertenece a [contratos v1.5](../../gisela/contracts/README.md), [documentación oficial](../../docs/README.md), [TRAITS](../../traits/README.md) y [DICE](../../dice/README.md). No mantener un glosario ni una referencia DSL paralela aquí.

## Secuencia de laboratorios reducidos (2–7)

Compruebe primero que el alumno puede explicar las referencias entre declaraciones. En 4, solicite el contexto exacto de la contribución, no solo una tirada afortunada. En 5, compare jugar y omitir una carta. En 6, exija distinguir el efecto guionizado de una verdadera política NPC. En 7, compruebe la conjunción de hechos. Los casos productivos siguen siendo el paso de integración y no deben reequilibrarse.

## Evaluación integradora

Use la [rúbrica de Unidad 9](evaluacion/09_integracion/RUBRICA.md); no dé por aprobado un ejercicio que solo supera admisión. Para las pruebas dirigidas de los puentes 04 y 06, consulte [evidencias reproducibles](evaluacion/RESULTADOS_PUENTES_04_06_Y_UNIDAD_09.md). No atribuya a la respuesta guionizada del laboratorio 6 las capacidades de selección de `play_first_skill` o `actuation.participants`.
