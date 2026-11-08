# Taller 02. El faro

En el primer taller, cada elección conducía directamente a un final distinto. Ahora aprenderás a recordar una decisión y utilizarla más adelante, cuando la historia llegue a un punto común.

## Antes de comenzar

Completa el [taller del paraguas](../01_paraguas/README.md) y ten GISELA instalado según la [guía de instalación](../03_instalacion.md). Trabajaremos con [`faro.package.json`](faro.package.json). Los comandos se ejecutan desde la raíz del repositorio, donde está `pyproject.toml`. Guarda una copia del archivo antes de modificarlo.

Esta es una versión breve de *El faro de niebla*. No pretende reproducir el paquete completo, que incluye otros sistemas y se encuentra en `gisela/packages/h46_faro_de_niebla.package.json`.

## 1. Juega las dos alternativas

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/02_faro/faro.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/02_faro/faro.package.json
```

Lara llega al faro y debe decidir si consulta el plano de las corrientes o sube directamente a la cúpula. Elige `A` para consultar el plano. Después de leer el final, reinicia la historia y elige `B`.

**Comprobación:** al consultar el plano, Lara encuentra una ruta segura para los barcos. Si sube directamente, Elio enciende una señal de espera. En ambos casos la historia pasa por la misma cúpula antes del desenlace.

## 2. Cómo se recuerda una decisión

Abre `faro.package.json` y busca la elección `preparacion`. Su primera opción contiene:

```json
"effects": [
  {"op": "record_fact", "fact": "plano_consultado"}
]
```

Un **hecho** es una marca que el motor registra cuando ocurre algo relevante. Aquí significa que Lara consultó el plano. El nombre `plano_consultado` aparece también en `manifest.facts`, donde se declara el hecho que el paquete utilizará.

Ambas opciones conducen al nodo `cupula`. No necesitamos escribir dos versiones de esa escena: GISELA conserva el hecho mientras se desarrolla la sesión.

## 3. Cómo influye el hecho

En el nodo `cupula`, el paso `recordar` utiliza una condición:

```json
{
  "id": "recordar",
  "op": "condition",
  "test": {"has_fact": "plano_consultado"},
  "then": {"node": "ruta_segura"},
  "else": {"node": "ruta_incierta"}
}
```

`has_fact` pregunta si el hecho fue registrado. Cuando la respuesta es afirmativa, se sigue `then`; en caso contrario, se sigue `else`. La condición no elige por azar ni pregunta otra vez al lector: consulta una consecuencia de lo que hizo antes.

Fíjate en la diferencia con el primer taller: antes cada opción tenía un destino distinto. Ahora las opciones pueden reunirse en una misma escena y una condición decide qué sucede después.

## 4. Cambia una consecuencia

Modifica únicamente el texto del paso `incierto`, dentro del nodo `ruta_incierta`. Puedes hacer que Lara y Elio acuerden mantener una luz encendida hasta que despeje la niebla. Conserva los identificadores y ejecuta las dos alternativas otra vez.

**Comprobación:** el texto que cambiaste debe aparecer solamente al subir sin consultar el plano.

## 5. Ejercicio final

Cambia las consecuencias de ambas opciones sin modificar los nodos ni sus textos: retira el efecto `record_fact` de la opción `leer` y agrégalo a la opción `subir`. Mantén el hecho declarado en `manifest.facts`.

Ejecuta las dos alternativas. Ahora subir directamente conducirá al final `La ruta segura` y consultar el plano al final `Esperar hasta el amanecer`. Esta inversión es intencional: permite comprobar que la condición responde al hecho registrado, no al nombre o al texto de una opción. Al terminar, restaura la versión original del paquete.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/02_faro/faro.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/02_faro/faro.package.json
```

Si hay un error, revisa las comillas y comas de JSON, la declaración en `manifest.facts` y las referencias de `then.node` y `else.node`. El validador comprueba la estructura y las reglas del paquete, pero no juzga su calidad literaria.

## Qué aprendiste

`record_fact` conserva un hecho ocurrido durante la sesión. `has_fact` permite consultarlo y `condition` decide qué recorrido seguir según ese resultado. De esta manera, una decisión puede tener consecuencias posteriores, incluso si las alternativas vuelven a encontrarse en la misma escena.

En talleres posteriores utilizaremos personajes, conversaciones y objetos. Para consultar los campos admitidos, utiliza la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).
