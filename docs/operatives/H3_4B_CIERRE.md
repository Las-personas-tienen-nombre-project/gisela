# H3.4b. Registro de cierre de S.O.F.I.A.

**Estado:** TERMINADO para atributos actuales y cálculo de Scoresheet.

**Fecha:** 30 de octubre de 2026.

## Alcance

Se implementaron las consultas tipadas de `base`, `current` y `effective`, la escritura transaccional de `current`, la suma pura de modificadores provenientes de efectos activos y la proyección de solo lectura `scoresheet(character)`. El contrato no almacena los valores efectivos de manera redundante.

La escala inicial es de 0 a 10, configurable desde el manifiesto. Los valores base y actuales deben respetarla; el efectivo puede excederla debido a modificadores. Un personaje sin definición S.O.F.I.A. no recibe valores inventados.

## Arquitectura y mantenimiento

La lógica de atributos se encuentra en `gisela/engine/sofia.py`. ALBERTO resuelve datos y precondiciones, mientras que el ejecutor de GISELA mantiene la transacción, el rollback y la restauración. No se incorporó un motor adicional ni se modificaron los schemas 1.2.

El control `tools/check_quality.py` exige archivos técnicos de hasta 500 líneas, funciones Python de hasta 30 líneas excluyendo el docstring inicial y un máximo de tres parámetros explícitos. `self` y `cls` se consideran receptores proporcionados por Python. Los contextos de ejecución agrupan datos relacionados, de manera que las firmas no dependan de argumentos extensos ni posicionales ambiguos.

Se revisaron las funciones del ejecutor y el validador semántico para aplicar el nuevo límite, procurando conservar responsabilidad única y una ruta evidente para cada operación. Los efectos activos se leen; su ciclo de vida se mantiene fuera de este hito.

## Pruebas y criterios de aceptación

- Los valores actuales ausentes se resuelven desde la carta sin materialización de estado.
- La consulta Scoresheet respeta el schema y no modifica turnos, revisiones o RNG.
- `set` y `add` sobre `current` respetan los enteros y la escala configurada.
- `base` y `effective` no admiten escrituras declarativas.
- Las reglas reactivas combinan sumas compatibles y rechazan conflictos.
- Los errores posteriores a un cambio revierten toda la operación.
- La restauración conserva los resultados y los cálculos.
- Scoresheet durante una transacción pendiente presenta solamente el estado confirmado.
- Los efectos iniciales aportan modificadores sin cambiar los valores base o actuales.
- La admisión rechaza atributos y modificadores dirigidos a personajes sin S.O.F.I.A.
- Se conservan las pruebas anteriores de H1, H2, H3.1 a H3.3 y H3.4a.

El ejemplo reproducible reside en `gisela/packages/h3_sofia.package.json`. La guía humana y el script están en `docs/guides/SOFIA_ATRIBUTOS.md` y `docs/guides/examples/ejemplo_sofia_dinamica.py`. El comprobador principal ejecuta las pruebas y el ejemplo.

## Límites y trabajo posterior

H4 deberá fijar la autorización de lectura de Scoresheet antes de exponer fichas a jugadores. La API Python actual permite consultas técnicas por identificador de personaje y no equivale a una autorización pública. H3.4c debe implementar aplicación, acumulación y expiración de efectos, con sus consecuencias y pruebas de exactitud causal. H3.4d debe implementar ejecución de habilidades, requisitos y políticas de retorno. Estos mecanismos no se dan por terminados por el hecho de que Scoresheet pueda leer instancias de efecto ya presentes en un guardado.
