# Contrato público de clientes de GISELA

## Responsabilidades

GISELA conserva la autoridad de la sesión, la evaluación declarativa, la ejecución de acciones y las transacciones. ALBERTO administra las entidades del mundo en borradores proporcionados por GISELA. S.O.F.I.A. calcula atributos. GLAUQUIR y Ren'Py solo presentan proyecciones y envían decisiones.

La CLI no debe importar `world.py`, modificar el estado de sesión, ejecutar reglas ni reconstruir a partir de la traza causal una historia pública. `debug_query` es una excepción diagnóstica para herramientas explícitamente autorizadas, nunca una fuente para presentar datos normales del jugador.

## API Python disponible

| Operación | Resultado |
| --- | --- |
| `admit_package_file(path)` | Valida estructura y semántica, calcula digest y admite definiciones. |
| `new_session(admitted)` | Crea una sesión de GISELA. |
| `restore_session(admitted, snapshot)` | Valida el guardado y la identidad del paquete. |
| `session.observe()` | Entrega contenido, actores, elementos y acciones, más inventario, habilidades, efectos y cartas públicas. |
| `session.act(request)` | Revalida una acción ofertada mediante identificador y revisión. |
| `session.read_public(identifier)` | Entrega título y descripción de una carta actualmente conocida. |
| `session.player_status()` | Entrega únicamente el Scoresheet del protagonista cuando existe. |
| `session.read_history(limit=None)` | Entrega copias del registro narrativo confirmado. |
| `session.export()` | Exporta un snapshot JSON sin estado provisional. |
| `session.debug_query(request)` | Entrega datos de diagnóstico, solo para herramientas de desarrollo. |

`Observe` incorpora campos opcionales para conservar compatibilidad con los consumidores anteriores. Las entradas del registro se almacenan en `history.reading` dentro de la sesión, como un dato autoritativo diferente de `history.trace`. Este agregado es compatible con snapshots v1.2 anteriores, aunque dichos snapshots no contienen la historia de lectura que no se llegó a registrar.

## Contrato de Act

El cliente debe leer primero una acción de `view.actions`, comprobar que está habilitada y enviar el mismo `action_id` y `revision`:

```python
view = session.observe()
action = next(item for item in view['actions'] if item['enabled'])
answer = session.act({
    'session_id': view['session_id'],
    'revision': view['revision'],
    'action_id': action['action_id']
})
```

Ningún verbo textual autoriza operaciones por sí mismo. Si hay dos coincidencias, el cliente no escoge automáticamente. Si la acción deja de estar disponible, GISELA la rechaza. Una acción puede detenerse para pedir una decisión auxiliar sin confirmar cambios del mundo ni del RNG.

## Historia de lectura

GISELA conserva los pasajes narrativos efectivamente confirmados al entrar en una escena, alcanzar un paso visible o confirmar una decisión. El historial público contiene textos en su orden original y no vuelve a ejecutar condiciones ni reconstruye descripciones usando el mundo presente.

La lectura del historial no produce nuevos registros, no cambia revisiones ni consume aleatoriedad. Una transacción pendiente conserva exclusivamente el estado anterior y su solicitud; los pasajes provisionales no se registran.

## Información visible y oculta

`read_public` solo permite cartas visibles, conocidas o poseídas conforme a la proyección actual. El inventario pertenece al protagonista y no publica pertenencias de otros personajes. El estado público de S.O.F.I.A. pertenece al protagonista. Las propiedades y conocimientos internos del mundo siguen reservados a las consultas diagnósticas de desarrollo hasta contar con políticas de visibilidad declaradas.

## Habilidades de exploración

La escena autoriza el ofrecimiento mediante `allow_skill_play: true`. GISELA evalúa requisitos y propiedad de la habilidad, publica la acción y resuelve su uso con las mismas transacciones de las ventanas narrativas. No se configura un segundo sistema de habilidades en el cliente.

## Compatibilidad

Los cambios de esta etapa amplían los campos opcionales de los schemas `session` y `observe`, pero mantienen el formato declarado en 1.2. El nuevo paquete de ejemplo usa ese formato. Un guardado previo puede restaurarse si sigue siendo válido y coincide su digest; sin embargo, no puede recuperar retroactivamente los textos anteriores a esta ampliación.

## Escenas físicas e inspección en H4.5f

GLAUQUIR (GISELA's Lightweight Access Utility for Queries, User Interaction, and Rendering) es el cliente textual oficial. `tools/glauquir.py` es el punto de entrada preferido; `tools/gisela_cli.py` permanece como alias compatible.

`scene.location` delimita un contexto físico de ALBERTO. GISELA revalida que la ubicación del protagonista coincide con dicho lugar en la admisión de entrada exploratoria y en cada guardado o confirmación. No hay movimiento implícito desde `set_scene`: una transición física requiere `move_character` y `set_scene` en la misma transacción. Una escena sin `location` representa un contexto no espacial cuya visibilidad es declarativa.

GISELA proyecta actores y elementos vinculados a entidades únicamente cuando están físicamente presentes, y no publica objetos poseídos por terceros solo por estar cerca. Se permite proyectar objetos propios del protagonista en su lugar actual. Las acciones de un elemento oculto tampoco se ofrecen ni se autorizan; los identificadores derivados de posiciones declaradas permanecen estables al cambiar la visibilidad. Los elementos sin vinculación física se gobiernan por `visible_if`.

El campo opcional `scene.elements[].description` usa `localized_text` y llega a `Observe.elements[].description`. GLAUQUIR puede leerlo mediante `mirar ELEMENTO`; cuando no existe, usa la carta pública del `entity` autorizado. Leer no ejecuta efectos. `examinar` conserva prioridad para las acciones declaradas del autor. El contrato de Act y el registro narrativo confirmado no cambian.

Véanse [semántica de escenas](ESCENAS_Y_PRESENCIA.md) y [pruebas ancladas](../operatives/INVARIANTES_H4_5F.md).

## E0 — Software solicitante no humano (implementado, anfitrión confiable)

`session.act()` y `session.observe()` se mantienen para clientes **locales confiables**. Para software externo o varias fuentes concurrentes existe `ExecutionGateway` (véase [frontera autorizada](E0_FRONTERA_AUTORIZADA_Y_PERSISTENCIA.md)). El anfitrión autentica a cada solicitante y le asigna capacidades; no hay relación automática entre ese principal, el `player_character` y la entidad narrativa de una acción. Una vez asociado el gateway, se bloquea la entrada `session.act()` directa. La API externa utiliza un `command_id` adicional, fuera del JSON `Act` versionado.

La lectura externa solo publica el contenido del protagonista si se concede explícitamente `observe_player`. `export_private` y `debug_private` son permisos privilegiados. El transporte entre instancias y otras audiencias **no** son capacidades implementadas.
