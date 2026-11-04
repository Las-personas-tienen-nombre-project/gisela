# Workshop — tres disposiciones autorales de Tegularis (v0.8.1a–b)

## Objetivo

La composición es parte del paquete productivo. GISELA mantiene el estado autoritativo; la presentación proyecta solo Observe y las decisiones pasan por Act. Estas variantes **no contienen reglas distintas de combate** y conservan el DSL 1.5.

## Probar las tres disposiciones

Ejecute desde la raíz de este repositorio, sin `--actuation`:

```sh
python -m gisela.cli.glauquir --package packages/tegularis_the_son_of_the_volcan/11_presentacion_participantes_v081.package.json
python -m gisela.cli.glauquir --package packages/tegularis_the_son_of_the_volcan/11_presentacion_decisiones_v081.package.json
python -m gisela.cli.glauquir --package packages/tegularis_the_son_of_the_volcan/11_presentacion_cronica_v081.package.json
```

- **Participantes:** recursos, efectos, orden e iniciativa primero; después decisiones e historial.
- **Decisiones:** turno y acciones autorizadas primero; después información contextual e historial.
- **Crónica:** sucesos confirmados al comienzo; después recursos, orden y decisiones.

Puede usar letras (`A`, `B`, etc.), números o `accion <id>` para elegir una oferta de la observación actual. `mirar` reimprime la pantalla sin avanzar; `guardar ruta.json` guarda la sesión. Para un recorrido sin interacción, agregue `--auto --save ruta.json`.

## Composición sin Python

Dentro de cada `.package.json`, la clave `presentation.regions` declara el orden y el anidamiento de regiones. Reorganice o cambie las etiquetas de las regiones utilizando componentes generales; conserve identificadores únicos y los `source` públicos válidos. Las ofertas se derivan de `actions`; las consecuencias se derivan de `actuation.causal`. Una etiqueta nunca autoriza una acción.

Para crear una cuarta variante, copie uno de los paquetes, cambie `presentation.id`, reorganice solo `presentation.regions` y valide con `admit_package_file` o las pruebas existentes. No altere `action_targets` sin una razón autoral comprobada ni cambie las definiciones del encuentro.

## Semántica de la salida

- Los recursos se agrupan por entidad; el valor y máximo son los ya publicados por Observe, que incluyen las bonificaciones iniciales verificadas por GISELA.
- Los efectos muestran beneficiario y duración restante, si hay efectos públicos.
- El orden de actuación aparece numerado; las puntuaciones de iniciativa se muestran aparte.
- Las acciones muestran la letra y su ID; los destinatarios autorizados ya aparecen en sus etiquetas cuando corresponde.
- El historial muestra las últimas diez entradas de la proyección causal pública (que conserva 40); mantiene sus números de secuencia, sin nuevas tiradas ni reconstrucción de consecuencias.
- El desenlace puede aparecer como «No disponible» hasta que el motor publique uno.

## Límites conocidos

No hay selector de variantes en caliente dentro de una sesión: se selecciona el archivo de paquete al iniciar GLAUQUIR. El cliente textual no implementa estilos arbitrarios ni parámetros dinámicos de Act. No se proporciona soporte de restauración cruzada entre paquetes con identidades diferentes; use el mismo paquete al restaurar.

## Ajustes de legibilidad v0.8.1c

Las tres variantes presentan «Orden de actuación» y «Tiradas de iniciativa» como etiquetas autorales diferentes. La selección de acciones admite letras o `accion <id>`. Cuando la crónica publicada contiene más de diez elementos, la consola indica cuántos muestra de esa ventana. Un desenlace todavía no publicado se lee como «Pendiente de confirmación».

Estos cambios no alteran Observe, Act, ni las consecuencias de las decisiones; el informe `RESULTADOS_V081C.md` documenta tres ejecuciones con trazas idénticas.
