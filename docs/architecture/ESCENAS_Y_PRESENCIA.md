# Escenas narrativas, lugares y presencia física. H4.5f

## Autoridad y conceptos

GISELA es la única autoridad de transición narrativa, validación y confirmación. ALBERTO administra las instancias de lugares, personajes y objetos, así como su ubicación o propietario. GLAUQUIR y Ren'Py presentan `Observe` y envían `Act`; no sincronizan personajes o inventarios por su cuenta.

Una escena tiene identidad narrativa (`scene.id`) y puede declarar un lugar físico (`scene.location`). Muchas escenas pueden representar el mismo lugar: por ejemplo, `puesto_b_tarde` y `puesto_b_noche` comparten la instancia física `puesto_b`. Una escena sin `location` no implica un lugar; sirve para recuerdos, conversaciones remotas o secuencias no espaciales.

## Invariantes de ubicación

1. `scene.location` requiere un ID literal de instancia de tipo `location`. Las referencias dinámicas sin ligadura no son admitidas en este campo.
2. En una entrada exploratoria con `player_character`, la ubicación inicial del protagonista debe coincidir con el lugar de la escena activa. Se comprueba durante la admisión del paquete.
3. Cada confirmación y restauración de un estado con escena física vuelven a comprobar esa coincidencia; un cambio inconsistente se rechaza sin confirmar el borrador.
4. `set_scene` cambia solo el contexto narrativo. Un traslado físico debe ejecutar `move_character` y `set_scene` dentro de la misma transacción, cuando el protagonista cambia de lugar.
5. Una escena sin `location` no impone co-ubicación física: el autor controla su contenido mediante `visible_if` y la lógica declarativa.

## Presencia, elementos y acciones

En una escena física, `actors` se filtra por ubicación real en ALBERTO además de `visible_if`. Un elemento con `entity` debe referenciar una instancia explícita. Para personajes se exige co-ubicación; para lugares, identidad con `scene.location`; para objetos, presencia en el lugar o propiedad del protagonista presente. Un objeto poseído por otro personaje no revela su ficha automáticamente, aunque ese personaje esté allí. Las habilidades y efectos no se representan como elementos físicos vinculados: se consultan mediante las proyecciones públicas correspondientes.

Los elementos sin `entity` son elementos narrativos declarativos y se rigen por `visible_if`. No se pretende que cualquier decoración deba existir como instancia de ALBERTO. Una vinculación a una entidad que todavía no existe no aparece; puede activarse cuando el motor la cree.

Las acciones asociadas a un elemento solo se ofrecen si el elemento es visible. `Act` revalida las acciones antes de ejecutarlas, incluida su presencia; las peticiones con IDs no ofrecidos se rechazan. Los IDs de las acciones exploratorias dependen de la posición declarada y no se renumeran cuando desaparece un elemento. Los IDs siguen estando sujetos a la revisión de sesión.

**Límite explícito:** las acciones generales de escena no tienen un campo de destino físico. Una acción como "Hablar con Gisela", declarada a nivel de escena, no puede inferir su objetivo por el texto de la etiqueta. El autor debe declarar `visible_if` o `enabled_if` para ese caso, o asociar la acción a un elemento `entity: "gisela"`. No se añade un parser semántico ni un motor de relaciones paralelo.

## Inspección textual

`scene.elements[].description` es un `localized_text` opcional. GISELA lo proyecta como `Observe.elements[].description` únicamente cuando el elemento está visible. `mirar ELEMENTO` en GLAUQUIR usa esa descripción, o la ficha pública autorizada de su `entity` si no existe una descripción propia; nunca ejecuta una operación. `examinar ACCIÓN` consulta las anotaciones sin ejecutar la oferta si `ACCIÓN` identifica inequívocamente por ID o etiqueta una acción visible; también informa si no hay notas. En los demás casos, `examinar` prioriza una acción declarada, que puede producir efectos, antes de consultar una ficha o elemento público. Una consulta no registra un hecho, no consume RNG ni avanza el reloj.

Ejemplo declarativo:

```json
{
  "id": "lavamanos",
  "label": {"text": "Lavamanos"},
  "description": {"text": "La llave está abierta y el agua sigue corriendo."},
  "visible_if": {"constant": true},
  "actions": []
}
```

El texto del ejemplo es estático. Para descripciones que dependen del estado no se debe introducir lógica en GLAUQUIR: utilice elementos alternativos con condiciones declaradas o nodos narrativos, hasta que exista un contrato de variantes dinámicas autorizado.

## Compatibilidad y límites

Se amplía de forma opcional `scene.schema.json` v1.2; `observe.schema.json` ya admitía descripciones de elementos. `act.schema.json` y el formato persistido de sesión no cambian. Al cambiar una definición, cambia su digest; no debe restaurarse un guardado contra un paquete diferente. `set_scene` conserva su semántica sin efectos implícitos.

GLAUQUIR significa **GISELA's Lightweight Access Utility for Queries, User Interaction, and Rendering**. El cliente canónico se ejecuta mediante `python tools/glauquir.py --package ...`; `tools/gisela_cli.py` y `tools/play_mvp.py` se conservan para compatibilidad.

Pruebas: `gisela/engine/tests/test_h45f_scene.py`. Registro de invariantes y test anclado: [INVARIANTES_H4_5F.md](../operatives/INVARIANTES_H4_5F.md).

Las referencias dinámicas a actores mediante `query` siguen permitidas por el contrato semántico general, pero el ejecutor actual las rechaza en la puerta de soporte (`UNSUPPORTED_FORMAT`). No se silencian ni se selecciona una instancia por aproximación. Los actores literales duplicados se rechazan durante la admisión.
