# Taller 03. Personajes en el faro

En los dos talleres anteriores, Lara y Elio aparecían solamente en el texto. Ahora aprenderás a declararlos como personajes del mundo de GISELA y a indicar dónde se encuentran. Seguiremos con una historia pequeña, sin habilidades, relaciones ni inventario.

## Antes de comenzar

Completa el [taller 02](../02_faro/README.md) y utiliza la [guía de instalación](../03_instalacion.md) si necesitas preparar el entorno. Trabajaremos con [`personajes.package.json`](personajes.package.json). Ejecuta los comandos desde la raíz del repositorio y guarda una copia antes de modificar el archivo.

## 1. Ejecuta la historia

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/03_personajes/personajes.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/03_personajes/personajes.package.json
```

Lara llega al faro, conversa brevemente con Elio y decide si lo acompaña a la cúpula o espera abajo. Repite la historia para comprobar los dos desenlaces.

## 2. La ficha de un personaje

Busca `cards` al principio del archivo. Allí encontrarás esta ficha:

```json
{
  "id": "lara",
  "kind": "character",
  "title": {"text": "Lara"},
  "description": {"text": "Una navegante que conoce las corrientes de la costa."}
}
```

Una **ficha** describe qué personaje puede existir en el relato. `id` es su identificador estable; `title` guarda el nombre de presentación de la ficha; `description` permite añadir una descripción. Esos textos no se muestran automáticamente en todas las pantallas de GLAUQUIR. El campo `kind` indica que la ficha corresponde a un personaje. Hay otra ficha para Elio y una ficha de lugar para el faro.

La ficha no coloca por sí sola al personaje en el mundo.

## 3. El personaje dentro de la historia

Busca ahora `initial_state.characters`:

```json
"characters": [
  {"id": "lara", "card": "lara", "location": "faro"},
  {"id": "elio", "card": "elio", "location": "faro"}
]
```

Estas son las **instancias** iniciales. Cada una tiene un identificador, señala qué ficha utiliza mediante `card` e indica su ubicación mediante `location`. El lugar `faro` también tiene una ficha y una instancia en `initial_state.locations`. De esta manera, el motor sabe que Lara y Elio existen en ese lugar al comenzar la sesión.

No confundas `cards` con `initial_state`: las fichas definen personajes y lugares; el estado inicial indica cuáles están presentes al comenzar la historia.

## 4. Cómo se utiliza un personaje

En el nodo `encuentro` hay dos intervenciones breves:

```json
{
  "id": "saludo_lara",
  "op": "dialogue",
  "speaker": "lara",
  "text": {"text": "El mar está cambiando. ¿Has visto las luces de los barcos?"}
}
```

`speaker` identifica quién habla, utilizando el `id` de la instancia del personaje. La intervención de Elio utiliza `"speaker": "elio"`. Por ahora basta con reconocer esa relación. Aprenderás a construir conversaciones con decisiones en el siguiente taller.

## 5. Ejercicio: cambia un personaje

Modifica el `title.text` de la ficha `elio` para que se llame **Elías**. No cambies los identificadores `id`, `card` ni `speaker`. Ejecuta el paquete y observa el resultado. GLAUQUIR muestra el identificador `elio` como etiqueta de la intervención; cambiar `title.text` no lo reemplaza automáticamente.

Luego cambia la descripción de Lara. Comprueba que la historia sigue funcionando. La descripción pertenece a la ficha, pero no se incorpora automáticamente al texto narrado.

**Comprobación:** el paquete sigue admitiéndose y el diálogo continúa identificado como `elio`. No esperes ver «Elías» ni la nueva descripción en esta escena: el ejercicio comprueba que los datos de la ficha pueden cambiar sin romper las referencias, no su presentación automática. Al terminar, restaura los textos originales.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/03_personajes/personajes.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/03_personajes/personajes.package.json
```

Si aparece un error, revisa que cada instancia apunte a una ficha existente y que su lugar también esté declarado. El validador comprueba la estructura y las referencias; no evalúa el estilo del relato.

## Qué aprendiste

Una ficha (`cards`) define un personaje o un lugar. Una instancia (`initial_state`) indica qué existe cuando comienza la historia y dónde se encuentra. Las referencias, como `speaker`, permiten utilizar esos personajes sin repetir sus definiciones.

En el próximo taller trabajaremos con conversaciones y decisiones. Para consultar otros campos disponibles, utiliza la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).

---

[Volver al índice del curso](../README.md) · [Siguiente taller](../04_dialogos_decisiones/README.md)
