# GISELA v0.8.2: Resultados parciales

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](REVISION_DOCUMENTAL_2026_11_04.md).

## Línea base de repositorio actualizado

- `python tools/check_quality.py`: APROBADO.
- `python -m pytest -q tools/test_quality.py`: 11/11 APROBADAS.

## Implementación en esta copia

- v0.8.2a: contrato aditivo para vistas y tablas genéricas, pivote por entidad y
  recursos públicos, renderizador tabular con variante vertical y ausencia visible.
- v0.8.2b: selección de eventos por clases y filtro escalar, límite y orden originales.
- No implementados/certificados: v0.8.2c/d/e.

## Controles posteriores

- Calidad estructural: APROBADA después del incremento.
- Pruebas dirigidas (incluyendo v0.8.0): 65 APROBADAS.
- Suite general: se inició, pero fue interrumpida por límite del entorno; **no
  se declara aprobada**.
- No hay certificación todavía de partidas completas, comparación de las tres
  variantes, guardado/restauración v0.8.2, seguridad global ni regresión completa.

## v0.8.2c: Incremento de correlación causal

**Implementado:** campo aditivo `causal_execution_id`, propagación mediante
contexto de efectos, persistencia en traza confirmada y Observe, agrupación
opcional `group_by: action` con fallback plano para inicios ausentes.

**Pruebas dirigidas:** ver resultados de la ejecución de la entrega. Incluyen
Act rechazado y obsoleto, restauración idéntica, continuación determinista,
identificadores independientes, filtro con eventos intercalados, ventana
truncada, compatibilidad con trazas antiguas e IDs inválidos.

**Ejemplo real:** `13_tablas_causal_v082c.package.json`; se admitió, abrió
sesión, ejecutó cuatro Act públicos y presentó tabla + bloques causales sin
intervenir las reglas de Tegularis.

**No certificado:** fase v0.8.2d, fase v0.8.2e, regresión completa, partidas
completas de las tres variantes y seguridad de extremo a extremo.

### Ejecución de validación v0.8.2c (4 de noviembre de 2026)

- `python tools/check_quality.py`: APROBADO, sin cambios a umbrales.
- `python -m pytest -q tools/test_quality.py`: 11 APROBADAS en ejecución inicial.
- Regresión dirigida (módulos de actuación, cartas, presentación y calidad):
  **51 APROBADAS**.
- Pruebas nuevas de correlación (incluidas en la regresión general):
  **6 APROBADAS**.
- Regresión de motor: `PYTHONPATH="$PWD:$PWD/gisela/engine/tests" python -m pytest -q --import-mode=importlib gisela/engine/tests`:
  **557 APROBADAS, 1 OMITIDA, 57 subpruebas aprobadas (85,26 s)**.
  Omisión documentada: `test_glauquir_mud.py`, paquete externo no instalado.
- Ejecución del paquete `13_tablas_causal_v082c.package.json`: admisión,
  sesión nueva y cuatro comandos por `Act` satisfactorios; proyección
  tabular y grupos causales comprobada. Esta ejecución **no equivale**
  a una partida completa.
- Suite de repositorio completa fuera de `gisela/engine/tests`: no ejecutada.
- Ruff/Bandit/Radon y tres partidas completas de Tegularis: no certificados.

## v0.8.2d: Resultados de esta entrega

- Línea base antes de modificar: `tools/check_quality.py`: conforme;
  `tools/test_quality.py`: 11 aprobadas.
- Schema v1.5 ampliado de modo **opcional** con `event_formats`; nuevo validador
  estático por tipo de acontecimiento y campos públicos permitidos.
- Proyección determinista: `semantic_role` y `display_text` se calculan desde
  copias de Observe. Se reutiliza `Styler` y no se añaden colores al motor.
- Ejemplo productivo `14_presentacion_semantica_v082d.package.json`:
  admisión real aprobada; la prueba de integración ejerce Observe/Act y restore.
- Pruebas dirigidas de nueva capacidad y correlación anterior: 20 aprobadas.
  La ampliación no bélica y literal de llaves se comprobaron después: 16 pruebas
  semánticas aprobadas.
- Control de calidad estructural: conforme (700/64/3), 11 pruebas de calidad
  aprobadas; compilación de módulos modificados aprobada.
- Suite más amplia de engine/contracts: **no certificada**. Una invocación sin
  PYTHONPATH apropiado falló en importación de un test heredado; al usar
  `PYTHONPATH=.:gisela/engine/tests` con `--import-mode=importlib`, la ejecución
  avanzó hasta aproximadamente el 37 % y fue interrumpida por límite de tiempo.
  No se le atribuye un resultado favorable ni un defecto del motor.
- Ruff, Radon y Bandit: herramientas no instaladas; controles pendientes.
- La clasificación semántica por intención de operación confirmada sigue
  pendiente: en esta entrega se permite la etiqueta *autoral* restringida, sin
  derivarla del signo de una variable. No se ha certificado v0.8.2e.

## v0.8.2e: Integración y auditoría reproducible (4 de noviembre de 2026)

**Estado: INCOMPLETA / NO CERTIFICADA.** La entrega conserva íntegramente v0.8.2a a d.
Se añadió `gisela/engine/tests/test_release_v082e.py` como prueba de
regresión entre seis paquetes productivos. No se alteraron las mecánicas,
cartas, semilla, RNG, política NPC, esquemas Observe/Act ni umbrales de calidad.

