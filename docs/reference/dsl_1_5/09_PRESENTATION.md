# 09 Public declarative presentation

## Ownership

The package author may declare `presentation` regions, views, action targets and supported formatting roles. GISELA checks the declarations and projects selected public data. GLAUQUIR is a presentation client, including terminal layout and colors; it does not own narrative truth or the authoritative world state.

## Views and constraints

In the implemented v0.8.2 presentation contract on DSL 1.5, `presentation.views` has at most 32 named views. A table view reads approved public sources including `actuation.resources`, `actuation.participants`, `actuation.effects`, and `actors`. It supports 1 to 12 columns and a row limit of 1 to 64. A limited `pivot_resources` transform is available only on actuation resources.

An event log reads `actuation.causal`, selects permitted kinds, supports a maximum 64 entry selection, and may group by causal action when the originating action remains in the published window. The public causal source itself is limited to the last 40 entries. There is no paging over full private history.

## Semantic roles are author labels

Permitted event roles are `damage`, `healing`, `buff`, `debuff`, `neutral`. They are display classifications and cannot certify the mechanical cause of a resource delta. A template may interpolate only allowed public fields. Unsafe attribute access and executable formatting are rejected by semantic validation. GLAUQUIR chooses how to render roles. A change in presentation data changes package digest but must not change narrative logic.

## Identity and presentation colors

Actor `unknown_name`, `known_if`, and optional stable `public_id` can limit premature identity exposure. Presentation colors are a fixed role vocabulary. Client visuals must not be used to infer new game consequences.

## Sources

- `docs/architecture/PRESENTACION_DECLARATIVA_V082.md`, `CORRELACION_CAUSAL_V082C.md`, `API_CLIENTES.md`
- `gisela/engine/presentation_views.py`, `presentation_semantics.py`
- `gisela/engine/tests/test_release_v082e.py`, `test_release_v082f.py`
