# Cierre del núcleo transaccional de H2

## Propósito y estado

H2 verifica el contrato de suspensión y reconstrucción aprobado en ADR-001 a ADR-005 para las operaciones que ejecuta el MVP. No declara terminado el motor general ni afirma que todos los orígenes futuros de decisiones auxiliares estén implementados. Las acciones de exploración, el uso de habilidades, las consultas especializadas y el anfitrión Ren'Py pertenecen a hitos posteriores.

## Responsabilidades

GISELA es la única autoridad de transacciones, turnos, historial, revisiones y sorteos. ALBERTO comprueba las invariantes del mundo, incluidas las capacidades de mano y reserva, y solicita una selección auxiliar cuando la concesión de una habilidad no cabe en ninguna de ellas. ALBERTO no decide si la solicitud es cancelable, no confirma borradores y no administra el RNG.

El módulo `pending.py` consume respuestas tipadas durante una repetición determinista. El estado de sesión conserva únicamente la fuente original, el origen voluntario u obligatorio, las respuestas ya entregadas y la siguiente solicitud. Nunca serializa un mundo provisional.

## Orígenes ejecutables

| Fuente | Momento | Cancelación | Estado previo confirmado |
| --- | --- | --- | --- |
| `session_start` | `new_session` necesita una respuesta antes de entrar al primer nodo | No | Turno cero, sin ejecución confirmada |
| `node_step` | Un avance ejecuta un efecto o reacción que necesita una respuesta | No | Cursor en el paso que ofreció avanzar |
| `choice_option` | Una elección produce un efecto o reacción que necesita una respuesta | Sí | Cursor en la elección original |

Los orígenes `scene_action` y `skill_play` pertenecen a capacidades posteriores. La validación estructural los reconoce, pero la ejecución H2 no los ofrece.

Cuando la sesión inicial carece de escena declarada y aparece una espera obligatoria, GISELA usa `status: preparing` y `preparing_for` con el nodo de entrada. La resolución retira ambos indicadores de preparación, abre la primera ejecución y la confirma una sola vez. Si ya existe una escena inicial, la sesión puede conservar `exploring` mientras espera la primera respuesta. No se crea una escena ficticia.

## Operación roll

`roll` recibe `sides`, un entero positivo de hasta 9007199254740991, y `store`, una referencia a una variable numérica declarada de sesión o mundo. La operación siempre produce un entero positivo, incluso cuando la variable admite valores de tipo número. El perfil del generador es `sha256_counter_v1` y su algoritmo permanece especificado en `docs/determinism/RNG_SHA256_CONTADOR.md`. Las operaciones `roll` se interpretan por GISELA en `consequences.py`, no por el módulo de mundo de ALBERTO.

La semilla y el contador forman parte del borrador. Si una reacción posterior solicita una decisión, el contador confirmado permanece intacto hasta responder. Una cancelación voluntaria o un conflicto deja el contador como estaba. Restaurar una solicitud reconstruye el mismo sorteo desde la semilla y el contador confirmados.

En una misma regla se conserva el orden declarado de efectos. En una ronda reactiva, GISELA selecciona las reglas habilitadas contra el mismo estado base y las ejecuta en orden lexicográfico de `rule.id`. Dos reglas que escriben un mismo destino son incompatibles y provocan `REACTION_CONFLICT`. El orden lexicográfico de ejecución no constituye una prioridad narrativa que autorice escrituras simultáneas al mismo destino.

## Garantías verificadas

1. Una solicitud pendiente no confirma mundo, historial, identidades, RNG ni avance de turno producido por la operación provisional.
2. Durante la espera, Observe solo publica el estado confirmado y la solicitud auxiliar actual.
3. Una transacción voluntaria puede cancelarse; una automática obligatoria no.
4. Guardar y restaurar una espera reproduce sus respuestas y la misma solicitud.
5. Al resolver la última solicitud, toda la operación se confirma exactamente una vez.
6. Un conflicto, respuesta inválida o referencia no autorizada conserva el último estado confirmado.
7. Las reglas con sorteos consumen el RNG en un orden estable independiente de su posición en la lista JSON.

Estas garantías se comprueban mediante `gisela/engine/tests/test_pending.py` y `gisela/engine/tests/test_h2_closure.py`. No son una prueba formal de todas las mecánicas posibles.

## Ejecutar y verificar

Desde la raíz del proyecto, con el entorno virtual y las dependencias instaladas:

```bash
python tools/check_project.py
python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q
python tools/play_mvp.py --package gisela/packages/h2_inicio_azar.package.json
```

El paquete `h2_inicio_azar.package.json` solicita un descarte al comenzar la sesión y calcula antes un sorteo provisional de seis caras. Puede utilizar `guardar sesion.json` durante la espera y restaurar con:

```bash
python tools/play_mvp.py --package gisela/packages/h2_inicio_azar.package.json --restore sesion.json
```

El contenido de este paquete es una prueba técnica, no una adaptación definitiva del relato.

## Límites y trabajo posterior

El RNG no incorpora todavía distribuciones adicionales, estadísticas S.O.F.I.A. ni ventanas de habilidades. La máquina reactiva actual ordena las reglas habilitadas, pero no debe confundirse esta implementación reducida con un sistema general de evaluación simultánea de todas las consecuencias posibles. Las ampliaciones de H3 deben proteger las garantías anteriores y aportar casos negativos de regresión.

Ren'Py todavía no consume la API de GISELA. No se ha comprobado la compatibilidad con su SDK ni se deben considerar jugables estos paquetes dentro de ese anfitrión.
