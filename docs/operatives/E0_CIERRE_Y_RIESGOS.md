# GISELA E0: Plan, cierre y riesgos residuales

Registro histórico: las herramientas, cifras y pendientes que siguen
corresponden a la etapa examinada. Para ejecutar los controles actuales,
consulte la [guía de verificación independiente](../guides/VERIFICACION_GISELA.md).

**Base:** ZIP (8) + núcleo TRAITS + parche TRAITS-ALBERTO/DICE; este cierre se aplica incrementalmente sobre esas integraciones. **Fuera de alcance:** ejecutar `evaluate`, mostrar dados, Ren'Py y transporte GISELA<->GISELA.

## E0.1; Correcciones locales

- Validar perfiles DICE con IDs de bandas exclusivos; primer intervalo como reserva inferior; `evaluate()` valida nuevamente un perfil no compilado. Entradas y código de DICE continúan independientes.
- Construir y validar `Observe` del candidato antes de confirmar cualquier acción, cancelación, pendiente o creación de sesión. Las consultas y exportación están protegidas durante escrituras.
- Añadir pruebas de fallos inducidos de proyección, incluso un objeto visual que incumple el schema. Validar `result` contra los códigos de dominio que ya produce el motor. **Riesgo residual:** coste adicional de validar cada proyección; considerar métricas de rendimiento antes de cambiar el caché de validadores.

## E0.2; Frontera de ejecución

- Un solo escritor por sesión (candado reentrante). Ningún turno adicional, y ninguna mutación de ALBERTO o MARY por el gateway.
- `Principal` establecido por el anfitrión, capacidades separadas, proyección únicamente si se concede `observe_player`; prohibida mutación directa tras enlazar el gateway.
- `command_id` separado de `action_id` y de futuros `evaluation_id`, respuesta deduplicada ligada al hash del comando y al principal. El recibo se re-filtra con los permisos **actuales**; revocar un principal invalida sus enlaces anteriores.
- Pruebas de carrera con solicitudes competidoras, revocación y rechazo de suplantación. **Riesgo residual:** no hay autenticador incorporado ni autorización de audiencia por personaje; la configuración la controla el anfitrión confiable.

## E0.3; Persistencia, replay y errores

- Checkpoint único de estado y recibos. Escritura en fichero temporal con sincronización y sustitución atómica, candado POSIX contra segundo propietario local, recuperación por `restore_session` y revisión del replay pendiente.
- Si falla la escritura antes de sustituir, rollback; si el reemplazo pudo ocurrir, bloquear el gateway hasta reconciliar.
- Validar formato de recibos, pertenencia de sesión y digest; rechazar JSON duplicado, no finito y archivos grandes. Respuestas externas no contienen mensajes diagnósticos internos.
- Pruebas de guardado/restauración con recibo, pendiente, falla inducida, fallo incierto, corrupción, reintento y consulta sin cambios. **Riesgo residual:** no existe MAC/cifrado de snapshots no confiables, archivado automático de recibos ni recuperación multi-host.

## E0.4; Cierre documental y trazabilidad

- ADR-020, arquitectura de frontera y actualización del contrato DICE hacia el futuro **v1.4**.
- Contrato matemático `dice.profile.v1` **sí** ejecutable; `evaluate` declarativo, perfiles en paquete y `pending_evaluation` continúan **propuestos**, sin implementación ni esquemas v1.4 falsamente anunciados.
- Registro estructurado de invariantes y test de su anclaje; verificar que **cada test nuevo E0** aparece en el registro, que cada anclaje existe y que todos los comandos de QA se ejecutan.
- La integración TRAITS-ALBERTO y la composición TRAITS-DICE previas mantienen responsabilidades, versiones y suites existentes; la puerta E0 no cambia sus contratos.

## Restricciones no resueltas antes de E1

1. Normalizador de autoría `evaluate`: produce el perfil materializado, los participantes, los valores de S.O.F.I.A., las contribuciones TRAITS y las ramas declarativas.
2. Catálogo de perfiles por paquete, versionado 1.4 y validación de fuentes de datos y privacidad de resultados.
3. Un único proceso causal pendiente que permita decisiones auxiliares tras una tirada fijada, sin reroll.
4. Reglas de audiencia distintas del protagonista; integración segura de otros principales/pares.
5. Transporte distribuido, monitor de rendimiento y almacenamiento alternativo para partidas muy largas.

**Criterio de éxito:** `python tools/check_project.py` debe terminar con código 0; las suites independientes y los recorridos CLI son obligatorios. No se declara aprobado el verificador integral hasta ver su salida completa.

## Verificación de cierre (revisión final)

La prueba integral `python tools/check_project.py` terminó con código de salida **0** sobre la integración E0. También se volvió a ejecutar `python -m unittest discover -s gisela/engine/tests -p 'test_*.py' -q` con **273/273** pruebas aprobadas. La suite acumulada consta de: ejecutor 273, contratos 150, TRAITS 25, DICE 15, MARY 21 y pruebas de calidad 10 (**494** en total). Se ejecutaron además admisiones y recorridos CLI de H2, H3.4, H4 y H4.5/GLAUQUIR. El catálogo de invariantes contiene **56 anclajes normativos**, incluidos los **42 tests específicos de E0**. Estos conteos se refieren a la ejecución efectuada sobre la copia verificada; no a un repositorio local externo.
