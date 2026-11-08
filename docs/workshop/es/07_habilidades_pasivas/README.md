# Taller 07. Habilidades pasivas

Lara debe cruzar una pasarela mojada en el faro. En este taller conocerás una habilidad pasiva: una capacidad que influye en las condiciones de la historia sin que el lector tenga que activarla como una acción.

## Antes de comenzar

Completa el [taller 06](../06_habilidades_activas/README.md). Trabajaremos con [`pasivas.package.json`](pasivas.package.json). Guarda una copia antes de modificarlo y ejecuta los comandos desde la raíz del repositorio.

## 1. Ejecuta la historia

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/07_habilidades_pasivas/pasivas.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/07_habilidades_pasivas/pasivas.package.json
```

Elige **Cruzar la pasarela**. Lara alcanza el otro extremo porque tiene el rasgo `equilibrio`, aportado por una habilidad pasiva. Repite la historia y elige **Esperar a Elio** para ver el otro final.

## 2. Declara el rasgo

El apartado `traits` contiene un catálogo TRAITS. En este ejemplo define `equilibrio` para personajes. Su contribución `bonus: 2` solo se aplica cuando una evaluación consulta el rol `actor` y la etiqueta `equilibrio`.

```json
{
  "id": "equilibrio",
  "label": "Equilibrio en altura",
  "entity_kinds": ["character"],
  "visibility": "public",
  "contributions": [
    {
      "id": "apoyo",
      "when": {"role": "actor", "all_tags": ["equilibrio"]},
      "add": {"slot": "bonus", "amount": 2}
    }
  ]
}
```

La historia **no realiza una evaluación numérica**: su desenlace depende de la presencia del rasgo. La contribución numérica queda declarada, pero no se aplica automáticamente a la narración ni a cualquier acción.

## 3. Asocia el rasgo con una habilidad pasiva

En `cards` encontrarás esta ficha:

```json
{
  "id": "paso_seguro",
  "kind": "skill",
  "title": {"text": "Paso seguro"},
  "description": {"text": "Lara mantiene el equilibrio sobre superficies estrechas."},
  "passive_traits": ["equilibrio"],
  "play": {"effects": []},
  "return_policy": {"default": "hand"}
}
```

`passive_traits` indica qué rasgos aporta la ficha cuando una instancia de esa habilidad pertenece al personaje. La habilidad pasiva **no aparece como acción utilizable** por el hecho de existir; por eso esta historia no abre una `skill_window`.

En `initial_state.skills`, la instancia `paso_seguro_01` pertenece a `lara`. Mientras esa instancia siga perteneciendo a Lara, el rasgo estará disponible. No es necesario copiarlo a `initial_state.characters[].traits`.

## 4. Comprueba la condición

Cuando eliges cruzar, el nodo `pasarela` comprueba:

```json
{
  "id": "comprobar",
  "op": "condition",
  "test": {"has_trait": {"entity": "lara", "trait": "equilibrio"}},
  "then": {"node": "cruce_seguro"},
  "else": {"node": "cruce_detenido"}
}
```

La condición consulta el rasgo efectivo de Lara, incluidos los que recibe de habilidades pasivas. Si lo tiene, cruza; si no, decide regresar. La condición no lanza dados ni calcula el bono `2`.

## 5. Ejercicios

Primero cambia el título de **Paso seguro** y su descripción, sin modificar los identificadores. Comprueba que la historia sigue admitiéndose.

Después elimina únicamente la instancia `paso_seguro_01` de `initial_state.skills`. Como es el único elemento de esa lista, debe quedar así:

```json
"skills": []
```

No elimines el campo `skills`, el catálogo de rasgos ni la ficha de habilidad. Valida el paquete y ejecuta **Cruzar la pasarela**. Esta vez Lara debe llegar a **Regresar a salvo**. Restaura la instancia cuando termines.

Por último, devuelve la instancia y cambia el texto del final `cruce_seguro`. Comprueba que el resultado se mantiene y que no tuviste que agregar una acción para activar la habilidad.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/07_habilidades_pasivas/pasivas.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/07_habilidades_pasivas/pasivas.package.json
```

La validación comprueba la estructura y las referencias. Ejecuta el recorrido con la instancia presente y ausente para verificar el cambio de resultado.

## Qué aprendiste

Una habilidad pasiva puede aportar un rasgo a un personaje sin que se utilice como una acción. `passive_traits` declara ese aporte; `initial_state.skills` asigna su fuente, y `has_trait` permite consultar si el personaje dispone del rasgo. TRAITS también puede aportar modificadores numéricos en evaluaciones que coincidan con su contexto, pero esa capacidad se estudiará más adelante. Consulta la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).

---

[Volver al índice del curso](../README.md) · [Siguiente taller](../08_combate/README.md)
