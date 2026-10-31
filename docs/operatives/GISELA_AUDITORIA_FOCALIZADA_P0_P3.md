# GISELA — Auditoría focalizada P0–P3 y Addendum A

Fecha de ejecución: 2026-10-31. Revisión de entrada: `264640220c6b651a045d7b5aaf94882ed3e93a5e` (`added guide to create a package`). Entorno observado: Python 3.13.5. El ZIP de entrada contenía modificaciones documentales no confirmadas en Git; se conservaron y no se atribuyen a esta intervención.

## Resumen ejecutivo

P0 estaba confirmado. `Validator.validate_session()` volvía a recorrer el schema completo del paquete en cada validación transaccional, aunque `AdmittedPackage` conserva el paquete como JSON canónico privado y `materialize()` entrega copias independientes. Se separó la validación pública de snapshot+paquete de la validación interna de snapshot contra un paquete ya admitido. En el mismo proceso y sobre el mismo snapshot, la mediana pasó de 10,170 ms a 1,570 ms. La instrumentación de creación de sesión más una acción ya no registró `check_schema('package', ...)` dentro del runtime.

P1 confirmó un punto de diagnóstico defectuoso en `action_handler`: `KeyError`, `TypeError`, `ValueError` o `StopIteration` inesperados se convertían en `INVALID_STATE` incluyendo el detalle técnico en el mensaje público. El código contractual de salida se conserva, porque `result.schema.json` no define un `INTERNAL_ERROR`, pero ahora el detalle se registra mediante logging con traceback y el consumidor recibe un mensaje genérico. La prueba nueva verifica diagnóstico y atomicidad. Las capturas equivalentes de restauración se conservaron: allí la entrada es un snapshot externo y `RESTORE_MISMATCH` es la frontera contractual adecuada, con causa encadenada.

P2 reproduce el crecimiento informado y lo clasifica como contractual, no accidental. En Faro de Niebla el historial representa 85,70 % del snapshot final; en Central Clasificadora, 91,97 %. El recorrido sintético de 120 movimientos muestra crecimiento aproximadamente lineal del tamaño (6.387 B de historial a 10 acciones; 50.944 B a 120). `history.reading` es explícitamente un registro autoritativo y persistente según la documentación vigente; no se compactó ni se separó sin una decisión de contrato. La mediana por acción aumenta de 35,747 ms a 82,610 ms entre los primeros y últimos bloques medidos porque la validación de sesión recorre estructuras históricas crecientes. Se documenta como costo residual, no se introduce un índice serializado ni un límite arbitrario.

P3 confirma soporte efectivo y pruebas representativas para 1.2–1.5. Los ADR vigentes obligan a conservar la semántica de 1.2–1.4, por lo que no se retiró soporte. La recomendación es tratar 1.5 como versión vigente para nuevas capacidades y 1.2–1.4 como compatibilidad heredada sin extenderlas salvo obligación contractual. Retirar cualquiera de ellas sigue **PENDIENTE DE APROBACIÓN**.

A1 confirmó alto acoplamiento interno deliberado alrededor de `GiselaSession`, pero no una duplicación de autoridad que justifique capas nuevas. `action_handler` es el único de los cinco módulos estudiados que confirma `_state`; `authorized_gateway` solo restaura `_state` al snapshot anterior cuando falla la persistencia antes de quedar incierta. `scene_actions`, `projection` y `public_view` son lectores/proyectores. No se introdujeron getters, protocolos ni servicios cosméticos.

A2 transforma la independencia documentada en contrato probado: MARY ya poseía una prueba por proceso aislado; se añadieron equivalentes para DICE, TRAITS y `narrative_conditions`. Los cuatro paquetes importan sin cargar `gisela` ni las bibliotecas vecinas prohibidas por cada prueba.

