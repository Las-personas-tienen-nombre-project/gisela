# Unidad 5: Cartas, habilidades y consecuencias

**Objetivo.** Traducir una intención de combate a una carta `kind: skill` del DSL 1.5, distinguir requisitos de operaciones y resultados condicionados, y comprobar un comportamiento real sin editar Python ni modificar el paquete productivo.

**Prerrequisitos:** unidades 1 a 4. **Conceptos nuevos:** carta de habilidad; `play.requires`; `play.effects`; `play.outcomes`; tirada, almacén temporal, comparación de ataque y evasión, costos, generación de TP y aplicación de daño; pruebas de admisión, predicción y ejecución.

**Fuente de referencia:** `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json`, cartas `slash`, `double_slash` y `blai`. Las variaciones están solo en copias completas de este paquete. Los archivos `soluciones/05_habilidades/` restituyen los valores productivos de referencia y **no son una simplificación del balance**.

## Primer paso obligatorio: laboratorio reducido

**Empiece por el [laboratorio de la Unidad 5](../paquetes/05_progresivo/README.md)**. Cree su copia en `mi_trabajo/`, prediga el resultado, modifíquela y ejecute esa copia. Solo después continúe con los fragmentos y ejercicios productivos de esta unidad. **Necesita dominar ahora:** la declaración que está modificando y su consecuencia; el resto de las estructuras de Tegularis solo debe reconocerlas hasta llegar a la integración. Consulte [cómo comprobar resultados](../COMO_COMPROBAR.md).

## Segundo paso: traslado a Tegularis

El material que sigue introduce gradualmente las declaraciones productivas. No se requiere comprender todos los campos del paquete antes de completar el laboratorio pequeño.

## 1. Cuatro preguntas antes de escribir una habilidad

1. **Intención:** ¿qué debería permitir hacer? Ejemplo: "Parnecio ataca con su espada y obtiene TP".
2. **Requisito:** ¿en qué estados puede realizarse? En `Slash`, Parnecio y Tegularis deben tener HP positivo; en `Blai`, además, TP >= 30.
3. **Procedimiento:** ¿qué se calcula cuando se usa? Las operaciones de `play.effects` pueden actualizar recursos, tirar dados y construir valores temporales de ataque, evasión y daño.
4. **Consecuencia:** ¿qué ocurre según la resolución? `play.outcomes` separa el acierto del fallo; en el acierto se modifica HP y se emite el mensaje correspondiente. Un dado tirado no demuestra todavía que hubo daño.

El objeto de carta contiene `id`, `kind: "skill"`, `title` y `play`. No se enseñará una sintaxis alternativa para luego traducirla. Los fragmentos de abajo son **fragmentos de las declaraciones reales**, no paquetes independientes: para ejecutar se requieren también fichas, variables, escena, reglas y demás secciones del paquete íntegro.

## 2. Slash: generar TP y resolver un golpe

El comienzo de `slash.play.effects` es:

```json
{
  "op": "set",
  "target": {"var": {"scope": "session", "key": "tp_parnecio"}},
  "value": {
    "math": {
      "op": "min",
      "left": {"literal": 50},
      "right": {
        "math": {
          "op": "add",
          "left": {"var": {"scope": "session", "key": "tp_parnecio"}},
          "right": {"literal": 10}
        }
      }
    }
  }
}
```

No es simplemente `add 10`: el `min` limita a 50. Si Parnecio tiene 45 TP, el resultado es 50; si tiene 20, es 30. El paquete no decide aquí el resultado del ataque. Las siguientes seis operaciones tiran dados de diez caras y suman atributos y `trait_total` a las variables `scratch_hit_parnecio` y `scratch_eva_parnecio`; después calculan `scratch_damage_parnecio`. El rasgo atacante usa `role: actor` y etiqueta `hit`, mientras que la defensa usa `role: defender` y `evasion`. Esto conecta directamente con la Unidad 4.

