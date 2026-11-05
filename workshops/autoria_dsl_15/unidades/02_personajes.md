# Unidad 2: Personajes, S.O.F.I.A. y estado inicial

**Objetivo.** Construir y comprobar las fichas de los cinco participantes sin confundir lo que el autor **define** con lo que el motor **instancia** y modifica. El alumno no necesita programar.

**Prerrequisito:** Unidad 1; reconocer cadenas, números, listas, objetos y referencias de JSON.

**Conceptos nuevos:** carta de personaje, S.O.F.I.A., referencia `card`, instancia, ubicación, `status`, rasgos asignados, recursos iniciales y valores calculados.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 2](../paquetes/02_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. De la intención a la declaración

**Intención.** Queremos presentar al caballero Parnecio Esparcales como personaje participante de la batalla.

**Regla.** Su identidad y atributos son datos persistentes de la definición. Debe existir una instancia que utilice la carta en una ubicación declarada; cambiar el rótulo visible no cambia su identificador.

**Declaración real**, extraída de `01_cartas_gisela_v15.package.json` (fragmento, no paquete autónomo):

```json
{
  "id": "parnecio",
  "kind": "character",
  "title": {"text": "Parnecio Esparcales"},
  "sofia": {"strength": 8, "openness": 5, "fortune": 6, "intelligence": 4, "awareness": 6},
  "traits": ["dodge"]
}
```

`id` es la clave estable para las referencias; `kind` indica que es un personaje; `title.text` es el rótulo que verá el lector. `sofia` contiene las cinco dimensiones S.O.F.I.A.: `strength` (fuerza), `openness` (apertura), `fortune` (fortuna), `intelligence` (inteligencia), `awareness` (percepción). Su escala está declarada en `manifest.sofia_scale`, con mínimo 0 y máximo 20 para este paquete. `traits` **asigna** rasgos definidos en la sección global `traits`: incluir `dodge` no crea su comportamiento; eso se estudiará en la Unidad 4.

**Integración.** Esta es su **instancia inicial** real, en `initial_state.characters`:

```json
{"id": "parnecio", "card": "parnecio", "location": "volcan", "status": {}}
```

Aquí `id` identifica esta instancia, `card` remite a la carta, `location` remite al lugar definido y `status` es un objeto de estado inicial. La carta responde **qué es el personaje**; la instancia **quién está presente y dónde**. No se duplican los atributos S.O.F.I.A. en la instancia.

## 2. Los cinco participantes de esta práctica

| ID | Nombre visible | Fuerza | Apertura | Fortuna | Inteligencia | Percepción | Rasgos asignados |
|---|---|---:|---:|---:|---:|---:|---|
| `parnecio` | Parnecio Esparcales | 8 | 5 | 6 | 4 | 6 | `dodge` |
| `gillius` | Gillius Cabezadeencina | 10 | 4 | 5 | 4 | 5 | `dodge` |
| `clarisa` | Clarisa de la Hojarasca | 4 | 7 | 9 | 7 | 7 | `magic_redux` |
| `iosepus` | Iosepus Knechti | 4 | 5 | 6 | 9 | 8 | `magic_redux` |
| `tegularis` | Tegularis, el Hijo del Volcán | 15 | 7 | 5 | 9 | 7 | `enorme`, `escamas` |

Los valores son los de **`01_cartas_gisela_v15`**; no deben mezclarse con variantes posteriores. Por ejemplo, en `14_presentacion_semantica_v082d`, Gillius presenta `awareness: 6`, no 5. La práctica conserva el valor de su propio paquete de referencia.

## 3. Estado y recursos: dónde NO poner los datos

En este paquete, `initial_state.characters` reúne las cinco instancias en `volcan`, todas con `status: {}`. La propiedad `initial_state.player_character` designa `parnecio`. `initial_state.capacities` contiene límites de `hand` y `reserve` por personaje; `initial_state.skills` mantiene instancias de habilidades con `id`, `card`, `character` y `zone`. `initial_state.session_variables` inicializa las variables declaradas en `manifest.variables`, por ejemplo `tp_parnecio: 0`.

**No confundir:** una capacidad de mano no es HP; el `status` vacío no significa que todos los recursos sean cero; una propiedad inicial no es el valor final tras ejecutar acciones. El motor determina el estado autoritativo al ejecutar; las variantes posteriores de actuación inicializan recursos mediante reglas de `actuation.setup`. No invente `hp` o `mp` dentro de la carta para corregir una salida observada: consulte primero el contrato y la declaración productiva.

## 4. Taller guiado: intención, predicción y comprobación

Todos los archivos del ejercicio son **paquetes íntegros de práctica**; sus datos ajenos al ejercicio se conservan para satisfacer las referencias originales. Trabaje **únicamente** en las copias de `ejercicios/02_personajes/`, nunca sobre `packages/tegularis_the_son_of_the_volcan/`.

1. **Identidad pública:** abra `01_identidad.package.json`. La carta `parnecio` tiene el título provisional "Caballero sin nombre". Cambie **solo** `title.text` por `Parnecio Esparcales`. **Prediga:** la identidad interna sigue siendo `parnecio`; no se modifican las referencias ni los resultados lógicos. Compare con `soluciones/02_personajes/01_identidad.package.json`.
2. **Atributo de ficha:** abra `02_sofia.package.json`. En la carta `gillius`, cambie `sofia.awareness` de 4 a **5**. **Prediga:** se modifica un valor de la ficha que una futura resolución podría consultar; no se garantiza por ello un resultado determinado de una tirada. Compruebe la admisión y la coincidencia con el original de práctica.
3. **Asignación de rasgo:** abra `03_rasgo.package.json`. En la carta `parnecio`, agregue `"dodge"` a la lista vacía `traits`. **Prediga:** la ficha vuelve a portar el rasgo; su bonificación no se aplica automáticamente a cualquier operación, sino solamente bajo los contextos declarados en el rasgo.
4. **Error controlado:** `04_referencia_invalida.package.json` contiene una instancia de Parnecio cuya propiedad `card` menciona `caballero_inexistente`. Intente admitirla; anote el mensaje del validador. Después corrija la referencia a `parnecio` y vuelva a admitir. No interprete el rechazo como fallo de formato JSON.

Los tres ejercicios válidos empiezan como variantes pedagógicas, **no constituyen un rebalanceo** de Tegularis. Las soluciones restituyen los datos exactos de la práctica inicial y conservan sus identificadores de manifiesto propios del workshop.

## 5. Comprobar de forma pública

Desde la raíz del repositorio:

```bash
PYTHONPATH=. python -c "from pathlib import Path; from gisela.contracts.admit_package import admit_package_file; print(admit_package_file(Path('workshops/autoria_dsl_15/ejercicios/02_personajes/01_identidad.package.json')).digest)"
python -m gisela.cli.glauquir --auto --package workshops/autoria_dsl_15/ejercicios/02_personajes/01_identidad.package.json
```

Repita para los otros archivos tras completarlos; para el cuarto, el rechazo inicial es **esperado**. Para ejercicios 2 y 3, puede ejecutar igualmente GLAUQUIR en modo automático. Que la ejecución termine sin error **no demuestra por sí sola** que un rasgo haya aportado a una tirada: esa comprobación requiere un concurso observable, objeto de la Unidad 4.

**Diagnóstico frecuente:** cambio de `id` sin actualización de `card`; escritura de atributos en `initial_state.characters`; rasgo referido sin definición; errata en nombres de propiedades; un número entre comillas donde se espera un número.

**Criterios de aprobación:** (a) identifica las cinco fichas y sus cinco instancias, (b) distingue `id`/`title.text` y carta/instancia, (c) explica para qué sirve S.O.F.I.A. sin atribuirle fórmulas no observadas, (d) restaura los tres ejemplos sin cambiar reglas originales, (e) detecta y corrige la referencia rota, (f) distingue admisión, ejecución y comprobación de efectos.

## 6. Recorrido autónomo

Sin consultar los solucionarios, use el paquete `01_cartas_gisela_v15` y esta especificación: la instancia del personaje controlado debe llamarse `parnecio`, usar la carta de Parnecio, comenzar en `volcan`, mostrar "Parnecio Esparcales", portar `dodge` y tener S.O.F.I.A. 8/5/6/4/6; Gillius debe mostrar 10/4/5/4/5 y portar `dodge`; Clarisa e Iosepus deben portar `magic_redux`; Tegularis debe portar `enorme` y `escamas`. Compruebe referencias y admisión. Justifique por qué el texto visible puede variar sin romper el identificador de carta, y por qué el efecto de los rasgos no puede deducirse exclusivamente de esta tabla.

**Cierre:** entregue los JSON corregidos, un registro de predicciones y el resultado de cada admisión; no basta con copiar una solución.
