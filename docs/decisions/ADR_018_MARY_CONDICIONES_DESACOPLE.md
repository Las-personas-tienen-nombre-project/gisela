# ADR-018. MARY y desacople progresivo de los subsistemas

**Estado:** aprobado para implementación v1, 30 de octubre de 2026.

## Contexto

GISELA es un motor para distintas historias, no una implementación particular de *Las personas tienen nombre*. La demo necesita progresión oculta y un futuro catálogo de oportunidades. Otros juegos necesitarán quests visibles, acumulación ponderada, seguimiento y fracasos.

El ejecutor ya dispone de condiciones, historial, reglas reactivas, borradores y confirmación. Copiar esas responsabilidades dentro de MARY introduciría dos autoridades contradictorias.

## A. Lenguaje común de condiciones

**Decisión:** extraer `narrative_conditions`, una biblioteca pura de operadores lógicos y comparación estricta. Las consultas de dominio se resuelven mediante una función proporcionada por el anfitrión. MARY interpreta hechos y valores neutralizados; GISELA conserva la interpretación de las consultas específicas del mundo.

**Por qué:** compartir el significado de `all`, `any`, `not`, igualdad y comparaciones evita dos implementaciones que discrepen ante valores booleanos, números o condiciones anidadas. No obliga a MARY a importar clases de GISELA.

**Límite:** las estructuras de `has_fact`, `owns`, `knows` o `at_location` pertenecen al dominio del anfitrión. Compartir operadores no significa dar a cualquier subsistema acceso completo a ALBERTO.

## B. Dos clases de progreso

**Decisión:** `milestone` conserva el cumplimiento y puede emitir un yield una sola vez. `current` se recalcula y no puede emitir yields. Una misión completada o fallida es terminal en v1.

**Por qué:** "haber completado una ronda" no debe deshacerse al volver a la portería, pero "tener una linterna" deja de ser cierto si Alberto ya no la posee. Guardar ambos fenómenos como la misma variable persistente provocaría resultados falsos.

## C. Los yields no son efectos ejecutados

**Decisión:** MARY devuelve resultados declarativos. El anfitrión valida, ejecuta o rechaza dentro de su propia transacción. En GISELA v1 solo se admiten yields de hechos declarados.

**Por qué:** otro motor puede usar MARY sin instanciar ALBERTO. Las recompensas no quedan confirmadas si un efecto posterior falla. No se crea otro historial ni una segunda transacción autónoma.

## Dependencias permitidas

- `narrative_conditions` no importa otros subsistemas.
- `mary` importa únicamente `narrative_conditions` y su validador JSON Schema; no importa GISELA, ALBERTO ni S.O.F.I.A.
- `gisela/engine/mary_bridge.py` depende de MARY y traduce datos del borrador, pero no ocurre lo inverso.
- GLAUQUIR consume la proyección pública; no pregunta directamente a MARY ni ALBERTO.

## Migración de los otros subsistemas

ALBERTO y S.O.F.I.A. siguen alojados parcialmente en `gisela/engine/`. La extracción completa no se realiza en este hito: afectaría contratos, persistencia y miles de pruebas sin resolver un problema inmediato de autoría. Es una deuda identificada, no independencia ya conseguida. Se deberá estudiar cada frontera con casos autónomos, APIs pequeñas y pruebas de compatibilidad antes de migrarla.

## Consecuencias y verificación

El paquete GISELA puede omitir `mary`, conservando el comportamiento anterior. Las definiciones MARY y el progreso no dependen del cliente. Las transiciones participan en el mismo rollback y replay de la sesión GISELA. La documentación de las invariantes y los tests correspondientes está en `docs/operatives/INVARIANTES_MARY.md`.
