# H4.5f. Revisión y cierre técnico

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Fecha:** 30 de octubre de 2026.

**Objetivo:** endurecer escenas y proyecciones antes de la autoría de la primera jornada canónica. GISELA mantiene la autoridad de ejecución y ALBERTO administra lugares y entidades. El cliente textual oficial se llama **GLAUQUIR: GISELA's Lightweight Access Utility for Queries, User Interaction, and Rendering**.

## H4.5f.1. Escena narrativa y lugar físico

**Cambio:** se valida `scene.location` como referencia a un lugar físico explícito y se comprueba la co-ubicación del protagonista al entrar en una escena exploratoria, restaurar y confirmar una transacción.

**Debilidad:** `set_scene` permitía cambiar de contexto espacial sin mover a Alberto. **Corrección:** un borrador inconsistente se rechaza íntegramente, sin modificar la semántica de `set_scene`. **Simplificación:** no se añade un administrador de escenas ni movimiento automático; el autor coordina `move_character` y `set_scene` en los efectos de una acción.

**Pruebas:** `H45F1Location`.

## H4.5f.2. Presencia y autorización

**Cambio:** se filtran actores y elementos ligados a entidades conforme a la ubicación o propiedad de ALBERTO. El inventario ajeno no se expone por la sola presencia del propietario. Las acciones de elementos ocultos desaparecen de `Observe` y quedan inhabilitadas en `Act`.

**Debilidad:** el identificador de una acción dependía del índice de elementos visibles; al ocultarse uno, un ID podía referirse a otra acción. **Corrección:** los índices corresponden a posiciones declaradas, que no cambian con `visible_if`. **Simplificación:** un único criterio de presencia para actores y elementos, sin duplicar estado en el cliente.

**Límite:** las acciones generales de escena todavía requieren condiciones explícitas de autoría si dependen de la presencia de un interlocutor.

**Pruebas:** `H45F2Presence` y regresiones de H4.

## H4.5f.3. Descripciones e inspección textual

**Cambio:** `scene.elements[].description` es opcional y se proyecta a `Observe`. GLAUQUIR incorpora `mirar ELEMENTO` como lectura pura. Cuando corresponde puede recurrir a la ficha pública de una entidad vinculada. `examinar` mantiene prioridad para acciones declaradas.

**Debilidad:** una interacción narrativa de examen podía confundirse con una consulta. **Corrección:** el comando de consulta pura no ejecuta `Act`. **Simplificación:** se reaprovechan `Observe`, `read_public` y el renderer existente, sin agregar un segundo registro ni intérprete.

**Pruebas:** `H45F3Inspection`.

## H4.5f.4. Revisión integral y documentación

Se documentaron las invariantes con sus pruebas concretas, la semántica espacial y la compatibilidad de los schemas v1.2. El ejecutable canónico es `tools/glauquir.py`; `tools/gisela_cli.py` sigue disponible como alias. Los contratos de Act y Session no cambian. Las pruebas deben ejecutarse desde la raíz del proyecto.

```bash
python -m unittest gisela.engine.tests.test_h45f_scene -q
python tools/check_quality.py
python tools/check_project.py
sha256sum -c MANIFEST.sha256
```

## Riesgos pendientes

1. Las acciones generales no incluyen destino físico tipado: la visibilidad de sus interlocutores debe quedar declarada por el autor.
2. Las descripciones de elementos son estáticas; las variaciones por estado requieren elementos condicionales o nodos, no código del anfitrión.
3. Las escenas sin `location` aceptan contenido no espacial y dependen de la política narrativa explícita del autor.
4. No se prueban todas las combinaciones de reglas; los nuevos paquetes canónicos deben añadir sus propios tests de continuidad.
5. La compatibilidad de Ren'Py todavía no está comprobada. La siguiente tarea es preparar el guion oficial para GLAUQUIR antes de H5.

Véanse [ESCENAS_Y_PRESENCIA.md](../architecture/ESCENAS_Y_PRESENCIA.md) y [INVARIANTES_H4_5F.md](INVARIANTES_H4_5F.md).
