# Construcción por transferencia (unidades 2–7)

Los archivos `*_inicio_incompleto` omiten **deliberadamente una declaración**. Los de las unidades 3, 4 y 5 son rechazados por admisión; los de las unidades 2, 6 y 7 pueden ser admitidos, pero representan una conducta incompleta. **Admisión no demuestra que el ejercicio esté resuelto.** No se entregan como soluciones ejecutables correctas. Las soluciones son una referencia para el instructor; el alumno debe construir sus propias declaraciones.

## Unidad 2

**Intención:** Defina de nuevo la instancia inicial de Tegularis, con `id`, `card`, `location` y `status`, sin copiar el JSON de Parnecio.

Copie `paquetes/transferencia/u02_inicio_incompleto.package.json` a `mi_trabajo/u02_transferencia.package.json`; agregue la declaración que falta. Valide con:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u02_transferencia.package.json
python tools/glauquir.py --package mi_trabajo/u02_transferencia.package.json --auto
```

Antes de mirar `u02_solucion_referencia.package.json`, indique qué comportamiento espera, cómo sabrá que ocurrió y qué situación alternativa lo refutaría. Una admisión satisfactoria no basta para aprobar.

## Unidad 3

**Intención:** Declare `permiso_entrada` en `manifest.variables` con tipo booleano y valor inicial coherente con la sesión.

Copie `paquetes/transferencia/u03_inicio_incompleto.package.json` a `mi_trabajo/u03_transferencia.package.json`; agregue la declaración que falta. Valide con:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u03_transferencia.package.json
python tools/glauquir.py --package mi_trabajo/u03_transferencia.package.json --auto
```

Antes de mirar `u03_solucion_referencia.package.json`, indique qué comportamiento espera, cómo sabrá que ocurrió y qué situación alternativa lo refutaría. Una admisión satisfactoria no basta para aprobar.

## Unidad 4

**Intención:** Cree el rasgo `dodge` completo y sus contribuciones defensivas a partir de las condiciones y tags reales.

Copie `paquetes/transferencia/u04_inicio_incompleto.package.json` a `mi_trabajo/u04_transferencia.package.json`; agregue la declaración que falta. Valide con:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u04_transferencia.package.json
python tools/glauquir.py --package mi_trabajo/u04_transferencia.package.json --auto
```

Antes de mirar `u04_solucion_referencia.package.json`, indique qué comportamiento espera, cómo sabrá que ocurrió y qué situación alternativa lo refutaría. Una admisión satisfactoria no basta para aprobar.

## Unidad 5

**Intención:** Construya la carta de habilidad `golpe_ensayo`, cuyo efecto confirma `golpe_ensayado`, y mantenga la referencia de la instancia.

Copie `paquetes/transferencia/u05_inicio_incompleto.package.json` a `mi_trabajo/u05_transferencia.package.json`; agregue la declaración que falta. Valide con:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u05_transferencia.package.json
python tools/glauquir.py --package mi_trabajo/u05_transferencia.package.json --auto
```

Antes de mirar `u05_solucion_referencia.package.json`, indique qué comportamiento espera, cómo sabrá que ocurrió y qué situación alternativa lo refutaría. Una admisión satisfactoria no basta para aprobar.

## Unidad 6

**Intención:** Construya el paso `turno_adversario` que ejecuta una respuesta guionizada mediante `play_skill`. Explique por qué no es prioridad NPC.

Copie `paquetes/transferencia/u06_inicio_incompleto.package.json` a `mi_trabajo/u06_transferencia.package.json`; agregue la declaración que falta. Valide con:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u06_transferencia.package.json
python tools/glauquir.py --package mi_trabajo/u06_transferencia.package.json --auto
```

Antes de mirar `u06_solucion_referencia.package.json`, indique qué comportamiento espera, cómo sabrá que ocurrió y qué situación alternativa lo refutaría. Una admisión satisfactoria no basta para aprobar.

## Unidad 7

**Intención:** Construya el paso `ir_final` con `all` de ambos hechos y dos destinos de desenlace; prediga ambas ramas.

Copie `paquetes/transferencia/u07_inicio_incompleto.package.json` a `mi_trabajo/u07_transferencia.package.json`; agregue la declaración que falta. Valide con:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u07_transferencia.package.json
python tools/glauquir.py --package mi_trabajo/u07_transferencia.package.json --auto
```

Antes de mirar `u07_solucion_referencia.package.json`, indique qué comportamiento espera, cómo sabrá que ocurrió y qué situación alternativa lo refutaría. Una admisión satisfactoria no basta para aprobar.

