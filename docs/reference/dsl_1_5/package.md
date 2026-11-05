# package schema fields

Contract source: [package.schema.json](../../../gisela/contracts/v1_5/package.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| manifest | yes | Reference to manifest |  |  |
| nodes | yes | array |  |  |
| cards | yes | array |  |  |
| scenes | yes | array |  |  |
| rules | yes | array |  |  |
| initial_state | yes | Reference to initial_state.schema.json |  |  |
| endings | yes | array |  |  |
| mary | no | object |  |  |
| strings | no | object | additionalProperties: {"type":"object","propertyNames":{"type":"string","pattern":"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$","maxLength":96},"additionalProperties":{"type":"string","minLength":1}} |  |
| traits | no | Reference to definitions.schema.json |  |  |
| dice_profiles | no | array | maxItems: 64 |  |
| actuation | no | object | additionalProperties: False |  |
| actuation.setup | no | array | maxItems: 128 |  |
| actuation.initiative_die | yes | integer | minimum: 2; maximum: 1000 |  |
| actuation.base_actions | yes | integer | minimum: 1; maximum: 16 |  |
| actuation.thresholds | no | array | maxItems: 16 |  |
| actuation.thresholds[].at | yes | integer |  |  |
| actuation.thresholds[].actions | yes | integer | minimum: 1; maximum: 16 |  |
| actuation.participants | yes | array | minItems: 1; maxItems: 32 |  |
| actuation.participants[].character | yes | Reference to id |  |  |
| actuation.participants[].main_stat | yes | Unspecified | enum: ["strength","openness","fortune","intelligence","awareness"] |  |
| actuation.participants[].allow_pass | no | boolean |  |  |
| actuation.participants[].candidates | no | array | maxItems: 64 |  |
| actuation.participants[].candidates[].skill_instance | yes | Reference to id |  |  |
| actuation.participants[].candidates[].when | no | object |  |  |
| actuation.participants[].candidates[].arguments | no | object |  |  |
| actuation.participants[].action_traits | no | object |  |  |
| actuation.event_policies | no | array | maxItems: 64 |  |
| actuation.event_policies[].id | yes | Reference to id |  |  |
| actuation.event_policies[].phase | yes | Unspecified | enum: ["immediate","after_action"] |  |
| actuation.event_policies[].when | yes | Reference to condition |  |  |
| actuation.event_policies[].effects | yes | array | maxItems: 128 |  |
| actuation.event_policies[].outcomes | no | array | maxItems: 16 |  |
| actuation.event_policies[].outcomes[].when | yes | Reference to condition |  |  |
| actuation.event_policies[].outcomes[].effects | yes | array | maxItems: 128 |  |
| actuation.outcome_policies | no | array | maxItems: 16 |  |
| actuation.outcome_policies[].id | yes | Reference to id |  |  |
| actuation.outcome_policies[].when | yes | Reference to condition |  |  |
| actuation.public_trace_variables | no | array | maxItems: 128; uniqueItems: True |  |
| actuation.public_resources | no | array | maxItems: 128 |  |
| actuation.public_resources[].entity | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| actuation.public_resources[].id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| actuation.public_resources[].current | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| actuation.public_resources[].maximum | no | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| presentation | no | object | additionalProperties: False |  |
| presentation.id | yes | string | pattern: ^[a-z][a-z0-9_.-]{0,95}$ |  |
| presentation.regions | yes | array | minItems: 1; maxItems: 64 |  |
| presentation.action_targets | no | array | maxItems: 128 |  |
| presentation.action_targets[].skill | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| presentation.action_targets[].target | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| presentation.views | no | array | maxItems: 32 |  |

type: "object"

additionalProperties: false

## Definition entry

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Definition stat_scale

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| min | yes | integer |  |  |
| max | yes | integer |  |  |

type: "object"

additionalProperties: false

## Definition manifest

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| format_version | yes | Unspecified | const: 1.5 |  |
| language | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| languages | no | array | minItems: 1 |  |
| entry | yes | Reference to entry |  |  |
| sofia_scale | no | Reference to stat_scale |  |  |
| variables | no | array |  |  |
| variables[].scope | yes | Unspecified | enum: ["session","world"] |  |
| variables[].id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| variables[].type | yes | Unspecified | enum: ["boolean","integer","number","string"] |  |
| variables[].initial | yes | Reference to json_scalar |  |  |
| claims | no | array |  |  |
| facts | no | array |  |  |
| signals | no | array |  |  |
| relationship_fields | no | array |  |  |
| relationship_fields[].id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| relationship_fields[].type | yes | Unspecified | enum: ["boolean","integer","number","string"] |  |
| relationship_fields[].initial | yes | Reference to json_scalar |  |  |
| disposition_display | no | object | additionalProperties: False |  |
| disposition_display.field | yes | Reference to id |  |  |
| disposition_display.minimum | yes | number |  |  |
| disposition_display.neutral | yes | number |  |  |
| disposition_display.maximum | yes | number |  |  |
| disposition_display.thresholds | no | array | minItems: 4; maxItems: 4 |  |

type: "object"

additionalProperties: false

## Definition ending

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | maxLength: 96; pattern: ^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$ |  |
| title | no | Reference to localized_text |  |  |

type: "object"

additionalProperties: false

## Definition presentation_node

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | pattern: ^[a-z][a-z0-9_.-]{0,95}$ |  |
| component | yes | string |  |  |
| label | no | string | maxLength: 160 |  |
| source | no | string | minLength: 1; maxLength: 160 |  |
| maximum | no | string | minLength: 1; maxLength: 160 |  |
| text | no | string | maxLength: 1000 |  |
| children | no | array | maxItems: 64 |  |
| view | no | string | pattern: ^[a-z][a-z0-9_.-]{0,95}$ |  |

type: "object"

additionalProperties: false

## Definition presentation_column

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | pattern: ^[a-z][a-z0-9_.-]{0,95}$ |  |
| label | yes | string | maxLength: 160 |  |
| align | no | Unspecified | enum: ["left","right"] |  |

type: "object"

additionalProperties: false

## Definition presentation_event_format

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| kind | yes | Unspecified | enum: ["initiative","event_triggered","encounter_completed","skill_started","skill_played","dice_roll","contest_resolved","author_message","variable_changed"] |  |
| variable | no | string | maxLength: 96 |  |
| role | no | Unspecified | enum: ["damage","healing","buff","debuff","neutral"] |  |
| template | no | string | maxLength: 1000 |  |
| missing | no | Unspecified | enum: ["omit","placeholder"] |  |

type: "object"

additionalProperties: false

## Definition presentation_table_view

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | pattern: ^[a-z][a-z0-9_.-]{0,95}$ |  |
| limit | no | integer | minimum: 1; maximum: 64 |  |
| component | yes | Unspecified | const: table |  |
| source | yes | Unspecified | enum: ["actuation.resources","actuation.participants","actuation.effects","actors"] |  |
| columns | yes | array | minItems: 1; maxItems: 12 |  |
| transform | no | Unspecified | const: pivot_resources |  |
| missing | no | string | maxLength: 160 |  |

type: "object"

additionalProperties: false

## Definition presentation_event_view

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| id | yes | string | pattern: ^[a-z][a-z0-9_.-]{0,95}$ |  |
| limit | no | integer | minimum: 1; maximum: 64 |  |
| component | yes | Unspecified | const: event_log |  |
| source | yes | Unspecified | const: actuation.causal |  |
| kinds | no | array | maxItems: 9; uniqueItems: True |  |
| filter_field | no | Unspecified | enum: ["kind","source"] |  |
| filter_value | no | string, number, boolean, null | maxLength: 160 |  |
| group_by | no | Unspecified | const: action |  |
| event_formats | no | array | maxItems: 32 |  |

type: "object"

additionalProperties: false

## Definition presentation_view

No direct properties are declared at this level.

This declaration includes composed schema branches. Read the linked schema for their exact conditions.

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
