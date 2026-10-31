# ADR-023 — E3: fijación y continuación de evaluaciones visibles (v1.5)

**Estado:** IMPLEMENTADO Y PROBADO (30-10-2026). **Alcance:** E3.1–E3.6.
**Precedentes:** ADR-007, ADR-008, ADR-019 (propuesta parcialmente adoptada), ADR-020, ADR-021, ADR-022.

## Decisiones aprobadas

1. `hidden` conserva la transacción única de E2. En v1.5, `visible` y `acknowledged` fijan dados/RNG en un primer commit y esperan un segundo `Act` para aplicar sus consecuencias. La diferencia entre ambas es la política del cliente: en `acknowledged` el solicitante debe reconocer el resultado antes de enviar el comando; no se finge comprobar atención humana desde el motor.
2. **Un comando público:** `continue_evaluation`, sin parámetros, ofrecido en la proyección autorizada. Se validan `session_id`, revisión y pertenencia a `Observe`, sin crear autoridad paralela. El `evaluation_id` se deriva de la revisión de preparación y se conserva en el pendiente; el cliente no escoge resultados.
3. **Una intención causal pendiente:** `pending_evaluation` y `pending_transaction` son excluyentes. El primero puede albergar una solicitud auxiliar bajo `auxiliary_request`, con las respuestas en el mismo `DecisionReplay`. Ni retiradas posteriores al resultado ni repetición voluntaria forman parte de v1.5.
4. **Borrador descartable:** se reconstruye la operación completa desde su origen, con `rng_initial`. Una cinta ordenada de resultados visibles ya confirmados verifica que la reconstrucción llega al mismo sitio, con iguales entradas efectivas y dados. Las tiradas ocultas anteriores o intermedias vuelven a calcularse *solo en el borrador* para verificar el replay; nunca vuelven a consumir RNG confirmado.
5. **Fronteras de compromiso:** preparar fija únicamente `pending_evaluation`, RNG y revisión. `world`, `narrative`, `history`, MARY, `turn`, `world_time`, cursor y `world_revision` no se confirman. Continuar puede fijar otra evaluación visible antes de completar la intención: en ese caso se acumula otra entrada comprobable en la cinta sin aplicar efectos parciales. La confirmación final utiliza el ejecutor, las reacciones y el cierre atómico A→B existentes.
6. **Errores y restauración:** un error previo a preparar no consume RNG confirmado. Un error en la continuación conserva el resultado, RNG y estado narrativo previos a esa continuación. Restaurar valida esquema, digest del paquete, origen, identidad, RNG y replay de resultados; una solicitud auxiliar pendiente también se verifica por replay. La duplicación y el principal autorizado siguen protegidos por el gateway de ADR-020.
7. **Privacidad:** `Observe` publica únicamente dados y banda de resultado, más una acción autorizada o, si corresponde, las opciones auxiliares. Los valores efectivos, perfiles privados, TRAITS y S.O.F.I.A. no se publican. No se publica el total de forma automática.
8. **Compatibilidad:** solo v1.5 habilita esta ejecución; v1.2–v1.4 y sus snapshots conservan su semántica. El contrato de autoría de `evaluate` conserva forma, perfiles y tres procedencias de v1.4. No hay migración implícita.

## Decisiones no aprobadas / diferidas

Retirada posterior al resultado, repetición autoral, sustitución de dados, total numérico público, presentación gráfica de dados y nuevos eventos de dominio. Su futuro diseño requiere contratos y pruebas independientes; no deben introducirse como convenciones implícitas.

## Riesgos conocidos

- El replay vuelve a ejecutar cálculos deterministas sobre un borrador, por lo que cadenas largas añaden costo CPU; se conservan los techos de pasos y el límite de una intención causal. Se limita la cinta persistente a 512 entradas.
- Un cliente `visible` puede enviar continuación automáticamente *después de presentar* el resultado. GISELA no puede observar una pantalla ni verificar la atención humana; esa política es responsabilidad del anfitrión.
- La restauración comprueba causalidad y formato, pero no ofrece firma criptográfica del archivo de guardado: el control de acceso al checkpoint sigue perteneciendo al anfitrión.
- La garantía de durabilidad de recibos ante errores de almacenamiento depende del gateway confiable y su checkpoint atómico; no es un protocolo de consenso distribuido.

**Pruebas:** `gisela/engine/tests/test_e3_visible.py` y matriz `docs/operatives/E3_INVARIANTES_TRAZABILIDAD.json`.
