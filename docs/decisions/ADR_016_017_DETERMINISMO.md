# Normalizaciones técnicas para el determinismo

**ADR-016. Digest canónico. Estado: DECIDIDO por ejecución de la sugerencia solicitada.** Se establece el perfil `GISELA-CJSON-1`, con objetos ordenados por clave Unicode, listas en su orden original, decimales normalizados y SHA-256 con prefijo de separación de dominio. El resultado se guarda como 64 caracteres hexadecimales. La documentación normativa está en `docs/determinism/DIGEST_CANONICO.md`.

**Motivo:** los guardados deben detectar cambios en las definiciones sin depender del orden de claves, espacios o saltos de línea. Se evita la complejidad de decidir qué colecciones del paquete podrían reordenarse, por lo que todas las listas conservan su orden. Los recursos externos al JSON quedan fuera del hash y esa limitación se declara expresamente.

**ADR-017. RNG de contador. Estado: DECIDIDO por ejecución de la sugerencia solicitada.** Se fija `sha256_counter_v1` con semilla de 32 bytes, contador serializable, bloques SHA-256, codificación big endian y extracción uniforme por rechazo. La documentación normativa se encuentra en `docs/determinism/RNG_SHA256_CONTADOR.md`.

**Motivo:** la reproducción no debe depender de `random` de Python ni del anfitrión. El módulo independiente entrega nuevo estado sin mutar el anterior, lo que facilita su integración posterior en la semántica transaccional. La prueba de rollback real sigue pendiente porque no existe el ejecutor.

Ambas ADR precisan campos que ya existían en los schemas 1.2; no cambian las enumeraciones ni la forma estructural. Por esa razón no se publica un schema 1.3 artificial. La versión normativa de la arquitectura pasa a 1.4, y los tests añaden vectores para comprobar que el perfil documentado y su implementación coinciden.
