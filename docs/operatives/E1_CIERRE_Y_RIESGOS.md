> **Actualización posterior (E2, ADR-022):** las limitaciones de ejecución v1.4 descritas a continuación corresponden al cierre histórico E1. El runtime E2 ejecuta evaluaciones ocultas y admite guardados v1.4; las evaluaciones visibles y reconocidas siguen pendientes.

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

# E1: Cierre operativo: admisión y normalización de `evaluate`

**Estado:** E1 implementada; E2-E5 pendientes. **Base:** ZIP (8) + parches TRAITS, TRAITS-ALBERTO/DICE y E0.

## Plan ejecutado

1. Congelar E0 como base diferencial y comparar esquemas v1.3 sin modificarlos.
2. Añadir 13 esquemas v1.4 con `dice_profiles` y `evaluation` en tres tipos de origen.
3. Extender puerta de admisión y validador semántico; recorrer las operaciones de todas las ramas para no omitir las validaciones ALBERTO/MARY.
4. Crear compilador puro, con datos exactamente compatibles con el puente TRAITS-DICE.
5. Mantener `check_supported` cerrado para v1.4 durante E1; preservar todos los paquetes de ejecución anteriores.
6. Anclar cada invariante a un test; añadir un paquete de admisión sin protagonista ni TRAITS/S.O.F.I.A.; ejecutar regresiones y `tools/check_project.py`.

## Riesgos examinados

- **Versionado:** v1.4 tiene `$id` distintos; las versiones anteriores no se reescriben. La prueba heredada que enumeraba versiones se hizo extensible.
- **Ambigüedad narrativa:** ramas exactas, efectos y saltos dentro de ramas, ninguna ejecución prematura. Las alternativas de escena y elección usan la misma declaración.
- **Desacoplamiento:** los perfiles DICE siguen siendo neutrales, TRAITS permanece optativo y S.O.F.I.A. se referencia como dato. No se introducen importaciones de GISELA dentro de sus núcleos.
- **Autoridad:** ninguna solicitud autoral puede atribuirse identidad de cliente o alterar permisos; el gateway E0 conserva la frontera externa.
- **Determinismo:** la admisión y normalización no tocan RNG, turnos ni estado de sesión.
- **Privacidad:** E1 no publica resultados; E3 debe filtrar totales y atributos del NPC por audiencia.
- **Límites:** los esquemas limitan tamaño de catálogos y listas; E2 debe comprobar la suma final antes de consumir RNG.
- **Restauración:** guardados v1.4 todavía se rechazan explícitamente; no se promete migración implícita ni compatibilidad ejecutable. **E2 deberá congelar el contrato de sesión v1.4 antes de permitir guardar; E3 deberá versionar cualquier cambio incompatible (p. ej., v1.5).**

## Trabajo pendiente antes de presentar dados

**E2:** compilar perfiles al cargar un ejecutor compatible, resolver entradas del mundo, ejecutar la evaluación oculta con efectos en un mismo commit, registrar causas y MARY, reaccionar de forma atómica, comprobar presupuestos finales y mantener `Act` autorizado por E0.

**E3:** `pending_evaluation`, fijación persistente de RNG, `Observe` filtrado por audiencia, confirmación y restauración sin reroll.

**E4:** decisiones auxiliares dentro de la misma obligación causal, sin duplicar un pendiente ni modificar ADR-007/008.

La auditoría de E1 no certifica estas funciones pendientes como implementadas.
