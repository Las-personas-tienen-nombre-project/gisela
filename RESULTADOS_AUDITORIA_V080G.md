# GISELA v0.8.0 — auditoría general de cierre (v0.8.0g)

## Alcance y fuente

Base: repositorio completo de `GISELA_v080f_Observe_Act_integracion.tar.gz`. No se cambian las reglas de combate, los balances, las cartas, las políticas NPC ni el protocolo de Act. Los cambios correctivos se limitan a rutas de pruebas de presentación y enlaces de documentación. Los dos árboles existentes se mantienen.

## Hallazgos reproducibles y correcciones

1. **Pruebas de presentación del árbol importable:** siete casos de `gisela/engine/tests/test_author_presentation_v080.py` buscaban `10_balance_v078.package.json` dentro de `gisela/gisela/packages`, que no contiene ese archivo. Se corrigió la raíz relativa hacia el paquete realmente distribuido. Una segunda prueba duplicada de `test_public_presentation_v080f.py` tenía el mismo defecto de ruta y se corrigió. La ejecución dirigida de ambos archivos con `--import-mode=importlib` terminó en **14 aprobadas**.
2. **Documentación:** el verificador de enlaces locales señaló 18 destinos inexistentes en `README.md`, `contracts/README.md` y `engine/README.md`. Se corrigieron las rutas relativas y `python tools/check_doc_links.py` devuelve OK. La comprobación dirigida de herramientas `tools/test_quality.py` y `tools/test_doc_links.py` terminó en **16 aprobadas, 33 subpruebas**.
3. **Controles estructurales:** `python tools/check_quality.py` terminó OK: 700 líneas/archivo, 64 líneas/función, 3 parámetros explícitos (con la excepción histórica expresamente codificada para `new_session`). `compileall` terminó sin errores.

## Regresión del kit original

Se ejecutó `python tools/check_gisela.py --full --timeout 120` sobre la base **antes de las correcciones**. Su resultado fue **11/18 grupos aprobados**. Las seis rutas narrativas de extremo a extremo (Faro de Niebla y Central Clasificadora) y los invariantes E0–E3 terminaron correctamente. El grupo del motor llegó al límite de 120 segundos y no puede aprobarse bajo ese límite. El grupo de herramientas presentó dos fallos: los enlaces locales ahora corregidos y una comprobación que necesita Ruff. Los grupos Ruff (lint y formato), Radon y Bandit no pudieron ejecutarse porque las herramientas no están disponibles en este entorno. Se intentó instalarlas, pero la resolución de paquetes falló por falta de conectividad. No se sustituyen por una falsa certificación.

Una ejecución extensa de la regresión del motor se interrumpió luego de **701 pruebas aprobadas, una omitida y siete fallidas**; las siete fallidas eran las rutas erróneas de `test_author_presentation_v080.py`, corregidas y repetidas con éxito. La ejecución completa posterior **terminó con 795 pruebas aprobadas, una omitida y 128 subpruebas aprobadas** en 319,02 segundos (exit 0); véase `evidence/v080g/core_final.log`. La prueba omitida depende de un paquete productivo externo que no está instalado.

## Seguridad: cobertura efectiva y límites

- Se comprobaron los casos dirigidos para rechazar un componente desconocido, raíces o rutas privadas, referencias incompatibles, destinos inexistentes y declaraciones inválidas. La proyección declarativa lee exclusivamente el documento público de Observe.
- La prueba de Act confirma una habilidad dirigida a un destinatario ofertado, el rechazo de un comando con revisión vencida y de un identificador inexistente; los rechazos no mutan la sesión.
- La inspección AST dirigida de `author_presentation.py`, `actuation_public.py`, `presentation.py`, `glauquir.py` y `semantic_validator.py` no encontró llamadas a `eval`, `exec`, `compile`, `pickle`, `os.system` o `subprocess` en esas rutas, salvo lectura JSON mediante `loads` en el validador. Este examen **no equivale a Bandit** ni a una auditoría de seguridad de todo el código.
- Las pruebas internas de la política estática, excluida únicamente la comprobación que ejecuta Ruff, finalizaron con **12 aprobadas, 1 no seleccionada y 5 subpruebas aprobadas**. Bandit, Radon y Ruff: **no certificados** por dependencia ausente. Revisar la política del repositorio en `docs/guides/VERIFICACION_GISELA.md` y ejecutar el kit en un entorno con `requirements-dev.txt` instalado antes de publicación.

## Decisión: parámetros dinámicos de habilidades por Act

**No incorporarlos en v0.8.0.** El encuentro actual utiliza instancias de habilidades con destinatarios previamente definidos y públicamente ofertados. Observe entrega un `action_id` por instancia; Act comprueba su autorización en la revisión vigente. Es suficiente para jugar el caso de validación sin tener que aceptar argumentos no comprometidos por la oferta.

Permitir parámetros arbitrarios en Act introduciría nuevos requisitos de esquema, admisión, autorización por valor y destinatario, caducidad, idempotencia, guardado, restauración y trazabilidad causal, además de la validación de las decisiones NPC. Hacerlo sin un caso autoral que lo exija aumentaría superficie de ataque y complejidad sin demostrar una necesidad funcional.

**Condición de reconsideración:** cuando un paquete real requiera elegir un parámetro que no pueda representarse razonablemente mediante un conjunto acotado de acciones autorizadas, diseñar primero una oferta de **opciones tipadas y acotadas publicada por Observe**, no un campo libre enviado directamente a Act. El motor deberá validar el par oferta/selección y la revisión en una sola transacción, sin introducir un segundo motor de reglas en el cliente. Documentar compatibilidad con acciones antiguas y pruebas adversariales antes de implementarlo.

## Criterio de salida

Esta auditoría corrige fallos comprobados y cierra la decisión arquitectónica; **no certifica una publicación final** mientras el kit completo, incluida la política estática Ruff/Radon/Bandit, no termine en 18/18 grupos satisfactorios.
