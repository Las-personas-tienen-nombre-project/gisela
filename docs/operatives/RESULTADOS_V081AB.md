# GISELA v0.8.1a a b: Resultados

Registro histórico: describe la entrega y el entorno examinados entonces. Para las comprobaciones de esta revisión, consulte el [informe actual](../../CHANGELOG.md).

## Alcance

Fuente: `gisela.tar(10).gz`. Tres variantes autorales completas de Tegularis; mejoras genéricas del renderizador textual de GLAUQUIR; sin cambios a reglas, cartas, RNG, actuation, autorización, DSL ni datos causales.

## Pruebas ejecutadas

- Pruebas específicas de las variantes: **6 aprobadas** (`engine/tests/test_layouts_v081.py`).
- Pruebas previas de presentación, integración Act/Observe y calidad: **25 aprobadas**.
- Límites estructurales: **aprobados**, sin elevar umbrales.
- Tres partidas completas con `--seed` igual a 64 ceros y `--auto`: **victoria en las tres**.
- Trazas de las tres partidas: **idénticas, 816 entradas cada una**.
- Composición y guardado final mediante cliente público: **comprobados**.

La prueba unitaria de equivalencia incluye las mismas 18 decisiones iniciales para las tres composiciones. Los eventos se renderizan sin consultar el estado privado ni repetir dados.

## Regresión oficial

La verificación oficial `python tools/check_gisela.py --full --timeout 600` terminó con **13/18 grupos aprobados**. Motor y contratos: **849 aprobadas, una omitida y 128 subpruebas aprobadas**. Los seis recorridos con restauración, invariantes E0 a E3, enlaces y calidad estructural aprobaron. Los cinco grupos sin aprobar se deben a la ausencia de Ruff, Radon y Bandit (uno de ellos es la prueba de herramientas que invoca Ruff). No hay certificación local completa de los análisis estáticos. Véase `docs/operatives/evidence/v081ab/full_check.log`.

## Limitaciones

La salida textual es un renderizador de propósito general, no un diseñador visual. El historial se acota a 10 acontecimientos en pantalla, conservando la secuencia y el orden publicados. El cambio de paquete se realiza al iniciar la sesión; no hay migración de guardados entre distintas variantes.
