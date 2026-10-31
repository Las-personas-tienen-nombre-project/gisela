# TRAITS-ALBERTO y TRAITS-DICE: Implementación y límites

**Base:** `las-personas-tienen-nombre(8).zip` más parche del núcleo TRAITS v1.
**Alcance:** primera integración ejecutable, reutilizable entre juegos.
**Estado:** código y pruebas de integración; **no** constituye implementación de ADR-019 (evaluaciones visibles).

## Fases ejecutadas

1. **Inventario y compatibilidad.** Contratos GISELA v1.2 intactos. Se incorpora la familia de contratos de paquete y sesión **v1.3**, con registro de validación separado, sin migración automática ni inserción silenciosa de campos en guardados antiguos.
2. **TRAITS-ALBERTO.** Catálogos declarados en `package.traits`, con límite de cinco rasgos por entidad por defecto (`max_traits` configurable). Cartas `character`, `location` y `object` pueden declarar `traits`; las instancias iniciales los heredan cuando omiten el campo y los sustituyen cuando lo incluyen, incluso `[]`. El conjunto actual se materializa en `session.world` y se conserva en el guardado.
3. **Operaciones.** `assign_trait` y `remove_trait` validan identidad, clase, capacidad y exclusiones, trabajan en el borrador transaccional y son idempotentes. `has_trait` consulta sin consumir RNG. Las escrituras de reglas reactivas sobre rasgos de una misma entidad compiten por la misma clave y producen `REACTION_CONFLICT` cuando son incompatibles.
4. **DICE independiente.** Perfiles neutrales v1 con modos `deterministic`, `single_die`, `dice_sum` y `dice_pool`, bandas de resultados y fuente de aleatoriedad inyectable. DICE no importa módulos de TRAITS, ALBERTO, S.O.F.I.A., MARY ni GISELA.
5. **Adaptador de integración.** `gisela.engine.traits_dice_bridge.resolve` consulta instancias actuales de ALBERTO, evalúa las contribuciones contextuales de TRAITS y, opcionalmente, un atributo S.O.F.I.A.; transforma los sumandos a entradas neutrales de DICE. Devuelve dados, resultado, contribuciones y siguiente estado RNG **sin mutar el guardado**.
6. **Pruebas y revisión.** Validación de formatos, persistencia, rollback, incompatibilidades, no duplicación, conflicto reactivo, reproducibilidad y funcionamiento de DICE sin TRAITS o S.O.F.I.A.

## Fronteras de responsabilidad

| Capa | Autoridad y contrato |
|---|---|
| GISELA | Admisión, transacción, estado confirmado, persistencia y RNG. |
| ALBERTO | Entidades, rasgos asignados y operaciones sobre borradores. |
| TRAITS | Catálogo, pertinencia y contribuciones puras; ninguna sesión propia. |
| S.O.F.I.A. | Atributos efectivos opcionales; ningún criterio universal de éxito. |
| DICE | Matemática y clasificación del resultado; sin acceso al mundo. |
| MARY | Misiones y progresión; sin dependencia nueva de TRAITS ni DICE. |

Las ranuras `bonus` y `difficulty` son un contrato del **adaptador**, no tipos incorporados universalmente al núcleo de TRAITS ni a DICE. Los demás juegos pueden ofrecer adaptadores diferentes. Las contribuciones/atributos ocultos son internos y no deben proyectarse íntegramente al cliente.

## Pendientes y riesgos reales

1. **ADR-019 no implementado.** No existe aún `pending_evaluation`, confirmación anticipada de RNG, presentación en `Observe`, continuación por `Act` ni sus garantías de reintentos. El adaptador es una **función interna** que solo debe usarse en un borrador cuya confirmación controle GISELA. Publicar su resultado directamente al cliente permitiría volver a resolver la tirada; está prohibido hasta implementar ADR-019.
2. **Declaración `evaluate` no implementada.** Ni el nodo, ni las opciones de diálogo ni las acciones de escena pueden invocar todavía el contrato de evaluación descrito en `DICE_EVALUACION_DECLARATIVA_PROPUESTA.md`. Los perfiles DICE v1 son utilizables mediante Python, pero todavía no forman parte del esquema de autoría del paquete.
3. **Persistencia v1.3 sin migración.** Los formatos 1.2 y 1.3 se validan por separado. Una sesión 1.2 no puede restaurarse con el catálogo v1.3 ni se recalculan rasgos a partir de cartas al restaurar; cualquier conversión futura exige migrador versionado, autorización y pruebas.
4. **Perfiles de DICE.** Los cuatro mecanismos básicos son deliberadamente limitados. Faltan evaluación enfrentada, costes de repetición, distribución analítica y perfiles numéricos especializados.
5. **Causalidad y RNG.** La salida `rng_after` es una propuesta, no un commit. Antes de exponer una evaluación por `Act`, habrá que asegurar identidad única, atomicidad con el estado, control de concurrentes y reversión con rollback.
6. **Capacidad y conflictos.** En v1 dos reglas distintas que alteran rasgos de una entidad en la misma ronda se rechazan conservadoramente; no hay planificador general de altas/bajas de conjuntos.
7. **Visibilidad.** La presencia de rasgos ocultos no autoriza exponerlos en Scoresheet o `Observe`. No se ha agregado ningún campo público de proyección.
8. **Duplicación de esquemas.** Se conserva el conjunto v1.2 y se añade v1.3 en `gisela/contracts/v1_3/`. Deben regenerarse o revisarse de forma conjunta cuando evolucione el vocabulario común; la caché evita cargar todos los esquemas en cada acción.

## Verificación recomendada

```bash
python -m unittest discover -s traits/tests -p 'test_*.py' -q
python -m unittest discover -s dice/tests -p 'test_*.py' -q
python -m unittest discover -s mary/tests -p 'test_*.py' -q
python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q
python -m unittest discover -s gisela/contracts -p 'test_*.py' -q
python tools/check_quality.py
python tools/check_gisela.py --full
```

El comando integral del proyecto encadena pruebas, admisión y recorridos CLI, por lo que puede superar el tiempo de una herramienta de ejecución. En caso de que eso ocurra, no se debe declarar aprobado sin haber completado también los recorridos restantes.
