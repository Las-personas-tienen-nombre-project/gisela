# Revisión documental y organización del repositorio

Fecha: 4 de noviembre de 2026.

## Cambios

Se trasladaron los talleres de presentación sueltos a `docs/guides/workshops/`,
los informes a `docs/operatives/` y los registros y snapshots a
`docs/operatives/evidence/`. README, licencias y configuración permanecen en la raíz.
En total se trasladaron 11 documentos y 47 evidencias; estas últimas conservan
los mismos bytes y hashes SHA-256.
El taller completo de autoría conserva su estructura en `workshops/autoria_dsl_15/`.
El [inventario de traslados](evidence/revision_documental_2026_11_04/traslados.json)
registra cada origen, destino y hash original.

Se corrigieron referencias, se amplió el índice y se consolidaron las capacidades
de presentación implementadas hasta v0.8.2f. Las guías del taller distinguen los
laboratorios disponibles, las comprobaciones de referencia y la evaluación de alumnos.
Los verificadores docentes solo aceptan `PackageRejected` como rechazo esperado;
otros errores ya no se presentan como resultados satisfactorios.

La revisión inicial de español aplicó los criterios de naturalidad, precisión y respeto
del registro de `INSTRUCCIONES_LECTURA_Y_EDICION_LITERARIA.md` y
`GUIA_LECTURA_REVISION_ESPANOL_CHILE.md`, facilitadas desde el repositorio narrativo.
En la primera pasada, la tipografía simple se limitó a la prosa documental.
La pasada complementaria descrita más abajo incluye las salidas del programa,
las plantillas y los diálogos de los paquetes, según el alcance acordado.

Los informes previos mantienen sus cifras y límites como registros históricos.
Las correcciones de aquella pasada no modificaron el motor, sus contratos ni
los paquetes narrativos.
El manual introductorio tenía duplicadas las secciones de instalación, JSON y
validación; se consolidaron en una sola secuencia. Los paquetes por etapas de
*El paraguas olvidado* no están en este repositorio: ahora se indica esa limitación
y se enlaza el ejemplo mínimo disponible. En el fragmento de `set_belief`, el campo
se corrigió de `key` a `claim`, conforme al contrato existente.

## Verificación anterior conservada

Estos resultados pertenecen a la revisión inicial y se conservan con sus registros.
No incluyen la prueba Dodge añadida después ni la limpieza de salidas y paquetes.
Todas las comprobaciones de aquella ejecución terminaron con código de salida 0:

| Control | Resultado | Evidencia |
|---|---|---|
| Kit oficial `python tools/check_gisela.py --full` | 18 de 18 grupos aprobados | [Registro completo](evidence/revision_documental_2026_11_04/check_gisela_full.log) |
| Motor, contratos, bibliotecas y Tegularis | 839 pruebas y 128 subpruebas aprobadas | Grupo inicial del kit |
| Herramientas | 69 pruebas y 100 subpruebas aprobadas | Segundo grupo del kit |
| Ruff, Radon, Bandit, calidad, enlaces e invariantes E0 a E3 | Aprobados | Registro completo del kit |
| Seis rutas de Faro y Central con restauración | Aprobadas | Registro completo del kit |
| Admisión de los 97 paquetes del taller | 87 admitidos y 10 rechazos didácticos previstos | [Detalle por paquete](evidence/revision_documental_2026_11_04/admision.jsonl) |
| Seis verificadores docentes | Aprobados; cada uno conserva su alcance específico | [Resumen del taller](evidence/revision_documental_2026_11_04/workshop_resumen.json) |
| Diez archivos de laboratorio por GLAUQUIR | Ejecuciones terminadas, con semilla de 64 ceros | Resumen del taller y registros individuales |
| Siete fragmentos de los manuales | Estructura conforme a los esquemas | [Registro de fragmentos](evidence/revision_documental_2026_11_04/fragmentos_manuales.log) |
| Traslados y hashes | 58 destinos presentes y 47 evidencias intactas | Prueba documental e inventario de traslados |

El comprobador documental ahora verifica anclas de encabezados ATX y anclas HTML
explícitas, además de destinos locales. Tiene regresiones para secciones ausentes,
acentos, encabezados repetidos y ejemplos dentro de bloques de código. Los metadatos
de distribución generados quedan fuera del recorrido. La prueba de traslados
comprueba rutas y hashes; no necesita reformatear los snapshots históricos.
Solo esos cinco snapshots tienen una excepción explícita al máximo de líneas;
los límites del código y de la documentación redactada se mantienen.

Los verificadores de las unidades 5, 6 y 7 comprueban admisión y propiedades;
no recorren todas sus ramas. El de la Unidad 8 compara siete presentaciones con
el canon, dos semillas y tres pasos, con restauración. Las diez ejecuciones
automáticas de laboratorio no equivalen a explorar todas las decisiones posibles.

## Reparación y pasada complementaria

Se reprodujeron los dos fallos comunicados: Ruff I001 en el import de
`test_reference_dodge_contexts.py` y Bandit B101 en su aserción. Se ordenó el
import y se registró exclusivamente esa aserción revisada, que comprueba un
contexto positivo y dos negativos de Dodge. Las cuatro entradas existentes de
Bandit cuyas aserciones cambiaron de tipografía se actualizaron conservando sus
cantidades. La política sigue bloqueando los hallazgos nuevos sin revisar.

