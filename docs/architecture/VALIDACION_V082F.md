# GISELA v0.8.2f: Determinismo, restauración y distribución

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](../operatives/REVISION_DOCUMENTAL_2026_11_04.md).

## Fuente de verdad

Se trabajó sobre `gisela.tar(20261104-181029).gz`, sin alterar el motor de reglas,
las cartas, Act/Observe, la versión del DSL ni los límites de calidad.

## Procedimiento y cobertura

- Hito 2: `test_release_v082f.py` compara seis presentaciones productivas de
  Tegularis, sus estados lógicos, RNG, traza y autorización pública.
- Hito 3: se comparan sesiones continuas con sesiones restauradas desde JSON;
  los snapshots manipulados se rechazan sin cambiar la sesión viva.
- Hito 4: se comprueba la proyección pura de tabla, eventos y plantillas sobre
  información no bélica de inspección. También se ejecuta el paquete antiguo
  `ejemplo_minimo.package.json` usando Observe/Act y restauración.
- Hito 5: se usa un paquete v1.5 sin presentación; las pruebas anteriores de
  v0.8.1 y v0.8.2 no fueron reemplazadas.
- Hito 6: se construyó la wheel 0.1.21 y se instaló en un venv limpio.
  La CLI no inicia sin dependencias; no se pudo obtener `jsonschema` desde el
  índice. Con dependencias del intérprete anfitrión mediante `PYTHONPATH`,
  `glauquir --help`, `gisela --help` y la historia mínima por CLI finalizaron
  con código 0. Esto NO equivale a instalación aislada verificada.

## Resultado de pruebas concluidas

- `python tools/check_quality.py`: aprobado, límites 700/64/3.
- `python -m pytest -q tools/test_quality.py`: 11 aprobadas.
- Pruebas de presentación anteriores: 30 aprobadas (`targeted.log`).
- Nueva batería de determinismo/restore: 3 aprobadas (`determinism4.log`).
- Pruebas adicionales del paquete heredado y proyección no bélica: 2 aprobadas.
- Wheel construida: `gisela_narrative_engine-0.1.21-py3-none-any.whl`.
- Instalada en entorno limpio con `--no-deps`; ejecución bloqueada por ausencia
  de `jsonschema`. En ejecución con dependencias prestadas, CLIs e historia OK.

## Controles no certificados

La suite completa de motor/contratos/bibliotecas superó el límite de tiempo,
sin resumen final (`regression.log`); otra ejecución combinada de pruebas
focalizadas también fue interrumpida (`final_focused.log`). No cuentan como
aprobadas. Ruff, Radon y Bandit no están disponibles en este entorno; la
verificación satisfactoria indicada por el usuario para la copia adjunta es
antecedente, no una nueva ejecución en esta entrega. La wheel no pudo resolver
sus dependencias desde un índice, así que la prueba de instalación en un
entorno limpio sigue pendiente.

## Reproducción en un entorno con dependencias

```bash
python -m pip install -r requirements-dev.txt
python tools/check_gisela.py --full
python -m pytest -q gisela/engine/tests/test_release_v082f.py
python -m pip wheel --no-deps --no-build-isolation -w dist .
python -m venv /tmp/gisela-v082f-clean
/tmp/gisela-v082f-clean/bin/python -m pip install dist/gisela_narrative_engine-*.whl
(cd /tmp && /tmp/gisela-v082f-clean/bin/glauquir --help)
(cd /tmp && /tmp/gisela-v082f-clean/bin/gisela --help)
python tools/verify_cli_wheel.py
```

**Estado:** verificación parcial de v0.8.2f. No afirmar cierre de certificación
sin suite completa y wheel aislada con dependencias instaladas.
