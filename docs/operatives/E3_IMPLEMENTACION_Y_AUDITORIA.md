# E3 — Informe de implementación, pruebas y auditoría

**Base:** `GISELA_E2_codigo_integrado.zip`, que contiene E2 v1.4 y ADR-022. Este documento no implica modificaciones al repositorio local del autor.

| Etapa | Implementación |
| --- | --- |
| E3.1 | ADR-023 aprueba las políticas mínimas; retirada y repetición diferidas. |
| E3.2 | Trece esquemas v1.5 y validador semántico; snapshots anteriores intactos. |
| E3.3 | Suspensión antes de rama, RNG confirmado y resultado privado; vista limitada a dados/banda. |
| E3.4 | `continue_evaluation`, replay de datos efectivos, consecuencias y MARY atómicas. |
| E3.5 | Restauración adversarial de resultado, RNG y solicitudes auxiliares; gateway persistente. |
| E3.6 | Pruebas nuevas, matriz de invariantes, control estructural y verificador integral. |

## Hallazgos y correcciones

1. El replay original de E2 solo comprendía decisiones auxiliares; se añadió una cinta de resultados visibles a `DecisionReplay` sin cambiar el RNG de DICE ni crear otro ejecutor.
2. Los pasos automáticos y transiciones podían producir resultados visibles después de efectos provisionales; la preparación publica solo RNG/resultado y reconstruye todo lo demás cuando se continúa.
3. Las tiradas ocultas intercaladas no son entradas de la cinta y no se confunden con resultados fijados.
4. La restauración verifica opciones auxiliares reales después de continuar un resultado, en vez de confiar en opciones editables del snapshot.
5. El código se separó en `evaluation_pending.py` y se mantuvieron los techos de 500 líneas por archivo, 30 por función y tres parámetros explícitos.

## Riesgos residuales

- El cliente controla el momento visual de reconocimiento; GISELA solo exige un nuevo comando autorizado.
- Guardados manipulados por un actor con acceso de escritura total no quedan protegidos por una firma independiente del anfitrión. La validación causal no sustituye a la autenticación ni al aislamiento de archivos.
- El coste de replay aumenta con la longitud de una intención; hay presupuesto estructural y límite de cinta.
- No se han implementado retiradas posteriores ni tiradas repetidas voluntarias. Permanecen fuera del alcance aprobado.

La ejecución real de verificadores, el resultado de aplicación del parche y el registro final se entregan por separado. Ninguna prueba debe considerarse aprobada antes de ejecutarse.
