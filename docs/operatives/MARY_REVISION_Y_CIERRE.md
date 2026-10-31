# MARY v1. Auditoría, etapas y cierre

## Punto de partida

El código inspeccionado ya ejecutaba hechos, reglas reactivas, condiciones y transacciones en `gisela/engine`. La dependencia directa de `conditions.py` respecto de las estructuras de sesión impedía reutilizar su lenguaje lógico. `reactions.py` tiene una autoridad de confirmación y un límite causal que MARY no debe duplicar.

## Etapa 1. Contrato compartido

Se extrajeron operadores booleanos y comparación tipada a `narrative_conditions`. GISELA conserva el lector de sus entidades; MARY recibe solo hechos y valores explícitos. Debilidad detectada: números decimales leídos desde JSON estricto pueden ser `Decimal`. La comparación compartida los admite sin confundir `bool` con un número.

## Etapa 2. Biblioteca autónoma

MARY valida declaraciones con un schema propio y evalúa condiciones, hechos distintos y pesos. Los objetivos tienen modo `milestone` o `current`; el plan y su progreso pueden serializarse y emplearse en otro anfitrión. Debilidad detectada: permitir yields en objetivos reversibles repetiría recompensas, por lo que se prohíbe. También se rechazan IDs duplicados y umbrales imposibles.

## Etapa 3. Integración transaccional

El adaptador de GISELA entrega contexto neutral y transforma únicamente yields de hechos declarados. La resolución participa en las rondas reactivas y queda bajo la misma confirmación que los cambios de ALBERTO. Debilidad detectada: dos yields podían registrar el mismo hecho; se evita reproducir un hecho ya presente en el borrador. Se comprueba el rollback ante una reacción posterior fallida.

## Etapa 4. Proyección, restauración y pruebas

Solo misiones visibles y sus objetivos públicos llegan a Observe y al comando `misiones` de GLAUQUIR. La admisión comprueba referencias a hechos y variables; la restauración verifica IDs y tipos del progreso. Los paquetes sin sección MARY siguen funcionando. La calidad estructural se extendió a las bibliotecas nuevas.

## Simplificaciones adoptadas

No hay bus de eventos adicional, gestor de misiones autónomo con escritura ni segundo evaluador lógico. MARY no intenta pronosticar todas las rutas futuras. La integración utiliza las operaciones `record_fact`, `settle`, `Observe` y el digest existentes. La API autónoma consta de cinco operaciones públicas.

## Riesgos y límites conocidos

- El evaluador examina todos los objetivos declarados en una frontera causal. El máximo inicial de 256 objetivos y 128 misiones limita el trabajo; la optimización mediante dependencias queda condicionada a mediciones.
- Solo hay lectura de hechos y variables; otros datos de ALBERTO necesitan proyecciones neutrales expresamente autorizadas.
- `scope` conserva metadatos, pero todavía no gestiona campañas ni passwords de jornadas.
- No existe automatismo para demostrar que una oportunidad futura sigue siendo alcanzable.
- No se ha extraído ALBERTO o S.O.F.I.A. a bibliotecas independientes; la separación por contratos queda como un trabajo posterior.
- La validación de un guardado comprueba estructura, procedencia de paquete y consistencia de IDs, pero no certifica criptográficamente que nadie lo haya manipulado.

## Evidencias

Las pruebas de unidad autónoma están en `mary/tests/test_mary.py`, y las de integración en `gisela/engine/tests/test_mary_integration.py`. El mapeo exigible entre invariantes y tests está en `INVARIANTES_MARY.md`. Los números finales de la batería se registran al terminar la verificación integral.

## Verificación final y entrega

En la copia de implementación se ejecutaron por separado las pruebas autónomas de MARY, los contratos, las pruebas del ejecutor y el control de calidad. Como el árbol de origen se reconstruyó a partir de una base histórica y no conserva exactamente el manifiesto instalado de H4.5f, el parche no reemplaza el manifiesto del usuario. Se incorpora `tools/update_manifest.py`, que actualiza los hashes de las entradas **ya existentes** y agrega únicamente los archivos nuevos de MARY, sin eliminar ni reemplazar otras rutas. Debe ejecutarse tras aplicar el parche, antes de `sha256sum -c MANIFEST.sha256`. Su salida también debe quedar sometida a pruebas.

Comprobaciones independientes ejecutadas en la copia de verificación: MARY 21, ejecutor 214, contratos 148, calidad 6 (incluidas dos pruebas de integridad del actualizador): **389 pruebas**. `check_project.py` excede el límite de tiempo de la ejecución de herramienta; las baterías se ejecutaron separadamente.
