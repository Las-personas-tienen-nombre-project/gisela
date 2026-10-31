# E2: Informe de implementación por subetapas

**Base exacta:** ZIP adjunto `las-personas-tienen-nombre(10).zip`, árbol Git `158990d` (E1). Las diferencias del trabajo están únicamente en el parche incremental adjunto.

## E2.1: Contrato de sesión

Se activó validación y restauración de snapshots v1.4 contra digest sin modificar los esquemas v1.2/v1.3. Se habilitó la materialización de rasgos en v1.4. E3 necesitará nueva versión si incorpora campos incompatibles de evaluación visible.

## E2.2: Estado efectivo

El índice se construye con la normalización pura E1. Las lecturas de entidades, atributos efectivos y contribuciones contextuales se realizan desde el borrador vigente al momento de resolver la evaluación, no en admisión.

## E2.3: Cálculo DICE

Se conserva una única fuente `sha256_counter_v1`. El puente valida sumas efectivas y presupuesto nominal antes de sortear. Solo se propaga el RNG propuesto al borrador; la sesión confirmada no lo cambia hasta el commit.

## E2.4: Orígenes

Paso `evaluate` automático, opción elegida y acción exploratoria de escena/elemento comparten el mismo índice y ejecutor. No existe API especial para personajes ni para clientes humanos.

## E2.5: Consecuencias

Cada rama utiliza `apply_operation`/`settle`, MARY y transiciones ordinarias. Elecciones y acciones solo dejan selección/traza en el estado confirmado si finaliza toda la transacción. Las decisiones auxiliares se reconstruyen con `DecisionReplay` sin almacenar resultados parciales.

## E2.6: Auditoría

Se añadieron pruebas de rutas, componentes independientes, límites, RNG, rollback, replay, MARY y restauración. Se actualizan trazabilidad, ADR-021 y se incorpora ADR-022. El informe de auditoría registra riesgos que no deben confundirse con fallos resueltos.

**Comprobaciones:** ejecutar `python tools/check_quality.py`, `python tools/verify_e0_invariants.py`, `python tools/verify_e1_invariants.py`, `python tools/verify_e2_invariants.py` y `python tools/check_project.py`. Los resultados reales de este encargo se entregan además en el registro externo de pruebas.