`slash.play.requires` exige `hp_parnecio > 0` y `hp_tegularis > 0`. La primera rama de `outcomes` compara `scratch_hit_parnecio > scratch_eva_parnecio`. Si se cumple, aplica daño con un límite inferior de cero y emite un mensaje; la otra rama usa `not` de esa misma comparación y emite el mensaje del fallo. **Un empate no es acierto**. No modifique solo una de las ramas: introduciría un hueco o una superposición de resultados.

## 3. Double Slash: costo y dos resoluciones independientes

En `double_slash.play.requires`, además de estar vivos Parnecio y Tegularis, se exige `tp_parnecio >= 10`. La primera operación descuenta 10 TP:

```json
{
  "op": "add",
  "target": {"var": {"scope": "session", "key": "tp_parnecio"}},
  "value": {"literal": -10}
}
```

Este número negativo es un costo; no confunda el signo con un efecto de daño. A continuación hay dos series diferenciadas: `double_hit_1`/`double_eva_1`/`double_dmg_1` y `double_hit_2`/`double_eva_2`/`double_dmg_2`. `play.outcomes` contiene cuatro ramas, una de acierto y otra de fallo para **cada** golpe. Por eso hay que observar los dos resultados en lugar de explicar la habilidad como "un ataque de doble daño". La existencia de dos series no garantiza dos aciertos.

## 4. Blai: umbral, consumo y potencia

`blai.play.requires` incluye `tp_parnecio >= 30`. La primera operación de `play.effects` descuenta 30 TP. El cálculo de daño usa tirada y Strength efectiva, `firesteel_parnecio`, `warcry_parnecio` y un término fijo **+8** antes de la mitigación. Al calcular la consecuencia, la rama de acierto incorpora las reducciones declaradas por el sistema, incluida la contribución pertinente de rasgos, y no permite que el daño efectivo sea negativo.

**Predicción importante:** "tener 30 TP" permite intentar `Blai`, pero no garantiza acertar ni producir un daño concreto. Si el umbral declarado fuese 20 y el costo continuara siendo 30, ambos números dejarían de expresar una misma política. Los ejercicios permiten encontrar ese error sin tocar los balances originales.

## 5. De la intención a la declaración y a la comprobación

| Paso | Pregunta del alumno | Sitio en la carta |
|---|---|---|
| Intención | ¿qué quiero producir? | Descripción de diseño, antes del JSON |
| Regla | ¿quién puede usarla y en qué estado? | `play.requires` |
| Declaración | ¿qué operaciones se calculan? | `play.effects` |
| Integración | ¿qué atributos y rasgos intervienen? | `stat`, `trait_total` |
| Predicción | ¿qué pasa si se acierta, falla o empata? | `play.outcomes` |
| Comprobación | ¿se admite y ejecuta? | GISELA / GLAUQUIR públicos |
| Variación | ¿qué cambia si edito un valor? | Copia del paquete, no original |

**Distinción adicional:** `emit_message` informa acerca de una consecuencia, pero no sustituye la operación que la produce; el HP no debe inferirse del texto del mensaje. La Unidad 8 estudiará cómo presentar los resultados sin recalcular reglas en GLAUQUIR.

## 6. Ejercicios guiados

Cada archivo de `ejercicios/05_habilidades/` es un paquete completo y admisible, excepto el sexto caso deliberadamente inválido. El alumno busca la propiedad indicada y reconstruye su valor. **Antes de corregir**, debe escribir la predicción y explicar por qué el valor del ejercicio altera el comportamiento. **Después**, valida, ejecuta y contrasta su JSON con el solucionario.

