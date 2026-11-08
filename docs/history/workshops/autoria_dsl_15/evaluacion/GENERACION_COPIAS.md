# Generación de las 68 copias didácticas, unidades 3 a 8

Las fuentes son el paquete productivo completo `packages/tegularis_the_son_of_the_volcan/14_presentacion_semantica_v082d.package.json` y el archivo declarativo `canonical_overlays.json`. Cada entrada identifica una copia por su ruta dentro del workshop y describe las diferencias respecto al canon. Las soluciones que son idénticas al canon tienen una lista vacía.

El generador **no altera el runtime ni la admisión**, y preserva los errores intencionales de los ejercicios. La composición ocurre antes de la admisión. Se mantienen completos e independientes los JSON resultantes.

Desde la raíz del repositorio:

```bash
python docs/history/workshops/autoria_dsl_15/evaluacion/build_canonical_copies.py
python docs/history/workshops/autoria_dsl_15/evaluacion/build_canonical_copies.py --write
```

El primer comando comprueba que las 68 copias existentes coincidan semánticamente con las fuentes, sin escribir nada. El segundo las regenera cuando hace falta. Si una copia ya coincide, conserva su formato y fecha de modificación. El comando no reescribe las siete copias especiales de la Unidad 2, ni los laboratorios progresivos, ni los paquetes de transferencia.

Las rutas de listas con identificadores se resuelven por `id`, `character` u otras claves inequívocas. Las listas sin identificador estable se reemplazan como unidad, con comparación previa del valor anterior. **Una divergencia incompatible del canon provoca error**, no una modificación silenciosa. Si se cambia deliberadamente el canon y se modifican los ejercicios, actualizar y revisar los overlays junto con las pruebas pedagógicas; no regenerar a ciegas.

Después de regenerar:

```bash
python -m pytest -q gisela/engine/tests/test_workshop_c4_regeneration.py
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_04.py
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_05.py
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_06.py
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_07.py
PYTHONPATH=. python docs/history/workshops/autoria_dsl_15/evaluacion/comprobar_unidad_08.py
```

El generador verifica correspondencia estructural, no sustituye la admisión ni las comprobaciones pedagógicas. Algunas variantes son deliberadamente inválidas.
