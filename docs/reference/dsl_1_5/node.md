# node schema fields

Contract source: [node.schema.json](../../../gisela/contracts/v1_5/node.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | no | Reference to localized_text |  |  |
| steps | yes | array | minItems: 1 |  |
| allow_preparation | no | boolean |  |  |
| annotations | no | Reference to annotations |  |  |

type: "object"

additionalProperties: false

## Definition step_base

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition narrate

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: narrate |  |
| text | yes | Reference to localized_text |  |  |
| presentation | no | Reference to presentation |  |  |
| annotations | no | Reference to annotations |  |  |

type: "object"

additionalProperties: false

## Definition dialogue

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: dialogue |  |
| speaker | yes | Reference to entity_ref |  |  |
| text | yes | Reference to localized_text |  |  |
| presentation | no | Reference to presentation |  |  |
| annotations | no | Reference to annotations |  |  |

type: "object"

additionalProperties: false

## Definition choice

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: choice |  |
| prompt | no | Reference to localized_text |  |  |
| options | yes | array | minItems: 1 |  |
| annotations | no | Reference to annotations |  |  |

type: "object"

additionalProperties: false

## Definition condition

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: condition |  |
| test | yes | Reference to condition |  |  |
| then | no | Reference to destination |  |  |
| else | no | Reference to destination |  |  |

type: "object"

additionalProperties: false

## Definition effect

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: effect |  |
| effects | yes | array | minItems: 1 |  |

type: "object"

additionalProperties: false

## Definition scene

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: scene |  |
| scene | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition transition

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: transition |  |
| next | yes | Reference to destination |  |  |

type: "object"

additionalProperties: false

## Definition ending

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: ending |  |
| ending | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition prepare_hand

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: prepare_hand |  |

type: "object"

additionalProperties: false

## Definition skill_window

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: skill_window |  |
| max_plays | no | integer | minimum: 1 |  |
| annotations | no | Reference to annotations |  |  |

type: "object"

additionalProperties: false

## Definition random

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| op | yes | Unspecified | const: random |  |
| branches | yes | array | minItems: 1 |  |
| branches[].id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| branches[].weight | yes | integer | minimum: 1 |  |
| branches[].effects | no | array |  |  |
| branches[].next | no | Reference to destination |  |  |

type: "object"

additionalProperties: false

## Definition step

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition evaluate

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | Reference to id |  |  |
| op | yes | Unspecified | const: evaluate |  |
| evaluation | yes | Reference to evaluation |  |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
