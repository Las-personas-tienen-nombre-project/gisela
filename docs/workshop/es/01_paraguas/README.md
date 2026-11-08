# Taller 01. El paraguas olvidado

En este taller modificarás una historia breve y comprobarás cómo una elección produce dos finales distintos. No necesitas crear una historia desde cero ni conocer todos los campos del DSL.

## Antes de comenzar

Completa la [instalación](../03_instalacion.md) y comprueba que puedes abrir GLAUQUIR. Todos los comandos se ejecutan desde la raíz del repositorio, donde está `pyproject.toml`.

El archivo de trabajo es [`paraguas.package.json`](paraguas.package.json). Usa cualquier editor de texto que permita guardar archivos UTF-8. Antes de cambiarlo, conserva una copia para poder recuperar el ejemplo original. Un archivo JSON utiliza comillas dobles, comas y llaves; si cambias solo el texto entre comillas, es menos probable que rompas su estructura.

## 1. Juega la historia

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/01_paraguas/paraguas.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/01_paraguas/paraguas.package.json
```

Elena encuentra un paraguas azul en la estación. Tomás cree reconocer a su dueña, pero no tiene pruebas. Al llegar a la elección, escribe `A` y presiona Enter. Observa cómo termina el relato. Ejecuta el mismo comando una segunda vez y elige `B` para conocer el otro desenlace. También puedes seleccionar por número o escribir `accion examinar` y `accion entregar`.

**Comprobación:** la primera opción permite descubrir las iniciales `M. R.`; la segunda termina sin esa pista. Ambas dejan el paraguas en objetos perdidos. Todavía no hay personajes ni objetos registrados en el estado del motor: Elena, Tomás y el paraguas aparecen solo en el texto de este primer ejemplo.

## 2. Reconoce las partes del archivo

Abre `paraguas.package.json`. Encontrarás estos elementos:

| Elemento | Para qué sirve |
|---|---|
| `manifest` | Identifica el paquete y señala el nodo inicial, `estacion`. |
| `nodes` | Contiene los fragmentos de la historia. |
| `narrate` | Muestra el texto de una situación. |
| `choice` | Presenta alternativas al lector. |
| `options` | Define el texto de cada alternativa y su destino en `next.node`. |
| `ending` y `endings` | Terminan el recorrido y dan un título al desenlace. |

Los campos `id` son identificadores usados por el motor: no son el texto que lee la persona. En cambio, las cadenas incluidas en `text` o `label.text` son parte del relato. Los caminos de campos como `text.text` se leen de izquierda a derecha: el campo `text` contiene otro campo llamado `text`. Las secciones vacías del archivo se mantienen porque forman parte de la estructura utilizada por el paquete mínimo.

## 3. Cambia un texto

Busca el paso con `"id": "encuentro"` y reemplaza solo su `text.text` por una versión propia de la llegada a la estación. Guarda el archivo y ejecútalo de nuevo. Si todo está bien, verás tu nueva redacción antes de las mismas dos opciones.

No cambies `op`, `id` ni `next.node` en este ejercicio. Conserva las comillas dobles y las comas de JSON.

## 4. Cambia el nombre de una opción

Busca la opción con `"id": "examinar"` y modifica únicamente su `label.text`, por ejemplo, a `Revisar el mango del paraguas`. Vuelve a ejecutar el relato y comprueba que aparece la nueva frase, pero que la opción todavía conduce al hallazgo de las iniciales.

Observa la diferencia: cambiar el texto visible de una opción no cambia su identificador ni el lugar al que conduce.

## 5. Ejercicio final

Modifica la descripción del final `sin_pista` para que Elena explique al encargado de objetos perdidos dónde encontró el paraguas. Después cambia el título de ese final en `endings`. No agregues una tercera opción todavía.

Comprueba ambos recorridos. Al terminar, el texto nuevo solo debe aparecer cuando eliges entregar el paraguas sin examinarlo.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/01_paraguas/paraguas.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/01_paraguas/paraguas.package.json
```

El validador revisa la estructura y las reglas admitidas. No puede decidir si un diálogo está bien escrito ni si un final es convincente; eso debes revisarlo tú.

Si el archivo deja de funcionar, revisa primero las comillas, las comas y que las referencias de `next.node` coincidan con un `id` de `nodes`. También puedes recuperar la copia original.

## Qué aprendiste

Una historia sencilla puede tener un comienzo común y dos desenlaces. `choice` ofrece la decisión y cada `next.node` señala el fragmento que se ejecutará. En el siguiente taller utilizaremos estado y condiciones para que una decisión también influya en situaciones posteriores.

Para conocer más campos y operaciones, consulta la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md). El [material histórico del paraguas](../../../history/authoring_manuals/es/README.md) contiene ideas para ejercicios posteriores, pero sus antiguos paquetes por etapas no forman parte de este taller.

---

[Volver al índice del curso](../README.md) · [Siguiente taller](../02_faro/README.md)
