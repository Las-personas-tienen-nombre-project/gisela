# initial_state schema fields

Contract source: [initial_state.schema.json](../../../gisela/contracts/v1_5/initial_state.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| world_time | yes | string | format: date-time |  |
| locations | yes | array |  |  |
| world_variables | no | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| session_variables | no | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| characters | yes | array |  |  |
| objects | yes | array |  |  |
| skills | yes | array |  |  |
| effects | yes | array |  |  |
| capacities | yes | array |  |  |
| relationships | no | array |  |  |
| facts | no | array |  |  |
| current_scene | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| player_character | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition location_instance

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| card | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| properties | no | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| traits | no | array | maxItems: 256; uniqueItems: True |  |

type: "object"

additionalProperties: false

## Definition character_instance

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| card | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| location | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| status | no | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| properties | no | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| stats | no | object | additionalProperties: {"type":"integer"} |  |
| knowledge | no | array |  |  |
| beliefs | no | object | additionalProperties: {"type":"boolean"} |  |
| traits | no | array | maxItems: 256; uniqueItems: True |  |

type: "object"

additionalProperties: false

## Definition object_instance

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| card | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| owner | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| location | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| properties | no | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| traits | no | array | maxItems: 256; uniqueItems: True |  |

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

type: "object"

additionalProperties: false

## Definition skill_instance

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| card | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| character | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| zone | yes | Unspecified | enum: ["hand","reserve"] |  |

type: "object"

additionalProperties: false

## Definition effect_instance

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| card | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| target | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| started_turn | yes | integer | minimum: 0 |  |
| started_at | yes | string | format: date-time |  |

type: "object"

additionalProperties: false

## Definition relationship

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| from | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| to | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| key | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| value | yes | Reference to json_scalar |  |  |

type: "object"

additionalProperties: false

## Definition capacity

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| character | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| hand | yes | integer | minimum: 0 |  |
| reserve | yes | integer | minimum: 0 |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
