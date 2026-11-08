# Unidad 1: Fundamentos del DSL

**Objetivo.** Identificar cada parte de un paquete GISELA productivo sin confundir los datos declarados con el programa que los interpreta.

**Prerrequisitos.** Uso básico de archivos de texto. No se requiere programación.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 1](../paquetes/01_fundamentos/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## De la intención a la declaración

Supongamos que queremos comenzar una historia con un personaje llamado Parnecio. La intención es narrativa; el motor necesita datos inequívocos que identifiquen al personaje. JSON representa esos datos mediante pares `clave: valor`, donde las claves van entre comillas y un valor puede ser texto, número, `true`, `false`, objeto o lista.

Este fragmento procede de la carta de personaje real del paquete v0.8.2d; **es un fragmento, no un paquete ejecutable por sí solo**:

```json
{
  "id": "parnecio",
  "kind": "character",
  "title": {
    "text": "Parnecio Esparcales"
  },
  "sofia": {
    "strength": 8,
    "openness": 5,
    "fortune": 6,
    "intelligence": 4,
    "awareness": 6
  },
  "traits": [
    "dodge"
  ]
}
```

La clave `id` identifica la definición; `kind` señala qué tipo de carta es; `title.text` corresponde al nombre mostrado; `sofia` agrupa cinco atributos numéricos; `traits` enumera rasgos que deben definirse en otro lugar. El hecho de que aparezca `dodge` no lo crea: obliga a que exista una definición coherente del mismo identificador.

La instancia de Parnecio en el estado inicial del mismo archivo es distinta de su definición:

```json
{
  "id": "parnecio",
  "card": "parnecio",
  "location": "volcan",
  "status": {}
}
```

El identificador `card` apunta a la definición; `location` especifica dónde aparece el personaje y `status` expresa su estado inicial. Esta diferencia entre **definición** e **instancia** será esencial en las habilidades de la unidad 5.

## Reconocer el guion productivo

Abra `packages/tegularis_the_son_of_the_volcan/01_cartas_gisela_v15.package.json` y encuentre `manifest`, `cards`, `nodes`, `initial_state`, `traits` (cuando exista), y `dice_profiles`. Después abra `14_presentacion_semantica_v082d.package.json` e identifique qué añadió el diseño de presentación.

**Ejercicio guiado.** Localice el objeto `manifest` y explique `format_version`, `language`, `entry`; busque la carta `parnecio` y su instancia en `initial_state.characters`. Registre tres referencias cruzadas reales. No cambie identificadores todavía.

**Predicción.** Si una instancia alude a una carta inexistente, el paquete no debería ser admitido. Compruebe la predicción sobre una copia, nunca sobre el original; restaure el identificador al terminar.

**Validación.** Desde la raíz con dependencias disponibles, use la interfaz de admisión:

```bash
PYTHONPATH=. python -c "from pathlib import Path; from gisela.contracts.admit_package import admit_package_file; print(admit_package_file(Path('packages/tegularis_the_son_of_the_volcan/01_cartas_gisela_v15.package.json')).digest)"
```

La admisión no demuestra todavía que se haya ejecutado una habilidad. Para ejecución pública de una copia admitida use GLAUQUIR y sus acciones ofrecidas; no intente alterar el estado desde el cliente.

**Errores frecuentes.** Olvidar comillas; usar coma final en un objeto; cambiar un `id` sin actualizar sus referencias; confundir el texto visible con el identificador; creer que JSON por sí solo ejecuta instrucciones.

**Criterio de aprobación.** El alumno explica la separación autor/motor/cliente, identifica una definición y su instancia, localiza tres referencias, predice un rechazo semántico y sabe distinguir admisión de ejecución.

## Primer laboratorio ejecutable reducido (revisión pedagógica)

Antes de abrir Tegularis, complete [el laboratorio mínimo](../paquetes/01_fundamentos/README.md). Incluye paquetes de alrededor de 1,6 KB, dos rutas observables y un rechazo de referencia que el alumno puede provocar y corregir en una copia. El paquete completo de Tegularis pasa a ser **integración**, no primer contacto con JSON.
