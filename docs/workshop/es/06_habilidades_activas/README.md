# Taller 06. Habilidades activas

Lara necesita orientar la luz del faro. En este taller aprenderás a declarar una habilidad, asignársela a un personaje y utilizarla durante la historia. También comprobarás qué cambia cuando decides no usarla.

## Antes de comenzar

Completa el [taller 05](../05_objetos_equipo/README.md). Trabajaremos con [`habilidades.package.json`](habilidades.package.json). Guarda una copia antes de editarlo y ejecuta los comandos desde la raíz del repositorio.

## 1. Prueba las dos alternativas

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/06_habilidades_activas/habilidades.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/06_habilidades_activas/habilidades.package.json
```

En la ventana de habilidades elige **Usar Orientar la señal**. Repite la historia y elige **Continuar** sin usarla. En ambos casos llegarás a un final diferente.

## 2. Define una habilidad

En `cards` encontrarás la ficha:

```json
{
  "id": "orientar_senal",
  "kind": "skill",
  "title": {"text": "Orientar la señal"},
  "description": {"text": "Lara conoce el modo de ajustar el reflector."},
  "play": {
    "label": {"text": "Usar Orientar la señal"},
    "effects": [{"op": "record_fact", "fact": "senal_ajustada"}]
  },
  "return_policy": {"default": "discard"}
}
```

Esta es **la definición de la habilidad**, no una habilidad que exista por sí sola en la historia. `play.effects` describe qué ocurre al utilizarla. Aquí registra el hecho `senal_ajustada`. `return_policy.default` indica qué sucede con la instancia después de usarla; `discard` la retira de las habilidades disponibles.

## 3. Asigna la habilidad a Lara

En `initial_state.skills` aparece su instancia:

```json
{
  "id": "orientar_01",
  "card": "orientar_senal",
  "character": "lara",
  "zone": "hand"
}
```

La instancia `orientar_01` pertenece a Lara y comienza en `hand`, la zona desde la que el motor permite utilizarla. En `initial_state.capacities`, Lara tiene capacidad para una habilidad en esa zona. Además, `player_character` identifica a Lara como el personaje controlado por el lector.

## 4. Abre una ventana de habilidades

En el nodo `inicio`, el paso siguiente permite utilizar la habilidad:

```json
{
  "id": "habilidad",
  "op": "skill_window",
  "max_plays": 1
}
```

La ventana ofrece la habilidad disponible y la opción **Continuar**. `max_plays: 1` limita a un uso de habilidades en esa ventana. No significa que la habilidad se use automáticamente.

## 5. Comprueba su consecuencia

Después de la ventana, un paso `condition` comprueba `has_fact: "senal_ajustada"`. Si Lara utilizó la habilidad, la historia llega a **La señal recuperada**. Si continuó sin utilizarla, llega a **Esperar a que despeje**.

La diferencia depende del hecho registrado por el motor, no de una frase escrita en la narración.

## 6. Ejercicios

Primero cambia el título y la etiqueta de uso de la habilidad, sin modificar sus identificadores. Comprueba que el nuevo texto aparece en GLAUQUIR.

Después reemplaza `"default": "discard"` por `"default": "hand"`. Valida el paquete y vuelve a ejecutar el recorrido. La historia seguirá registrando el mismo hecho, pero la instancia de habilidad permanecerá en la mano de Lara. **El final no cambia y esa permanencia puede no ser visible en la escena:** estás modificando una regla del estado, no el desenlace. Restaura el valor inicial cuando termines.

Por último, cambia el texto del final `con_senal`, sin modificar `record_fact` ni `condition`, y comprueba que ambos recorridos siguen funcionando.

## 7. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/06_habilidades_activas/habilidades.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/06_habilidades_activas/habilidades.package.json
```

La validación revisa la estructura y las referencias. Juega ambas alternativas para comprobar también sus consecuencias.

## Qué aprendiste

Una ficha `skill` define la habilidad; `initial_state.skills` crea una instancia que pertenece a un personaje. `skill_window` permite utilizarla, `play.effects` aplica sus consecuencias y `return_policy` determina qué ocurre con ella después. Este taller no utiliza parámetros elegidos por el jugador, dados ni rasgos pasivos; los estudiaremos por separado. Para revisar los campos disponibles, consulta la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).

---

[Volver al índice del curso](../README.md) · [Siguiente taller](../07_habilidades_pasivas/README.md)
