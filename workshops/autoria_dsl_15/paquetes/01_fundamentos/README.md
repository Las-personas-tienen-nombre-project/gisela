# Laboratorio mínimo: Unidad 1

Se usa el paquete completo oficial `gisela/packages/ejemplo_minimo.package.json` (copia local `00_base`) para aprender declaración y referencia antes de abrir un paquete productivo grande. **No recrea la batalla de Tegularis**, sino que introduce la estructura que el alumno necesitará después.

## 0. Identificar

Abra `00_base.package.json` (aproximadamente 1,6 KB), localice `manifest.entry.node`, `nodes[0].id` y las dos opciones con `next.node`. Explique en voz alta cómo se enlazan. Localice también `endings`.

## 1. Descubrir (archivo `01_primera_decision`)

**Intención:** dos alternativas en la portería con diferentes desenlaces.

**Predicción:** al seleccionar la primera alternativa, el texto del nodo `puerta_abierta` precederá al final `adentro`; al elegir la segunda, el nodo `pasillo` precederá al final `afuera`.

**Construcción:** cambie el texto de una alternativa y observe que el destino no cambia. Luego cambie su `next.node` para que apunte al otro nodo existente: prediga el final nuevo y compruébelo. Restaure la referencia correcta.

## 2. Transferir (archivo `02_otra_decision`)

**Intención:** escuchar la radio o seguir caminando. Sin consultar el archivo anterior, cambie el primer desenlace, manteniendo dos referencias válidas y explicando por qué no fue necesario programar una función.

## 3. Preparar y validar el trabajo propio

Desde la raíz de GISELA, cree su propia copia. **Todos los comandos posteriores apuntan a esta copia**, nunca al archivo distribuido:

```bash
mkdir -p mi_trabajo
cp workshops/autoria_dsl_15/paquetes/01_fundamentos/01_primera_decision.package.json mi_trabajo/u01.package.json
```

Antes de empezar, abra `mi_trabajo/u01.package.json` y cambie una etiqueta visible; compruebe luego que el archivo original conserva su texto. Para una prueba negativa, altere solamente la copia y guarde el diagnóstico. No copie el archivo original sobre su solución al terminar.

```bash
PYTHONPATH=. python -m gisela.contracts.admit_package mi_trabajo/u01.package.json
python tools/glauquir.py --package mi_trabajo/u01.package.json --auto --choose abrir
python tools/glauquir.py --package mi_trabajo/u01.package.json --auto --choose seguir
```

Pruebe ambas elecciones después de cada cambio; `--choose` selecciona el identificador declarado, no el texto de la opción. Para la transferencia `02_otra_decision`, cópiela a `mi_trabajo/u01_transferencia.package.json` y sustituya la ruta en los comandos.


**Aprobación:** explica objeto/lista/clave/referencia, muestra admisión y ambas ramas, y razona un rechazo real. Si solo editó etiquetas sin explicar el salto por ID, no ha completado el ejercicio.

**Fuentes oficiales:** [crear paquete](../../../../docs/guides/CREAR_PAQUETE.md) y [contratos](../../../../gisela/contracts/README.md).
