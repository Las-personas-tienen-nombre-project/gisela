# Unidad 3: Variables, condiciones y expresiones

**Objetivo.** Traducir una intención autoral en condiciones reales del DSL 1.5 y verificar qué mecanismo controla. La sintaxis procede de `gisela/contracts/v1_5/common.schema.json` y las declaraciones se extraen de `14_presentacion_semantica_v082d.package.json`; no se ha introducido un DSL pedagógico alternativo.

**Prerrequisito:** unidades 1 y 2. **Conceptos:** variable declarada, valor literal, referencia pública, comparación, conjunción, predicado, requisito de habilidad y política de acontecimiento.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 3](../paquetes/03_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. Datos, valores y referencias

El manifiesto declara variables de sesión mediante objetos que incluyen `scope`, `id`, `type` e `initial`. Por ejemplo, `hp_parnecio` es un entero de sesión inicializado a 158 en el paquete de referencia. Leerlo no equivale a escribir el número 158 directamente: el primero consulta el estado autoritativo que puede cambiar después de una acción, mientras que el segundo es un literal constante.

Fragmentos reales de **valor** (no son paquetes completos):

```json
{"var": {"scope": "session", "key": "hp_parnecio"}}
```

```json
{"literal": 0}
```

La clave de lectura `key` debe coincidir con una variable declarada. No debe asumirse que un identificador interno o un valor privado de GISELA sea legible por el autor. Los predicados consultan referencias admitidas por el contrato y por su validador semántico.

## 2. Primera intención: solo puede atacar un personaje vivo

**Regla:** la habilidad `slash` de Parnecio necesita que `hp_parnecio` sea mayor que cero. **Declaración válida**, fragmento de `cards[].play.requires`:

```json
{
  "compare": {
    "left": {"var": {"scope": "session", "key": "hp_parnecio"}},
    "op": "gt",
    "right": {"literal": 0}
  }
}
```

`compare` exige `left`, `op` y `right`; `gt` significa "mayor que". El contrato admite `eq`, `ne`, `lt`, `lte`, `gt` y `gte`. Una comparación devuelve una condición booleana, no modifica el HP. **Predicción:** si el HP es 0, no satisface el requisito; con HP positivo, esta condición particular sí se satisface. Eso no garantiza que la acción llegue a ejecutarse: también existen turno, disponibilidad, objetivos y demás restricciones.

## 3. Segunda intención: ambos contendientes deben seguir vivos

El paquete productivo utiliza la conjunción siguiente en `slash.play.requires`:

```json
{
  "all": [
    {"compare": {"left": {"var": {"scope": "session", "key": "hp_parnecio"}}, "op": "gt", "right": {"literal": 0}}},
    {"compare": {"left": {"var": {"scope": "session", "key": "hp_tegularis"}}, "op": "gt", "right": {"literal": 0}}}
  ]
}
```

`all` significa que **todas** deben ser verdaderas. `any` permite que alguna lo sea; `not` invierte una condición. El esquema exige al menos una entrada para `all` y `any`. No confundir `all` con "ejecutar ambas acciones": son condiciones, no operaciones. A diferencia del requisito sobre HP del actor, una condición sobre el adversario evita permitir `slash` contra un Tegularis ya derrotado.

## 4. Tercera intención: un acontecimiento al alcanzar un umbral

La política real `pride_of_the_volcan_son` se encuentra en `actuation.event_policies`. Su condición exige que Tegularis siga vivo y que diez veces su HP actual sea menor o igual que tres veces su HP máximo:

```json
{
  "all": [
    {"compare": {"left": {"var": {"scope": "session", "key": "hp_tegularis"}}, "op": "gt", "right": {"literal": 0}}},
    {"compare": {
      "left": {"math": {"op": "multiply", "left": {"var": {"scope": "session", "key": "hp_tegularis"}}, "right": {"literal": 10}}},
      "op": "lte",
      "right": {"math": {"op": "multiply", "left": {"var": {"scope": "session", "key": "max_hp_tegularis"}}, "right": {"literal": 3}}}
    }}
  ]
}
```

Esto expresa "HP positivo y HP actual como máximo al 30 % del máximo", sin redondeo porcentual intermedio. **Importante:** el predicado solo establece el umbral; el momento y la frecuencia del acontecimiento dependen también de la política y del motor. No cambie sus efectos ni su balance.

## 5. Tabla de verdad para predecir antes de ejecutar

| HP Parnecio | HP Tegularis | Parnecio vivo | Ambos vivos |
|---:|---:|---|---|
| 158 | 500 | verdadero | verdadero |
| 0 | 500 | falso | falso |
| 158 | 0 | verdadero | falso |
| 0 | 0 | falso | falso |

Ejemplo del umbral de Pride con HP máximo de 100 **solo para hacer el cálculo mental** (no cambia los datos de Tegularis): 31 no cumple; 30 cumple; 0 no cumple por la primera comparación.

## 6. Taller guiado: paquetes completos

1. **Condición simple** (`ejercicios/03_condiciones/01_condicion_simple.package.json`): sustituya `cards[id=slash].play.requires = {"constant": true}` por la comparación que exige `hp_parnecio > 0`. Prediga el comportamiento en HP 0 y HP positivo; admita y ejecute. Compare con la solución homónima.
2. **Condición compuesta** (`02_condicion_compuesta.package.json`): partiendo del requisito sobre Parnecio, agregue mediante `all` el requisito `hp_tegularis > 0`. Explique por qué `any` sería incorrecto. Admita y ejecute.
3. **Umbral de Pride** (`03_umbral_pride.package.json`): restaure **solo** `actuation.event_policies[id=pride_of_the_volcan_son].when`, que empieza como `{"constant": false}`, utilizando la condición productiva explicada arriba. No altere `effects`, `phase` ni otras reglas. Admita y ejecute.
4. **Error deliberado** (`04_referencia_invalida.package.json`): la condición de Slash consulta `clave_privada_inexistente`, que no está declarada. Registre el rechazo semántico; corrija la referencia a una variable pública real. No basta con que el JSON se analice.

Los ejercicios de entrada 1 a 3 **son variantes válidas de práctica**, pero los valores originales están conservados en sus **solucionarios**. No sustituya el paquete productivo por los ejercicios.

### Comandos de autor

Desde la raíz del repositorio, para cada paquete corregido:

```bash
PYTHONPATH=. python -c "from pathlib import Path; from gisela.contracts.admit_package import admit_package_file; print(admit_package_file(Path('workshops/autoria_dsl_15/ejercicios/03_condiciones/01_condicion_simple.package.json')).digest)"
python -m gisela.cli.glauquir --auto --package workshops/autoria_dsl_15/ejercicios/03_condiciones/01_condicion_simple.package.json
```

La **admisión** verifica contratos y referencias; la **ejecución** comprueba que el paquete puede iniciarse y avanzar. Ninguna de las dos, por sí sola, demuestra la rama de HP cero o el disparo de Pride. Para demostrarlo hacen falta escenarios de estado y trazas de acciones con los umbrales correspondientes.

## 7. Recorrido autónomo

Sin consultar las soluciones: describa la intención de `slash.play.requires`, reconstruya su condición compuesta real; explique cómo se lee `hp_tegularis`, qué diferencia hay entre `literal` y `var`, por qué el umbral de Pride usa multiplicación cruzada y cuál es el papel de `when` en una política. Entregue JSON corregido, predicciones, comprobaciones y un ejemplo de referencia rechazada.

## 8. Errores frecuentes y criterios de aprobación

**Errores:** usar `>` en lugar de `gt`; escribir `{"var":"hp_parnecio"}` en vez de `{"var":{"scope":"session","key":"hp_parnecio"}}`; mezclar `all` y `any`; referir a una variable ausente; emplear texto "0" donde se requiere un número; confundir comparar con asignar; inferir ejecución únicamente a partir de la admisión.

**Aprobación:** el alumno (a) interpreta las referencias, (b) construye las comparaciones reales, (c) explica `all`, `any` y `not`, (d) identifica cuándo una habilidad tiene requisitos, (e) reconstruye el umbral productivo sin rebalancearlo, (f) diagnostica una referencia inválida y (g) distingue predicción de comportamiento de prueba de comportamiento.
