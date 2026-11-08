# Cómo comprobar un ejercicio sin programar

Trabaje desde la **raíz del repositorio** y cambie solo archivos en `mi_trabajo/`.

## Tres preguntas distintas

1. **¿El JSON se puede analizar?** Llaves, comillas, comas y tipos son correctos; eso NO implica que GISELA lo admita.
2. **¿GISELA lo admite?** `PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u03.package.json`. Anote el código de salida y el error si lo hay.
3. **¿Hace lo que predije?** `python tools/glauquir.py --package mi_trabajo/u03.package.json --auto`. El proceso debe terminar; registre elección y desenlace, no solo que empezó.

## Ejemplo de observación reproducible

| Comando | Campo o señal observable | Interpretación |
|---|---|---|
| `python -m gisela.contracts.admit_package mi_trabajo/u03.package.json` | Terminó sin excepción y código de salida `0` | Admisión; no prueba la guarda |
| `python tools/glauquir.py --package mi_trabajo/u05.package.json --auto --choose golpe_01` | Acción elegida y desenlace (compruebe el ID ofrecido) | Si se registra `golpe_ensayado`, puede elegirse la rama correspondiente; no equivale a demostrar daño |
| `python tools/glauquir.py --package mi_trabajo/u05.package.json` | Elección manual de la alternativa que omite la habilidad | Prueba negativa del hecho, no de una tirada de ataque |
| Cambiar una referencia por un `id` inexistente y admitir | Diagnóstico del validador o admisión inesperada | Registre el comportamiento real del contrato; no invente el resultado |

**Advertencia:** los identificadores admitidos por `--choose` deben obtenerse de la sesión real; no los deduzca del texto visible de la opción. En sesiones de combate, `--auto` puede elegir una rama sin cubrir las demás. Cuando las salidas no presenten todos los detalles de una contribución, anote "no observable con esta ejecución" y consulte la comprobación dirigida del instructor y su alcance en la [guía docente](GUIA_DEL_INSTRUCTOR.md). Nunca infiera causalidad por dos mensajes contiguos.

## Diagnóstico de una referencia

Si una declaración menciona `card: "parnecio_no_existe"`, busque primero la carta correspondiente en `cards`. Compruebe que `id` coincida exactamente (mayúsculas incluidas). Vuelva a admitir **su copia**. Si el error no desaparece, conserve el texto completo y consulte los contratos oficiales. No silencie el error cambiando el motor.

## Ficha para entregar en cada unidad

```text
Unidad y ruta de mi archivo:
Intención de la modificación:
ID o propiedad que creé:
Predicción (caso positivo y negativo):
Comando de admisión y resultado:
Comando de ejecución y acción elegida:
Observación / desenlace:
¿En qué difiere de la predicción?:
¿Qué prueba todavía falta?:
```

Para variables, examine los valores definidos y los acontecimientos confirmados disponibles; para `dodge`, una ejecución de combate por sí sola **no demuestra +2**, que debe corroborarse con la prueba dirigida de contribuciones o las interfaces públicas de evaluación. Para presentación, un rótulo cambiado no afecta el estado lógico, pero demostrar determinismo exige mismas semillas y mismas acciones.
