# Crea tu primer paquete

Esta guía muestra cómo crear un relato pequeño con una elección y dos finales. Trabaja desde la raíz del repositorio. Necesitas Python 3.10 o posterior y las dependencias del [inicio rápido](QUICK_START.md).

## Crea una copia

El [paquete mínimo](../../gisela/packages/ejemplo_minimo.package.json) es un archivo JSON completo que funciona con GISELA. Cópialo para escribir tu propia historia.

```bash
cp gisela/packages/ejemplo_minimo.package.json mi_historia.package.json
```

Abre `mi_historia.package.json` en un editor de texto. Cambia el valor de `manifest.id` por `mi_historia`. Cambia el texto de `entrada`, las dos opciones de `decision` y los textos de los dos finales. Puedes dejar los identificadores de los nodos tal como están. Así no tendrás que cambiar sus referencias en `next`.

El archivo tiene estas partes.

1. `manifest` da nombre al paquete, indica la versión del formato y señala el nodo donde empieza la historia.
2. `nodes` contiene el texto, la elección y los pasos que llevan a cada final. Cada opción usa `next` para señalar el nodo siguiente.
3. `endings` declara los finales que usan los pasos con `op` igual a `ending`.
4. `initial_state` indica el estado al comenzar. Este relato no tiene personajes, objetos ni datos de mundo, por eso sus listas están vacías.
5. `cards`, `scenes` y `rules` también están vacíos. GISELA los necesita en el archivo, aunque esta historia no los use.

Los identificadores son los nombres internos que conectan las partes del paquete. Los textos visibles se pueden cambiar sin tocar esos nombres. Si cambias un identificador, cambia también todas las referencias que apuntan a él.

## Comprueba y juega

Primero pide a GISELA que compruebe el archivo.

```bash
python gisela/contracts/admit_package.py mi_historia.package.json
```

Si el archivo es válido, verás `ADMITTED` y una serie de letras y números. Si aparece `REJECTED`, lee la ruta y el mensaje del error. Revisa primero las comas del JSON y los identificadores que aparecen en `next` o `ending`.

Juega desde la consola.

```bash
python tools/glauquir.py --package mi_historia.package.json
```

La consola muestra el primer texto. Escribe `1` para avanzar. Cuando aparezcan las opciones, escribe `1` para abrir la puerta o `2` para seguir de largo. Escribe `1` otra vez para avanzar al final. El resultado será `Final: Dentro de la pieza` o `Final: Al final del pasillo`, según el título declarado para cada final.

También puedes recorrer cada camino sin escribir opciones durante la partida.

```bash
python tools/glauquir.py --package mi_historia.package.json --auto --choose abrir
python tools/glauquir.py --package mi_historia.package.json --auto --choose seguir
```

Si necesitas personajes, escenas, reglas o dados, consulta los [contratos](../../gisela/contracts/README.md) y los paquetes más completos en `gisela/packages`.

## Catálogos y anotaciones

Los textos literales del ejemplo pueden convertirse a `{"text_key":"..."}` para presentar la misma historia en diferentes idiomas. Las notas auxiliares dirigidas a GLAUQUIR pueden declararse en escenas, acciones, nodos y pasos observables de formato v1.5. Consulte [la guía de localización y anotaciones](LOCALIZACION_Y_ANOTACIONES.md) para ejemplos completos y el comando de ensamblado determinista.
