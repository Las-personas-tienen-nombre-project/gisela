# H3. Revisión, hallazgos y plan de ALBERTO

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Estado:** EN CURSO. Primera etapa implementada y comprobada.

**Base:** H2 terminado, contratos JSON 1.2 y decisiones arquitectónicas consolidadas. Este documento describe el código ejecutable y las comprobaciones disponibles; no confunde la admisión estática de un paquete con el soporte dinámico de todas sus operaciones.

## 1. Objetivo y criterios de diseño

ALBERTO debe representar las instancias del mundo y aplicar sus operaciones sin convertirse en otro motor. GISELA conserva la sesión, crea el borrador causal, interpreta los pasos, ejecuta las reacciones, administra el RNG y confirma o descarta todos los cambios de una sola vez.

La revisión utiliza estos criterios, en orden: corrección de invariantes, responsabilidad única, contratos explícitos, simplicidad, apertura para otros relatos, mantenimiento y rendimiento razonable. No se incorporan repositorios de entidades, colas de mensajes ni servicios separados si el estado actual y las operaciones declarativas resuelven la necesidad.

Desde H3 se establece una política de mantenimiento: máximo 500 líneas por archivo mantenido y máximo 30 líneas por función Python, sin contar el docstring inicial. Las guías técnicas pueden contener párrafos extensos si mejoran la comprensión. No se impone un máximo de palabras ni de longitud de oración.

## 2. Catálogo de hallazgos

| ID | Prioridad | Hallazgo comprobado | Decisión y estado |
| --- | --- | --- | --- |
| H3-01 | Alta | `world.py` concentraba acceso a entidades, habilidades, identidades y operaciones. | Separar por responsabilidades manteniendo un solo despachador. IMPLEMENTADO. |
| H3-02 | Alta | `runtime.py` mezclaba proyección, recepción de acciones, inicialización y ejecución de nodos. | Extraer módulos internos sin alterar la API pública. IMPLEMENTADO. |
| H3-03 | Alta | Faltaban movimiento de personajes, conocimiento y creencias individuales. | Implementar operaciones explícitas y condiciones de consulta puras. IMPLEMENTADO. |
| H3-04 | Alta | La creación y retiro dinámicos de entidades no tenían ejecutor, pese a existir en los contratos. | Reutilizar el registro transaccional de IDs; rechazar borrados con referencias. IMPLEMENTADO PARA ENTIDADES BÁSICAS. |
| H3-05 | Alta | Las habilidades podían concederse, pero no moverse o descartarse mediante operaciones declaradas. | Validar propiedad y capacidad antes de mover o descartar. IMPLEMENTADO. |
| H3-06 | Media | `transfer` solo operaba sobre posesión, aunque los contratos admiten objetos ubicados en lugares. | Comprobar origen y destino tipados, con exactamente un propietario o lugar. IMPLEMENTADO. |
| H3-07 | Media | Faltaba avance explícito del reloj ficticio mediante una operación declarada. | Incorporar `advance_time` en el borrador de GISELA, sin temporizador paralelo. IMPLEMENTADO. |
| H3-08 | Alta | El validador semántico tenía demasiadas responsabilidades y superaba el tamaño permitido. | Dividir sus reglas por clases de contrato y conservar su fachada pública. IMPLEMENTADO. |
| H3-09 | Alta | Varias definiciones JSON Schema superaban 500 líneas por el formato original. | Compactar su presentación sin alterar datos, IDs ni versión. IMPLEMENTADO. |
| H3-10 | Media | No existía una prueba automática de los nuevos límites de tamaño. | Añadir verificador Python y regresiones a `check_project.py`. IMPLEMENTADO. |
| H3-11 | Media | La documentación antigua continuaba describiendo H2 como estado actual de ALBERTO. | Actualizar referencias, API, pruebas y roadmap. IMPLEMENTADO EN ESTA ENTREGA. |
| H3-12 | Alta | Relaciones mutables, efectos, uso y retorno de habilidades y atributos S.O.F.I.A. aún no son ejecutables. | Mantener H3 EN CURSO y diseñar primero los casos de aceptación respectivos. PENDIENTE. |
| H3-13 | Media | Las referencias contextuales y las acciones exploratorias todavía son rechazadas por el ejecutor. | Conservar el rechazo explícito hasta resolver alcance y procedencia; exploración pertenece a H4. PENDIENTE. |

