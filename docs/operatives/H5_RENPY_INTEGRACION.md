# H5 — Integración de GISELA con Ren'Py (laboratorio)

## Alcance

Se incorpora un cliente de presentación Ren'Py para consumir los paquetes
H4.6 y H4.6b sin duplicar lógica de autoría. El cliente renderiza exploración,
texto narrado, diálogo, elección, habilidades, solicitudes auxiliares,
evaluaciones visibles y finales. Los textos y las opciones proceden de
`GiselaSession.observe()` mediante `ExecutionGateway`.

## Decisiones

- GISELA continúa siendo la autoridad del mundo, reloj, RNG y consecuencias.
- La sesión se serializa como JSON opaco, único dato narrativo guardado en Ren'Py.
- Se restaura cada petición desde el snapshot, evitando objetos mutables
  compartidos con el guardado y sin servidor adicional.
- No se permite seleccionar acciones por índice sin consultar su `action_id`
  actual y la revisión correspondiente.
- Se deshabilita el rollback interactivo para no permitir nuevas tiradas
  tras un retroceso del cliente; guardar y cargar sigue habilitado.
- Se utiliza un solicitante local explícito con capacidades `act`,
  `observe_player` y `export_private`. La exportación no llega a la interfaz.
- El empaquetador solo copia código necesario y contratos; nunca código
  específico para controlar los finales del faro.

## Invariantes y pruebas

| Identificador | Invariante | Prueba |
|---|---|---|
| H5-01 | Tres rutas del faro terminan con el mismo snapshot que el cliente textual | `test_three_routes_match_gisela_state` |
| H5-02 | Una evaluación pendiente guarda y restaura idéntico resultado | `test_pending_evaluation_survives_restore` |
| H5-03 | Una acción no ofrecida o vencida no altera la partida | `test_rejects_stale_and_unoffered_actions` |
| H5-04 | Un guardado corrupto o con digest distinto no abre una sesión | `test_malformed_state_and_unknown_story_fail_closed` |
| H5-05 | El segundo paquete entra por el mismo adaptador | `test_second_adventure_uses_same_bridge` |
| H5-06 | La distribución excluye las pruebas internas y conserva contratos v1.5 | `test_packaging_excludes_author_tests` |
| H5-07 | El código empacado carga desde una ruta independiente del repositorio | `test_isolated_staged_runtime` |
| H5-08 | Repetir una petición desde el mismo snapshot fija idéntico resultado | `test_retry_same_snapshot_reuses_result` |

Las ocho pruebas residen en `tools/test_h5_adapter.py` y se descubren por el
verificador integral `tools/check_project.py`.

## Limitaciones comprobables

La ejecución en CPython no equivale a lanzar la interfaz del SDK. Antes de
considerar cerrado H5 para distribución deben verificarse en Ren'Py real:
instalación de las dependencias para su Python, lectura de contratos fuera de
archivos RPA, guardado/carga a mitad de una evaluación, entradas por teclado,
visualización de todos los estados y exportación a cada plataforma.

No se han integrado gráficos ni música comercial, ni se han publicado los
contenidos literarios del demo.