A3 estaba confirmado en dos niveles. `dice.evaluate()` recompilaba siempre el perfil recibido y `traits_dice_bridge.resolve()` volvía a llamar `compile_profile()` aunque `EvaluationRoutes` ya había compilado esos perfiles al crear la sesión. DICE ahora reconoce una compilación intacta mediante una huella defensiva; si el llamante muta el mapping, vuelve a validar. El bridge reutiliza el perfil que ya compiló `compile_package_evaluations`. En microbenchmark, `evaluate()` pasó de 0,1292 ms con perfil crudo a 0,0053 ms con perfil compilado.

## Registro de hallazgos

| Código | Severidad | Evidencia | Causa | Resolución | Estado |
|---|---|---|---|---|---|
| P0-01 | Alta rendimiento | `validate_session` ejecutaba schema `package` y `session` en cada `_validate_state` | Una misma rutina servía frontera no confiable y transacción interna | `_validate_admitted_session` omite solo schema de paquete; conserva schema/semántica/digest de sesión | Corregido |
| P1-01 | Media diagnóstico | `action_handler.act` capturaba errores estructurales y publicaba su texto como `INVALID_STATE` | Falta de canal interno de diagnóstico | logging con traceback + mensaje público genérico; rollback se mantiene | Corregido dentro del contrato vigente |
| P2-01 | Media costo | Faro 85,70 %, Central 91,97 % del snapshot en historial | Historial autoritativo persistente, especialmente `reading` | No se cambia contrato; costo medido y documentado | Conservado |
| P2-02 | Media rendimiento | Acción sintética: 35,747 → 82,610 ms al crecer 20 → 120 acciones | Validación de sesión recorre historial creciente | Sin optimización especulativa; queda riesgo residual | Conservado |
| P3-01 | Baja mantenimiento | 52 schemas JSON: 13 por cada versión 1.2–1.5 | Compatibilidad explícita y evolución versionada | Mantener; 1.5 vigente, anteriores heredadas | Conservado |
| A1-01 | Media mantenibilidad | Módulos de orquestación leen atributos privados de sesión | Son colaboradores internos de una única autoridad | No añadir fachada artificial; documentar fronteras | Conservado |
| A2-01 | Media verificación | Solo MARY tenía importación aislada explícita | Cobertura desigual del contrato de independencia | Tests aislados para DICE, TRAITS y condiciones | Corregido |
| A3-01 | Media rendimiento | `evaluate` y bridge recompilaban perfil ya compilado | No existía señal verificable de compilación | mapping compilado con huella; bridge reutiliza plan compilado | Corregido |

## P0 — admisión frente a transacción

`AdmittedPackage` guarda `_payload_json` y `materialize()` reconstruye un objeto nuevo. Las pruebas existentes `test_admitted_copy_not_affected_by_caller_mutation` y `test_mutating_materialized_package_does_not_change_session` ya protegen referencias compartidas. La sesión conserva su propia materialización y no expone un booleano de confianza.

La API pública `Validator.validate_session(snapshot, package, digest)` continúa validando `package` y `session`. Solo `GiselaSession._validate_state()` usa la ruta privada para paquete admitido. Restauración sigue usando la validación completa porque el snapshot cruza una frontera no confiable.

Medición registrada en `docs/operatives/evidence/focal_metrics.json`:

| Ruta | n | Mediana | Mínimo | Máximo |
|---|---:|---:|---:|---:|
| validación completa | 15 | 10,170 ms | 7,480 ms | 15,733 ms |
| paquete admitido | 15 | 1,570 ms | 1,237 ms | 2,103 ms |

Instrumentación de creación + una acción: `session, observe, act, session, observe`; no aparece `package`.

## P1 — clasificación de capturas