No se ha identificado un motivo para sustituir el modelo de sesión o cambiar los schemas 1.2. La comprobación de soporte dinámico continúa siendo una barrera adicional a la admisión estructural y semántica.

## 3. Plan de ejecución y aceptación

### H3.1. Reducir responsabilidades

Separar las operaciones de ALBERTO en acceso e identidades, entidades, habilidades y ciclo de vida. Separar la presentación y la recepción de acciones de la autoridad del ejecutor. Dividir el validador semántico en módulos especializados sin cambiar el comportamiento externo. Preservar las firmas `new_session`, `restore_session`, `observe`, `act` y `export`.

**Aceptación:** las pruebas de contratos y H1-H2 siguen pasando, las importaciones públicas no cambian y no aparecen dobles fuentes persistentes de verdad. **Resultado:** implementado.

### H3.2. Operaciones esenciales de mundo

Implementar `move_character`, `learn_fact`, `set_belief`, `create_instance`, `remove_instance`, `move_skill` y `discard_skill`. Extender `transfer` a personas y lugares y permitir `advance_time` explícito. Aplicar cada cambio sobre el borrador de la transacción de GISELA, nunca directamente sobre el estado confirmado.

**Aceptación:** pruebas de éxito, error, integridad de referencias, capacidades, restauración y rollback. **Resultado:** implementado para el subconjunto indicado.

### H3.3. Garantías y control de calidad

Probar que una instancia eliminada no habilita la reutilización de su ID; que un fallo después de una creación devuelve el asignador a su estado confirmado; que un personaje referenciado no se borra y que no hay sobrescritura silenciosa cuando dos reglas modifican el mismo destino o una retira una instancia usada por otra regla. Incorporar una verificación mecánica de tamaño al procedimiento general de pruebas.

**Aceptación:** todas las pruebas existentes y nuevas pasan desde `python tools/check_project.py`. **Resultado:** implementado.

### H3.4. Contratos y mecánicas todavía pendientes

Para cerrar H3 global faltan los mecanismos que dependan de casos de uso narrativos concretos: modificación de relaciones y propiedades de instancia, creación y expiración de efectos, ejecución de habilidades y sus políticas de retorno, valores efectivos y consultas de S.O.F.I.A. Cada incorporación debe demostrar sus invariantes y su conducta frente a transacciones pendientes, no solo aceptar el JSON correspondiente.

**Aceptación:** paquete de ejemplo reproducible para cada mecanismo, condiciones positivas y negativas, rollback, restauración y documentación de errores. **Resultado:** pendiente. H3 no debe declararse terminado todavía.

## 4. Decisiones de implementación

**Autoridad:** GISELA crea el borrador. ALBERTO devuelve modificaciones y sucesos; no controla revisiones, persistencia ni confirmación. `record_fact`, `roll` y `advance_time` se coordinan en las consecuencias de GISELA, no en un proceso autónomo.

**Identidades:** las instancias comparten el registro `used_instance_ids` y el contador `next_sequence`. Los IDs explícitos se rechazan si ya fueron utilizados; los automáticos no se vuelven a asignar después de un retiro confirmado. Ambos permanecen en el borrador hasta el commit.

**Objetos:** en cada instante confirmado un objeto está en posesión de un personaje o ubicado en un lugar, pero nunca en ambos. El traslado comprueba el origen antes de actualizar la relación. `set_scene` no mueve personajes.

**Conocimiento y creencias:** aprender un hecho no crea una ocurrencia histórica, y una creencia verdadera no convierte la afirmación en hecho. El historial de GISELA sigue siendo distinto de la experiencia individual de los personajes.

