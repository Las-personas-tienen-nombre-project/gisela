# GLAUQUIR v0.7.3 y verificación v0.7.4

## Base y alcance

Construido encima del paquete `08_desenlaces_v072.package.json` de GISELA v0.7.2. Se preserva el DSL 1.5 y su modelo de actuación autoral, separado del turno narrativo.

### Contrato público

- `observe()` publica el bloque optativo `actuation`: ronda, actor, acciones restantes, orden, puntuaciones y dados de iniciativa, últimos acontecimientos y mensajes confirmados. La observación no muta el estado.
- El turno del jugador ofrece `actuation_skill` con el identificador real de instancia y `actuation_pass` solo cuando lo autoriza el paquete.
- El turno NPC ofrece exclusivamente `actuation_advance`; el anfitrión no elige su carta.
- `act()` autoriza por `session_id`, `revision`, `action_id` presente y habilitado en Observe. Se ejecuta sobre una copia, aplica el ciclo de actuación como fuente autoral y confirma mediante el `_commit` existente.
- El gateway ya implementado maneja identidad, capacidades e idempotencia por `command_id`; no existe una vía paralela nueva con más privilegios.
- Los desenlaces terminados se proyectan como `status=ended`, sin acciones, conservando el estado persistido y el identificador de desenlace de la política autoral.
- La consola de GLAUQUIR utiliza Observe/Act sin `--actuation`. Se mantiene la bandera anterior exclusivamente para comparar el laboratorio.

### Garantías comprobadas

- Rechazo de acciones ajenas, no ofrecidas y vencidas sin mutación.
- Igualdad entre estados y observaciones después de restaurar y continuar en dos sesiones, en una secuencia dirigida.
- Acceso autenticado y recibos idempotentes de gateway.
- Mensajes de `author_message` del historial confirmado, sin resultados provisionales.
- Reloj narrativo independiente de las oportunidades.

### Límites

- El guion publica texto y valores de daño confirmados. La tirada individual de ataque, evasión o daño de cada carta no siempre se conserva como evento público estructurado: GLAUQUIR **no la reconstruye ni inventa**. Sí muestra los dados de iniciativa y los resultados informativos existentes.
- Las cartas Protección y Bless conservan las decisiones autorales pendientes identificadas en v0.7.1; el presente cambio no las completa.
- Las pruebas de explosión y derrota de v0.7.2 se hicieron con estados preparados. Cuatro partidas ordinarias por Observe/Act terminaron en victoria; no se ha demostrado con partidas naturales la accesibilidad de derrota o destrucción mutua.
- La regresión general del motor se interrumpió por el límite de ejecución después de aproximadamente un 57 % sin fallos visibles hasta ese punto. No se certifica completa.
- El camino legacy `actuation_step()` permanece como interfaz local de laboratorio para compatibilidad.

## Reproducción

Desde la raíz del repositorio, con entorno Python preparado:

```sh
PYTHONPATH=. pytest -q gisela/engine/tests/test_actuation_public_v073.py
PYTHONPATH=. pytest -q gisela/packages/tegularis_the_son_of_the_volcan/test_desenlaces_v072.py
PYTHONPATH=. pytest -q gisela/engine/tests/test_e0_gateway.py
PYTHONPATH=. python tools/glauquir.py \
  --package gisela/packages/tegularis_the_son_of_the_volcan/08_desenlaces_v072.package.json \
  --seed $(printf '1%.0s' {1..64}) --auto --color never
```

Para guardar, añada `--save mi_partida.json` a GLAUQUIR; para restaurar, use `--restore mi_partida.json` y el mismo paquete. Observe/Act ya es la ruta ordinaria. Para seleccionar cartas de Parnecio manualmente, omita `--auto`.

## Workshop de aceptación final

1. Abrir una sesión con semilla conocida y anotar iniciativa y orden.
2. Avanzar los NPC con la acción publicada, sin seleccionar habilidades fuera de Observe.
3. En el turno de Parnecio elegir una habilidad habilitada y comprobar el mensaje de efecto publicado.
4. Guardar; restaurar; repetir exactamente la misma elección y comparar snapshot, RNG, inventario, acciones restantes, consecuencias y mensajes.
5. Intentar una acción vencida y otra no ofrecida, verificando respuesta de error y ausencia de cambios.
6. Continuar hasta un resultado y comprobar que la explosión precede al desenlace, no hay acciones posteriores y no se modifica el estado al observar.
7. Repetir con diferentes semillas y estrategias, incluyendo búsqueda de los tres desenlaces. Registrar semillas, decisiones y resultados.
8. Ejecutar la regresión general completa **sin límite de tiempo impuesto**, con un reporte final de fallos y duración. Solo entonces cerrar formalmente v0.7.4.
