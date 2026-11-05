# Laboratorio mínimo: Unidad 8: presentación sin alterar reglas

**Prerrequisito:** haber completado las unidades 1 a 7. Este paquete de unos pocos kilobytes extiende el encuentro reducido de la Unidad 7. No contiene el sistema completo de presentación productiva de Tegularis.

## Propósito

Aprender a separar datos públicos y rótulos visuales del estado lógico. La presentación tiene una región de acciones autorizadas y una vista pequeña de acontecimientos. Consulte la [referencia oficial](../../../../docs/architecture/PRESENTACION_DECLARATIVA_V082.md).

## Archivo propio

Desde la raíz del repositorio:

```bash
mkdir -p mi_trabajo
cp workshops/autoria_dsl_15/paquetes/08_progresivo/08_laboratorio.package.json mi_trabajo/u08.package.json
```

1. Abra `mi_trabajo/u08.package.json`; encuentre `presentation.regions`, `presentation.views`, `id`, `view`, `component` y `label`. Primero **solo reconozca** `source` y `kinds`.
2. Prediga qué cambia si el rótulo `Lo que ocurrió` pasa a `Registro público` y qué no cambia.
3. Cambie ese rótulo en su copia. Valide y ejecute. Explique por qué `cards`, `nodes`, `initial_state` y las decisiones no cambiaron.
4. **Construcción nueva:** agregue una segunda región `event_log` con un `id` único y una etiqueta propia, apuntando a la vista existente `hechos`. Prediga cómo se verán ambos paneles; no cree reglas ni nuevos acontecimientos.
5. Como prueba negativa, cambie temporalmente `view` por `vista_que_no_existe`: registre si el contrato lo rechaza y restaure la referencia. Si el validador lo admite, indíquelo como límite, no como prueba verde.

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u08.package.json
python tools/glauquir.py --package mi_trabajo/u08.package.json --auto
```

Compare también la ejecución con `mi_trabajo/u07.package.json` usando las mismas elecciones. **No afirme equivalencia del RNG por una sola ejecución**: la comprobación dirigida completa corresponde al instructor.

## Qué observar

La etiqueta de la región cambia; la secuencia de decisiones y el desenlace lógico no cambian por una modificación puramente visual. Si GLAUQUIR en modo textual no dibuja todas las regiones, compruebe la presentación declarada con las interfaces públicas y documente esa limitación. Consulte [guía de observación](../../COMO_COMPROBAR.md).

**Aprobación:** entrega el archivo propio, una región creada por usted, admisión, una ejecución terminada y una explicación de qué es visual y qué es autoritativo. Continúe con los ejercicios productivos solo después.
