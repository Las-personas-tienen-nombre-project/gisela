# Resultados de validación — GISELA v0.8.0, avance parcial

## Fuente

Repositorio `gisela.tar.gz` adjunto por el usuario, conservado íntegramente y
modificado en copia. El paquete usado es `10_balance_v078.package.json`, que
representa la versión más reciente de Tegularis presente en la fuente y declara
el DSL 1.5. Se han sincronizado las copias de módulos raíz y `gisela/`.

## Comprobaciones terminadas

- Basal `python tools/check_quality.py`: **OK**, 700 líneas / 64 por función / 3 parámetros explícitos.
- Basal `python -m pytest -q tools/test_quality.py`: **11 aprobadas**.
- Tras cambios, ambos controles de calidad: **OK; 11 aprobadas**.
- `PYTHONPATH=/mnt/data/work python -m pytest -q engine/tests/test_author_presentation_v080.py`: **8 aprobadas**.
- `PYTHONPATH=/mnt/data/work python -m pytest -q engine/tests/test_actuation_public_v073.py`: **7 aprobadas** (versión original sin presentación).
- Admisión real del paquete modificado: **aceptada**, digest iniciado `2bd6022cc9ee`.
- Prueba de integración directa nueva sesión / Observe / Act: **acción confirmada**.
- Trazabilidad causal después de Act: **31 elementos públicos** observados.
- Restauración desde snapshot: **presentación idéntica**.
- Repetición de acción con revisión obsoleta: **rechazada `STALE_PROJECTION`**.
- Prueba de ejemplo no bélico: proyección pura de lista vacía y texto autoral.

## Pruebas no completadas o no certificadas

- Se inició regresión conjunta de cuatro suites de actuación y presentación;
  se interrumpió al llegar al límite de ejecución, después de emitir 13 puntos
  de progreso. **No se certifica el resultado de esa ejecución.**
- No se ha ejecutado campaña natural completa desde GLAUQUIR con las nuevas
  regiones de Tegularis.
- No se ha completado selección de objetivos parametrizados desde el cliente.
- No se dispone de `ruff` en el entorno para ejecutar esa comprobación adicional.
- No se ha ejecutado la validación exhaustiva con Bandit ni regresión general.

## Limitaciones funcionales conocidas

La presentación autoral se limita a regiones y vinculación segura sobre Observe
actual. El contrato público no publica en esta vertical una estructura de
estado detallado para todos los participantes, ni ofertas completas con
parámetros; sería incorrecto fabricar esa información desde la capa gráfica.
Esta entrega **no cumple todavía todos los criterios de aceptación de v0.8.0**.
No se alteraron reglas de combate, balance ni mecanismo RNG.
