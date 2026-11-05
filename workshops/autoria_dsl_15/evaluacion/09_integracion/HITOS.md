# Hitos reproducibles — Unidad 9

**Objeto:** evaluación de autoría, no mera prueba de regresión. El alumno usa `mi_trabajo/`; el instructor comprueba **la ruta entregada**, nunca el JSON de ejemplo distribuido.

| Hito | Archivo que entrega el alumno | Evidencia exigida | Caso negativo / límite |
|---|---|---|---|
| 1. Fichas | `mi_trabajo/h01.package.json` | Cinco fichas, instancias, referencias y admisión | ID de ficha inexistente rechazado o documentado |
| 2. Variables | `mi_trabajo/h02.package.json` | Variable, guarda y predicción, dos elecciones | Guarda falsa no permite la acción |
| 3. TRAITS | `mi_trabajo/h03.package.json` | Definición y asignación, aportes por rol y etiqueta | Atacante y falta de `evasion` no reciben +2 |
| 4. Habilidades | `mi_trabajo/h04.package.json` | Slash, Double Slash, Blai: requisitos, costos y consecuencias | TP insuficiente o fallo no causa consecuencia de acierto |
| 5. Actuación | `mi_trabajo/h05.package.json` | Candidatos, objetivos, Observe/Act y elección documentada | Rechazo de acción inválida o guarda falsa |
| 6. Encuentro | `mi_trabajo/h06.package.json` | Firebreath, estados, Pride, Última llama y ramas | Umbral no alcanzado, habilidad no disponible |
| 7. Cierre | `mi_trabajo/h07.package.json` | Victoria, derrota y destrucción mutua; actas de los tres | No afirmar cobertura por una sola ejecución |
| 8. Presentación | `mi_trabajo/h08.package.json` | Dos regiones/vistas y comparación del estado lógico | Cambiar presentación no concede acciones |
| 9. Persistencia | `mi_trabajo/h09_evidencia.md` | Semilla, acciones, revisión, comparación antes/después de restaurar | Semilla sola no demuestra restauración |

La secuencia es acumulativa: `h02` parte de `h01`, etc. Una entrega puede reutilizar todo el paquete previo; debe destacarse qué declaración **fue creada** en el hito actual. Los paquetes de integración productivos son referencias de fidelidad, no plantillas para copiar sin explicación. Los archivos propios pueden ser extensos al final, pero no al principio.

## Registro obligatorio para cada hito

```text
Hito / archivo exacto:
Intención y contrato oficial consultado:
Declaración nueva (id, referencias):
Predicción caso positivo / negativo:
Comando ejecutado sobre mi ruta:
Admisión (salida y código):
Semilla y acciones ofrecidas/elegidas:
Acontecimientos confirmados / desenlace:
Comparación con canon: propiedades que deben ser idénticas:
Restauración y estado lógico, cuando aplique:
Fallo o limitación sin encubrir:
```

## Verificación de rutas de entrega

Desde la raíz del repositorio, para cada archivo `h01`…`h08`:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/h01.package.json
python tools/glauquir.py --package mi_trabajo/h01.package.json --auto
```

Cambie `h01` por el hito evaluado. Un paquete deliberadamente incompleto no pasa esta etapa. Para contribuciones, ramas de NPC, Pride, Última llama, desenlaces y restauración, **los comandos anteriores no bastan**: el instructor debe usar las pruebas dirigidas públicas del repositorio aplicables a la ruta del alumno, o registrar como no certificado el caso que no pudo forzar. Nunca declarar aprobación de una rama que no fue observada.

La [rúbrica](RUBRICA.md) se aplica por evidencia, no por cantidad de archivos. No se entregan semillas o estados forzados imaginarios como si existiera una herramienta pública de inyección de estados; si no hay herramienta confirmada, ese control queda abierto.