- `action_handler`: datos de `Act` ya pasaron schema y autorización antes de ejecutar. Un error estructural inesperado puede ser defecto interno. Se conserva `INVALID_STATE` por compatibilidad de schema, pero se registra el traceback y se evita filtrar el detalle al consumidor.
- `runtime.restore_session`, `_validate_replay` y `evaluation_pending.validate_replay`: la operación reconstruye un snapshot suministrado por el host. `RESTORE_MISMATCH` es apropiado; la excepción original permanece en `__cause__`.
- `authorized_gateway`: los dos `except Exception` protegen adquisición/liberación de store y persistencia. No convierten defectos del motor en errores narrativos; repropagan o elevan `GatewayError`, y el rollback/estado incierto es deliberado.
- Validadores semánticos y compiladores: las capturas examinadas operan sobre documentos autorales o entradas numéricas y producen diagnósticos de admisión; se conservaron.

No se añadió una nueva jerarquía de excepciones ni un código público no previsto por schemas.

## P2 — historial

Consumidores identificados:

- `facts`: condiciones narrativas, validación de referencias y causalidad.
- `executions`: turnos, cursor y selecciones persistentes.
- `trace`: procedencia causal y algunas consultas internas, por ejemplo retorno de habilidades.
- `reading`: API pública de historial y continuidad de lectura; la documentación H4.5 lo define como dato autoritativo dentro de la sesión.

Resultados representativos:

| Caso | Turnos | Snapshot | Historial | % historial | restore mediana |
|---|---:|---:|---:|---:|---:|
| Central, ruta casete | 15 | 19.049 B | 17.520 B | 91,97 % | 63,148 ms |
| Faro, ruta completa | 7 | 11.102 B | 9.514 B | 85,70 % | 54,783 ms |

Recorrido sintético de movimientos repetidos en Central:

| Acciones | Snapshot | Historial | trace | reading |
|---:|---:|---:|---:|---:|
| 10 | 7.888 B | 6.387 B | 11 | 27 |
| 30 | 15.958 B | 14.457 B | 31 | 67 |
| 60 | 28.091 B | 26.590 B | 61 | 127 |
| 120 | 52.447 B | 50.944 B | 121 | 247 |

La forma observada es lineal en almacenamiento. No se encontró duplicación accidental independiente de la semántica: cada movimiento conserva la acción y la nueva presentación en `reading`, tal como exige el registro de lectura. Compactarlo cambiaría la experiencia de historial restaurado. P2 se cierra como **Conservado**.

## P3 — matriz de compatibilidad

| Capacidad | 1.2 | 1.3 | 1.4 | 1.5 |
|---|---|---|---|---|
| Admisión estructural | Soportada | Soportada | Soportada | Soportada |
| Validación semántica | Soportada | Soportada | Soportada | Soportada |
| Inicio de sesión | Soportado | Soportado | Soportado para el subconjunto ejecutable E2 | Soportado |
| Ejecución representativa | Sí | Sí, TRAITS | Sí, evaluación oculta | Sí, visible/acknowledged y escenas actuales |
| Restauración estable | Sí | Sí | Sí | Sí |
| Restauración pendiente | Según capacidades de versión | Según capacidades de versión | Sin `pending_evaluation` visible | Sí |
| Rechazo de incompatibilidades | Sí | Sí | Sí | Sí |

Consumidores del repositorio: nueve paquetes 1.2, ningún archivo de paquete 1.3 pero fixtures de prueba TRAITS, un paquete 1.4 y tres paquetes 1.5. Los trece schemas de cada versión permanecen presentes (52 JSON). `test_pa001_version_restore.py` verifica roundtrip representativo de las cuatro versiones y las 12 restauraciones cruzadas incompatibles.

Recomendación: **B — 1.5 vigente; 1.2–1.4 compatibilidad heredada**. No extender capacidades nuevas sobre formatos antiguos salvo necesidad contractual. El retiro de soporte contradice ADR-020/022/023 y queda **PENDIENTE DE APROBACIÓN**.

## A1 — mapa de dependencias internas

