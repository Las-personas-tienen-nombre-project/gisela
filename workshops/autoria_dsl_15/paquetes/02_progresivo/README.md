# Laboratorio acumulativo 2: Personajes e instancias

## Archivo de trabajo obligatorio

Desde la raíz de GISELA, cree su propia copia. **Todos los comandos posteriores apuntan a esta copia**, nunca al archivo distribuido:

```bash
mkdir -p mi_trabajo
cp workshops/autoria_dsl_15/paquetes/02_progresivo/02_laboratorio.package.json mi_trabajo/u02.package.json
```

Antes de empezar, abra `mi_trabajo/u02.package.json` y cambie una etiqueta visible; compruebe luego que el archivo original conserva su texto. Para una prueba negativa, altere solamente la copia y guarde el diagnóstico. No copie el archivo original sobre su solución al terminar.

**Prerrequisito:** laboratorio 1 (Unidad 1: fundamentos). **Objetivo:** Crear dos fichas reales, una ubicación y dos instancias iniciales.

## Intención y mecanismo

`cards` define a Parnecio y Tegularis, más la carta de la ubicación `volcan`; `initial_state` crea la ubicación y las dos instancias. Los rasgos asignados proceden de Tegularis, pero todavía no se invocan.

## Construcción y predicción

Cambie únicamente `title.text` de Parnecio; compruebe que su `id` y la referencia `initial_state.characters[].card` permanecen intactos. Después cambie `sofia.awareness` en una copia y prediga qué valor podría consultar una resolución posterior.

Trabaje sobre una **copia** de `02_laboratorio.package.json`. El archivo distribuido es la referencia de partida, no un espacio para escribir la solución. Antes de ejecutarlo, escriba la predicción del comportamiento y explique qué identificadores y referencias ha utilizado.

## Comprobar mediante interfaces públicas

Desde la raíz del repositorio, sobre **su propio archivo**:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u02.package.json
python tools/glauquir.py --package mi_trabajo/u02.package.json --auto
```

Para otros desenlaces, ejecute el mismo archivo con `--choose ID` si el nodo ofrece esa opción; verifique el identificador real en las elecciones públicas. `--auto` por sí solo no demuestra todas las ramas. Registre el mensaje de admisión, la acción elegida, el texto final y la razón por la que corresponde a su predicción. Consulte [cómo leer el resultado](../../COMO_COMPROBAR.md).

## Errores frecuentes y aprobación

No cambie `id` sin actualizar las referencias; no suponga que un texto narrado refleja el estado lógico; no trate la admisión semántica como cobertura de todas las ramas. Si el motor rechaza una declaración, conserve el diagnóstico y compare con los esquemas y validadores oficiales antes de corregirla.

**Aprobación:** identificar la declaración, anticipar el comportamiento, efectuar una modificación propia, admitir la copia, ejecutarla y explicar la observación. Solo después pase al ejercicio productivo correspondiente en `../../ejercicios/02_personajes/`.

**Referencia oficial:** [guía de paquetes](../../../../docs/guides/CREAR_PAQUETE.md), [contratos](../../../../gisela/contracts/README.md) y documentación técnica del mecanismo en el repositorio. No se mantiene una segunda especificación del DSL en este workshop.

## Transferencia: crear, no solo modificar

Después del cambio guiado, complete el [ejercicio de construcción de esta unidad](../transferencia/README.md#unidad-2). El archivo de partida omite una declaración que usted debe reconstruir a partir de una intención; no basta con copiar el valor de otro campo. Entregue la declaración, explique sus dependencias y valide la **solución propia** desde `mi_trabajo/`.
