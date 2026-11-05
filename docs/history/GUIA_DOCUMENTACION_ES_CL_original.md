# Guía de documentación técnica en español de Chile

Registro histórico: este documento conserva el estado de su etapa original.
Consulte el [índice del archivo](README.md) para distinguir sus antecedentes
de las instrucciones vigentes.

## Alcance

Este proyecto utiliza español de Chile para los documentos de diseño, revisión, operaciones y pruebas. La prosa debe ser precisa, natural y formal, sin intentar reproducir por escrito modismos coloquiales que no correspondan al público de un manual técnico. Los identificadores, comandos, campos y valores de JSON conservan su grafía inglesa por decisión arquitectónica.

## Redacción

Se preferirán párrafos desarrollados que establezcan una idea, sus condiciones y sus consecuencias. Las oraciones breves sirven cuando separan pasos operativos, pero no deben reemplazar sistemáticamente relaciones de causalidad por frases telegráficas. En instrucciones se utilizará la forma impersonal o el tratamiento de usted cuando haga falta dirigirse al lector.

Se escribirán tildes y signos de apertura de interrogación o exclamación cuando correspondan. Se usarán signos convencionales del español y puntuación corriente. Se evitarán flechas decorativas, emoticonos, iconos, símbolos de estado vistosos y comillas tipográficas especiales en los documentos redactados para esta entrega. El guion y la barra vertical pueden aparecer por su función técnica en rutas, comandos y tablas Markdown.

Los anglicismos se emplearán solamente cuando constituyan nombres de operaciones o términos técnicos útiles, como `schema`, `snapshot`, `RNG`, `commit`, `CLI` o `frontend`. No se reemplazarán términos de programación por traducciones imprecisas. En el resto de la explicación se preferirán expresiones claras como "estado confirmado", "validación", "guardar una sesión" y "reglas de ejecución".

## Trazabilidad

Cada documento debe indicar su alcance y su estado. Una implementación probada no equivale a un motor terminado. Se debe distinguir entre DECIDIDO, PROPUESTO, PENDIENTE, DESCARTADO y VERIFICADO. No se debe usar VERIFICADO para una capacidad solo documentada o cubierta por un JSON Schema.

Las decisiones técnicas del proyecto no pueden alterar hechos del manuscrito ni reemplazar la intención del autor. Las tres guías editoriales adjuntas sirven de referencia cultural y lingüística, pero no autorizan por sí solas a cambiar el contenido literario.

## Política de mantenimiento desde H3

Los archivos técnicos mantenidos no podrán superar 500 líneas, y las funciones Python no podrán superar 30 líneas de código, sin contar el docstring inicial, ni aceptar más de tres parámetros explícitos. Los receptores self y cls no cuentan como parámetros aportados por quien llama. Se debe dividir por responsabilidad concreta, no por alcanzar una cantidad artificial de clases. Se aplicarán los principios SOLID cuando reduzcan acoplamiento y faciliten pruebas, sin introducir abstracciones que todavía no resuelvan un problema real.

Todo cambio funcional requiere pruebas para éxito y fracaso, documentación de entradas, salidas e invariantes, actualización del roadmap y registro de los hallazgos relevantes. El control `python tools/check_project.py` incluye `tools/check_quality.py`; un archivo mantenido que incumpla los límites falla la verificación. Los archivos del archivo histórico y el manuscrito de referencia permanecen intactos y se encuentran fuera de esta política, según lo explicado en `docs/operatives/H3_REVISION_PLAN_IMPLEMENTACION.md`.


## Criterio de legibilidad y Zen de Python

La documentación y el código seguirán el principio de que lo explícito, simple y legible es preferible a una abstracción difícil de explicar. Cada función tendrá una responsabilidad identificable, hasta tres parámetros explícitos y errores claros, sin silencios ni valores adivinados ante entradas ambiguas. Los contextos de ejecución podrán agrupar datos realmente relacionados para evitar listas extensas de parámetros. Se evitará crear una clase solo para satisfacer una métrica si un módulo o una función pequeña bastan.
