# v0.8.2e — Criterios de integración pendientes de certificación

La validación no debe cambiar la fuente de verdad Observe ni la autorización Act.
La comparación de presentaciones mide estado lógico, traza causal y RNG, sin
comparar el contenido de `presentation`, que por definición cambia por autoría.

Se agregó `gisela/engine/tests/test_release_v082e.py`: seis paquetes con igual
semilla y doce comandos públicos; restaura durante la secuencia. Esta es
una prueba de invariancia parcial, no un recorrido completo de partida.

Para cerrar el hito se necesita: instalar las dependencias fijadas en
`requirements-dev.txt`, completar `python tools/check_gisela.py --full`,
ejecutar por GLAUQUIR tres partidas completas de las variantes v0.8.1,
comprobar desenlaces con estrategia y semilla reproducibles, verificar
compatibilidad con un paquete anterior sin `presentation`, y revisar la
clasificación semántica sin atribuir semántica causal inexistente.

Los detalles y resultados observados están en `RESULTADOS_V082.md`.
