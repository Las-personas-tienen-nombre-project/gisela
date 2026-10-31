# H4. Revisión, implementación y cierre de la exploración

Fecha de revisión: 30 de octubre de 2026.

## Alcance

H4 incorpora exploración con acciones declarativas, interacción con el mundo, consultas diagnósticas para autores y una CLI de referencia. No modifica los contratos v1.2 ni incorpora una segunda autoridad narrativa. Ren'Py sigue pendiente.

## H4.1. Exploración básica

Estado: terminado.

Se permite abrir un paquete directamente en una escena o entrar a ella desde un paso narrativo. `Observe` presenta los actores y elementos visibles, junto con acciones propias de la escena y de sus elementos. Cada acción tiene un identificador de proyección y una procedencia que señala su propietario.

Pruebas: escena inicial sin turno, proyección de actores y elementos, elementos ocultos, identificadores repetidos en propietarios distintos, lectura sin mutación y restauración del mismo estado.

Debilidad detectada: el contrato de la escena no define una operación de observación especial para inspeccionar objetos. Se resolvió mediante acciones declarativas comunes, sin incorporar otro lenguaje ni inferir consecuencias a partir del nombre de la acción.

## H4.2. Interacción con el mundo

Estado: terminado para las operaciones declarativas implementadas.

Las acciones exploratorias permiten ejecutar consecuencias de ALBERTO, registrar hechos, cambiar de escena y abrir nodos. La procedencia se revalida antes de ejecutar. Las modificaciones se procesan sobre el borrador transaccional de GISELA, incluidas las reacciones y solicitudes de decisiones adicionales.

Pruebas: inspección mediante hechos, transferencia de un objeto, desplazamiento, transición a diálogo, revisión obsoleta, errores con rollback, solicitud auxiliar, cancelación y restauración determinista.

Debilidad detectada: una acción exploratoria no debe asumir que mostrar otra escena desplaza físicamente al personaje. `set_scene` y `move_character` siguen siendo operaciones distintas, bajo control del autor.

## H4.3. Consultas de ALBERTO y S.O.F.I.A.

Estado: terminado para diagnósticos explícitos de desarrollo.

`session.debug_query()` permite leer entidades, personajes, propiedades, relaciones, hechos y Scoresheet sin modificar el estado confirmado. La CLI exige `--developer` para ofrecer estos comandos.

Pruebas: propiedades y relaciones con valores iniciales, conocimientos, habilidades, Scoresheet, consultas inválidas y ausencia de cambios de sesión.

Debilidad detectada: un diagnóstico completo puede revelar información oculta. No forma parte de `Observe` del jugador. La visibilidad para interfaces públicas continúa determinada por las escenas y sus condiciones declarativas.

## H4.4. CLI de referencia

Estado: terminado para el recorrido de paquetes y diagnóstico humano.

La CLI presenta escenas, actores, elementos, diálogos, decisiones, habilidades y errores, y permite guardar, cargar y consultar el estado confirmado. Las acciones se obtienen de `Observe` y se envían mediante `Act`. No contiene consecuencias narrativas propias.

Pruebas: recorrido automático hasta un final, consola interactiva, guardado, carga, consultas y regresiones del MVP y de H2 y H3.

Debilidad detectada: `--auto` no planifica rutas de exploración complejas. Su finalidad es repetir caminos de prueba, no tomar decisiones por el autor. Para recorridos más largos se usan tests o ejemplos Python que seleccionan acciones ofrecidas por el motor.

## Restricciones y oportunidades pendientes

Se mantienen los límites de 500 líneas por archivo mantenido, 30 líneas por función sin docstring y tres parámetros explícitos. Los módulos nuevos separan proyección, selección, consulta y consola según su responsabilidad. Se conservan versiones y digest de paquetes al restaurar.

No se implementan referencias contextuales no vinculadas, juego libre de habilidades desde escenas, preparación exploratoria de mano ni adaptación visual con Ren'Py. Su incorporación requerirá pruebas nuevas y una decisión expresa, sin simular soporte desde la CLI.

## Evidencia

`gisela/engine/tests/test_h4_exploration.py` verifica las cuatro etapas. El paquete `gisela/packages/h4_exploracion.package.json` y `docs/guides/examples/ejemplo_exploracion.py` permiten reproducir el flujo. `python tools/check_project.py` concentra las comprobaciones generales y la guía `docs/guides/EXPLORACION_CLI.md` documenta su uso.
