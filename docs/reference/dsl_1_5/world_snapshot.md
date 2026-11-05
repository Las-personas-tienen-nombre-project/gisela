# world_snapshot schema fields

Contract source: [world_snapshot.schema.json](../../../gisela/contracts/v1_5/world_snapshot.schema.json)

This page is an extraction of the public JSON schema for DSL 1.5. Schema acceptance, semantic admission, and runtime execution are different checks.

## Root structure

| Field path | Required at its parent | Declared type | Explicit constraints | Description |
| --- | --- | --- | --- | --- |
| revision | yes | integer | minimum: 0 |  |
| world_time | yes | string | format: date-time |  |
| characters | yes | array |  |  |

type: "object"

additionalProperties: false

## Validation boundary

- Structural status: grounded in the linked schema.
- Semantic status: requires package admission against the public validator.
- Runtime status: requires an executable example using the public session API.
- Any behavior not supported by those sources remains not established.
