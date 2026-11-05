# observe schema fields

Contract source: [observe.schema.json](../../../gisela/contracts/v1_5/observe.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| session_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| revision | yes | integer | minimum: 0 |  |
| world_revision | yes | integer | minimum: 0 |  |
| world_time | yes | string | format: date-time |  |
| turn | yes | integer | minimum: 0 |  |
| scene | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| content | yes | Reference to view_content |  |  |
| actions | yes | array |  |  |
| actors | no | array |  |  |
| elements | no | array |  |  |
| presentation | no | Reference to presentation |  |  |
| status | yes | Unspecified | enum: ["preparing","node","exploring","ended"] |  |
| inventory | no | array |  |  |
| skills | no | array |  |  |
| effects | no | array |  |  |
| cards | no | array |  |  |
| quests | no | array |  |  |
| quests[].id | yes | string |  |  |
| quests[].title | yes | string |  |  |
| quests[].status | yes | Unspecified | enum: ["inactive","active","completed","failed","abandoned"] |  |
| quests[].objectives | yes | array |  |  |
| quests[].objectives[].title | yes | string |  |  |
| quests[].objectives[].completed | yes | boolean |  |  |
| scene_title | no | string |  |  |
| scene_description | no | string |  |  |
| actuation | no | object | additionalProperties: False |  |
| actuation.round | yes | integer | minimum: 1 |  |
| actuation.actor | yes | string, null |  |  |
| actuation.remaining | yes | integer | minimum: 0 |  |
| actuation.order | yes | array |  |  |
| actuation.outcome | yes | string, null |  |  |
| actuation.events | yes | array |  |  |
| actuation.events[].kind | yes | string |  |  |
| actuation.events[].detail | yes | string |  |  |
| actuation.messages | yes | array |  |  |
| actuation.initiative | yes | array |  |  |
| actuation.initiative[].actor | yes | string |  |  |
| actuation.initiative[].die | yes | integer |  |  |
| actuation.initiative[].score | yes | integer |  |  |
| actuation.rolls | yes | array | maxItems: 12 |  |
| actuation.rolls[].source | yes | string |  |  |
| actuation.rolls[].sides | yes | integer | minimum: 1 |  |
| actuation.rolls[].result | yes | integer | minimum: 1 |  |
| actuation.rolls[].store | yes | string |  |  |
| actuation.contests | yes | array | maxItems: 12 |  |
| actuation.contests[].source | yes | string |  |  |
| actuation.contests[].profile | yes | string |  |  |
| actuation.contests[].winner | yes | Unspecified | enum: ["left","right"] |  |
| actuation.contests[].left | yes | Reference to contest_side |  |  |
| actuation.contests[].right | yes | Reference to contest_side |  |  |
| actuation.causal | yes | array | maxItems: 40 |  |
| actuation.causal[].sequence | yes | integer | minimum: 0 |  |
| actuation.causal[].kind | yes | string |  |  |
| actuation.causal[].source | yes | string |  |  |
| actuation.causal[].detail | yes | object | additionalProperties: {"type":["string","integer","number","boolean","null"]} |  |
| actuation.causal[].causal_execution_id | no | string | maxLength: 96; pattern: ^action_[0-9]{8,}$ |  |
| actuation.participants | no | array | maxItems: 32 |  |
| actuation.participants[].id | yes | string | maxLength: 96 |  |
| actuation.resources | no | array | maxItems: 128 |  |
| actuation.resources[].entity | yes | string | maxLength: 96 |  |
| actuation.resources[].id | yes | string | maxLength: 96 |  |
| actuation.resources[].value | yes | number |  |  |
| actuation.resources[].maximum | no | number |  |  |
| actuation.effects | no | array | maxItems: 64 |  |
| actuation.effects[].id | yes | string | maxLength: 96 |  |
| actuation.effects[].beneficiary | yes | string | maxLength: 96 |  |
| actuation.effects[].remaining | yes | integer |  |  |

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

type: "object"

additionalProperties: false

## Definition contest_side

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| rolls | yes | array |  |  |
| die_value | yes | integer |  |  |
| base | yes | integer |  |  |
| bonus | yes | integer |  |  |
| total | yes | integer |  |  |

type: "object"

additionalProperties: false

## Definition option

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| action_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| label | yes | string | minLength: 1 |  |
| enabled | yes | boolean |  |  |
| reason | no | string | minLength: 1 |  |
| kind | yes | Unspecified | enum: ["advance","choose","interact","play_skill","prepare","resolve_pending","cancel_pending","continue_evaluation","resolve_evaluation_auxiliary","actuation_skill","actuation_pass","actuation_advance"] |  |
| role | no | Unspecified | enum: ["exit"] |  |
| target | no | string | maxLength: 96 |  |

type: "object"

additionalProperties: false

## Definition element

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| label | yes | string | minLength: 1 |  |
| actions | yes | array |  |  |
| entity | no | string |  |  |
| description | no | string |  |  |
| role | no | Unspecified | enum: ["portable_object","fixed_object"] |  |
| color | no | Unspecified | enum: ["default","red","yellow","green","cyan","blue","magenta","white"] |  |

type: "object"

additionalProperties: false

## Definition actor

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| name | no | string | minLength: 1 |  |
| presentation | no | Reference to presentation |  |  |
| identity_hidden | no | boolean |  |  |
| color | no | Unspecified | enum: ["default","red","yellow","green","cyan","blue","magenta","white"] |  |

type: "object"

additionalProperties: false

## Definition stat_row

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| name | yes | Unspecified | enum: ["strength","openness","fortune","intelligence","awareness"] |  |
| base | yes | integer |  |  |
| current | yes | integer |  |  |
| modifier | yes | integer |  |  |
| effective | yes | integer |  |  |

type: "object"

additionalProperties: false

## Definition character_location

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| location | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| status | yes | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |

type: "object"

additionalProperties: false

## Definition view_content

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition public_card

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string |  |  |
| card | yes | string |  |  |
| kind | yes | string |  |  |
| title | yes | string |  |  |
| description | no | string |  |  |

type: "object"

additionalProperties: false

## Definition public_skill

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string |  |  |
| card | yes | string |  |  |
| kind | yes | string |  |  |
| title | yes | string |  |  |
| description | no | string |  |  |
| zone | yes | Unspecified | enum: ["hand","reserve","in_play"] |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
