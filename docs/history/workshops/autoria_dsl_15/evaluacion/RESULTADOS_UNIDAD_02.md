# Verificación de la Unidad 2

Repositorio de referencia: `GISELA_workshop_inicio.tar.gz`; paquete base `01_cartas_gisela_v15.package.json`.

Comprobaciones realizadas con `gisela.contracts.admit_package.admit_package_file` y `python -m gisela.cli.glauquir --auto --package RUTA`:

| Archivo | Admisión | Ejecución automática |
|---|---|---|
| ejercicio `01_identidad` | aprobada | exit 0 |
| ejercicio `02_sofia` | aprobada | exit 0 |
| ejercicio `03_rasgo` | aprobada | exit 0 |
| ejercicio `04_referencia_invalida` | rechazado, como se pretendía | no ejecutado |
| solución `01_identidad` | aprobada | exit 0 |
| solución `02_sofia` | aprobada | exit 0 |
| solución `03_rasgo` | aprobada | exit 0 |

Se conservó el paquete productivo original sin modificaciones. Estas verificaciones confirman admisión y recorrido automático de la práctica, no equivalencia de todos los resultados de combate, ni que se hayan observado las contribuciones `dodge` en una tirada. La regresión general no fue ejecutada en esta entrega; el autor informa de que está verde localmente.
