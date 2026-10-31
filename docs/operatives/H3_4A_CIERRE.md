# H3.4a. Propiedades y relaciones. Registro de implementación

Fecha: 30 de octubre de 2026.

Estado: TERMINADO para el subconjunto descrito en este documento.

## 1. Acuerdos aplicados

Se aprobaron relaciones dirigidas y dispersas con valores iniciales declarados, y la combinación de escrituras compatibles en una misma ronda reactiva. No se agregó un segundo sistema de ejecución ni se modificaron los schemas v1.2.

Las definiciones de cartas, variables y relaciones se indexan al crear la sesión. No se guardan nuevamente en el snapshot: el digest del paquete permite asociar el estado con sus definiciones originales.

## 2. Operaciones

`set`, `add` y `compare` pueden utilizar variables de sesión o mundo, propiedades de personajes, lugares y objetos, y relaciones dirigidas entre instancias existentes. Las consultas son puras. Una escritura usa el borrador entregado por GISELA y aplica restricciones de tipo; los límites declarados se comprueban para propiedades.

La ausencia de un campo en una instancia o de una relación concreta no impide consultarlo: se obtiene el valor inicial de la definición. La primera escritura materializa la entrada incluso si el nuevo valor es igual al inicial. Un suceso `state_changed` se produce únicamente cuando cambia el valor efectivo.

## 3. Reactividad

Las reglas de una ronda leen la misma instantánea, incluso cuando una escritura usa otra propiedad como operando. Las sumas compatibles se agregan antes de ejecutar la ronda y se aplican una sola vez por destino. Las asignaciones idénticas se consolidan; las contradictorias y la mezcla `set` más `add` se rechazan con `REACTION_CONFLICT`.

Las operaciones reactivas no conmutativas mantienen la política conservadora de conflictos. El control de ciclos, el límite de rondas y la autoridad transaccional siguen en GISELA.

## 4. Validaciones y rechazos

La admisión estática verifica los campos declarados, los tipos inferibles y las referencias iniciales. En ejecución también se comprueba que exista la instancia, que su carta admita la propiedad, que la relación tenga un campo declarado y que el resultado cumpla tipos y límites.

Los errores utilizados incluyen `INVALID_REFERENCE`, `TYPE_MISMATCH`, `PROPERTY_RANGE` y `REACTION_CONFLICT`. Un rechazo deja intactos mundo, historial, RNG, identidades y revisión confirmada.

## 5. Evidencia

El paquete `gisela/packages/h3_relaciones.package.json` permite reproducir el caso de reglas que suman confianza y modifican un casete. `gisela/engine/tests/test_h34a_values.py` incluye escenarios de éxito, conflictos, lectura sin materialización y rollback, además de una restauración que verifica la misma transacción pendiente.

La verificación general incluye admisión semántica, control de 500 líneas por archivo, máximo 30 líneas de código por función Python, recorridos anteriores y ejemplo H3.4a.

## 6. Pendiente fuera de H3.4a

La lectura y escritura de atributos de S.O.F.I.A. se abordará en H3.4b. Los efectos temporales y la ejecución de habilidades corresponden a H3.4c y H3.4d. Los selectores de entidades que requieren contexto dinámico y las acciones exploratorias no están incluidos en esta etapa.

La siguiente actividad recomendada es diseñar el cálculo de atributos `base`, `current` y `effective` sin duplicar sus valores confirmados.
