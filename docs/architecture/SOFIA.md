# S.O.F.I.A. Atributos opcionales de ALBERTO

## Propósito

S.O.F.I.A. es un conjunto opcional de cinco atributos de personaje. No es un motor independiente, no establece reglas narrativas universales y no confirma transacciones. GISELA conserva la autoridad sobre las acciones, mientras que ALBERTO resuelve los atributos de las instancias y sus restricciones.

La API implementada se explica con ejemplos en este contrato de S.O.F.I.A.. Para comenzar desde cero, consulte el [inicio rápido](../guides/QUICK_START.md).

## Atributos y definiciones

Los cinco nombres admitidos por los contratos son `strength`, `openness`, `fortune`, `intelligence` y `awareness`. Una carta de personaje puede declarar el objeto `sofia` con esos cinco enteros. Cuando se omite, el personaje no participa de esta mecánica.

La escala de los atributos base y actuales se fija mediante `manifest.sofia_scale`, cuyos valores predeterminados son mínimo 0 y máximo 10. El validador semántico verifica los valores declarados en cartas e instancias. No se generan atributos implícitos para personajes sin S.O.F.I.A.

## Valores y responsabilidad

| Componente | Fuente | Modificable directamente |
| --- | --- | --- |
| `base` | Carta de personaje | No |
| `current` | Instancia de personaje, con `base` como predeterminado | Sí, mediante `set` o `add` |
| `modifier` | Modificadores de las instancias de efecto activas | No |
| `effective` | `current + modifier` | No |

La lectura no materializa propiedades ausentes. El ejecutor solo necesita guardar `current` cuando difiere de `base`; volver al valor base puede eliminar el valor sobrescrito. El cálculo no altera el mundo ni las revisiones. Los modificadores pueden hacer que `effective` supere la escala, sin elevar los límites de `current`.

Las operaciones de escritura deben referirse al componente `current`, utilizar un entero y respetar los límites. Los conflictos de una ronda reactiva siguen la semántica de H3.4a: las sumas compatibles se combinan, las asignaciones iguales se consolidan y las escrituras incompatibles producen rollback.

## API del ejecutor

La API disponible es `sesion.scoresheet("id_del_personaje")`. Devuelve un documento compatible con `scoresheet.schema.json` y contiene la revisión confirmada, las cinco filas de atributos, las instancias de efectos activos y las habilidades de mano y reserva.

La versión actual es una API Python de la sesión y no implementa por sí misma filtros de visibilidad entre personajes. Un anfitrión no debe exponer fichas ajenas al jugador sin una política explícita de autorización; la API Python de Scoresheet no impone ese filtro por sí sola.

Esta operación no es una acción `Act`: no avanza turnos, no consume RNG y no modifica el estado. Cuando existe una transacción pendiente se observa únicamente el estado confirmado. Las expresiones narrativas `stat` y las condiciones `compare` también pueden consultar los atributos base, actuales y efectivos.

## Modificadores de efectos

El cálculo actual admite efectos declarados en el estado inicial cuya carta incluye la lista `modifiers`. Se suman los importes para cada atributo y personaje de destino. H3.4c también permite aplicar, acumular y terminar dinámicamente esos efectos. La ejecución de habilidades pertenece a H3.4d.

## Errores y determinismo

ALBERTO rechaza referencias a personajes inexistentes, consultas a personajes sin S.O.F.I.A., valores no enteros y resultados `current` fuera de escala. Una excepción controlada dentro de `Act` provoca el descarte íntegro del borrador y deja intactos mundo, historial y RNG.

La proyección Scoresheet no se persiste por separado. Se obtiene a partir de las definiciones admitidas y de la sesión confirmada, lo que permite reproducirla tras una restauración con el mismo paquete.

## Verificación y límites

El paquete de ejemplo se encuentra en `gisela/packages/h3_sofia.package.json`. Sus operaciones están cubiertas por `gisela/engine/tests/test_h34b_sofia.py` (no se distribuye el antiguo módulo de ejemplos del demo). Las pruebas de S.O.F.I.A. pueden ejecutarse con `python -m unittest gisela.engine.tests.test_h34b_sofia -q`; la política estructural se verifica mediante `python tools/check_quality.py`.

S.O.F.I.A. no impone chequeos universales de atributos: el autor declara las condiciones que necesita. El uso de habilidades fuera de sus ventanas autorizadas no está permitido por el ejecutor; véase la prueba `test_playing_skill_outside_window_is_rejected`. Esta API Python tampoco proporciona una interfaz Ren'Py de Scoresheet. El [roadmap](../operatives/ROADMAP.md) enumera los pendientes generales del proyecto, pero no declara estas tres características como entregas comprometidas.

## Habilidades y S.O.F.I.A.

Los requisitos y resultados de habilidades pueden consultar `base`, `current` o `effective` mediante condiciones declarativas. S.O.F.I.A. no ejecuta ni consume cartas. Véase [ALBERTO, operaciones de habilidades](ALBERTO.md).

## Significado de atributos e integración con DICE

`openness` representa apertura interpersonal, empatía y carisma; `awareness` está orientado a la percepción de fenómenos sobrenaturales. No deben tratarse como estadísticas intercambiables ni deducir de su valor un interés romántico universal. El adaptador interno TRAITS-DICE puede solicitar un atributo efectivo opcional mediante una referencia S.O.F.I.A. que resuelve ALBERTO; DICE solo recibe números. La evaluación declarativa y su presentación visible fueron implementadas posteriormente en E2 y E3. Véanse [TRAITS](../../traits/README.md), [DICE](../../dice/README.md) y [E3](E3_EVALUACIONES_VISIBLES.md).
