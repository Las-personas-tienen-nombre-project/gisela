# Laboratorio acumulativo 7 — Integración causal mínima

## Archivo de trabajo obligatorio

Desde la raíz de GISELA, cree su propia copia. **Todos los comandos posteriores apuntan a esta copia**, nunca al archivo distribuido:

```bash
mkdir -p mi_trabajo
cp workshops/autoria_dsl_15/paquetes/07_progresivo/07_laboratorio.package.json mi_trabajo/u07.package.json
```

Antes de empezar, abra `mi_trabajo/u07.package.json` y cambie una etiqueta visible; compruebe luego que el archivo original conserva su texto. Para una prueba negativa, altere solamente la copia y guarde el diagnóstico. No copie el archivo original sobre su solución al terminar.

**Prerrequisito:** laboratorio 6 (paquete anterior). **Objetivo:** Combinar una habilidad elegida, una respuesta guionizada y una condición compuesta de desenlace.

## Intención y mecanismo

El paquete conserva dos personajes, atributos, contribuciones, variable, habilidad, respuesta y desenlaces. Su condición compuesta solo se cumple si se registraron **ambos** hechos. No reproduce aún Firebreath, Pride ni Última llama.

## Construcción y predicción

Localice la condición `all` que exige `golpe_ensayado` y `respuesta_tegularis`. Prediga el desenlace si usa el golpe y si lo omite. Ejecute ambas rutas, y finalmente explique cómo trasladaría estas relaciones al paquete productivo sin alterar su balance.

Trabaje sobre una **copia** de `07_laboratorio.package.json`. El archivo distribuido es la referencia de partida, no un espacio para escribir la solución. Antes de ejecutarlo, escriba la predicción del comportamiento y explique qué identificadores y referencias ha utilizado.

## Comprobar mediante interfaces públicas

Desde la raíz del repositorio, sobre **su propio archivo**:

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u07.package.json
python tools/glauquir.py --package mi_trabajo/u07.package.json --auto
```

Para otros desenlaces, ejecute el mismo archivo con `--choose ID` si el nodo ofrece esa opción; verifique el identificador real en las elecciones públicas. `--auto` por sí solo no demuestra todas las ramas. Registre el mensaje de admisión, la acción elegida, el texto final y la razón por la que corresponde a su predicción. Consulte [cómo leer el resultado](../../COMO_COMPROBAR.md).

## Errores frecuentes y aprobación

No cambie `id` sin actualizar las referencias; no suponga que un texto narrado refleja el estado lógico; no trate la admisión semántica como cobertura de todas las ramas. Si el motor rechaza una declaración, conserve el diagnóstico y compare con los esquemas y validadores oficiales antes de corregirla.

**Aprobación:** identificar la declaración, anticipar el comportamiento, efectuar una modificación propia, admitir la copia, ejecutarla y explicar la observación. Solo después pase al ejercicio productivo correspondiente en `../../ejercicios/07_tegularis/`.

**Referencia oficial:** [guía de paquetes](../../../../docs/guides/CREAR_PAQUETE.md), [contratos](../../../../gisela/contracts/README.md) y documentación técnica del mecanismo en el repositorio. No se mantiene una segunda especificación del DSL en este workshop.

## Transferencia: crear, no solo modificar

Después del cambio guiado, complete el [ejercicio de construcción de esta unidad](../transferencia/README.md#unidad-7). El archivo de partida omite una declaración que usted debe reconstruir a partir de una intención; no basta con copiar el valor de otro campo. Entregue la declaración, explique sus dependencias y valide la **solución propia** desde `mi_trabajo/`.
