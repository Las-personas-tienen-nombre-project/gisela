# S.O.F.I.A. Atributos opcionales de ALBERTO

## Propósito

S.O.F.I.A. es un conjunto opcional de cinco atributos de personaje. No es un motor independiente, no establece reglas narrativas universales y no confirma transacciones. GISELA conserva la autoridad sobre las acciones, mientras que ALBERTO resuelve los atributos de las instancias y sus restricciones.

La API implementada se explica con ejemplos en la [guía de S.O.F.I.A.](../guides/SOFIA_ATRIBUTOS.md). Para comenzar desde cero, consulte la [guía de inicio rápido](../guides/INICIO_RAPIDO.md).

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

La versión actual es una API Python de la sesión y no implementa por sí misma filtros de visibilidad entre personajes. Un anfitrión no debe exponer fichas ajenas al jugador sin una política explícita de autorización en H4.

Esta operación no es una acción `Act`: no avanza turnos, no consume RNG y no modifica el estado. Cuando existe una transacción pendiente se observa únicamente el estado confirmado. Las expresiones narrativas `stat` y las condiciones `compare` también pueden consultar los atributos base, actuales y efectivos.

## Modificadores de efectos

El cálculo actual admite efectos declarados en el estado inicial cuya carta incluye la lista `modifiers`. Se suman los importes para cada atributo y personaje de destino. H3.4c también permite aplicar, acumular y terminar dinámicamente esos efectos. La ejecución de habilidades pertenece a H3.4d.

## Errores y determinismo

ALBERTO rechaza referencias a personajes inexistentes, consultas a personajes sin S.O.F.I.A., valores no enteros y resultados `current` fuera de escala. Una excepción controlada dentro de `Act` provoca el descarte íntegro del borrador y deja intactos mundo, historial y RNG.

La proyección Scoresheet no se persiste por separado. Se obtiene a partir de las definiciones admitidas y de la sesión confirmada, lo que permite reproducirla tras una restauración con el mismo paquete.

## Verificación y límites

El paquete de ejemplo se encuentra en `gisela/packages/h3_sofia.package.json`. Puede ejecutarse mediante `python -m docs.guides.examples.ejemplo_sofia_dinamica`. El verificador general, `python tools/check_project.py`, incluye las pruebas de S.O.F.I.A., los ejemplos y la política estructural de mantenimiento.

No están disponibles los chequeos universales de atributos, las acciones de habilidades fuera de las ventanas de nodo ni una interfaz de Ren'Py para Scoresheet. Esas capacidades se mantienen expresamente como trabajo pendiente en el [ROADMAP](../operatives/ROADMAP.md).

## Habilidades y S.O.F.I.A.

Los requisitos y resultados de habilidades pueden consultar `base`, `current` o `effective` mediante condiciones declarativas. S.O.F.I.A. no ejecuta ni consume cartas. Véase [Habilidades](../guides/HABILIDADES.md).

## Significado de atributos e integración con DICE

`openness` representa apertura interpersonal, empatía y carisma; `awareness` está orientado a la percepción de fenómenos sobrenaturales. No deben tratarse como estadísticas intercambiables ni deducir de su valor un interés romántico universal. El adaptador interno TRAITS–DICE puede solicitar un atributo efectivo opcional mediante una referencia S.O.F.I.A. que resuelve ALBERTO; DICE solo recibe números. La evaluación declarativa y su presentación visible siguen pendientes de ADR-019. Véase [integración fase 1](TRAITS_DICE_INTEGRACION_FASE_1.md).
