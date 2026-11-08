# Taller 04. Diálogos y decisiones

En este taller continuarás la historia de Lara y Elio. Aprenderás a escribir intervenciones de personajes y a ofrecer distintas preguntas al lector. Cada pregunta conduce a una respuesta diferente y a un desenlace propio.

## Antes de comenzar

Completa el [taller 03](../03_personajes/README.md). Trabajaremos con [`dialogos.package.json`](dialogos.package.json). Guarda una copia antes de editarlo. Ejecuta los comandos desde la raíz del repositorio.

## 1. Lee las dos conversaciones

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/04_dialogos_decisiones/dialogos.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/04_dialogos_decisiones/dialogos.package.json
```

Lara llega al faro y Elio le permite hacer una pregunta. Primero consulta por la luz y sigue la historia hasta el final. Después reinicia el paquete y pregunta por los barcos. Comprueba que las respuestas y los finales son diferentes.

## 2. Escribe una intervención

Busca la primera intervención de Elio:

```json
{
  "id": "saludo_elio",
  "op": "dialogue",
  "speaker": "elio",
  "text": {"text": "Tenemos poco tiempo. ¿Qué necesitas saber?"}
}
```

`dialogue` presenta una intervención. `speaker` señala el identificador del personaje que habla y `text.text` contiene sus palabras. El identificador `elio` corresponde a la instancia declarada en `initial_state.characters`, como vimos en el taller anterior. GLAUQUIR muestra el identificador del hablante como etiqueta; no lo reemplaza automáticamente por el título de su ficha.

## 3. Ofrece preguntas al lector

El paso `pregunta` utiliza `choice`. Su campo `prompt.text` presenta la pregunta general y `options` contiene las alternativas:

```json
{
  "id": "preguntar_luz",
  "label": {"text": "¿Por qué se apagó la luz?"},
  "next": {"node": "respuesta_luz"}
}
```

`id` identifica la opción, `label.text` es lo que lee el jugador y `next.node` indica a qué nodo conduce. La segunda alternativa lleva a `respuesta_barcos`. Una elección cambia la ruta narrativa; no es necesario registrar un hecho para obtener estos dos desenlaces.

## 4. Responde con una escena distinta

En `respuesta_luz`, Elio explica el daño en la lámpara, Lara responde y la historia termina con la señal encendida. En `respuesta_barcos`, los personajes hablan de una sirena y el relato termina en el muelle. Observa que ambos nodos incluyen `dialogue`, `narrate` y `ending`, pero no introducen nuevas operaciones.

Este ejemplo representa **dos conversaciones alternativas**, no una conversación libre ni un sistema que interprete preguntas escritas por el lector. Las opciones están definidas por el autor.

## 5. Ejercicios

Primero cambia el texto de la pregunta sobre la luz, sin modificar su `id` ni `next`. Ejecuta ambas rutas y comprueba que siguen funcionando.

Después cambia la respuesta de Elio en `respuesta_barcos` y añade una intervención de Lara en ese mismo nodo. Usa un `id` nuevo para la intervención, `op: dialogue`, `speaker: lara` y `text` con su contenido. Respeta las comas y corchetes del JSON.

**Comprobación:** el primer recorrido debe terminar en «La señal encendida» y el segundo en «La campana del muelle». Restaura el ejemplo original si necesitas comparar.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/04_dialogos_decisiones/dialogos.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/04_dialogos_decisiones/dialogos.package.json
```

El validador comprueba la estructura y las referencias, pero no decide si los diálogos resultan naturales o interesantes.

## Qué aprendiste

`dialogue` muestra lo que dice un personaje. `choice` presenta alternativas y conecta cada una con un nodo. Combinándolos, puedes escribir conversaciones con respuestas diferentes y consecuencias narrativas visibles. Para los campos admitidos, consulta la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).
