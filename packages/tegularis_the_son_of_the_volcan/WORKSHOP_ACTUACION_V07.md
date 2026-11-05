# Taller de actuación v0.7: laboratorio GISELA

**Alcance histórico:** este documento registra una etapa incremental de
Tegularis. Sus pendientes corresponden a esa etapa; consulte el
[taller de cierre v0.7.7](WORKSHOP_CIERRE_V077.md) para el combate completo.

**Propósito:** comprobar que un autor puede declarar un reloj de oportunidades dentro de GISELA, sin convertir el turno narrativo en un turno de combate.

1. Consulte el contrato `actuation` del paquete `05_actuacion_v07_laboratorio.package.json`: cinco participantes, iniciativa 1d10, un turno por personaje en cada ronda, umbrales autorales 7 y 10.
2. Ejecute `glauquir --actuation --rounds 3 --auto --package ...` con la semilla que figura en el documento arquitectónico.
3. Compruebe en la transcripción la iniciativa persistente, las dos acciones de Clarisa y Parnecio y las tres de Gillius y Tegularis.
4. Seleccione Slash y después Double Slash cuando los TP de Parnecio permitan la carta; verifique los mensajes `emit_message` que registra la ejecución confirmada.
5. Guarde la sesión y retómela durante otra ronda con `--restore`. El orden inicial no se recalcula.
6. Ejecute `pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_actuacion_nativa_v07.py`: deberá superar las comprobaciones de relojes, duración, paralización, restauración y rechazo.

**Alcance:** este taller valida el *planificador de actuación*. Firebreath, Fénix, Regeneración, Preponderancia y las demás cartas todavía tienen que conectarse con consecuencias completas del combate. Las pruebas de efectos del planificador emplean cartas de prueba aisladas, no se hacen pasar por las cartas definitivas del juego.
