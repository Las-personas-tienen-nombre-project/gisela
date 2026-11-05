# ADR-022: E2: ejecución transaccional de evaluaciones ocultas

**Estado:** implementado y sujeto a las pruebas de `E2_INVARIANTES_TRAZABILIDAD.json`.
**Fecha:** 30 de octubre de 2026.
**Depende de:** ADR-007, ADR-008, ADR-019, ADR-020 y ADR-021.

## Decisiones congeladas

1. **Contrato:** las sesiones v1.4 usan el esquema `session.schema.json` versionado en E1, ahora ejecutable sin campos de tirada visible. Los paquetes v1.2/v1.3 conservan sus propios esquemas, su estado y su significado. Cambios incompatibles para E3 requerirán una nueva versión.
2. **Presentación:** solo `presentation: hidden` es ejecutable en E2. Los valores `visible` y `acknowledged` siguen siendo válidos como *autoría de futuro*, pero no se ejecutan; `check_supported` los rechaza explícitamente con `UNSUPPORTED_FORMAT`. No existe `pending_evaluation`.
3. **Una ejecución:** pasos `evaluate`, opciones y acciones de escena (incluidos elementos) resuelven rutas declarativas en `EvaluationRoutes`; la decisión de ejecutar depende únicamente del cursor/oferta autorizada. No se introducen APIs específicas de usuario ni lógica del demo.
4. **Datos efectivos:** la compilación E1 solo indexa planes. Al ejecutar, GISELA obtiene instancias ALBERTO, componentes S.O.F.I.A., rasgos TRAITS, constantes y perfiles. El catálogo opcional TRAITS no es obligatorio para un perfil literal DICE.
5. **RNG:** el integrador compone `{base,bonus,difficulty}` y verifica cada entero efectivo dentro de +/-1.000.000 **antes del primer sorteo**. Verifica además el presupuesto nominal del contador. DICE obtiene exclusivamente el RNG inmutable de GISELA, que se propone como `rng_after`.
6. **Atomicidad:** después de seleccionar una rama completa, su RNG y efectos solo se escriben en el borrador transaccional de GISELA. El ejecutor aplica `settle`, MARY, reacciones, transiciones y validación de proyección antes de sustituir el estado confirmado. Un fallo descarta todo el borrador, incluso si se obtuvo un resultado matemático.
7. **Replay:** `DecisionRequired` conserva únicamente procedencia, respuestas y solicitud auxiliar; nunca guarda resultados parciales ni un RNG intermedio. La misma evaluación se reconstruye a partir del último estado confirmado y la semilla; solo la transacción completa puede consumir dados confirmados.
8. **Privacidad y autoridad:** `Observe` no incorpora tiradas ocultas, modificadores ni datos de personajes. Las acciones externas siguen atravesando ADR-020 y el mismo `Act` del ejecutor.

## Alternativas no adoptadas

No se duplicó el ejecutor para cada origen, no se extendió DICE para controlar sesiones, no se añadió RNG secundario y no se implementó la máquina de estados de evaluaciones visibles de ADR-019. Una evaluación oculta no crea por sí misma un turno narrativo; el turno continúa asociado a la ejecución de un nodo.

## Riesgo residual

El control previo del RNG asegura un presupuesto de `count` sorteos, pero el muestreo uniforme por rechazo de `sha256_counter_v1` puede necesitar bloques adicionales. El posible agotamiento de contador se detecta durante el cálculo y provoca rollback completo; no queda estado parcialmente confirmado. Cualquier política estricta de reserva del *peor caso teórico* requiere una decisión aparte porque el muestreo por rechazo no tiene cota determinista finita.
