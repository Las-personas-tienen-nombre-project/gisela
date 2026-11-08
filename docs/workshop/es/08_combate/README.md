# Taller 08. Un encuentro por turnos con resistencia

Lara sorprende a un intruso que intenta sabotear el reflector del faro. En lugar de representar heridas, este encuentro utiliza **resistencia**: cuando alguien llega a cero, no puede continuar la confrontación. Lara intenta detener al intruso; él trata de escapar.

Este taller utiliza el **laboratorio de actuación** de GISELA. No es una pantalla de combate integrada al recorrido narrativo habitual: GLAUQUIR ejecuta el reloj autoral con `--actuation`. El ejemplo utiliza solamente DSL 1.5, sin generadores Python.

## Antes de comenzar

Completa el [taller 07](../07_habilidades_pasivas/README.md). Abre [`combate.package.json`](combate.package.json) con un editor de texto y guarda una copia antes de modificarlo. Ejecuta los comandos desde la raíz del repositorio.

## 1. Ejecuta el encuentro

En Linux:

```bash
glauquir --package docs/workshop/es/08_combate/combate.package.json --actuation --rounds 12 --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/08_combate/combate.package.json --actuation --rounds 12 --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

Cuando llegue el turno de Lara, elige **Interceptar al intruso**. Los turnos del intruso se ejecutan automáticamente. En este recorrido, Lara consigue detenerlo. La opción **Pasar** permite gastar la oportunidad sin utilizar una habilidad.

Para observar una derrota reproducible, cambia la semilla por 64 letras `d`. Mantén el resto del comando igual y elige siempre **Interceptar al intruso**. La semilla fija permite repetir exactamente las mismas tiradas e iniciativa. El límite `--rounds 12` es una protección para el laboratorio; no significa que el encuentro deba durar doce rondas.

## 2. Define el encuentro y sus turnos

En `actuation`, `participants` enumera a `lara` y `intruso`. El reloj calcula la iniciativa con sus atributos y un dado de seis caras (`initiative_die: 6`). `base_actions: 1` concede una oportunidad por turno a cada participante.

Lara utiliza una habilidad que el lector escoge. El intruso tiene una candidata en `candidates`, por lo que GISELA la ejecuta mediante su política de actor no jugador. No hay una inteligencia táctica general: el autor declara qué acción intentará.

## 3. Declara la resistencia

El apartado `manifest.variables` registra cuatro variables enteras: `resistencia_lara`, `resistencia_intruso`, `tirada_lara` y `tirada_intruso`. Sus valores iniciales aparecen también en `initial_state.session_variables`.

Las dos resistencias comienzan en **3**. Las tiradas comienzan en **0** y se actualizan al ejecutar las habilidades. `actuation.setup` vuelve a fijar las resistencias en 3 al comenzar el encuentro. Resistencia es un nombre elegido por el autor, no un recurso especializado del motor.

## 4. Resuelve una acción

La ficha `interceptar` incluye `play.effects` para tirar un dado de seis caras y guardar el resultado en `tirada_lara`. Después, `play.outcomes` evalúa esa tirada:

- Con un resultado de **3 a 6**, el intento acierta y la resistencia del intruso disminuye en uno.
- Con un resultado de **1 o 2**, el intento falla y ninguna resistencia cambia.

La ficha `forcejear` aplica la misma regla contra Lara. Los efectos `set` y las expresiones `math` actualizan las variables; `emit_message` comunica el resultado. La política `return_policy: hand` permite utilizar la habilidad nuevamente durante otra oportunidad.

## 5. Termina el encuentro

En `actuation.event_policies` se declaran los avisos de victoria y derrota. En `actuation.outcome_policies`, dos condiciones verifican si alguna resistencia llegó a cero:

- `lara_detiene_intruso`: la resistencia del intruso es cero.
- `intruso_escapa`: la resistencia de Lara es cero.

Estas políticas hacen que el **reloj de actuación termine**. No activan por sí solas un nodo narrativo ni un final de historia. En la implementación actual, la evaluación de `outcome_policies` se realiza dentro de la resolución de políticas de eventos; por eso este paquete declara ambas secciones expresamente.

## 6. Ejercicios

Primero cambia el texto de una de las habilidades y comprueba que la iniciativa y las reglas siguen siendo las mismas. Después cambia ambas resistencias iniciales a **4**, tanto en `initial_state.session_variables` como en `actuation.setup`, y ejecuta un encuentro nuevo. Por último, modifica el umbral de acierto de **3** a **4** en las condiciones `gte` y `lt` de ambas habilidades; comprueba que ahora acertar es más difícil.

Modifica un aspecto cada vez y restaura el paquete original antes de continuar con el siguiente ejercicio.

## 7. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/08_combate/combate.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/08_combate/combate.package.json
```

La admisión confirma la estructura y las referencias. Para verificar las consecuencias, debes ejecutar el encuentro, porque la validación no prueba todas las tiradas ni todos los desenlaces.

## Qué aprendiste

Un encuentro por turnos puede construirse con el reloj de actuación, dos habilidades, variables de sesión, tiradas, condiciones y políticas de cierre. GISELA no define puntos de vida ni daño de forma universal: el autor decide qué significa perder resistencia y cuándo termina una confrontación. Puedes consultar la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md) para conocer el resto de las operaciones.
