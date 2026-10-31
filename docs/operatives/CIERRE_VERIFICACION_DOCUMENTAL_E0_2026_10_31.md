# Cierre focalizado: verificador y documentación de GISELA

Fecha: 2026-10-31. Alcance: ZIP `gisela(4).zip` recibido y copia de trabajo.
No se alteraron schemas, políticas de versiones ni comportamiento del motor.

## Causa y corrección E0

`tools/verify_e0_invariants.py` contrasta cada método de prueba nuevo de
`dice/tests/test_dice_hardening.py` con el catálogo
`E0_INVARIANTES_TRAZABILIDAD.json`. Faltaban los métodos D08, D09 y D10 en
el catálogo, aunque las pruebas existían. Se registraron respectivamente las
garantías de importación independiente de DICE, omisión de revalidación para
perfil compilado intacto y revalidación de perfil compilado mutado. **No se
relajó el validador ni se renombraron pruebas para evitar el error**.

## Coherencia documental

- README principal: verificación consolidada bajo `check_gisela.py`, sin
  instrucciones duplicadas. La ejecución desde fuera requiere ruta absoluta.
- `docs/guides/VERIFICACION_GISELA.md`: alcance, comandos y limitaciones.
- Arquitectura ALBERTO, E2, E3 y TRAITS/DICE: invocaciones vigentes cambiadas
  al verificador autónomo `check_gisela.py --full`.
- `docs/README.md`: nueva entrada de navegación a la guía de verificación.
- `tools/test_doc_links.py`: una prueba comprueba que el README y la arquitectura
  vigente no recomienden `python tools/check_project.py` y que los scripts
  de verificación citados estén presentes.
- ADR y registros históricos: sin alteraciones. Sus referencias al antiguo
  monorrepositorio se interpretan como historia, no como instrucciones actuales.

## Evidencias de esta ejecución

| Comprobación | Resultado |
| --- | --- |
| `python -m pytest -q dice/tests/test_dice_hardening.py tools/test_doc_links.py tools/test_quality.py` | 23 PASS, 24 subtests PASS, 2,68 s |
| `python tools/verify_e0_invariants.py` | PASS, tres anclajes nuevos reconocidos |
| `python tools/verify_e1_invariants.py` | PASS |
| `python tools/verify_e2_invariants.py` | PASS |
| `python tools/verify_e3_invariants.py` | PASS |
| `python tools/check_quality.py` | PASS |
| `python tools/check_doc_links.py` | PASS |
| Faro: rutas `completa`, `parcial`, `sin_preparacion` con `--verify-restores` | 3 PASS |
| Central: rutas `casete`, `solo`, `radio` con `--verify-restores` | 3 PASS |
| `python tools/check_gisela.py --full` | INCONCLUSO: primera suite llegó a 68 % sin fallos visibles antes del corte externo de 200 s; no hubo resultado global |

Las pruebas focales y los recorridos fueron ejecutados separadamente; **no
se declara que la ejecución integral conjunta haya pasado**. Tampoco se
verifican exhaustivamente semántica documental y aceptación gráfica de Ren'Py.

## Invariantes de diseño preservadas

El gateway de autoridad, la política de versiones de contratos y las
responsabilidades narrativas no fueron modificados. La corrección del catálogo
E0 conserva la verificación estricta de que los tests están anclados.
