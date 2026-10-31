# GISELA: Informe técnico de procedencia y admisión v0.2

**Fecha:** 29 de octubre de 2026  
**Origen:** schemas 1.1 + validador semántico v0.1  
**Salida:** schemas 1.2 + validador estático v0.2, independiente del motor histórico.

## Objetivo y resultado

Se resolvieron dos defectos de procedencia y se creó una puerta de admisión para paquetes narrativos. No se implementó el ejecutor GISELA ni se modificó `lptn.zip`. Las soluciones minimizan datos redundantes, preservan la autoridad transaccional única y admiten nuevas escenas y elecciones sin cambiar identificadores existentes.

| Asunto | Antes (1.1) | Ahora (1.2) |
|---|---|---|
| Historial de opciones | `selected_options` solo guardaba `option_id` | Cada elemento es `{step_id, option_id}`, interpretado dentro del nodo de la ejecución |
| Origen de acción de elemento | Solo `scene` + `action`; el validador prohibía repetir IDs en toda la escena | `source.element` opcional diferencia un elemento de la escena; IDs únicos por propietario |
| Carga de paquetes | `verify_contracts.py` comprobaba solo formato, y la validación semántica tenía entrada independiente | `admit_package.py` aplica lectura estricta + JSON Schema + validación semántica y `verify_contracts.py` usa la misma puerta |
| Compatibilidad | Formatos 1.1 | `$id`/`$ref` `/v1.2/`, manifest y snapshots 1.2; **no hay migración automática** |

## Contrato de admisión

La función `admit_package_file(path)` rechaza JSON sintácticamente inválido (incluidas claves duplicadas y `NaN`/`Infinity`), estructura inválida o errores semánticos. Devuelve un `AdmittedPackage` que conserva una copia del paquete; `materialize()` devuelve una copia independiente. Errores: bloqueantes. Advertencias: no bloqueantes por defecto, visibles y opcionalmente rechazables con `--reject-warnings`. La CLI usa `0` admitido, `1` error de contrato y `2` error de entrada.

El parser estricto evita que el último valor de una clave duplicada sobrescriba silenciosamente el primero. La puerta está implementada y comprobada **offline**. La integración con un ejecutor futuro es una obligación de diseño, no un resultado de esta entrega.

## Comprobaciones nuevas

- Ejecución con elección `{step_id, option_id}` válida; rechazo de paso inexistente, paso que no es `choice`, opción inexistente y lista antigua de strings.
- Dos `choice` del mismo nodo pueden tener opciones homónimas sin perder procedencia.
- Acción con mismo ID en escena y elemento válida; referencias de origen diferenciadas por `element`.
- Rechazo de origen que omite el elemento cuando solo existe una acción del elemento; rechazo de elemento o acción inexistentes.
- Duplicación dentro de un único propietario prohibida.
- Paquete válido admitido; paquete con referencia inexistente u operación desconocida rechazado; entrada de formato 1.1 rechazada.
- Rechazo de JSON con claves duplicadas y de constantes no JSON; prueba de códigos de salida 0/1/2.
- Aislamiento de la copia del paquete admitido, aunque el llamante modifique el objeto de entrada o una copia materializada.

## Verificación efectuada

- **13** JSON Schemas válidos bajo Draft 2020-12 y enlaces locales resueltos.
- **133/133** pruebas unitarias aprobadas: 41 originales estructurales, 69 originales semánticas y 23 regresiones nuevas de procedencia/admisión.
- `python verify_contracts.py`: pasa; ahora también comprueba admisión semántica del paquete.
- `python admit_package.py example.package.json`: `ADMITTED`.
- Tres fixtures nuevas en `semantic_examples/`, con digest ilustrativo, verifican procedencia sin simular restauración.

## Límites deliberados

La admisión no comprueba atomicidad real, rollback, reacciones dinámicas, secretos de `Observe`, reconstrucción de transacciones pendientes, cálculo del digest, vectores de RNG ni migración de versiones anteriores. Los snapshots de `examples/` continúan siendo estructurales, no necesariamente sesiones válidas. Los warnings `DIGEST_UNVERIFIED` y `REPLAY_UNVERIFIED` conservan su significado.

**Pendiente antes del ejecutor:** definir una canonicalización de digest, vectores de RNG y políticas de presupuesto de ejecución. La admisión no constituye un segundo subsistema de ejecución y no contradice ADR-001-014; ADR-015 sigue pendiente de aprobación expresa.
