# Evidencia: Unidad 8: presentación declarativa

**Base:** `14_presentacion_semantica_v082d.package.json` del repositorio incorporado a la Unidad 7. Se generan únicamente copias para trabajo autoral. No se modifica motor, contrato ni paquete canónico.

## Comprobaciones realizadas

- Siete variantes admisibles de `presentation`; cada una difiere del canon **solo** en el objeto `presentation`.
- Siete solucionarios admitidos e idénticos al paquete canónico.
- Un paquete con plantilla `{actor.password}` rechazado por contrato.
- Comparación de equivalencia de estado lógico frente al canon para cada variante, en dos semillas (`0`*64 y `f`*64), tres pasos de Observe/Act y restauración de estado antes del segundo Act. Los estados comparados incluyen revisión, tiempo, mundo, narrativa, historial, RNG, actuación y cursor. Se verificó coincidencia de la información pública de actuación y de la solicitud de acción habilitada elegida.
- Registro textual: `LOG_UNIDAD_08.txt`.

Comando desde la raíz:

```bash
PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_unidad_08.py
```

## Interpretación

Esta comprobación demuestra, para los escenarios ejercitados, que cambiar vistas, regiones, plantillas y rótulos no altera la evolución lógica con la misma semilla y las mismas acciones. La comparación no interpreta por su cuenta cambios numéricos como daño o curación.

## Límites

La ejecución de tres pasos no asegura haber ejercitado todos los efectos o ramas del combate, ni que cada visualización aparezca poblada en pantalla con datos adecuados. No se ha ejecutado aquí una regresión general ni una prueba visual manual de todas las pantallas. Los test existentes de v0.8.2e/f brindan cobertura adicional, pero deben ejecutarse por separado y registrarse antes de considerarlos aprobados en esta entrega.
