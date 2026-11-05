# common schema fields

Contract source: [common.schema.json](../../../gisela/contracts/v1_5/common.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

No direct properties are declared at this level.

## Definition id

No direct properties are declared at this level.

type: "string"

## Definition localized_text

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition json_scalar

No direct properties are declared at this level.

type: ["null", "boolean", "integer", "number", "string"]

## Definition entity_query

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| query | yes | object | additionalProperties: False |  |
| query.kind | yes | Unspecified | enum: ["character","location","object","skill","effect"] |  |
| query.where | yes | Reference to condition |  |  |
| query.selection | yes | Unspecified | enum: ["one","all"] |  |

type: "object"

additionalProperties: false

## Definition entity_ref

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition var_ref

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| scope | yes | Unspecified | enum: ["session","world","character","location","object"] |  |
| key | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| entity | no | Reference to entity_ref |  |  |

type: "object"

additionalProperties: false

## Definition stat_ref

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| character | yes | Reference to entity_ref |  |  |
| name | yes | Unspecified | enum: ["strength","openness","fortune","intelligence","awareness"] |  |
| component | yes | Unspecified | enum: ["base","current","effective"] |  |

type: "object"

additionalProperties: false

## Definition relation_ref

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| from | yes | Reference to entity_ref |  |  |
| to | yes | Reference to entity_ref |  |  |
| key | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition value

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition lvalue

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition condition

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition destination

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition guarded_ops

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| when | yes | Reference to condition |  |  |
| effects | yes | array |  |  |

type: "object"

additionalProperties: false

## Definition choice_option

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| label | yes | Reference to localized_text |  |  |
| visible_if | no | Reference to condition |  |  |
| enabled_if | no | Reference to condition |  |  |
| effects | no | array |  |  |
| next | no | Reference to destination |  |  |
| evaluation | no | Reference to evaluation |  |  |

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

type: "object"

additionalProperties: false

## Definition action

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| label | yes | Reference to localized_text |  |  |
| visible_if | no | Reference to condition |  |  |
| enabled_if | no | Reference to condition |  |  |
| effects | no | array |  |  |
| next | no | Reference to destination |  |  |
| requires | no | Unspecified | enum: ["none","hand_preparation"] |  |
| evaluation | no | Reference to evaluation |  |  |
| role | no | Unspecified | enum: ["exit"] |  |
| public_id | no | Reference to id |  |  |
| annotations | no | Reference to annotations |  |  |

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

type: "object"

additionalProperties: false

## Definition expiration_clause

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition expiration

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| mode | yes | Unspecified | const: any |  |
| clauses | yes | array | minItems: 1 |  |

type: "object"

additionalProperties: false

## Definition operation

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition trigger

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition property_definition

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| type | yes | Unspecified | enum: ["boolean","integer","number","string"] |  |
| initial | yes | boolean, integer, number, string |  |  |
| min | no | number |  |  |
| max | no | number |  |  |

type: "object"

additionalProperties: false

## Definition presentation

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| color | no | Unspecified | enum: ["default","red","yellow","green","cyan","blue","magenta","white"] |  |

type: "object"

additionalProperties: {"type": ["string", "number", "boolean", "null", "object", "array"]}

## Definition evaluation

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | Reference to id |  |  |
| profile | yes | Reference to id |  |  |
| presentation | yes | Unspecified | enum: ["hidden","visible","acknowledged"] |  |
| inputs | yes | object | additionalProperties: False |  |
| inputs.base | yes | One of 2 alternatives |  |  |
| inputs.difficulty | no | object | additionalProperties: False |  |
| inputs.difficulty.literal | yes | integer | minimum: -1000000; maximum: 1000000 |  |
| context | no | object | additionalProperties: False |  |
| context.tags | no | array | maxItems: 16; uniqueItems: True |  |
| context.participants | no | array | maxItems: 8 |  |
| context.participants[].entity | yes | Reference to id |  |  |
| context.participants[].role | yes | Reference to id |  |  |
| branches | yes | array | minItems: 1; maxItems: 16 |  |
| branches[].outcome | yes | Reference to id |  |  |
| branches[].effects | no | array |  |  |
| branches[].next | no | Reference to destination |  |  |

type: "object"

additionalProperties: false

## Definition annotation

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| audience | yes | Unspecified | const: glauquir |  |
| text | yes | Reference to localized_text |  |  |

type: "object"

additionalProperties: false

## Definition annotations

No direct properties are declared at this level.

type: "array"

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
