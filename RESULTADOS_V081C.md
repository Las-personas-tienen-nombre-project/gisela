# GISELA v0.8.1c — Evaluación de legibilidad de GLAUQUIR

## Fuente y alcance

Base: repositorio completo entregado como `GISELA_v081ab_presentaciones.tar.gz`. No se modificaron el DSL 1.5, las reglas del encuentro, la RNG, los contratos Observe/Act, la autorización, la iniciativa ni la trazabilidad causal.

La evaluación examinó las salidas textuales de las tres variantes mediante partidas automáticas. **No equivale a una prueba de usabilidad con personas**.

## Problemas encontrados y correcciones

1. «Participantes» e «Iniciativa» podían confundirse: los rótulos autorales ahora son «Orden de actuación» y «Tiradas de iniciativa». Solo se modificaron las etiquetas de los tres paquetes de presentación.
2. La lista de acciones mostraba letras e identificadores, pero no indicaba claramente el comando: ahora explica «Elija una letra o escriba: accion <id>».
3. La ventana de sucesos mostraba diez registros sin explicar que era parcial: cuando corresponde, muestra «Últimos 10 de N registros publicados»; no descarta ni reordena los registros de Observe.
4. «Desenlace: No disponible» era una indicación poco informativa durante el combate: ahora se presenta «Pendiente de confirmación» mientras el dato no ha sido publicado.

Se conservaron los identificadores de acciones, los datos publicados, las secuencias causales y el contenido original de los snapshots. Las mejoras se limitan al renderizado y las etiquetas autorales.

## Evidencias ejecutadas

- `python -m pytest -q engine/tests/test_lectura_v081c.py engine/tests/test_layouts_v081.py gisela/engine/tests/test_author_presentation_v080.py gisela/engine/tests/test_public_presentation_v080f.py`: **76 pruebas aprobadas**.
- `python tools/check_quality.py`: **aprobado**.
- `python -m pytest -q tools/test_quality.py`: **11 pruebas aprobadas**.
- Tres partidas completas mediante `python -m gisela.cli.glauquir --auto` con semilla idéntica: desenlace **victoria**, ronda final **6**, **816 registros causales por partida**.
- Hash SHA-256 de las tres trazas confirmadas: `5a55eb3ce7e854a048f34351060f1b967630bea48efdb8252dce9b016820e869`.
- Registros en `evidence/v081c/{participantes,decisiones,cronica}.{log,json}` y resumen en `evidence/v081c/comparacion_trazas.json`.

## Limitaciones y siguiente validación

La salida aún es extensa: imprime el estado público en cada decisión; la crónica expone identificadores técnicos como `session:bonus_mp_gillius`. No se eliminaron campos causales ni se inventaron mensajes narrativos para ocultarlos. Para cambiar el nivel de detalle se recomienda introducir una **preferencia del cliente** (resumen/detalle), nunca un nuevo estado del motor, y probarla con usuarios reales.

No se realizó una prueba manual con personas ni la regresión oficial completa `check_gisela --full` en este incremento. Ruff, Radon y Bandit siguen sin estar instalados en este entorno; el verde completo debe comprobarse localmente con el verificador oficial.
