# Resultados — Unidad 3

Referencia: `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json` y `contracts/v1_5/common.schema.json`.

## Admisión pública

- Paquetes de inicio 01, 02 y 03: **admitidos**.
- Solucionarios 01, 02 y 03: **admitidos**.
- Paquete 04 con referencia `clave_privada_inexistente`: **rechazado** (resultado esperado).

## Ejecución

- Paquetes de inicio 01 y 02: `python -m gisela.cli.glauquir --auto` terminó con código 0.
- El paquete de inicio 03 y los solucionarios: comprobación de ejecución **no concluida** en esta sesión (tiempo máximo de ejecución agotado o ejecución interrumpida). No se declaran aprobados.
- No se ha demostrado mediante trazas dirigidas la rama con HP cero ni el umbral Pride. Pendiente de pruebas con estado controlado.
- La regresión total del proyecto no se ha repetido. El usuario informa que las pruebas locales del proyecto están verdes; esto no sustituye la comprobación de los paquetes nuevos.

Los archivos `.log` de intentos están en `evaluacion/logs_u03` y pueden contener salidas parciales. Un log incompleto no prueba finalización.