| Módulo | Acceso privado | Lectura/escritura | Responsabilidad | Riesgo |
|---|---|---|---|---|
| `action_handler` | `_state`, `_validate_state`, `_project_state`, `_execute_source`, `_commit`, `_publish_*`, `_fail` | Lee y confirma `_state` | autorizar y coordinar una transacción | Medio: autoridad sensible, pero explícita y cubierta por rollback |
| `scene_actions` | `_state`, `_definitions`, `_scenes`, `_cards` | Solo lectura | resolver acciones exploratorias y su procedencia | Bajo |
| `authorized_gateway` | `_state`, `_lock`, `_admitted`, `_gateway_attached` | Lee; escribe marcador y rollback de `_state` | exclusión, autorización externa y checkpoint | Medio: rollback directo justificado por atomicidad de persistencia |
| `projection` | `_state`, `_cards`, `_definitions`, `_mary`, `_current_step` | Solo lectura | construir `Observe` | Bajo |
| `public_view` | `_state`, `_cards`, `_definitions` | Solo lectura | enriquecer proyección pública | Bajo |

No se encontró ciclo problemático de importación en arranque. Hay colaboración bidireccional diferida entre `projection` y `scene_actions` mediante imports locales, y `public_view` importa `projection.text`; los imports diferidos evitan el ciclo de inicialización. Cambiar un atributo interno puede romper varios colaboradores, pero todos viven dentro del paquete `gisela.engine` y dependen de la misma autoridad. Sustituirlos por getters o protocolos no reduciría responsabilidades ni autoridad.

Decisión A1: **Conservar** la frontera interna. La escritura de `action_handler` y el rollback del gateway son los puntos que deben seguir cubiertos por pruebas transaccionales; no se justifica un rediseño.

## A2 — independencia verificable

Pruebas por proceso nuevo:

- MARY: preexistente, no importa GISELA/ALBERTO.
- DICE: nueva, no importa GISELA/TRAITS/MARY.
- TRAITS: nueva, no importa GISELA/DICE/MARY.
- `narrative_conditions`: nueva, no importa GISELA/DICE/TRAITS/MARY.

Resultado: MARY 21 tests; DICE 18; TRAITS 26; `narrative_conditions` 1; todos PASS.

## A3 — perfiles DICE compilados

`compile_package_evaluations()` ya compilaba `dice_profiles` y guardaba el resultado dentro del plan. Sin embargo, `traits_dice_bridge.resolve()` lo recompilaba antes de llamar `dice.evaluate()`, que lo compilaba otra vez. La corrección conserva la validación de perfiles crudos en el API independiente de DICE y evita repetirla cuando el objeto proviene de `compile_profile()` y no fue modificado.

La clase privada `_CompiledProfile` conserva semántica de mapping/dict y una firma de contenido. Si una estructura anidada cambia, la firma deja de coincidir y `evaluate()` vuelve a pasar por `compile_profile`, por lo que la optimización no equivale a confiar ciegamente en un objeto mutable.

Microbenchmark: perfil crudo 0,1292 ms por `evaluate`; perfil compilado 0,0053 ms. Una prueba de integración crea la sesión antes de interceptar `compile_profile` y verifica que ejecutar una evaluación GISELA no lo invoque nuevamente.

## Invariantes y pruebas

| ID | Invariante | Implementación | Prueba/resultado |
|---|---|---|---|
| P0-I1 | paquete no confiable se valida en admisión | `admit_package` + `validate_session` público | contratos + prueba focal PASS |
| P0-I2 | transacción valida estado pero no schema autoral inmutable | `_validate_admitted_session` | `test_admitted_package_schema_is_not_revalidated_by_action` PASS |
| P0-I3 | copia externa no muta definiciones admitidas | `AdmittedPackage._payload_json` | pruebas PA001/admisión existentes |
| P1-I1 | fallo interno no confirma draft | commit posterior a proyección/validación | prueba focal de KeyError PASS |
| P1-I2 | causa interna queda diagnosticable | `LOGGER.exception` | `assertLogs` PASS |
| P2-I1 | historial restaurado conserva secuencia | validator + snapshot | walkthroughs con `--verify-restores` PASS |
| P3-I1 | no hay restauración cruzada silenciosa | digest + versión | 12 cruces en `test_pa001_version_restore` PASS |
| A2-I1 | bibliotecas importables de manera independiente | imports neutrales | procesos aislados PASS |
| A3-I1 | perfil compilado intacto no revalida schema | `_CompiledProfile` | DICE + integración GISELA PASS |
| A3-I2 | mutación invalida compilación | firma de contenido | `test_e0_d10_mutated_compiled_profile_is_revalidated` PASS |

