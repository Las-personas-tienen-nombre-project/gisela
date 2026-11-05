# H4.5. Revisión y cierre de la CLI textual

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Fecha:** 30 de octubre de 2026.

**Alcance:** cliente textual de un jugador, integrado a la API de GISELA, sin Ren'Py y sin lógica narrativa en Python de autor. Esta etapa se implementó después de H4 y antes de la integración gráfica.

## H4.5.0. Contratos públicos

**Resultado:** GISELA entrega información pública del protagonista, cartas conocidas, descripciones de escenas e historial narrativo persistente. Los campos nuevos de `Observe` y `Session` son opcionales para preservar compatibilidad con consumidores y guardados v1.2 previos.

**Debilidad encontrada:** `history.trace` identifica causas y reglas, pero no conserva la prosa que experimentó el jugador; reejecutar una descripción después de cambiar el mundo podría alterar el pasado.

**Corrección:** se incorpora `history.reading` como registro de lectura dentro de la misma sesión autoritativa, capturado al confirmar una transición o acción. No se duplica el estado del mundo ni se construye una historia en la CLI. Se comprueba su secuencia en el validador de sesiones.

**Simplificación:** no se implementa una API de consulta diferente para cada categoría de carta. `read_public` conserva una única verificación de visibilidad.

**Pruebas:** `H450Contracts` de `gisela/engine/tests/test_h45_cli.py`, más `test_h4_exploration.py` y los verificadores estructurales.

## H4.5a. Lectura y opciones

**Resultado:** presentación de escenas, actores, elementos, narraciones, diálogos, elecciones y solicitudes pendientes. Se admiten números y comandos textuales sobre acciones publicadas.

**Debilidad encontrada:** una opción deshabilitada podía seleccionarse numéricamente y provocar un error de ejecución que terminaba la consola.

**Corrección:** la CLI identifica la opción deshabilitada antes de enviarla y permite elegir nuevamente. GISELA conserva la comprobación definitiva mediante `Act`.

**Simplificación:** se utiliza `print` sobre cadenas completas en lugar de paneles de terminal, interfaces gráficas o bibliotecas adicionales.

**Pruebas:** `H45APresentation` y recorridos del ejecutor anterior.

## H4.5b. Inventario, cartas y comandos

**Resultado:** `inventario`, `cartas`, `habilidades`, `ficha`, `estado`, `acciones`, `examinar` y comandos contextuales.

**Debilidad encontrada:** una consulta de objeto podía confundirse con una acción que el autor diseñó para producir consecuencias.

**Corrección:** `ficha` siempre es una consulta; `examinar` prefiere una acción declarada si GISELA la ofrece y, de no existir, puede leer una carta conocida.

**Simplificación:** el intérprete solo compara verbos y etiquetas explícitas publicadas por GISELA; no hace inferencias psicológicas ni interpreta lenguaje natural libre. Ante ambigüedad, no ejecuta nada.

**Pruebas:** `H45BObjects`, en particular `test_examine_prefers_author_action` y `test_ambiguous_selection_never_guesses`.

## H4.5c. Habilidades y acontecimientos

**Resultado:** las escenas que declaren `allow_skill_play: true` ofrecen habilidades de mano con requisitos cumplidos. Se reutiliza la ejecución y el rollback de H3.4d.

**Debilidad encontrada:** la oferta de habilidades de los nodos dependía indebidamente de disponer de un cursor, por lo que no podía reutilizarse directamente en exploración.

**Corrección:** la validación de autorización distingue ventanas narrativas de escenas, pero ambas convergen en el mismo ejecutor y en las mismas transacciones. La traza de uso indica el nodo o la escena según la procedencia.

**Simplificación:** no se crea un ejecutor alternativo para acciones de exploración. Los eventos no generan prosa que el autor no haya definido. La CLI puede anunciar las acciones confirmadas usando el registro público.

**Pruebas:** `H45CSkills` y pruebas históricas de habilidades y transacciones.

## H4.5d. Registro, guardado y depuración

**Resultado:** `history`, `history 20`, `history all`, `guardar`, `cargar`, `estado` y consultas diagnósticas sujetas a `--developer`.

**Debilidad encontrada:** resolver una transacción pendiente en una escena podía registrar de nuevo la misma descripción aun cuando la escena no hubiera cambiado.

**Corrección:** el comparador de presentaciones considera el estado confirmado anterior a la espera y evita duplicaciones. El historial se escribe únicamente al confirmar; guardado y restauración preservan el mismo contenido.

**Simplificación:** el cliente no almacena su propia bitácora de lectura. Las consultas de desarrollo permanecen separadas de `Observe`.

**Pruebas:** `H45DHistory` y pruebas anteriores de restauración de H2.

## H4.5e. Recorridos y endurecimiento

**Resultado:** un paquete técnico completo, ejecutable por comandos, prueba inventario, fichas, habilidades, traslados, entrega de objetos, conversación, historial y final narrativo.

**Debilidad encontrada:** el programa terminaba con excepción si la entrada estándar llegaba a su fin sin escribir `salir`.

**Corrección:** EOF y la interrupción del usuario se tratan como término de la aplicación, sin afirmar que se haya guardado automáticamente.

**Simplificación:** un punto de entrada de pocos renglones, `tools/gisela_cli.py`, reutiliza la CLI anterior, que continúa disponible para compatibilidad. No se añade un servidor MUD.

**Pruebas:** `H45EIntegration`, la batería de contratos, la del ejecutor y `tools/check_quality.py`.

## Riesgos y límites restantes

1. El registro de lectura no recupera textos de partidas creadas antes de H4.5. Los snapshots v1.2 anteriores pueden seguir siendo válidos, pero no tienen esas entradas antiguas.
2. El motor no genera descripciones de reacciones a partir de cambios internos. La reacción visible necesita texto declarativo del autor.
3. La consulta pública de objetos no muestra arbitrariamente sus propiedades internas. Para permitirlo se necesitaría una política de visibilidad explícita en el contenido.
4. Los comandos no aceptan lenguaje natural libre ni escogen referentes ambiguos. Las acciones no publicadas se rechazan.
5. Ren'Py todavía no está integrado y no se declara ninguna equivalencia visual probada.
6. El registro es una fuente autoritativa de lectura, pero la persistencia no firma digitalmente cada entrada; un usuario que altere un archivo local podría manipular su contenido. La validación comprueba estructura y secuencia, no autenticidad criptográfica.

## Comprobación de cierre

Ejecute desde la raíz:

```bash
python tools/check_quality.py
python -m unittest gisela.engine.tests.test_h45_cli -q
python tools/check_project.py
sha256sum -c MANIFEST.sha256
```

La lista de invariantes y sus pruebas se encuentra en [INVARIANTES_H4_5.md](INVARIANTES_H4_5.md). El hito se considera terminado para el cliente textual y las capacidades declaradas del motor, no para un lenguaje natural completo ni para el futuro anfitrión Ren'Py.
