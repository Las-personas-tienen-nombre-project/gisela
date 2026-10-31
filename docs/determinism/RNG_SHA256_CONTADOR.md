# GISELA. Generador aleatorio reproducible, versión 1

**Estado:** perfil `sha256_counter_v1` especificado, probado e integrado al ejecutor H2 mediante `roll` con destino numérico. La interfaz de Ren'Py y otras operaciones aleatorias especializadas siguen pendientes.

## Objetivo

El motor puede ejecutar sorteos declarados por el autor. Para que un guardado pueda restaurarse y una ejecución pueda repetirse en distintas interfaces, el resultado no puede depender del generador de Python, de Ren'Py, del reloj del sistema ni del orden accidental de recorridos sobre diccionarios. Se utiliza una secuencia de bloques SHA-256 identificados por semilla y contador.

## Estado serializable

`algorithm` debe ser la cadena `sha256_counter_v1`. `seed` es una cadena hexadecimal en minúscula de 64 caracteres, que representa exactamente 32 bytes. `counter` es un entero desde cero hasta 9007199254740991, ambos extremos incluidos como estado válido. Un sorteo requiere que el contador sea menor que el valor máximo; si se alcanza el límite, se informa un error técnico, sin reutilizar bloques.

Una semilla suministrada como número entero o texto de usuario debe transformarse en 32 bytes mediante un procedimiento de entrada explícito del anfitrión, que no forma parte de este perfil. No se define una conversión implícita para evitar que dos interfaces entiendan el mismo número como semillas diferentes. Los vectores usan semillas hexadecimales literales.

## Generación de un bloque

Para obtener el bloque asociado al contador `c`, se concatenan los bytes ASCII de `GISELA-RNG-v1`, un salto de línea, los 32 bytes de la semilla y `c` codificado como entero sin signo de 64 bits en orden big endian. SHA-256 de esos bytes produce 32 bytes. Esos bytes se interpretan como un entero sin signo de 256 bits en orden big endian.

Los bloques se obtienen con contadores consecutivos a partir del valor confirmado de la sesión. No se utiliza sal oculta, orden del sistema, estado global ni otra fuente de aleatoriedad. La semilla no se considera secreta; el mecanismo sirve para reproducción, no para usos criptográficos que requieran impredecibilidad ante un adversario.

## Muestreo uniforme para un entero entre 1 y N

El parámetro `sides` es un entero entre 1 y 9007199254740991. Se define `space` como 2 elevado a 256 y `limit` como `space` menos el resto de `space` dividido por `sides`. Se genera un bloque y se incrementa el contador provisional. Si el valor del bloque es menor que `limit`, el resultado es 1 más el resto de dividir el valor por `sides`. Si el valor es igual o mayor que `limit`, ese bloque se rechaza y se utiliza el contador siguiente. El procedimiento continúa hasta obtener una muestra aceptada o hasta que se agote el contador.

El rechazo evita la pequeña diferencia de probabilidad que aparecería si se utilizara directamente el resto de dividir cualquier valor de 256 bits por un número arbitrario de caras. Una muestra rechazada consume un bloque de la secuencia provisional. Se considera error técnico si el contador se agota antes de obtener un resultado.

## Frontera transaccional

La función de referencia recibe un estado inmutable y devuelve dos valores: el resultado y un nuevo estado. No modifica el estado recibido. El ejecutor coloca ese nuevo estado en el borrador y solo lo confirma al terminar la operación con todas sus reacciones causales. Si el jugador cancela una acción voluntaria o una reacción provoca un error técnico, el estado confirmado de la semilla y el contador permanece sin cambios.

Mientras una transacción espera una decisión del jugador, su evaluación provisional no se publica ni se serializa. Al restaurarla, GISELA volverá a calcularla desde el último estado confirmado y las decisiones provisionales guardadas, tal como establecen ADR-001 a ADR-005. Las pruebas de `test_h2_closure.py` comprueban la inmutabilidad del estado confirmado, la cancelación, el rollback por conflicto y el replay de transacciones suspendidas tras un sorteo.

## Orden de los sorteos

Cuando una secuencia autoral declara varias operaciones `roll`, estas se ejecutan en su orden explícito. Las rondas reactivas tienen condiciones simultáneas; si varias reglas requieren sorteos en una misma ronda, GISELA ejecuta las reglas de cada ronda en orden lexicográfico de `rule.id`; dentro de cada regla conserva el orden declarado de `effects`. El orden se ha probado con un paquete de reglas reordenadas. El criterio se aplica al subconjunto actual y podrá requerir una revisión explícita si se amplía la semántica de efectos concurrentes.

## Vectores públicos

Para la semilla de 32 bytes cero, el contador inicial cero y `sides` igual a 6, el resultado es 6 y el contador nuevo es 1. Para esa misma semilla, `sides` igual a 10 entrega 6 y contador 1. Para la semilla `0123456789abcdef` repetida cuatro veces, `sides` igual a 6 entrega 4 y contador 1. Los demás casos se encuentran en `VECTORES.json` y se verifican con `test_determinism.py`.

## Límites

No se implementan distribuciones particulares ni tiradas automáticas de S.O.F.I.A. Tampoco se afirma que la secuencia sea compatible con versiones futuras que cambien el prefijo, el orden de bytes, el algoritmo de hash o el criterio de rechazo. Esos cambios exigirían un identificador nuevo y una política explícita de migración, sin alterar partidas antiguas de forma silenciosa.
