# H4.6b — Central Clasificadora: jornada de adaptación jugable

**Estado: PROTOTIPO JUGABLE — pendiente de aprobación editorial.**

Se trata de una **adaptación condensada de prueba** inspirada en *Blue Forever / Las personas tienen nombre*. No constituye una nueva cronología canónica. Se ejecuta exclusivamente como contenido declarativo de GISELA v1.5 en GLAUQUIR. No se modificó la lógica narrativa del motor, DICE, ALBERTO, S.O.F.I.A., TRAITS ni MARY.

## Qué puede jugarse

Alberto inicia su turno en portería, recorre primer piso, ascensor y Puesto B; puede conversar con Marcela, ayudar a Gisela, comentar su trenza, escuchar una advertencia de Araya, ofrecer una copia de Def Leppard y probar la radio. El reloj de ficción avanza mediante recorridos de seis minutos o períodos de trabajo de sesenta minutos. A las 23:00 se deshabilitan los encuentros sociales y queda disponible la ronda nocturna; la elección ante la silueta del patio determina un desenlace de horror o permite uno de dos epílogos cotidianos.

Los hechos `casete_entregado`, `comentario_trenza`, `marcela_escuchada`, `araya_advirtio` y los de la ronda permiten comprobar decisiones y consecuencias sin calcular «puntos de afecto». La copia física del casete cambia realmente de propietario; no basta registrar el hecho. Gisela decide intervenir en la conversación musical y no hay obligación de aceptar ni devolver afecto.

## Fuentes y diferencias con la novela

- **Fuente:** *Blue Forever* (edición adjunta), especialmente «La Hueá que estaba ahí» (Araya y la regla de mirar), «Gisela. Señorita Gisela», «La trenza maría», «Gisela. La trenza», «El gallito» y «Gisela. Pálido y Def Leppard».
- **Canon:** los episodios de la trenza, la copia del casete y el encuentro sobrenatural no ocurren todos durante la noche del 24 de julio de 1998. La novela sitúa la trenza el 24 de julio y el casete ofrecido a Gisela el 6 de agosto; la historia de Araya sobre la silueta figura en junio.
- **Adaptación:** unifica esos acontecimientos en una jornada ficticia de pruebas del motor y crea diálogos y alternativas nuevas para hacerla interactiva. Estas alternativas **no sustituyen los acontecimientos de la novela** y requieren validación del autor antes de llamarlas canónicas.
- **Producción:** no incluye canciones ni grabaciones comerciales. Menciona los nombres de las bandas únicamente como parte del relato. La posibilidad de publicar el demo se mantiene sin resolver por la condición de ineditismo del libro.
- **Aspectos abiertos:** horarios exactos y autonomía de las rutinas de NPC, revelación gráfica de rostros, escenas audiovisuales, correspondencia con manuscrito y evaluación del ritmo dramático. No se afirma que exista aún un planificador de NPC o un sistema de recursos Ren'Py.

## Jugar la aventura en GLAUQUIR

Desde la raíz del proyecto, con las dependencias instaladas:

```bash
python gisela/contracts/admit_package.py gisela/packages/h46b_central_clasificadora.package.json
python tools/glauquir.py --package gisela/packages/h46b_central_clasificadora.package.json
```

La consola admite los identificadores de acciones mostrados en `acciones`, `mirar`, `guardar archivo.json`, `cargar archivo.json`, `inventario`, `history` y otros comandos propios de GLAUQUIR. No necesita Ren'Py. Para llegar al cierre, vuelva a portería después de las 23:00 y seleccione `cerrar_turno`.

## Recorridos repetibles

```bash
python tools/h46b_walkthrough.py --route casete --verify-restores
python tools/h46b_walkthrough.py --route solo --verify-restores
python tools/h46b_walkthrough.py --route radio --verify-restores
python -m unittest gisela.engine.tests.test_h46b_central -q
python tools/check_project.py
```

| Ruta | Resultado | Estado verificable |
| --- | --- | --- |
| `casete` | `casete_en_la_pieza` | Conversaciones, gesto de la trenza, transferencia del casete, radio visible y tirada reconocida. |
| `solo` | `escalera_azul` | Una jornada sin encuentros sociales forzados; el casete sigue en poder de Alberto. |
| `radio` | `reporte_sin_novedad` | Otra respuesta al fenómeno, con consecuencias diferentes. |

Los recorridos se automatizan *fuera* del motor: `h46b_walkthrough.py` solo envía acciones autorizadas por `Observe` mediante `Act`; no altera estados directamente. Las pruebas guardan y restauran resultados DICE antes de aplicar consecuencias, verifican el corte horario, proyecciones, rechazo de acciones vencidas, MARY y reacciones. Son una cobertura de integración, no una garantía exhaustiva de las combinaciones posibles.

## Decisiones y pendientes

- **DECIDIDO para la prueba:** cuatro espacios, jornada 19:00–23:00, tres desenlaces, GLAUQUIR como anfitrión y ninguna excepción programada en el motor.
- **PROPUESTO, no canon:** la nueva secuencia condensada, sus elecciones y las frases escritas para conectarlas.
- **ABIERTO:** aprobación del autor, guion definitivo, calendario y disponibilidad real de NPC, dirección artística, derechos musicales, publicación y la adaptación Ren'Py.
- **DESCARTADO del prototipo:** romance cuantificado, interacción social posterior a las 23:00 y reproducción de música sin licencia.
