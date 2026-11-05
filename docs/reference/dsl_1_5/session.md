# session schema fields

Contract source: [session.schema.json](../../../gisela/contracts/v1_5/session.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| schema_version | yes | Unspecified | const: 1.5 |  |
| package_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| package_digest | yes | string | pattern: ^[0-9a-f]{64}$ |  |
| session_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| revision | yes | integer | minimum: 0 |  |
| world_revision | yes | integer | minimum: 0 |  |
| turn | yes | integer | minimum: 0 |  |
| status | yes | Unspecified | enum: ["preparing","node","exploring","ended"] |  |
| world_time | yes | string | format: date-time |  |
| cursor | no | Reference to cursor |  |  |
| current_scene | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| player_character | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| world | yes | object | additionalProperties: False |  |
| world.locations | yes | array |  |  |
| world.characters | yes | array |  |  |
| world.objects | yes | array |  |  |
| world.skills | yes | array |  |  |
| world.effects | yes | array |  |  |
| world.capacities | yes | array |  |  |
| world.relationships | yes | array |  |  |
| world.world_variables | yes | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| narrative | yes | object | additionalProperties: False |  |
| narrative.session_variables | yes | object | additionalProperties: {"$ref":"https://schemas.gisela.invalid/v1.5/common.schema.json#/$defs/json_scalar"} |  |
| history | yes | object | additionalProperties: False |  |
| history.facts | yes | array |  |  |
| history.trace | yes | array |  |  |
| history.executions | yes | array |  |  |
| history.reading | no | array |  |  |
| ending | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| preparing_for | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| rng | yes | object | additionalProperties: False | Committed RNG state only; provisional draws are never saved. |
| rng.algorithm | yes | Unspecified | const: sha256_counter_v1 |  |
| rng.seed | yes | string | pattern: ^[0-9a-f]{64}$ |  |
| rng.counter | yes | integer | minimum: 0; maximum: 9007199254740991 |  |
| identity | yes | object | additionalProperties: False | Includes removed instance IDs, for nonreuse after restore. Semantic validation verifies completeness. |
| identity.used_instance_ids | yes | array | uniqueItems: True |  |
| identity.next_sequence | yes | integer | minimum: 1; maximum: 9007199254740991 |  |
| mary | no | object | additionalProperties: False |  |
| mary.objectives | yes | object | additionalProperties: {"type":"boolean"} |  |
| mary.missions | yes | object | additionalProperties: {"enum":["inactive","active","completed","failed","abandoned"]} |  |
| pending_transaction | no | Reference to pending_transaction |  |  |
| pending_evaluation | no | Reference to pending_evaluation |  |  |
| actuation | no | object | additionalProperties: False |  |
| actuation.round | yes | integer | minimum: 1; maximum: 1000 |  |
| actuation.order | yes | array | minItems: 1; maxItems: 32 |  |
| actuation.initiative | yes | array |  |  |
| actuation.initiative[].actor | yes | string |  |  |
| actuation.initiative[].score | yes | integer |  |  |
| actuation.initiative[].die | yes | integer |  |  |
| actuation.initiative[].strength | yes | integer |  |  |
| actuation.initiative[].awareness | yes | integer |  |  |
| actuation.initiative[].fortune | yes | integer |  |  |
| actuation.index | yes | integer | minimum: 0 |  |
| actuation.remaining | yes | integer | minimum: 0; maximum: 16 |  |
| actuation.turn_serial | yes | integer | minimum: 0 |  |
| actuation.effects | yes | array | maxItems: 2048 |  |
| actuation.effects[].id | yes | string |  |  |
| actuation.effects[].beneficiary | yes | string |  |  |
| actuation.effects[].remaining | yes | integer | minimum: 1; maximum: 1000 |  |
| actuation.effects[].linked | no | boolean |  |  |
| actuation.events | yes | array | maxItems: 16000 |  |
| actuation.events[].sequence | yes | integer | minimum: 1 |  |
| actuation.events[].kind | yes | string |  |  |
| actuation.events[].detail | yes | object |  |  |
| actuation.complete | yes | boolean |  |  |
| actuation.fired | no | array | maxItems: 64; uniqueItems: True |  |
| actuation.outcome | no | string, null |  |  |
| actuation.event_policies | no | array | maxItems: 64 |  |
| actuation.outcome_policies | no | array | maxItems: 16 |  |
| actuation.public_trace_variables | no | array | maxItems: 128; uniqueItems: True |  |

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

type: "object"

additionalProperties: false

## Definition cursor

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| node | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| step | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| execution_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition execution

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| execution_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| node | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| turn | yes | integer | minimum: 0 |  |
| started_at | yes | string | format: date-time |  |
| completed_at | no | string | format: date-time |  |
| selected_options | no | array |  | Ordered selections within this node execution; provenance uses step_id + option_id. |
| selected_options[].step_id | yes | Reference to id |  |  |
| selected_options[].option_id | yes | Reference to id |  |  |
| completed | yes | boolean |  |  |

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

type: "object"

additionalProperties: false

## Definition fact_event

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| sequence | yes | integer | minimum: 0 |  |
| fact | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| source | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| payload | no | object | additionalProperties: {} |  |

type: "object"

additionalProperties: false

## Definition reaction_event

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| sequence | yes | integer | minimum: 0 |  |
| kind | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| source | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| detail | no | object | additionalProperties: {} |  |
| causal_execution_id | no | string | maxLength: 96; pattern: ^action_[0-9]{8,}$ |  |

type: "object"

additionalProperties: false

## Definition pending_source

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition pending_answer

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| request_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| option_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |

type: "object"

additionalProperties: false

## Definition pending_request

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| request_id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| kind | yes | Unspecified | const: select_one |  |
| options | yes | array | minItems: 1; uniqueItems: True |  |
| description | no | string | minLength: 1 |  |
| purpose | yes | Reference to id |  |  |

type: "object"

additionalProperties: false

## Definition pending_transaction

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| origin | yes | Unspecified | enum: ["voluntary","mandatory"] |  |
| source | yes | Reference to pending_source |  |  |
| initiated_revision | yes | integer | minimum: 0 |  |
| context | yes | object | additionalProperties: {"type":"string","pattern":"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$","maxLength":96} |  |
| answers | yes | array |  |  |
| request | yes | Reference to pending_request |  |  |

type: "object"

additionalProperties: false

## Definition reading_entry

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| sequence | yes | integer | minimum: 1 |  |
| kind | yes | Unspecified | enum: ["scene","ending","narrate","dialogue","choice","action","skill"] |  |
| source | yes | string |  |  |
| text | yes | string | minLength: 1 |  |
| turn | yes | integer | minimum: 0 |  |

type: "object"

additionalProperties: false

## Definition fixed_result

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| key | yes | array | minItems: 3; maxItems: 4 |  |
| presentation | yes | Unspecified | enum: ["visible","acknowledged"] |  |
| result | yes | object | additionalProperties: True |  |
| rng_before | yes | Reference to rng |  |  |
| rng_after | yes | Reference to rng |  |  |

type: "object"

additionalProperties: false

## Definition pending_evaluation

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| evaluation_id | yes | Reference to id |  |  |
| prepared_revision | yes | integer | minimum: 1 |  |
| origin | yes | Unspecified | enum: ["voluntary","mandatory"] |  |
| source | yes | Reference to pending_source |  |  |
| initiated_revision | yes | integer | minimum: 0 |  |
| rng_initial | yes | Reference to rng |  |  |
| fixed | yes | array | minItems: 1; maxItems: 512 |  |
| answers | yes | array | maxItems: 512 |  |
| auxiliary_request | no | Reference to pending_request |  |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
