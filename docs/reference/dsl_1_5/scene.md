# scene schema fields

Contract source: [scene.schema.json](../../../gisela/contracts/v1_5/scene.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | no | Reference to localized_text |  |  |
| location | no | Reference to entity_ref |  |  |
| description | no | Reference to localized_text |  |  |
| elements | no | array |  |  |
| actors | no | array |  |  |
| actions | no | array |  |  |
| allow_skill_play | no | boolean |  |  |
| presentation | no | Reference to presentation |  |  |
| annotations | no | Reference to annotations |  |  |

type: "object"

additionalProperties: false

## Definition element

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| label | yes | Reference to localized_text |  |  |
| description | no | Reference to localized_text |  |  |
| entity | no | Reference to entity_ref |  |  |
| visible_if | no | Reference to condition |  |  |
| actions | no | array |  |  |
| role | no | Unspecified | enum: ["portable_object","fixed_object"] |  |
| public_id | no | Reference to id |  |  |
| public_entity | no | Reference to id |  |  |
| presentation | no | Reference to presentation |  |  |

type: "object"

additionalProperties: false

## Definition actor_display

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| character | yes | Reference to entity_ref |  |  |
| visible_if | no | Reference to condition |  |  |
| presentation | no | Reference to presentation |  |  |
| unknown_name | no | Reference to localized_text |  |  |
| known_if | no | Reference to condition |  |  |
| public_id | no | Reference to id |  |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
