# 08 Observe and Act

`observe.schema.json`, `act.schema.json`, and `session.schema.json` have distinct roles. Observe is a public view of available content and enabled actions. Act is the request for one currently offered action. Session is private committed and pending state for restoration and debugging. Do not copy private session fields into public UI data.

## Act request

An Act request has `session_id`, `revision`, `action_id` and optional `parameters`, subject to the actual schema. The public action ID must be taken from the current observation. The executor checks both identity and revision, validates the action is offered and enabled, and refuses nonempty parameters in the current implemented subset.

## Observable and confirmed data

An observation can contain narrative content, actions, visible scene actors or elements, and actuation information when present. A public action is not a raw game operation. Runtime changes, events, and causal records are committed by GISELA. The current event presentation window is bounded; displaying causality does not grant access to all past private facts.

During an auxiliary choice, the observation exposes permitted resolution actions. During a visible pending evaluation, the observation exposes `continue_evaluation` or the relevant auxiliary resolution. The continuation does not reroll fixed dice.

## Permissions and privacy

External access through `ExecutionGateway` is bound to a trusted principal. `observe_player` permits player projection; `act` permits actions; privileged capabilities such as `debug_private` and `export_private` are separate. `observe_glauquir` is a trusted GLAUQUIR view and is not the general player Observe API.

## Sources

- [Observe fields](observe.md), [Act fields](act.md), [Session fields](session.md)
- `gisela/engine/authorized_gateway.py`, `action_handler.py`, `projection.py`
- `docs/architecture/API_CLIENTES.md`, `E0_FRONTERA_AUTORIZADA_Y_PERSISTENCIA.md`
