# Workshop: construir una presentación declarativa

1. Abra un paquete admitido con `manifest.format_version` `1.5`.
2. Incorpore una propiedad raíz `presentation` según este ejemplo no bélico:

```json
"presentation": {
  "id": "waiting_room",
  "regions": [
    {"id":"heading","component":"text","text":"Turnos de atención"},
    {"id":"visitors","component":"entity_collection","source":"actors"},
    {"id":"choices","component":"choice_list","source":"actions"}
  ]
}
```

3. Adapte `source` solo a campos existentes en Observe; no puede acceder a
variables internas ni ejecutar expresiones.
4. Valide con `python -m gisela.contracts.admit_package archivo.package.json`.
5. Ejecute GLAUQUIR con el paquete, por ejemplo:
   `python -m gisela.cli.glauquir --package archivo.package.json`.
6. Reordene las regiones en el JSON y compruebe que cambia la pantalla sin
cambiar las acciones o el estado del motor.

Para un encuentro con actuación hay un ejemplo completo de contrato en
`packages/tegularis_the_son_of_the_volcan/10_balance_v078.package.json`.
Las acciones no autorizadas jamás se pueden añadir desde esta definición.

## Taller v0.8.0f: recursos y destinatarios

1. Declare una variable numérica de sesión y autorice su publicación incluyendo
   su identificador en `actuation.public_trace_variables`.
2. Agregue a `actuation.public_resources` una entrada como:
   `{"entity":"personaje","id":"energia","current":"energia_personaje","maximum":"max_energia_personaje"}`.
   Los cuatro identificadores deben corresponder a datos declarados y admitidos.
3. Añada una región `entity_collection` con `source: "actuation.resources"`.
4. Si su paquete ya dispone de instancias de habilidades dirigidas a diferentes
   participantes, declare en `presentation.action_targets` entradas como
   `{"skill":"curar_aliado_01","target":"aliado"}`. Es solo un ejemplo;
   debe usar los identificadores existentes de su propio paquete.
5. Añada una región `choice_list` con `source: "actions"`. GLAUQUIR mostrará la
   acción y su destinatario sin crear un comando privilegiado.
6. Compruebe la admisión del paquete y ejecute `python -m gisela.cli.glauquir
   --package RUTA_AL_PAQUETE --auto --save salida.json`. Para selección manual,
   omita `--auto`. El estado restaurado debe corresponder al mismo digest de paquete.

Las cartas con parámetros dinámicos no se habilitan automáticamente por esta
capacidad. Los ejemplos no autorizan revelar variables fuera de la lista pública.
