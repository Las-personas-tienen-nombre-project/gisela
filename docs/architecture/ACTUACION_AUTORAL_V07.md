# GISELA: Integración incremental del reloj autoral v0.7

Registro del incremento indicado en el título. Sus pendientes describen esa etapa; consulte el [roadmap](../operatives/ROADMAP.md) y la [presentación actual](PRESENTACION_DECLARATIVA_V082.md) para las capacidades posteriores.

## Estado de esta entrega

Se implementó **la infraestructura de actuación** en el repositorio actualizado de GISELA, no una versión definitiva del combate de Tegularis. El diseño sigue siendo autoral. Las nuevas claves `actuation` de paquete y de snapshot son **optativas** y están limitadas al contrato 1.5. Los paquetes anteriores no activan el mecanismo.

### Capacidades nativas verificadas

1. Iniciativa única al iniciar el paquete: suma de STR, AWA, FOR efectivos y dado autoral; desempate por AWA, STR, FOR e identificador, consumiendo el RNG confirmado de GISELA.
2. Orden persistente en el snapshot, rondas y oportunidades separadas de `state['turn']` de la narración. El presupuesto de acciones se recalcula al iniciar cada turno del actor; se definen atributo principal, umbrales y contribución opcional de TRAITS en el paquete.
3. Las habilidades de NPC se ejecutan por la ruta nativa `execute_first_available`; el jugador solo puede seleccionar instancias propias. Los errores abortan el borrador completo, incluidos dados, identificadores y reloj.
4. Efectos de cartas con `actuation_turns`, `actuation_blocks_actions` y `on_actor_turn_start` (opcional). Las operaciones periódicas se ejecutan una vez al iniciar el turno del beneficiario y `on_expire` se invoca al vencer. La eliminación de la instancia de ALBERTO y los eventos de GISELA ocurren en la misma transacción.
5. Operación neutral `emit_message` con valores del DSL (`{damage}`, etc.). Proyecta mensajes únicamente tras confirmar la acción; no evalúa Python suministrado por el autor.
6. Comando de consola `--actuation --rounds 3` en GLAUQUIR. Guarda/restaura usando los snapshots nativos. El modo laboratorio se mantiene separado del flujo narrativo ordinario.

### Lo que **NO** debe declararse concluido

- El paquete de demostración contiene las 32 instancias del workshop original, pero **la mayoría de las cartas NPC todavía poseen `effects: []`**. Su selección automática no produce daño, escudo ni curación.
- Las prioridades utilizadas son una primera lista de prueba de la selección nativa, **no** las políticas finales de Clarisa, Gillius, Iosepus o Tegularis.
- No se implementaron los impactos independientes, `Magic Blast` parametrizado desde la selección del jugador, el cálculo completo de daño grupal, las redirecciones de Protección, Fénix, Pride, explosión final y tres finales dentro del DSL admitido.
- La ruta `actuation_step()` es una API de laboratorio de `GiselaSession`; todavía no sustituye la interfaz normal Observe/Act ni está expuesta por `ExecutionGateway`. No usarla como una frontera de confianza de producción.
- El reloj inicia en la creación de la sesión para el paquete opcional. El comienzo de un encuentro posterior dentro de una historia y la transición entre varios encuentros siguen sin contrato.
- La corrida global de pytest no completó antes del límite de ejecución; se interrumpió aproximadamente al 76 % sin fallos visibles hasta ese punto. **No es una certificación global**.

### Pruebas aceptadas

- `pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_actuacion_nativa_v07.py`: 17 pruebas aprobadas. Incluyen tres rondas, iniciativa única, desempates, recursos de actuación, rechazo sin mutación, reproducción por semilla, restauración, efectos vinculados, bloqueo de un turno completo, operación de mensajes y rechazo de snapshot adulterado.
- Batería dirigida con pruebas anteriores de NPC y práctica de Tegularis: 77 aprobadas.
- Se ejecutó GLAUQUIR durante 3 rondas con semilla fija, se exportó JSON nativo y se retomó una cuarta ronda desde el guardado.

### Uso

```sh
PYTHONPATH=. python -m gisela.cli.glauquir \
  --actuation --auto --rounds 3 \
  --seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  --package gisela/packages/tegularis_the_son_of_the_volcan/05_actuacion_v07_laboratorio.package.json \
  --save /tmp/tegularis-v07.json

PYTHONPATH=. python -m gisela.cli.glauquir \
  --actuation --auto --rounds 1 \
  --restore /tmp/tegularis-v07.json \
  --package gisela/packages/tegularis_the_son_of_the_volcan/05_actuacion_v07_laboratorio.package.json
```

### Pendiente antes de producción

Cerrar la admisión declarativa de habilidades con argumentos elegidos por el jugador; traducir las 32 cartas del diseño a consecuencias nativas; definir las prioridades condicionales y la secuencia de muerte/fin; añadir una ruta Observe/Act/gateway autenticada; verificar pruebas exhaustivas de transacción, consistencia de TRAITS, reactores y resultados. **No sustituir los scripts históricos por este paquete de laboratorio.**
