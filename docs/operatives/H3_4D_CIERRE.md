# H3.4d. Cierre de ejecución de habilidades

## Alcance implementado

Se incorpora la ejecución de cartas de habilidad durante `skill_window`, con requisitos declarativos, consecuencias, condiciones de resultados, límite opcional de usos, retorno a mano o reserva y descarte. GISELA administra la acción voluntaria, la transacción y su reconstrucción; ALBERTO administra las zonas, capacidades y la identidad de las instancias.

El historial de ejecución registra cada intento confirmado como `skill_played`, con identificador de ejecución y paso. El contador de la ventana se deriva de esa traza; no se persiste otra variable con el mismo significado.

## Semántica fijada

1. Solo se ofrecen habilidades en la mano de `player_character`, dentro de una ventana activa.
2. Los requisitos fallidos inhabilitan la acción. No equivalen a un intento consumido.
3. Un intento autorizado retira temporalmente la instancia de su mano y ejecuta las consecuencias en un borrador de GISELA.
4. Los resultados habilitados se determinan después de las consecuencias base y antes de ejecutar cualquiera de los resultados.
5. El retorno se decide después de ejecutar los resultados. Las políticas contradictorias producen un error sin confirmación parcial.
6. Si falta una política de retorno explícita, la carta se descarta. Si la zona de retorno está llena, se solicita una decisión auxiliar cuando exista una alternativa legal.
7. Solo un intento confirmado consume un uso de la ventana. Error, cancelación o solicitud pendiente no consumen usos confirmados.
8. `play_skill` se revalida al recibir `Act` y nuevamente durante la reconstrucción de una espera guardada.

No se modifican los schemas v1.2: sus contratos ya contienen estos campos. No se incorporan scripts de autor, nuevas autoridades de estado ni selección arbitraria de cartas.

## Pruebas y criterios de aceptación

`gisela/engine/tests/test_h34d_skills.py` comprueba el consumo, la opción de continuar, requisitos, zonas, retornos, políticas en conflicto, restauración, cancelación, errores técnicos y límites de uso. El ejemplo `docs/guides/examples/ejemplo_habilidades.py` muestra la API pública. El proyecto mantiene los límites automáticos de 500 líneas por archivo técnico, 30 líneas por función y tres parámetros explícitos.

Para repetir el control:

```bash
python -m docs.guides.examples.ejemplo_habilidades
python -m unittest gisela.engine.tests.test_h34d_skills -q
python tools/check_project.py
```

## Trabajo posterior

H3.4d cierra las habilidades disponibles durante nodos y deja H3.4 terminado para el subconjunto ejecutable. Las acciones de escena y las referencias contextuales pertenecen a H4. La integración con Ren'Py pertenece a H5. Ninguno de estos hitos queda validado por la implementación actual.
