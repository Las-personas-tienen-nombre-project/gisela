# Fuente de las variantes de presentación 11–14

El paquete `10_balance_v078.package.json` contiene la lógica canónica del
combate, incluidos las cartas, variables, actuaciones y condiciones. Las seis
variantes 11–14 **solo** reemplazan el objeto `presentation`.

La fuente editable de esas variantes es `v081_v082_presentations.json`, un
objeto cuyas claves son nombres de archivo completos y cuyos valores son
objetos `presentation`. Los nombres son identificadores, no posiciones dentro
de un arreglo; el generador rechaza rutas con subdirectorios.

Para compilar desde este directorio:

```bash
python build_v078.py
python build_presentations.py
```

Para verificar que el repositorio contiene exactamente lo producido por el
generador, ejecutar desde la raíz:

```bash
python -m pytest -q gisela/engine/tests/test_corrective_generators_c4.py
```

Los artefactos JSON son **paquetes completos y autocontenidos**; la composición
se realiza antes de la admisión, nunca durante la ejecución. No se altera el
contrato de GISELA ni se introducen dependencias entre paquetes al ejecutar.

La versión 14 se normalizó con un salto de línea al final del archivo, sin
modificar ninguno de sus valores JSON.
