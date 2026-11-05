# Presentación autoral v0.8.0: arquitectura y alcance comprobado

## Contrato

La propiedad opcional raíz `presentation` del paquete DSL **1.5** define un identificador
estable y una colección ordenada de `regions`. Cada región especifica `id`,
`component`, una etiqueta `label` opcional y, según componente, `source`, `text`,
`maximum` o `children`. Se conserva el resto del contrato: paquetes sin
`presentation` mantienen Observe y GLAUQUIR anteriores.

## Responsabilidades

- **Autor**: compone regiones y selecciona rutas fijas a datos públicos.
- **GISELA**: valida la declaración al admitir el paquete, produce Observe,
  añade una proyección de presentación sin tocar la sesión, RNG ni revisiones.
- **GLAUQUIR textual**: recorre los componentes e imprime su representación,
  ofreciendo únicamente los comandos de `choice_list` provenientes de Observe.
  La selección conserva la ruta Act existente.

## Catálogo actual

| Componente | Contrato | Comportamiento sin dato |
|---|---|---|
| `text` | `text` literal o `source` | "No disponible" |
| `stat` | `source` de escalar | "No disponible" |
| `meter` | `source` y `maximum` numéricos | "Magnitud no disponible" |
| `entity_status` | `source` objeto público | "Tipo incompatible" |
| `entity_collection` | `source` lista pública | Lista vacía / mensaje |
| `choice_list` | `source` lista de ofertas | Solo elementos `enabled` |
| `event_log` | `source` lista pública | Lista vacía / mensaje |
| `initiative_order` | `source` lista pública | Lista vacía / mensaje |
| `section` | `children` | Contenedor vacío |
| `conditional` | `source` booleano y `children` | Oculta si falso/ausente |

## Seguridad y límites

Solo se aceptan rutas estáticas de segmentos alfanuméricos de un conjunto
explícito de raíces de **Observe** (`actions`, `actuation`, `content`, etc.).
No existe evaluación de expresiones, referencias arbitrarias, acceso a estado
privado, Python ni HTML ejecutable. La validación estática rechaza componentes,
propiedades y referencias no permitidos. La resolución dinámica trata ausencia
y tipos incompatibles sin romper la sesión. Máximo: 64 nodos, profundidad 8,
64 elementos por colección. La selección usa las ofertas existentes, no genera
permisos ni comandos nuevos.

## Trazabilidad

`actuation.causal` procede del historial confirmado, ya filtrado por la
proyección causal existente; incluye secuencias, fuentes y datos autorizados.
No se vuelven a tirar dados ni se infieren daños desde el texto. La visualización
no guarda estado y puede reconstruirse tras restauración.

## Compatibilidad y evolución

La capacidad se incorporó al esquema público **1.5**. Las versiones anteriores
siguen funcionando sin ella. El incremento v0.8.0f añadió recursos públicos,
efectos y destinatarios declarados, descritos a continuación. La
[presentación v0.8.2](PRESENTACION_DECLARATIVA_V082.md) amplía ese contrato con
vistas, tablas, agrupación causal y plantillas. Las restricciones de cada entrega
se conservan en sus informes; no deben confundirse con carencias actuales.

## Incremento v0.8.0f: proyección pública y destinatarios

El paquete DSL 1.5 permite opcionalmente `actuation.public_resources`, una lista
acotada de `{entity,id,current,maximum?}`. Cada `entity` debe ser un participante
admitido. `current` y `maximum` deben identificar variables numéricas ya
declaradas en `initial_state.session_variables` e incluidas **explícitamente** en
`actuation.public_trace_variables`. La admisión rechaza una ruta privada, un
participante desconocido o un tipo no numérico. La proyección publica únicamente
`{entity,id,value,maximum?}` en `actuation.resources`, nunca rutas internas.
No se infieren nombres de recursos en el motor: HP/MP/TP se configuran solo en
el paquete productivo de Tegularis. Se publican además `participants` (IDs
públicos declarados) y `effects` (efectos confirmados del reloj: id, beneficiario,
turnos restantes), manteniendo el orden autoral.

El autor puede declarar `presentation.action_targets`, una lista acotada de
`{skill,target}` para instancias de habilidad ya existentes. La admisión
comprueba que ambos identificadores existan y que no se repita una habilidad.
Una oferta válida se muestra como `Habilidad -> destinatario`, conservando
`action_id`, `revision` y toda la autorización original. El cliente no inventa
un comando con objetivo ni resuelve reglas de selección: cada alternativa
corresponde a una instancia de habilidad dirigida por el guion productivo.
La versión presente de Parnecio ofrece las alternativas declaradas de Protección
para Gillius, Clarisa e Iosepus. No existe aún un selector genérico para cartas
con parámetros dinámicos arbitrarios; el subconjunto Act H3 sigue rechazando
parámetros entrantes no autorizados.

El registro `actuation.causal` continúa siendo la única fuente para mostrar
resultados, tiradas, impactos, evasiones, cambios de recursos y desenlace. La
ventana de presentación muestra los últimos 40 acontecimientos, sin recrear
historial mediante cálculo; un registro completo permanece en el snapshot del
motor. Esta limitación no garantiza mostrar un historial completo de partidas
largas desde la pantalla, aunque sí conserva orden e identidad en la ventana.

La política de compatibilidad es aditiva: ambos campos autorales son opcionales,
y las sesiones sin ellos continúan usando las proyecciones existentes. Debido
a que los paquetes tienen digest canónico, agregar estos campos cambia el digest;
una sesión grabada con un paquete anterior no debe restaurarse con el paquete
modificado. Se conserva la versión declarada de DSL 1.5.
