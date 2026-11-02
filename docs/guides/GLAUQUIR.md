# GLAUQUIR: comandos y presentación

GLAUQUIR es el cliente textual de GISELA. Presenta lo publicado por `Observe` y envía a `Act` el `action_id` de una oferta vigente. Las reglas, la visibilidad y las consecuencias pertenecen al motor.

## Jugar

```bash
glauquir --package gisela/packages/h46b_central_clasificadora.package.json
```

`mirar` muestra la escena, las personas y elementos visibles, las salidas declaradas y las acciones habilitadas. `acciones` enumera solo ofertas habilitadas; `acciones ELEMENTO` hace lo mismo para un elemento visible. Las categorías vacías se omiten. Los elementos sin rol declarado figuran como «ELEMENTOS»; GLAUQUIR no deduce portabilidad ni cantidades a partir del nombre o de los verbos.

| Comando | Uso |
| --- | --- |
| `mirar`, `mirar ELEMENTO` | Leer escena o inspeccionar un elemento público. |
| `acciones`, `acciones ELEMENTO` | Consultar ofertas ejecutables. |
| `accion ID` | Ejecutar una oferta habilitada por su ID público. |
| `A`, `B`, …, `Z`, `AA`, … | Ejecutar la oferta que muestra esa letra en la observación actual. |
| `hablar`, `ir`, `examinar`, `tomar`, `dejar`, `dar`, `usar` | Buscar una oferta habilitada por verbo y objeto. |
| `inventario`, `estado`, `ficha`, `misiones`, `history`, `ayuda` | Leer información pública; `history` muestra pasajes narrativos confirmados. |
| `guardar RUTA`, `cargar RUTA`, `salir` | Gestionar la sesión. |

Las letras y los números siguen el orden mostrado: primero las salidas y luego las demás acciones habilitadas. Las letras se reasignan al cambiar las opciones; `acciones ELEMENTO` conserva la letra de cada oferta en la lista completa. La pantalla también presenta el comando `accion ID` de cada oferta. Una acción bloqueada no puede ejecutarse por ID, verbo, letra ni número. `--auto` se detiene si no hay acciones habilitadas; no garantiza llegar a un final.

Cuando tanto la entrada como la salida son terminales y Python dispone de `readline`, `↑` recorre los comandos escritos durante esta ejecución y `←` y `→` mueven el cursor para editarlos. Si se eligió una letra, `↑` recupera el comando completo `accion ID`. Este historial de entrada no se guarda en la partida y es distinto de `history`, el registro narrativo confirmado. La entrada redirigida o por tubería sigue aceptando los mismos comandos, sin edición interactiva de línea.

## Diagnóstico

Inicie con `--developer` para consultar datos privados en una sesión local confiable. `mirar` añade los recuentos, sin imprimir la lista de acciones bloqueadas. `acciones bloqueadas` muestra ID, etiqueta y `reason` si GISELA lo publica; `acciones todas` separa las dos listas. Ambas órdenes se rechazan en modo normal. El modo desarrollador conserva exactamente la misma validación de `Act`.

`hechos`, `relacion ORIGEN DESTINO CAMPO`, `propiedad ENTIDAD CAMPO` y `disposicion PERSONA` son consultas diagnósticas. Siguen disponibles `consultar` y `depurar` con sus subcomandos. `disposicion` acepta la referencia pública de una persona visible y muestra la relación dirigida NPC → protagonista, su valor efectivo, escala, valor normalizado, categoría y fuente de color. La CLI nunca solicita este diagnóstico en modo normal. Para clientes externos, el gateway exige `debug_private`; `--developer` por sí solo no concede esa capacidad.

## Color

`--color auto` es el valor inicial y solo usa ANSI si stdout es una terminal compatible, `TERM` no es `dumb` y `NO_COLOR` está ausente. `--color never` desactiva ANSI. `--color always` lo fuerza, incluso con `NO_COLOR` o salida redirigida. La paleta es ANSI básica; encabezados y etiquetas conservan su sentido sin color. La ruta de Windows intenta activar el modo de terminal virtual y, si falla en `auto`, deja texto simple.

En modo normal, el color de una persona u objeto procede solo de un rol narrativo explícito o del tema. En `--developer`, una persona sin color explícito puede tomar el color de su categoría de disposición real. `default` es un rol explícito que aplica el estilo ANSI predeterminado; también prevalece sobre la disposición.

Para declarar colores, referencias públicas y escalas en un paquete v1.5, consulte la [API de clientes](../architecture/API_CLIENTES.md) y los [contratos](../../gisela/contracts/README.md).