1. **`01_slash_tp`:** `Slash` tiene alterada la suma de TP: +0 en vez de +10. Restáurela y explique por qué el recurso no puede superar 50. Prediga los resultados desde 20 y 45 TP.
2. **`02_double_slash_costo`:** el descuento inicial de TP es 0. Restáurelo a -10 y explique por qué deben existir también el requisito de TP >= 10 y las dos series de tiradas.
3. **`03_blai_requisito`:** el requisito de TP se rebajó a 20, aunque el costo sigue en -30. Restituya 30; prediga disponibilidad con 20, 29 y 30 TP, manteniendo a los participantes vivos.
4. **`04_slash_acierto`:** se cambió a `gte` la comparación de ataque/evasión en **las dos ramas complementarias**. Restituya `gt` y explique quién gana el empate y por qué debe mantenerse la complementariedad de éxito y fallo.
5. **`05_blai_potencia`:** el término fijo de daño de `Blai` fue cambiado de +8 a 0. Restáurelo, localice los demás sumandos y explique la diferencia entre daño provisional y daño aplicado tras mitigación.
6. **`06_referencia_invalida`:** una condición de `Blai` apunta a `tp_inexistente`. Ejecute admisión y localice el error; corríjalo usando la clave pública existente `tp_parnecio`. No elimine el requisito para ocultar el fallo.

Los ejercicios 1 a 5 trabajan **una variable de diseño cada uno**; el sexto comprueba que una sintaxis JSON correcta puede incumplir el contrato semántico. El alumno no necesita escribir Python. El instructor dispone de una herramienta de comprobación adicional, separada de la autoría.

## 7. Recorrido autónomo

Sin consultar los solucionarios, reciba esta especificación: "Parnecio puede hacer Slash mientras ambos estén vivos; este ataque genera 10 TP hasta un máximo de 50 y determina separadamente acierto, fallo y daño. Double Slash requiere 10 TP, consume 10 y resuelve dos golpes. Blai requiere y consume 30 TP, con +8 fijo en el cálculo de daño". Con ayuda de la referencia DSL y una copia del paquete completo, identifique y corrija las cinco alteraciones. Entregue una matriz de: intención, campo alterado, valor corregido, predicción, admisión, observación. Explique cómo `dodge` o `escamas` podrían intervenir sin modificar el código del motor.

Este recorrido no equivale a escribir desde cero cada operación de combate del paquete completo: la reconstrucción acumulativa y la composición final de Tegularis continúan en la Unidad 7. Aquí se aprende a **leer, editar y razonar** cada mecanismo y a construir una habilidad con los mismos contratos públicos.

## 8. Validación y ejecución

Desde la raíz del repositorio, para un ejercicio corregido:

```bash
PYTHONPATH=. python -c "from pathlib import Path; from gisela.contracts.admit_package import admit_package_file; print(admit_package_file(Path('workshops/autoria_dsl_15/ejercicios/05_habilidades/01_slash_tp.package.json')).digest)"
```

Para una ronda automática de GLAUQUIR:

```bash
python -m gisela.cli.glauquir --auto --actuation --rounds 1 --package workshops/autoria_dsl_15/ejercicios/05_habilidades/01_slash_tp.package.json
```

El instructor puede ejecutar `PYTHONPATH=. python workshops/autoria_dsl_15/evaluacion/comprobar_unidad_05.py` para verificar admisión, rechazo y propiedades canónicas de los solucionarios. **La ronda automática demuestra funcionamiento general, no necesariamente que se haya utilizado la habilidad específica cuya propiedad cambió**. Para comprobar exhaustivamente una rama condicionada se necesitan situaciones dirigidas que la disparen; no confunda admisión ni una ejecución genérica con cobertura de todos los desenlaces.

## 9. Errores frecuentes y criterios de aprobación

**Errores comunes:** confundir `requires` con un costo; declarar costo sin requisito coherente; creer que `roll` aplica daño; alterar solo la rama de fallo; sumar TP sin límite; confundir `gt` y `gte`; usar una variable temporal inexistente; interpretar el valor provisional antes de reducciones como HP perdido; asumir que dos golpes implican dos impactos.

**Aprobación:** explica campo por campo al menos un `play` real; restaura los cinco mecanismos sin modificar el original; predice los casos límite TP 20/29/30 y empate; diferencia ataque, evasión, cálculo de daño y consecuencia confirmada; identifica y corrige la referencia inválida; admite y ejecuta su paquete mediante las herramientas públicas. La evaluación se basa en explicación de comportamiento y comprobación, no en copiar JSON sin comprenderlo.
