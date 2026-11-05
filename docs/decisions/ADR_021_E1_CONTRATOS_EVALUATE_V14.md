> **Actualización posterior (E2, ADR-022):** las limitaciones de ejecución v1.4 descritas a continuación corresponden al cierre histórico E1. El runtime E2 ejecuta evaluaciones ocultas y admite guardados v1.4; las evaluaciones visibles y reconocidas siguen pendientes.

# ADR-021: E1: contrato de autoría `evaluate` v1.4

**Estado:** IMPLEMENTADO (admisión y compilación estática E1); **ejecución NO habilitada**.
**Fecha:** 30 de octubre de 2026. **Ámbito:** GISELA y sus contratos, no DICE ni TRAITS.
**Relacionados:** ADR-007/008 (transacción y turno), ADR-019 (tirada fijada), ADR-020 (autoridad y acceso).

Nota de mantenimiento: las referencias a `tools/check_project.py` corresponden
al repositorio original. En este árbol se utiliza el
[verificador independiente](../guides/VERIFICACION_GISELA.md).
Las evaluaciones visibles posteriores se documentan en [ADR-023](ADR_023_E3_EVALUACIONES_VISIBLES_V15.md).
Estas referencias no modifican las decisiones históricas de E1.

## Decisiones

1. **Versionado explícito.** Los trece esquemas v1.4 viven en `gisela/contracts/v1_4/`. v1.2 y v1.3 conservan su sintaxis y ejecución. `Validator` puede admitir v1.4, pero `GiselaSession` **rechaza v1.4** con `UNSUPPORTED_FORMAT` hasta E2. Los snapshots v1.4 todavía no son restaurables. Los esquemas públicos de sesión/Act/Observe copiados en E1 son **reservas no ejecutables**, no una promesa de compatibilidad de runtime; E2 deberá congelar su contrato público efectivo. Si E3 necesita campos incompatibles para `pending_evaluation`, se usará otra versión (por ejemplo v1.5), no se reinterpretarán silenciosamente guardados v1.4 ya ejecutables.
2. **Perfiles neutralizados.** `dice_profiles[]` es catálogo autoral opcional; cada entrada cumple `dice.profile.v1`, sus IDs son únicos y `compile_profile()` comprueba umbrales y resultados. Los perfiles no contienen scripts arbitrarios.
3. **Orígenes admitidos.** Un paso `{op: "evaluate", evaluation: ...}`; una opción `choice_option.evaluation`; una acción `scene.action.evaluation`, incluida una acción de elemento. **Ningún otro origen** admite `evaluation` (ni reacciones, vencimientos o transición de nodos).
4. **Alternativas excluyentes.** Una opción/acción con `evaluation` no puede declarar `effects` ni `next` simultáneos. Las ramas contienen efectos y posibles destinos; ninguna rama implícita.
5. **Resultado exhaustivo.** `branches[].outcome` coincide uno a uno con `dice_profiles[].bands[].id`. Las ramas repetidas, omitidas y desconocidas son errores de admisión; no hay prioridades por orden de archivo.
6. **Entradas tipadas v1.** `inputs.base` acepta `{literal: entero}` o `{stat: {character,name,component}}`; `inputs.difficulty` acepta `{literal: entero}` y por omisión vale 0. `context` permite hasta ocho participantes explícitos con `entity` y `role`, y hasta dieciséis etiquetas; no inventa actor a partir del jugador ni atribuye autoridad a los participantes.
7. **Normalización pura.** `evaluation_plan.normalize_evaluation()` transforma esas entradas en la estructura que ya recibe `traits_dice_bridge.resolve`: `{profile,base,difficulty,participants,tags,stat?}`. Compila referencias de perfil y ramas, **sin consultar un mundo que todavía puede cambiar, ejecutar DICE, consumir RNG o aplicar efectos**.
8. **Validación transversal.** La admisión valida destinos, referencias a ALBERTO, fichas S.O.F.I.A., operaciones, vocabulario de hechos y rasgos de las ramas existentes. Cada evaluación está indexada por su **ruta estructural**, no por un ID global inventado para una acción local.
9. **Identidades de acceso.** El autor declara entidades narrativas; el solicitante autorizado permanece en la frontera E0 de `Act`/`Observe`, fuera de `inputs` y de la interfaz neutral DICE. Se admite que el solicitante sea software u otra instancia de GISELA sin permitirle inyectar reglas.

## Restricciones de presupuesto E1

Máximo 64 perfiles por paquete, 16 bandas por perfil, 16 ramas por evaluación, 8 participantes, 16 etiquetas, literales +/-1.000.000. Rigen además los máximos internos del perfil DICE y la capacidad del catálogo TRAITS. Las sumas efectivas y su validación antes del RNG pertenecen a E2.

## Garantías deliberadamente pendientes

E1 **no** crea ofertas `Act`, nuevos estados `Observe`, `pending_evaluation` ni guardados v1.4 válidos. Tampoco decide quién ve cifras privadas. El tratamiento de elecciones e historial, la presentación antes de efectos, las decisiones auxiliares y el consumo de RNG se implementarán y probarán en E2-E4, respetando ADR-007/008/019/020. No se altera la semántica de `roll` anterior.

## Invariantes y pruebas

Registro verificable en `docs/operatives/E1_INVARIANTES_TRAZABILIDAD.json`; `tools/verify_e1_invariants.py` comprueba anclajes y cobertura de pruebas nuevas. `tools/check_project.py` ejecuta ambas comprobaciones.