**Consultas:** `knows`, `believes` y `has_skill` son lecturas puras. Las referencias ambiguas o dependientes de un contexto que el ejecutor no haya vinculado se rechazan; no se elige una entidad por orden de aparición.

**Habilidades:** conceder, mover y descartar se separan del uso de cartas. No se implementa aún una segunda máquina de efectos de habilidad. Los límites de mano y reserva se revisan antes de modificar el borrador.

**Simplicidad:** el despachador conserva operaciones explícitas y funciones pequeñas. No se introduce una jerarquía de clases de entidad ni un ORM. Los schemas siguen siendo el contrato de datos, mientras que la validación dinámica protege el subconjunto ejecutable.

## 5. Organización interna

- `gisela/engine/world_base.py`: resolución de instancias, variables e identidades.
- `gisela/engine/world_entities.py`: movimiento, conocimiento, creencias y objetos.
- `gisela/engine/world_skills.py`: capacidad y operaciones sobre habilidades.
- `gisela/engine/world_lifecycle.py`: creación y retiro de entidades.
- `gisela/engine/world.py`: frontera pública de operaciones de ALBERTO.
- `gisela/engine/conditions.py`: evaluación pura de condiciones de mundo e historial.
- `gisela/engine/consequences.py`: operaciones causales y coordinación de efectos de sesión.
- `gisela/engine/reactions.py`: rondas, conflictos y límites de ejecución.
- `gisela/engine/runtime.py`: autoridad de GISELA y API pública.
- `gisela/engine/initialization.py`: estado inicial confirmado.
- `gisela/engine/action_handler.py`: recepción y validación de acciones.
- `gisela/engine/projection.py`: construcción de Observe.
- `gisela/engine/support.py`: rechazo anticipado de mecanismos sin soporte.
- `gisela/contracts/semantic_*.py`: validación semántica repartida por clase de contrato.
- `tools/check_quality.py`: control automático de tamaño.

Los módulos internos no son una API pública adicional. Su separación responde a responsabilidades comprobables y permite cambiar las operaciones sin reescribir el control de sesión.

## 6. Política de tamaño y excepción documentada

Las comprobaciones automáticas examinan archivos mantenidos en `gisela`, `tools`, `renpy` y `docs`. Ningún archivo de esos ámbitos puede superar 500 líneas ni una función Python 30 líneas de código, descontando el docstring inicial. El control forma parte de `python tools/check_project.py` y dispone de regresiones positivas y negativas.

Se excluyen de esta regla los contenidos históricos de `archive` y el manuscrito de referencia `docs/narrative/reference/Blue_Forever.md`. Este último se conserva íntegro, pues dividir o reescribir una fuente narrativa solo para satisfacer una norma de ingeniería podría alterar la referencia autoral. La excepción no se extiende a documentación técnica ni a código nuevo. No se agregaron otras excepciones.

## 7. Pruebas y resultados

Para repetir toda la verificación desde la raíz:

```bash
source .venv/bin/activate
python tools/check_project.py
sha256sum -c MANIFEST.sha256
```

Las pruebas de `gisela/engine/tests/test_h3_world.py` comprueban operaciones y consulta de hechos, movimiento, capacidades, propiedad de habilidades, creación, retiro, identidades, avance temporal, referencias inválidas y conflictos. Las pruebas anteriores siguen protegiendo la cancelación y la restauración de H2. Las verificaciones de tamaño se ejecutan mediante `tools/check_quality.py` y `tools/test_quality.py`.

No se ha realizado una ejecución en el SDK Ren'Py. No debe inferirse compatibilidad de ese anfitrión a partir de la consola Python.

## 8. Próxima decisión de alcance

Cerrar H3 global requiere seleccionar primero el caso narrativo que utilizará relaciones y efectos. La siguiente intervención debería implementar únicamente las operaciones demostrablemente necesarias, incluidas sus variantes de fallo, antes de avanzar a la exploración H4. Si una operación exige un cambio de schema, se debe tramitar como decisión de contrato separada y registrar el impacto sobre guardados anteriores.