El primer intento completo de esta pasada terminó con 17 de 18 grupos aprobados:
la huella de las transcripciones del simulador todavía esperaba las comillas
anteriores. Se compararon 100 trayectorias con el código previo y el actual;
resultados, trazas y RNG coinciden al normalizar únicamente esas comillas.
Después se actualizó la huella esperada y se repitió el verificador completo.
La [comparación de transcripciones](evidence/reparacion_y_revision_2026_11_04/transcripciones.json)
conserva las dos huellas y el alcance de la comprobación. El intento previo
permanece registrado como fallido.

La consola usa dos puntos y punto y coma como separadores, `->` para resultados
y destinatarios, y `-` para datos ausentes en tablas y plantillas. Los diálogos
de Faro de Niebla y Central Clasificadora usan comillas dobles rectas, con los
incisos ajustados. Se mantienen tildes, signos de apertura, voseo, chilenismos y
el contenido narrativo. Una regresión comprueba que los destinatarios se muestran
una sola vez, tanto si la oferta ya trae la etiqueta como si la añade GLAUQUIR.

Se modificaron únicamente textos en 72 archivos de paquetes: plantillas de
presentación o parlamentos. La comparación estructural contra el estado inicial
comprueba que no cambian claves, números, condiciones, efectos ni destinos.
Los digests anteriores y nuevos quedan registrados. Los guardados anteriores
requieren el paquete original; no se implementó una migración automática.

La revisión de redacción corrigió el tratamiento del lector en el inicio rápido,
la terminología de los manuales, las tildes del cierre PA-001 y las rutas del
ejemplo de balance. Se agregaron índices de manuales, informes operativos y
archivo histórico, sin nuevos traslados. Las guías de Tegularis distinguen ahora
la práctica inicial del combate completo de las etapas posteriores. Las notas
de mantenimiento de ADR e informes orientan hacia los verificadores actuales
sin cambiar decisiones, cifras ni resultados originales.

La tipografía es una preferencia de esta entrega. Las guías editoriales no
consideran incorrectas por sí mismas las rayas ni las comillas tipográficas.
La corrección se centra en claridad y consistencia y conserva el registro chileno.
Los documentos en inglés mantienen su idioma.

### Comprobaciones de la pasada complementaria

Las evidencias nuevas se guardan en
[`reparacion_y_revision_2026_11_04`](evidence/reparacion_y_revision_2026_11_04/).
Las 72 evidencias que ya existían al comenzar conservan sus bytes.

| Control | Resultado | Evidencia nueva |
|---|---|---|
| Verificador completo | Código 0; 18 de 18 grupos aprobados | [Registro final](evidence/reparacion_y_revision_2026_11_04/check_gisela_full_final.log) |
| Motor, contratos, bibliotecas y Tegularis | 841 pruebas y 128 subpruebas aprobadas | Grupo inicial del registro final |
| Herramientas | 69 pruebas y 100 subpruebas aprobadas | Segundo grupo del registro final |
| Ruff, Radon, Bandit, calidad, enlaces e invariantes E0 a E3 | Aprobados; Bandit sin bloqueantes | Registro final |
| Seis rutas de Faro y Central con restauración | Código 0 en las seis | Registro final |
| Admisión del taller | 87 admitidos y 10 rechazos previstos, sobre 97 paquetes | [Detalle](evidence/reparacion_y_revision_2026_11_04/admision.jsonl) |
| Seis verificadores docentes | Código 0 en los seis | [Resumen](evidence/reparacion_y_revision_2026_11_04/taller.json) |
| Wheel y CLI fuera del repositorio | Código 0; entorno virtual nuevo con dependencias instaladas | [Resultado](evidence/reparacion_y_revision_2026_11_04/wheel_cli_red.log) |
| Contenido de la wheel | 172 archivos comparados, incluidos 75 recursos JSON; bytes idénticos a las fuentes | [Comparación](evidence/reparacion_y_revision_2026_11_04/wheel_contenido.json) |
| Integridad, copias y tipografía | 72 evidencias originales intactas; 72 paquetes con cambios solo textuales | [Comparación](evidence/reparacion_y_revision_2026_11_04/integridad.json) |

El primer intento de verificar la wheel falló por resolución de red dentro del
sandbox. Se conserva ese registro como intento fallido. La repetición fuera del
sandbox descargó las dependencias y aprobó el verificador existente; no utilizó
dependencias prestadas del entorno anfitrión.

La ejecución final completa duró 212,89 segundos. Sus metadatos usan UTC; el
cierre corresponde al 4 de noviembre de 2026 en la zona America/Santiago.

## Límites

La admisión de paquetes y los verificadores estructurales no demuestran ejecución
de todas las ramas. Los controles de referencia no evalúan automáticamente archivos
creados por alumnos. Siguen pendientes las pruebas pedagógicas con personas reales,
la cobertura de la reconstrucción autónoma y la aceptación gráfica de Ren'Py.
La validación estructural de fragmentos no comprueba sus referencias semánticas
en un paquete completo. La nueva comprobación de la wheel y las CLI es independiente
de los recorridos pedagógicos y no certifica la totalidad de sus ramas.
No se publica una versión como parte de esta revisión.
