# Verificación: corrección pedagógica 02

## Alcance y material

Se añadieron seis paquetes pequeños, completos y acumulativos para las unidades 2 a 7. Parten del paquete mínimo oficial de GISELA y reutilizan las declaraciones reales de personajes, traits, evaluación y habilidad. Los ejercicios productivos originales de Tegularis no se sustituyen.

| Unidad | Paquete | Intención principal | Límite de esta comprobación |
|---|---|---|---|
| 2 | `02_progresivo` | Dos fichas y dos instancias | No hay tiradas |
| 3 | `03_progresivo` | Variable y guarda | No fuerza todos los estados posibles |
| 4 | `04_progresivo` | Contribución `dodge` en `evaluate` | Sin comprobación dirigida del aporte numérico |
| 5 | `05_progresivo` | Habilidad y hecho confirmado | No simula daño ni concurso |
| 6 | `06_progresivo` | Respuesta guionizada de Tegularis | **No equivale a política NPC autónoma** |
| 7 | `07_progresivo` | Conjunción causal y desenlace | No reproduce la batalla completa |

## Resultados reproducidos

- Admisión semántica: **6/6 ADMITTED** con `gisela/contracts/admit_package.py`.
- Ejecución con GLAUQUIR: **12/12 rutas completas**, dos por paquete. Ruta de `abrir`/`seguir` en 2 a 4 y ejecución/omisión en 5 a 7.
- Las rutas de habilidad de 5 a 7 terminan en `Dentro de la pieza`; al omitir la carta terminan en `Al final del pasillo`. Son títulos heredados del paquete mínimo, no desenlaces productivos de Tegularis.
- `python tools/check_quality.py`: **OK**.
- `python tools/check_doc_links.py`: **OK**.
- Registros de ejecución: `evaluacion/logs_progresivos/`.

## Limitaciones pendientes

La Unidad 4 todavía necesita una prueba dirigida que confirme la cifra exacta de la contribución en la resolución, y la Unidad 6 exige integrar y comprobar políticas NPC reales, no meras llamadas `play_skill` de guion. No se declara el recorrido de autoría independiente aprobado por pruebas de alumnos. No se ha realizado regresión completa ni completado Unidad 9. El motor, sus esquemas y los paquetes canónicos no fueron editados.

## Procedimiento general

Desde la raíz:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package workshops/autoria_dsl_15/paquetes/07_progresivo/07_laboratorio.package.json
python tools/glauquir.py --package workshops/autoria_dsl_15/paquetes/07_progresivo/07_laboratorio.package.json --auto
python tools/glauquir.py --package workshops/autoria_dsl_15/paquetes/07_progresivo/07_laboratorio.package.json --auto --choose continue
python tools/check_quality.py
python tools/check_doc_links.py
```
