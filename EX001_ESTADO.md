# EX-001 — estado de extracción desde la versión actualizada

Fuente: `las-personas-tienen-nombre(20261031-201649).zip`.

- Conserva el código de GISELA, MARY, TRAITS, DICE y el normalizador de condiciones.
- Conserva contratos, pruebas y documentación técnica existente.
- No incluye el demo Ren'Py, su copia vendorizada ni el archivo histórico `archive/`.
- El wheel no debe incluir `gisela/packages/` ni otros relatos. Estos paquetes se conservan en el árbol candidato para no perder fixtures y rutas de prueba; **no están liberados bajo Apache 2.0**.
- `pyproject.toml` tiene nombre y versión provisional; se elimina la dependencia de los tags `demo-v*`.
- Próximo paso: aislar definitivamente herramientas de recorrido dependientes del demo; comprobar suites en entorno limpio; instalar desde pip en el demo; fijar una versión de Codeberg y ejecutar sus verificaciones.
- No publicar sin revisar la titularidad y el permiso de difusión de todos los relatos y el texto íntegro de licencia.

- Pruebas: la primera ejecución no pudo recolectar dos módulos por faltar herramientas de recorrido; se recuperaron los auxiliares desde la misma fuente. La ejecución posterior excedió el tiempo disponible, por lo que la regresión integral queda SIN ACREDITAR en este candidato.