### Evidencia que sí concluyó satisfactoriamente

- Línea base: `python tools/check_quality.py` conforme (700/64/3),
  `python -m pytest -q tools/test_quality.py`: 11 aprobadas.
- `python -m pytest -q --import-mode=importlib gisela/contracts`:
  **181 aprobadas y 63 subpruebas aprobadas**.
- `python -m pytest -q --import-mode=importlib` con los cuatro módulos de
  pruebas `test_release_v082e.py`, `test_presentation_views_v082.py`,
  `test_causal_execution_v082c.py`, `test_presentation_semantics_v082d.py`:
  **26 aprobadas (23,85 s)**.
- La nueva prueba admite y ejecuta seis variantes del mismo paquete:
  `11_presentacion_{participantes,decisiones,cronica}_v081`,
  `12_tablas_v082_parcial`, `13_tablas_causal_v082c` y
  `14_presentacion_semantica_v082d`. Con semilla fija, ejecuta doce Act
  autorizados, compara en cada paso actuación pública, estado lógico,
  traza, revisión y RNG; restaura las seis sesiones a mitad del recorrido.
  Esta prueba es una **secuencia parcial**, no seis partidas completas.
- `python tools/check_doc_links.py`: conforme.
- `python tools/verify_e{0,1,2,3}_invariants.py`: cuatro controles conformes.
- Control estructural repetido tras agregar las pruebas: conforme.

### Evidencia no aprobada o pendiente

- `tools/test_quality.py`, `tools/test_doc_links.py`, `tools/test_static_quality.py`
  y `tools/test_tegularis_campaign.py` ejecutados juntos:
  **64 aprobadas, 1 fallida, 40 subpruebas aprobadas**. El fallo
  `RuffPolicyTest.test_lint_and_format_boundaries` se debe a la ausencia del
  ejecutable `ruff`, que la prueba espera invocar (no se ha observado un
  defecto del código de aplicación en esa prueba).
- `ruff`, `radon` y `bandit` están ausentes; intento de instalación fallido
  por falta de resolución de red. Por tanto no se certifican lint, formato,
  complejidad ni análisis Bandit.
- La suite de motor completa y otra regresión dirigida larga se interrumpieron
  por tiempo antes del resumen final. Sus avances parciales **no cuentan como
  pruebas aprobadas**.
- Una primera invocación de la suite extensa recopiló el árbol de pruebas
  no canónico y encontró rutas de fixtures ausentes; otra invocación combinada
  sufrió interferencias de importación durante la colección. Se corrigió la
  selección para los grupos que sí terminaron y se conserva el diagnóstico.
- No se completaron tres partidas completas por GLAUQUIR, campañas de Tegularis
  con desenlace, el kit `check_gisela.py --full`, wheel instalada ni validación
  multi-plataforma. Por tanto **v0.8.2e no satisface los criterios finales**.
- La clasificación `damage`/`healing` aún es metadato de presentación autoral,
  no intención de operación confirmada; la documentación lo declara así.

### Reproducción

Desde la raíz del repositorio con dependencias de desarrollo instaladas:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
python tools/check_quality.py
python -m pytest -q --import-mode=importlib gisela/contracts
python -m pytest -q --import-mode=importlib \
  gisela/engine/tests/test_release_v082e.py \
  gisela/engine/tests/test_presentation_views_v082.py \
  gisela/engine/tests/test_causal_execution_v082c.py \
  gisela/engine/tests/test_presentation_semantics_v082d.py
python tools/check_gisela.py --full
```

Los registros brutos de esta sesión están en `docs/operatives/evidence/v082e/`. Las
invocaciones sin resumen final documentan progreso o interrupción, no éxito.

## Reparación local de integración y calidad (4 de noviembre de 2026)

Se recuperaron las conexiones de los incrementos v0.8.2a a d: admisión de vistas
nombradas, tablas públicas, selección y agrupación de eventos, formatos
semánticos y propagación transaccional de `causal_execution_id`. La comparación
de las seis presentaciones conserva estado lógico y RNG, con restauración
intermedia. Se añadieron regresiones de límites, habilidades anidadas y
propagación del contexto durante el ciclo de efectos.

Pytest selecciona ahora los paquetes canónicos bajo `gisela/` antes de la
colección, mediante `tools.pytest_canonical` y el modo `importlib`. Las copias
de fuentes de la raíz se conservan. También se corrigió el límite de plantillas
para contar 16 sustituciones, respetando las llaves literales.

Ejecución real de `.venv/bin/python tools/check_gisela.py --full`:

- **18/18 comprobaciones satisfactorias; código de salida 0.**
- Motor, contratos y bibliotecas: **834 aprobadas y 128 subpruebas aprobadas**.
- Herramientas: **65 aprobadas y 41 subpruebas aprobadas**.
- Ruff, formato, Radon, Bandit, límites estructurales, enlaces e invariantes:
  aprobados, conservando los umbrales existentes.
- Seis recorridos narrativos del kit: aprobados con restauraciones.

El [registro completo de la reparación](evidence/v082e/repair_check_gisela_full.log)
conserva comandos, resultados y tiempos del kit. Los apartados anteriores
mantienen la evidencia histórica de las entregas parciales. La certificación
de partidas completas adicionales por GLAUQUIR, wheel y otras plataformas
continúa pendiente según la auditoría v0.8.2e.
