# Unidad 8: Presentación declarativa: mostrar sin decidir

**Objetivo:** construir dos o más presentaciones de una misma batalla de Tegularis, interpretar sus tablas y acontecimientos y demostrar que ninguna modifica las reglas, el azar ni el estado lógico.

**Prerrequisitos:** unidades 1 a 7, lectura de objetos y listas JSON, habilidades y estados, Observe/Act, acontecimientos confirmados.

**Conceptos nuevos:** región, vista, fuente pública, tabla, columna, transformación, selector de acontecimientos, límite de historial, agrupación causal, plantilla restringida, rol semántico, equivalencia de ejecución.

**Referencia verificada:** `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`. Contratos: `gisela/contracts/v1_5/package.schema.json`, `gisela/contracts/presentation_views_validation.py`, `gisela/contracts/presentation_templates_validation.py`. Consulte el [taller de presentación](../../../docs/guides/workshops/WORKSHOP_PRESENTACION_V082.md) y la [arquitectura actual](../../../docs/architecture/PRESENTACION_DECLARATIVA_V082.md).

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 8](../paquetes/08_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. La responsabilidad de cada pieza

El **autor** declara qué datos públicos desea mostrar y cómo nombrarlos; **GISELA** conserva y ejecuta el estado autoritativo y publica acontecimientos; **GLAUQUIR** representa las regiones y ofrece únicamente las acciones autorizadas en Observe, remitiendo las decisiones mediante Act. Un rótulo como "Daño recibido" no demuestra daño: la clasificación tiene que estar respaldada por la semántica de todos los acontecimientos seleccionados.

Una presentación no es una habilidad ni un efecto. Cambiar `presentation` no debe modificar `manifest`, `cards`, `traits`, `initial_state`, `actuation`, el orden de turnos ni el RNG. Observe puede exponer proyecciones visuales distintas; para comprobar equivalencia hay que comparar el estado lógico y las mismas acciones, no esperar igualdad textual de pantallas.

## 2. Anatomía de un paquete real

Fragmento de la presentación productiva:

```json
{
  "id": "tegularis_semantica_v082d",
  "regions": [
    {"id":"tabla","component":"table","label":"Estado publicado","view":"estado"},
    {"id":"hechos","component":"event_log","label":"Acontecimientos seleccionados","view":"hechos"},
    {"id":"acciones","component":"choice_list","label":"Acciones autorizadas","source":"actions"}
  ]
}
```

La región indica **dónde** se presenta información; `view` enlaza con una definición en `presentation.views`. La región `choice_list` toma las acciones públicas, no crea nuevas facultades de combate. En el paquete hay también `action_targets`: son parámetros de presentación para decisiones admitidas, no un mecanismo para saltarse las reglas de Act.

## 3. Tablas: columnas y fuentes públicas

La vista productiva `estado` declara `component: "table"`, `source: "actuation.resources"`, `transform: "pivot_resources"` y columnas `entity`, `hp`, `mp`, `tp`. Su operación es representar recursos ya publicados. Un encabezado como `SALUD` no cambia HP. La transformación `pivot_resources` exige exactamente esa fuente.

Fragmento de vista válido, **adicional** y comprobado en el ejercicio 7:

```json
{
  "id": "efectos_publicos",
  "component": "table",
  "source": "actuation.effects",
  "columns": [
    {"id":"id","label":"EFECTO"},
    {"id":"beneficiary","label":"DESTINATARIO"},
    {"id":"remaining","label":"TURNOS","align":"right"}
  ]
}
```

El autor debe crear además una región con `component: "table"` y `view: "efectos_publicos"`. Los campos aceptados dependen de la fuente: `actuation.effects` admite `id`, `beneficiary`, `remaining`; `actuation.participants` admite `id`; `actors` admite `id`, `name`, `color`. En las columnas, el contrato permite `align: "left"` o `"right"`, **no** `"center"`. Una tabla no debe consultar variables privadas directamente.

## 4. Acontecimientos: seleccionar no equivale a interpretar

La vista `hechos` usa `component: "event_log"` con `source: "actuation.causal"` y una lista de `kinds`, entre ellos `skill_started`, `contest_resolved`, `dice_roll`, `variable_changed`, `author_message`, `skill_played`. Su `limit: 40` es el máximo configurado en este caso y no equivale a historial completo. Observe mantiene su propia ventana pública acotada.

`group_by: "action"` agrupa únicamente por la identidad causal pública de una ejecución y su comienzo visible en la ventana. Sin esa propiedad los mismos acontecimientos se muestran planos. **Nunca agrupe por proximidad temporal ni infiera que dos registros consecutivos pertenecen a un solo ataque.**

## 5. Plantillas restringidas y categorías semánticas

Ejemplo real de `presentation.views[].event_formats`:

```json
{"kind":"skill_started","role":"neutral","template":"{actor} ejecuta {card}"}
```

Cada clase tiene campos permitidos: `skill_started` admite `actor`, `card`, `origin`; `dice_roll` admite `sides`, `result`, `store`; `variable_changed` admite `variable`, `before`, `after`; `author_message` admite `text`. Una expresión como `{actor.password}`, índices, conversiones o formatos ejecutables **no** son permitidos. Para una llave literal se escribe `{{` o `}}`.

Los roles admitidos son `neutral`, `damage`, `healing`, `buff` y `debuff`. La selección de `damage` **no** demuestra que una reducción numérica de HP represente daño: solamente úselo si todos los registros que satisfacen el selector cuentan con ese significado confirmado. Cuando no exista garantía, elija `neutral`. Los formatos con `missing: "omit"` o `"placeholder"` expresan un comportamiento de sustitución permitido; los espacios privados siguen vedados.

## 6. Recorrido guiado: modificar la presentación sin tocar el combate

Cada archivo en `ejercicios/08_presentacion/` es un paquete **completo y admisible** salvo el octavo, que ilustra un rechazo. Empiece por localizar `presentation` y compare con la versión productiva. Las siete variantes están intencionalmente presentadas con un aspecto distinto; **no se trata de restauraciones obligatorias del balance**. Las copias idénticas al canon de `soluciones/08_presentacion/` permiten comparar o restablecer la presentación original.

| Ejercicio | Variación que debe explicar | Predicción verificable |
|---|---|---|
| `01_regiones` | Cambia el rótulo de la región de hechos | cambia el encabezado, no el motor |
| `02_columnas` | Cambia rótulos y alineación | se mantienen los recursos y sus valores |
| `03_acontecimientos` | Muestra inicio y fin de habilidad, límite 12 | selección visual más estrecha; no elimina los eventos del motor |
| `04_causalidad` | Quita la agrupación `action` | crónica plana con las mismas reglas |
| `05_plantillas` | Reescribe el comienzo de habilidad | cambia el texto, no la ejecución |
| `06_semantica` | Reformula cambios de recursos con rol neutral | no se atribuye daño sin prueba |
| `07_otra_vista` | Agrega tabla de estados activos | muestra `actuation.effects` sin alterar efectos |
| `08_error_plantilla` | Intenta usar `{actor.password}` | rechazo del contrato público |

Para cada ejercicio: **(1)** enuncie qué quiere comunicar el autor, **(2)** localice la vista o región, **(3)** identifique y explique el campo cambiado, **(4)** prediga qué aparecerá en pantalla, **(5)** compruebe admisión y sesión, **(6)** compare estado y decisiones autorizadas, **(7)** proponga otra modificación válida. No acepte como explicación "cambié el JSON".

Comprobación individual, desde la raíz del repositorio:

```bash
PYTHONPATH=. python -c 'from gisela.contracts.admit_package import admit_package_file; admit_package_file("workshops/autoria_dsl_15/ejercicios/08_presentacion/07_otra_vista.package.json"); print("Admitido")'
```

Comprobación automatizada del instructor, también desde la raíz:

```bash
PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_unidad_08.py
```

Este programa compara los siete paquetes con el canon, rechaza una plantilla no pública y contrasta varias sesiones con dos semillas; **no es código que el alumno tenga que escribir**. Sus resultados se documentan en `evaluacion/RESULTADOS_UNIDAD_08.md`.

## 7. Recorrido autónomo

Sin mirar el solucionario, prepare a partir de la variante canónica dos presentaciones admisibles: **control de recursos** (tabla HP/MP/TP más efectos activos) y **crónica de acontecimientos** (hechos con identidad causal pública y plantillas neutrales). Mantenga visible el acceso a acciones autorizadas, compruebe que ambas admiten el paquete y ejecute la misma secuencia de decisiones con la misma semilla. Documente por qué los cambios de presentación no pueden generar un resultado bélico distinto.

Entregue los dos paquetes, una descripción de las modificaciones dentro de `presentation`, un ejemplo de registro causal interpretado sin inventar daño, una comparación de estados lógicos y el registro de validación. Si se limita a mostrar capturas o a copiar el JSON, no demuestra independencia autoral.

## 8. Errores frecuentes

1. Confundir `presentation.regions` con las definiciones en `presentation.views`.
2. Usar `align: "center"`, aunque el esquema solo permite `left` o `right`.
3. Confundir el título de una columna con una variable ejecutable.
4. Usar un campo no público como `actor.password` dentro de una plantilla.
5. Interpretar `group_by: "action"` como agrupación por simple proximidad de acontecimientos.
6. Etiquetar `variable_changed` como daño sin semántica confirmada.
7. Afirmar que la admisión de JSON demuestra equivalencia de estados; necesita ejecución con la misma semilla y las mismas decisiones.

## 9. Criterios de aprobación

El alumno aprueba cuando identifica las responsabilidades de autor/motor/presentación, construye y valida dos vistas públicas, explica la diferencia entre tablas y hechos, utiliza correctamente causalidad y plantillas restringidas, interpreta un rechazo de plantilla, y demuestra mediante observaciones y estado lógico que sus modificaciones no alteraron las reglas ni el desenlace. No basta con recuperar los rótulos canónicos del solucionario.

**Límite de las pruebas aportadas:** dos semillas, tres pasos por sesión y una restauración; no cubren todos los desenlaces, combinaciones de efectos ni la totalidad de la batalla.
