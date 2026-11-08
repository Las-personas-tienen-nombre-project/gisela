# Taller 05. Objetos y pertenencias

En este taller volverás al faro con Lara y Elio. Aprenderás a declarar un objeto, indicar quién lo tiene y trasladarlo de un personaje a otro. La linterna permitirá subir una escalera oscura; sin ella, Lara deberá esperar.

## Antes de comenzar

Completa el [taller 04](../04_dialogos_decisiones/README.md). Trabajaremos con [`objetos.package.json`](objetos.package.json). Guarda una copia antes de modificarlo y ejecuta los comandos desde la raíz del repositorio.

## 1. Juega los dos recorridos

En Linux, con el entorno virtual activado:

```bash
glauquir --package docs/workshop/es/05_objetos_equipo/objetos.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/05_objetos_equipo/objetos.package.json
```

Primero elige «Pedirle la linterna a Elio». Después reinicia la historia y elige «Subir sin la linterna». Comprueba que llegan a la misma escalera, pero terminan de manera diferente.

## 2. Declara un objeto

En `cards` encontrarás la ficha de la linterna:

```json
{
  "id": "linterna",
  "kind": "object",
  "title": {"text": "Linterna de emergencia"},
  "description": {"text": "Una linterna que funciona con baterías."},
  "portable": true
}
```

La ficha describe **qué tipo de objeto es**. `portable: true` declara que puede transportarse. Su título sirve para presentar el objeto; el identificador `linterna` permite referirse a la ficha desde el estado inicial.

En `initial_state.objects` encontrarás una instancia concreta:

```json
{
  "id": "linterna_01",
  "card": "linterna",
  "owner": "elio"
}
```

Esta instancia representa **la linterna que existe en el mundo**. Al comienzo, Elio la tiene. `linterna_01` es el identificador que utilizarán las operaciones de la historia. La ficha y la instancia no son lo mismo.

## 3. Entrega la linterna

La opción `pedir` contiene este efecto:

```json
{
  "op": "transfer",
  "object": "linterna_01",
  "from": "elio",
  "to": "lara"
}
```

`transfer` cambia la pertenencia del objeto desde Elio hacia Lara. El efecto se ejecuta al escoger esa opción; no basta con narrar que Lara recibió la linterna. La opción también utiliza `enabled_if` con `owns` para comprobar que Elio tiene el objeto antes de ofrecer la entrega.

## 4. Comprueba quién tiene el objeto

En el nodo `escalera` hay una condición:

```json
{
  "id": "comprobar_linterna",
  "op": "condition",
  "test": {
    "owns": {
      "owner": "lara",
      "object": "linterna_01"
    }
  },
  "then": {"node": "con_luz"},
  "else": {"node": "sin_luz"}
}
```

La historia comprueba la **pertenencia real** de la linterna, no el texto de la elección anterior. Si Lara la tiene, puede subir con luz. Si sigue en poder de Elio, espera. Aquí `owns` comprueba la pertenencia; no ejecuta ninguna transferencia.

## 5. Ejercicios

Primero cambia el título y la descripción de la linterna, sin modificar los identificadores. Ejecuta los dos recorridos y verifica que siguen funcionando.

Después cambia la pertenencia inicial de la linterna: en `initial_state.objects`, reemplaza `"owner": "elio"` por `"owner": "lara"`. Prueba ambas elecciones. La opción de pedir la linterna ya no debería estar habilitada, pues Elio no la tiene; Lara podrá subir con luz porque la linterna ya le pertenece. Restaura el archivo para repetir el ejercicio original.

Por último cambia solo la narración del desenlace `con_luz`, sin tocar la condición. Comprueba que el resultado técnico sigue siendo el mismo aunque cambie el texto.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/05_objetos_equipo/objetos.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/05_objetos_equipo/objetos.package.json
```

La validación revisa la estructura y las referencias. Recorre las dos alternativas en GLAUQUIR para comprobar también sus consecuencias.

## Qué aprendiste

`cards` define los tipos de objetos; `initial_state.objects` contiene sus instancias. `transfer` cambia quién tiene un objeto y `owns` permite comprobarlo. Este taller trata **pertenencia y transferencia**, no un sistema de ranuras de equipo, ropa equipada o estadísticas de equipamiento. Para conocer los campos admitidos, consulta la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).

---

[Volver al índice del curso](../README.md) · [Siguiente taller](../06_habilidades_activas/README.md)