## Cambios de código

Archivos funcionales modificados por esta intervención:

- `gisela/contracts/semantic_sessions.py`: separa validación completa de validación contra paquete admitido.
- `gisela/engine/runtime.py`: usa la ruta admitida solo en validación transaccional interna.
- `gisela/engine/action_handler.py`: registra defectos estructurales internos y no filtra su detalle en el mensaje público.
- `dice/core.py`: conserva compilación verificable de perfiles.
- `gisela/engine/traits_dice_bridge.py`: reutiliza el perfil ya compilado por `EvaluationRoutes`.
- pruebas de DICE, TRAITS, `narrative_conditions` y `test_focal_p0_addendum.py`.
- `dice/README.md`: documenta la nueva semántica de perfil compilado.
- `docs/operatives/evidence/focal_metrics.json`: mediciones reproducibles de esta intervención.

Los cambios documentales que ya venían modificados en el ZIP se conservaron sin reescritura atribuible a esta auditoría.

## Regresión ejecutada

- `python -m pytest -q gisela/contracts/test_admission_v12.py gisela/contracts/test_contracts.py gisela/contracts/test_e1_evaluations_v14.py gisela/engine/tests/test_pa001_version_restore.py gisela/engine/tests/test_e0_transactions.py gisela/engine/tests/test_e2_evaluations.py gisela/engine/tests/test_e3_visible.py`: **156 passed, 46 subtests**, 5,37 s.
- focal P0/P1/A3 + DICE: **14 passed**.
- MARY: **21 tests PASS**.
- DICE: **18 tests PASS**.
- TRAITS: **26 tests PASS**.
- `narrative_conditions`: **1 test PASS**.
- Faro completa con `--verify-restores`: PASS, 26 pasos y final terminal.
- Central ruta casete con `--verify-restores`: PASS y final terminal.
- `python tools/check_quality.py`: PASS, límites 500/30/3.
- `python tools/check_doc_links.py`: PASS.
- distribución: `pip install . --no-deps --no-build-isolation --target ...` seguido de importación desde `/tmp`: PASS. El intento con aislamiento de build falló únicamente porque el entorno no tiene acceso de red para descargar `setuptools>=80`; no se atribuye al paquete.

El `pytest` raíz fue intentado dos veces. Antes del cambio P0 alcanzó 64 % sin fallos antes del límite de 180 s de la herramienta; después alcanzó 76 % sin fallos antes del límite de 240 s. No se aumentaron timeouts ni se presenta el root run como aprobado. La extracción tampoco contiene `tools/check_project.py`, aunque documentos del repositorio todavía lo mencionan; por eso no fue posible ejecutar ese agregador histórico.

## Riesgos residuales

1. La validación transaccional de sesión sigue recorriendo el historial completo. Con sesiones muy largas, el costo por acción crece aproximadamente linealmente con el historial; optimizarlo correctamente exigiría demostrar una validación incremental equivalente, no omitir invariantes.
2. `history.reading` domina snapshots reales. Su eliminación, compactación o externalización modificaría el contrato de historial autoritativo y necesita decisión explícita.
3. El código público de errores no posee `INTERNAL_ERROR`. Esta intervención mejora diagnóstico sin alterar schemas; distinguirlo externamente requeriría versionar el contrato.
4. La ausencia de `tools/check_project.py` deja divergencia entre documentación histórica y archivos distribuidos. No se recreó un agregador sin mandato.
5. P3 conserva cuatro versiones por obligación vigente. Reducir ese costo requiere aprobar una ruptura de compatibilidad.
