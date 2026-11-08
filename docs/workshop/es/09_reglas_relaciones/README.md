# Taller 09. Relaciones y reglas automáticas

Una tormenta amenaza el faro. Lara debe decidir si ayuda a Elio a asegurar la lámpara o si sube sola a revisar la señal. La decisión modifica la confianza entre los personajes y una regla automática determina si pueden colaborar más adelante.

Este taller utiliza el flujo narrativo normal de GLAUQUIR. No requiere el laboratorio de actuación del taller anterior ni un generador Python.

## Antes de comenzar

Completa el [taller 08](../08_combate/README.md) y abre [`reglas.package.json`](reglas.package.json) con un editor de texto. Ejecuta los comandos desde la raíz del repositorio.

## 1. Ejecuta la historia

En Linux:

```bash
glauquir --package docs/workshop/es/09_reglas_relaciones/reglas.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\glauquir.exe --package docs/workshop/es/09_reglas_relaciones/reglas.package.json
```

Prueba las dos alternativas. Cuando Lara ayuda, ambos mantienen encendida la señal. Cuando decide trabajar sola, no consiguen coordinarse a tiempo.

## 2. Declara una relación

En `manifest.relationship_fields` aparece `confianza`, un valor entero que comienza en cero. No es un atributo universal del motor: el autor elige su nombre y su significado. La relación distingue la dirección `from: lara` y `to: elio`; no debes suponer que la confianza de Elio hacia Lara cambia automáticamente.

En la primera opción, el efecto `add` suma 2 a esa relación. La segunda resta 1. Ninguno de los dos efectos contiene directamente el final de la historia.

## 3. Crea una reacción automática

La regla `confianza_ganada` escucha el evento `state_changed` de la relación. Su condición `when` verifica que la confianza haya llegado al menos a 2 y que todavía no exista el hecho `apoyo_mutuo`. Si se cumplen ambas condiciones, el efecto `record_fact` registra ese hecho.

La regla no es una conversación ni un paso del relato. Se activa como consecuencia del cambio de estado. La comprobación del hecho evita volver a registrarlo una vez concedido.

## 4. Usa esa consecuencia

En el nodo `despues`, la operación `condition` consulta `has_fact: apoyo_mutuo`. Si existe, Lara y Elio mantienen la señal; de lo contrario, deben esperar a que pase la tormenta.

Esto permite separar tres decisiones del autor: qué cambia una elección, cuándo se dispara una reacción y cómo influye después en la narración.

## 5. Ejercicios

Primero cambia el texto de ambas opciones y comprueba que los resultados no cambian. Después modifica el incremento de confianza de 2 a 1: la regla ya no debería registrar `apoyo_mutuo` y ambos caminos terminarán sin señal. Por último, restaura el incremento a 2 y cambia el umbral `gte` de 2 a 3 para observar el mismo efecto desde la condición de la regla.

Modifica un valor cada vez y conserva una copia del archivo original.

## 6. Valida el paquete

En Linux:

```bash
gisela validate docs/workshop/es/09_reglas_relaciones/reglas.package.json
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\gisela.exe validate docs/workshop/es/09_reglas_relaciones/reglas.package.json
```

La admisión comprueba el contrato; para comprobar las consecuencias debes ejecutar ambas elecciones.

## Qué aprendiste

Una relación puede cambiar por una decisión y provocar una regla automática. La regla registra un hecho que el relato consulta más adelante. Para más detalles consulta la [referencia DSL 1.5](../../../reference/dsl_1_5/README.md).
