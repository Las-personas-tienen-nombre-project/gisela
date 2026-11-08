# Unidad 4: Construcción autoral de rasgos y contribuciones

**Objetivo.** Definir un rasgo propio mediante el DSL 1.5, asignarlo a una entidad, predecir cuándo contribuye a una resolución y comprobar la predicción. Al terminar, el alumno distinguirá "tener un rasgo" de "obtener su contribución" y de "ganar una resolución".

**Prerrequisitos:** unidades 1 a 3 (objetos/listas JSON, ficha e instancia, condiciones y referencias). **Conceptos nuevos:** catálogo de TRAITS, rol en la resolución, etiqueta contextual, contribución, ranura de acumulación, asignación, efecto que concede rasgos y evaluación dirigida.

**Fuentes verificadas en este repositorio:** `traits/schemas/definitions.schema.json`, `traits/schemas/evaluation.schema.json`, `traits/README.md`, `traits/evaluator.py`, `gisela/engine/traits_dice_bridge.py`, `contracts/semantic_traits.py` y `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`. Los ejemplos son fragmentos reales de ese paquete o modificaciones válidas indicadas expresamente; los paquetes íntegros están en `ejercicios/04_rasgos/` y `soluciones/04_rasgos/`.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 4](../paquetes/04_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. Primero, la intención autoral

"Quiero que Parnecio sea más difícil de alcanzar cuando puede esquivar". Esta intención no describe una esquiva garantizada: pide una **bonificación al cálculo de evasión**. En GISELA, el autor define las propiedades en `traits.traits`, asigna el identificador del rasgo en una ficha (`cards`), y una resolución posterior aporta rol, etiquetas y ranuras. TRAITS determina si corresponde sumar una contribución; el motor compone esta información con los demás mecanismos de resolución y confirma el resultado. GLAUQUIR presenta lo que autorizan las interfaces públicas.

### Definición productiva completa de `dodge`

Este objeto es una **definición de rasgo**, extraída de `traits.traits` del paquete de referencia, no un paquete JSON autónomo:

```json
{
  "id": "dodge",
  "label": "Evasión pasiva +2",
  "entity_kinds": ["character"],
  "visibility": "public",
  "contributions": [
    {
      "id": "contribucion",
      "when": {"role": "defender", "all_tags": ["evasion"]},
      "add": {"slot": "bonus", "amount": 2}
    }
  ]
}
```

Lea cada campo: `id` es la referencia estable; `label` es una denominación visible, **no** la regla que modifica el cálculo; `entity_kinds` permite asignarlo a personajes; `visibility` indica la visibilidad declarada (la proyección pública sigue su propio contrato); `contributions` enumera las aportaciones; el identificador de regla `contribucion` permite distinguirla de otras; `when` exige un rol y etiquetas; `add` suma un entero a la ranura indicada. Aquí el contexto debe incluir `evasion`, el portador debe ser **defender**, y la resolución debe admitir `bonus`. Si se cumplen, aporta **+2**. No se comprueba aquí ninguna probabilidad de éxito ni se cambia HP directamente.

### Definición frente a asignación

En la ficha de personaje `cards[id=parnecio]` aparece `"traits": ["dodge"]`. La definición vive en `traits.traits`; la ficha **referencia** ese ID. Durante el inicio, GISELA materializa el estado de la entidad. En los paquetes de referencia, las instancias de `initial_state.characters` no repiten esas listas: el motor hereda lo declarado en la ficha cuando corresponde. No suponga que las cartas y las instancias sean la misma cosa; en una sesión los rasgos pueden cambiar mediante operaciones autorizadas.

Una declaración de rasgo no asignada a nadie no otorga bonificaciones. Una asignación existente no activa automáticamente todas sus contribuciones: depende del contexto de cada resolución.

## 2. Predicción de la contribución de evasión

| Portador | Rol | Etiquetas de la resolución | Contribución `dodge` |
|---|---|---|---:|
| Parnecio | `defender` | `evasion` | +2 a `bonus` |
| Parnecio | `actor` | `evasion` | 0 |
| Parnecio | `defender` | `hit` | 0 |

No confunda la etiqueta de una resolución (`evasion`) con un nombre de habilidad ni con una condición `compare` de la Unidad 3. El autor configura propiedades admitidas en el DSL; el mecanismo de ejecución pasa el contexto correspondiente al evaluador. `all_tags` exige **todas** las etiquetas enumeradas; el contrato también admite `none_tags` para excluir coincidencias. No invente roles o ranuras fuera de los contratos.

## 3. Una penalización también es un rasgo

**Intención:** "Quiero un personaje cuya torpeza reste 2 a su defensa evasiva". El ejercicio `02_penalizacion` agrega un rasgo nuevo llamado `paso_torpe`, con `when.role = defender`, `all_tags = ["evasion"]`, `add.slot = bonus` y `add.amount = -2`. Se asigna a Gillius, que ya posee `dodge` (+2). La contribución acumulada de esos dos rasgos en ese contexto es **0**: +2 - 2. El cálculo final de esquiva no queda necesariamente en cero porque podría haber otras fuentes de bonificación, dificultad, tiradas o atributos.

**Importante:** el estado inicial de Gillius y las reglas originales del encuentro **no se modifican en el paquete productivo**. El ejercicio es una copia aislada que permite observar el caso. La solución restaura el comportamiento exigido por el enunciado sin borrar `dodge`.

## 4. Un rasgo para el atacante

**Intención:** "Quiero una ventaja de +1 cuando Parnecio intenta acertar". `ojo_certero` usa `when.role = actor` y `all_tags = ["hit"]`, con `add.slot = bonus` y `add.amount = 1`. El ejercicio 03 entrega inicialmente una etiqueta equivocada; el alumno debe corregir el contexto, no cambiar el valor ni asignarlo a un defensor. Prediga: con `actor`+`hit`, +1; con `defender`+`hit`, 0. Así comprobará que la pertinencia depende de la combinación, no del texto de `label`.

## 5. Rasgos de reducción: etiquetas diferentes

El paquete de referencia incluye los siguientes rasgos:

| Rasgo | Portador inicial o procedencia | Coincidencia | Cantidad |
|---|---|---|---:|
| `escamas` | Tegularis | defensor + `physical_damage_reduction` | +5 a `bonus` |
| `magic_redux` | Clarisa e Iosepus | defensor + `magic_damage_reduction` | +3 a `bonus` |
| `pride_redux` | Concedido por `ef_pride_volcan` | defensor + `damage_reduction`, `physical_damage_reduction` o `magic_damage_reduction` | +1 en cada contexto coincidente |

**No son sinónimos.** `escamas` no reduce mágicamente por el simple hecho de ser un rasgo defensivo. `magic_redux` no ofrece la bonificación física. En `pride_redux`, hay tres **contribuciones separadas**, no una regla que se active siempre para cualquier daño. Si un contexto contiene varias etiquetas coincidentes, se deben interpretar las reglas efectivamente habilitadas, no asumir un efecto físico equivalente a un efecto genérico sin comprobarlo.

**Cadena causal de Pride en el paquete productivo:** `actuation.event_policies[id=pride_of_the_volcan_son]` dispara la operación `apply_effect` con `effect = ef_pride_volcan` y `target = tegularis`; la carta `cards[id=ef_pride_volcan]` contiene `granted_traits: ["pride_redux"]` y modificadores S.O.F.I.A. Esta unidad se concentra en el rasgo; las condiciones y el ciclo completo del efecto se desarrollan en las unidades 5 y 7. No asigne `pride_redux` inicialmente a Tegularis para simular el desenlace del encuentro: falsearía la cronología del balance.

## 6. Cinco ejercicios guiados, de alcance creciente

Los archivos de inicio contienen la **estructura ejecutable y válida** del encuentro, pero una parte de la contribución que el alumno debe construir está desactivada mediante un valor nulo o una etiqueta deliberadamente distinta. No son reproducción del balance: solo los archivos `soluciones/04_rasgos/` restauran el objetivo de cada ejercicio. Todas las soluciones 01, 04 y 05 igualan exactamente el paquete productivo de referencia para las propiedades trabajadas.

1. **01_dodge:** busque `traits.traits[id=dodge]`, cambie `add.amount` de 0 a 2. Prediga los tres contextos de la tabla y compruebe cuáles activan el rasgo. No cambie el rol ni las etiquetas.
2. **02_penalizacion:** edite el rasgo nuevo `paso_torpe`, que ya aparece asignado a Gillius en la copia; cambie su cantidad de 0 a **-2**. Prediga la suma con su `dodge` original. Explique por qué no corresponde quitar `dodge` para obtener la misma suma.
3. **03_precision:** repare `ojo_certero` para que su contribución +1 se active únicamente cuando Parnecio sea `actor` y la resolución tenga `hit`, no `evasion`. Explique qué ocurriría si `role` fuera `defender`.
4. **04_escamas:** restaure `escamas` de 0 a +5 para Tegularis. Demuestre por qué el contexto `magic_damage_reduction` no recibe ese +5 y revise `magic_redux` como contrapunto.
5. **05_pride_redux:** restaure +1 en cada una de las tres contribuciones existentes de `pride_redux`, sin agregar etiquetas ni modificar el efecto que lo concede. Explique por qué el rasgo no tiene efecto al inicio del combate.

**Error deliberado:** `06_rasgo_inexistente.package.json` asigna `rasgo_que_no_existe` a Parnecio. Debe rechazarse en la admisión semántica. Corríjalo retirando la referencia o declarando un rasgo válido, sin esconder el error ni introducir campos desconocidos.

### Validación de paquetes completos

Desde la raíz del repositorio, tras corregir cada ejercicio:

```bash
PYTHONPATH=. python -c "from pathlib import Path; from gisela.contracts.admit_package import admit_package_file; print(admit_package_file(Path('docs/history/workshops/autoria_dsl_15/ejercicios/04_rasgos/01_dodge.package.json')).digest)"
```

Sustituya el nombre para cada ejercicio. Para comprobar su ejecución mediante el cliente público:

```bash
python -m gisela.cli.glauquir --auto --package docs/history/workshops/autoria_dsl_15/ejercicios/04_rasgos/01_dodge.package.json
```

La admisión por sí sola no demuestra que se aplicó un +2. Para comprobar **contextos y aportes**, el instructor dispone de `python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_04.py`, una herramienta de evaluación **del workshop** que utiliza las API públicas de admisión y TRAITS. Los alumnos no deben programar Python: deben entender el resultado y modificar exclusivamente declaraciones JSON. Esta herramienta comprueba los solucionarios de referencia; el instructor puede repetir su procedimiento sobre los ejercicios corregidos antes de calificarlos.

## 7. Recorrido autónomo

Sin mirar los solucionarios, escriba una especificación de `paso_torpe` que penalice únicamente la defensa evasiva en 2, y otra de `ojo_certero` que contribuya al ataque con `hit` en 1. Defina cada rasgo y asígnelo a un personaje en una copia íntegra de un paquete válido. Antes de ejecutar, entregue una tabla con al menos tres situaciones que deberían activar y no activar las contribuciones. Explique en qué difieren `escamas`, `magic_redux` y `pride_redux`; localice la operación que concede este último. Compruebe admisión, predicción y evaluación. No se permite alterar el motor.

## 8. Errores frecuentes, criterios de aprobación

**Errores:** usar `label` como si fuese regla; confundir `cards[].traits` con `traits.traits`; usar `actor` donde corresponde `defender`; omitir `all_tags`; agregar `bonus` cuando la resolución no admite esa ranura; suponer que +2 equivale a éxito; asignar `pride_redux` desde el comienzo; duplicar un ID; superar capacidad de rasgos; confundir reducción física, mágica y general; creer que JSON válido equivale a un paquete admitido y ejecutado.

**Aprobación:** el alumno explica `dodge` campo a campo; crea y asigna dos rasgos nuevos; predice activaciones positivas y negativas; explica la suma +2 - 2; comprueba contribuciones sin deducir automáticamente éxito o daño; distingue el caso de Pride y corrige una referencia inválida. Puede presentar las salidas y explicar su significado sin escribir código Python.
