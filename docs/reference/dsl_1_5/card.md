# card schema fields

Contract source: [card.schema.json](../../../gisela/contracts/v1_5/card.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition loose_presentation

No direct properties are declared at this level.

## Definition character

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | yes | Reference to localized_text |  |  |
| description | no | Reference to localized_text |  |  |
| presentation | no | Reference to loose_presentation |  |  |
| kind | yes | Unspecified | const: character |  |
| properties | no | array |  |  |
| sofia | no | object | additionalProperties: False |  |
| sofia.strength | yes | integer |  |  |
| sofia.openness | yes | integer |  |  |
| sofia.fortune | yes | integer |  |  |
| sofia.intelligence | yes | integer |  |  |
| sofia.awareness | yes | integer |  |  |
| traits | no | array | maxItems: 256; uniqueItems: True |  |

type: "object"

additionalProperties: false

## Definition location

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | yes | Reference to localized_text |  |  |
| description | no | Reference to localized_text |  |  |
| presentation | no | Reference to loose_presentation |  |  |
| kind | yes | Unspecified | const: location |  |
| properties | no | array |  |  |
| traits | no | array | maxItems: 256; uniqueItems: True |  |

type: "object"

additionalProperties: false

## Definition object

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | yes | Reference to localized_text |  |  |
| description | no | Reference to localized_text |  |  |
| presentation | no | Reference to loose_presentation |  |  |
| kind | yes | Unspecified | const: object |  |
| portable | no | boolean |  |  |
| properties | no | array |  |  |
| traits | no | array | maxItems: 256; uniqueItems: True |  |

type: "object"

additionalProperties: false

## Definition skill

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | yes | Reference to localized_text |  |  |
| description | no | Reference to localized_text |  |  |
| presentation | no | Reference to loose_presentation |  |  |
| kind | yes | Unspecified | const: skill |  |
| passive_traits | no | array | maxItems: 256; uniqueItems: True |  |
| play | yes | object | additionalProperties: False |  |
| play.label | no | Reference to localized_text |  |  |
| play.requires | no | Reference to condition |  |  |
| play.effects | yes | array |  |  |
| play.outcomes | no | array |  |  |
| play.parameters | no | array | maxItems: 8; uniqueItems: True |  |
| play.parameters[].id | yes | Reference to id |  |  |
| play.parameters[].kind | yes | Unspecified | enum: ["integer","character"] |  |
| play.parameters[].min | no | integer |  |  |
| play.parameters[].max | no | integer |  |  |
| return_policy | no | object | additionalProperties: False |  |
| return_policy.default | yes | Unspecified | enum: ["discard","hand","reserve"] |  |
| return_policy.when | no | array |  |  |
| return_policy.when[].if | yes | Reference to condition |  |  |
| return_policy.when[].to | yes | Unspecified | enum: ["discard","hand","reserve"] |  |

type: "object"

additionalProperties: false

## Definition effect

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | yes | Reference to localized_text |  |  |
| description | no | Reference to localized_text |  |  |
| presentation | no | Reference to loose_presentation |  |  |
| kind | yes | Unspecified | const: effect |  |
| granted_traits | no | array | maxItems: 256; uniqueItems: True |  |
| on_reapply | no | Unspecified | enum: ["reject","refresh"] |  |
| stacking | no | Unspecified | enum: ["additive","unique_per_target"] |  |
| modifiers | no | array |  |  |
| modifiers[].stat | yes | Unspecified | enum: ["strength","openness","fortune","intelligence","awareness"] |  |
| modifiers[].amount | yes | integer |  |  |
| expiration | no | Reference to expiration |  |  |
| on_apply | no | array |  |  |
| on_expire | no | array |  |  |
| actuation_turns | no | integer | minimum: 1; maximum: 1000 |  |
| expire_on_actor_turn_start | no | boolean |  |  |
| actuation_blocks_actions | no | boolean |  |  |
| on_actor_turn_start | no | array | maxItems: 64 |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
