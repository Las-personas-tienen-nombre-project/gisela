# GISELA. Perfil de digest canónico de paquetes, versión 1

**Estado:** normalización técnica aplicada y probada sobre los contratos JSON 1.2. Este documento fija el comportamiento de `canonical.py` y del campo `session.package_digest`. No define una firma digital, un mecanismo de autenticación ni un inventario de recursos físicos.

## Propósito

Las definiciones autorales son inmutables durante una sesión. Si un guardado pudiera restaurarse contra definiciones modificadas sin detectar el cambio, el mismo cursor o la misma decisión podría producir resultados diferentes. El digest vincula un estado guardado con el contenido exacto del paquete narrativo al que pertenece. No depende de espacios, saltos de línea ni del orden accidental de claves JSON.

Se utiliza el perfil `GISELA-CJSON-1`. Se escogió un procedimiento de alcance pequeño, completamente especificado y con una implementación de referencia sin dependencias criptográficas externas. No se declara equivalencia con RFC 8785, cuya normalización numérica y orden de claves tienen convenciones distintas.

## Entrada y alcance

La entrada es el objeto lógico completo del paquete autoral admitido: manifiesto, nodos, cartas, escenas, reglas, estado inicial, finales y textos opcionales. El resultado se calcula sobre el contenido del paquete, no sobre su ruta de archivo. No se omite ningún campo por considerarlo visual o auxiliar. No se ordenan las listas: su orden se preserva incluso si un catálogo pudiera tratarse como conjunto, porque decidir cuáles listas son conmutativas agregaría una dependencia semántica innecesaria al serializador.

Los archivos gráficos, de sonido y otros recursos externos no forman parte del digest. Las rutas o identificadores de recursos que figuran dentro del JSON sí quedan cubiertos porque son cadenas del paquete. Si en el futuro resulta necesario comprobar los bytes de recursos externos, deberá establecerse un contrato de integridad separado. No se debe atribuir al digest actual una protección que no ofrece.

## Serialización GISELA-CJSON-1

1. Se aceptan los valores JSON `null`, booleanos, cadenas, números, listas y objetos. No se aceptan valores de tipos Python particulares, como conjuntos, tuplas o bytes.
2. Las claves de cada objeto son cadenas Unicode y se ordenan en orden ascendente de puntos de código Unicode. No se usa el orden de inserción ni la configuración regional del sistema. Los elementos de las listas se conservan en su orden original.
3. Se utiliza UTF-8 sin marca de orden de bytes. No se aplica normalización Unicode. Dos cadenas visualmente parecidas con distinta secuencia de puntos de código producen digests diferentes.
4. Las cadenas se escriben entre comillas dobles. Las comillas y las barras invertidas se escapan con la barra invertida; los controles U+0000 a U+001F se escriben mediante las secuencias de escape JSON equivalentes a `json.dumps` de Python con `ensure_ascii=False`, incluyendo los escapes cortos convencionales. Las barras diagonales no se escapan. Se rechazan sustitutos Unicode aislados.
5. `true`, `false` y `null` se escriben en minúscula, sin espacios, saltos de línea ni tabulaciones. Se escriben dos puntos entre clave y valor y comas entre elementos.
6. Los enteros se escriben en base 10 sin ceros iniciales. Por interoperabilidad, se rechazan enteros cuyo valor absoluto supera 9007199254740991.
7. Los decimales se procesan como valores exactos; sus ceros fraccionarios finales se eliminan y la notación exponencial se expande a decimal ordinario. El cero negativo se normaliza a `0`. No se aceptan números no finitos. Para limitar entradas desproporcionadas, el exponente y la cantidad de cifras tienen un máximo de 4096.
8. La lectura de JSON utiliza detección de claves duplicadas. Para conservar las fracciones exactas se utiliza `decimal.Decimal`, con `parse_float=Decimal`. Si un consumidor crea datos en memoria mediante `float`, se usa su representación decimal de ida y vuelta, pero los paquetes de archivo deben seguir la ruta estricta de admisión.

El resultado es una secuencia de bytes UTF-8. Esta especificación es normativa para el perfil 1; cualquier cambio en la serialización requiere un nuevo identificador de perfil y vectores de prueba nuevos. No se deben alterar estos bytes sin versionar el procedimiento.

## Hash del paquete

Se concatenan, en este orden, los bytes ASCII de `GISELA-PACKAGE-DIGEST-v1`, un salto de línea (byte 0A) y los bytes UTF-8 de `GISELA-CJSON-1`. Se calcula SHA-256 sobre esa concatenación y se representa como 64 caracteres hexadecimales en minúscula, sin prefijo. Esa es la representación que exige `session.schema.json` para `package_digest`.

El prefijo separa este uso de SHA-256 de otras funciones del proyecto, como la extracción del RNG. El campo no es una firma y no sustituye la confianza en la fuente del paquete. Su función es detectar incompatibilidades involuntarias y manipulaciones del estado respecto de las definiciones que se han suministrado al motor.

## Verificación de una sesión

El validador calcula el digest del paquete recibido y lo compara con `snapshot.package_digest`. Cuando se ha proporcionado además un digest confiable por el anfitrión, se compara este valor con el mismo paquete. Ninguna coincidencia entre el guardado y un paquete modificado demuestra, por sí sola, que el archivo procede de una fuente autorizada. La restauración real también tendrá que comprobar las invariantes del mundo, los cursores y las transacciones pendientes.

Un cambio de contenido, incluso si parece editorial o no altera la ruta seleccionada, exige un digest nuevo. Se rechazan las discrepancias en vez de realizar migraciones silenciosas. Un guardado válido estructuralmente puede seguir sin ser restaurable mientras no exista el ejecutor que reconstruya su estado.

## Vectores de referencia

La prueba `test_determinism.py` fija el digest del objeto `{"b":2,"a":1}` como `71f9517491c6e88f57079c8863c0a9d743df687ec07f4eb60a375b85fb14d85e`. También verifica un objeto con texto en español, decimales equivalentes, orden de listas y datos rechazados. El paquete `gisela/contracts/example.package.json` debe producir el digest `f6ffaf227c512a4aa10510703811f9f18539521a288ea57959350c648d81cabb`.

El archivo `VECTORES.json` publica entradas y salidas para futuras implementaciones. Estos vectores permiten comprobar compatibilidad entre Python, el anfitrión Ren'Py y cualquier otra plataforma sin utilizar el mismo código como único criterio de verdad.

## Decisiones de diseño y límites

La implementación no utiliza un algoritmo de ordenación configurable, porque una segunda forma de serializar los mismos datos dañaría la comparabilidad. Tampoco normaliza por ID las listas de nodos o reglas, ya que habría que demostrar primero cuáles no dependen del orden. El costo de procesar completamente el paquete al admitirlo es aceptable en esta fase: ocurre antes de crear la sesión y evita mantener una caché de digest con reglas de invalidación difíciles de verificar.
