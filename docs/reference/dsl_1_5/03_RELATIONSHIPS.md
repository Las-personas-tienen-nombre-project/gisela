# 03 Declarations and relationships

The package manifest supplies the package identity, language, entry point and global vocabularies. Cards define reusable characters, locations, objects, skills and effects. `initial_state` creates instances from those definitions; a definition is not the same object as a runtime instance. A scene selects what can be seen and interacted with, subject to location, presence and visibility conditions. Nodes define narrative steps, conditional branches and transitions. Rules respond to declared triggers. Traits and DICE profiles are optional catalogs referenced by other declarations.

## Reference checks

The semantic validator indexes cards, nodes, scenes, declarations, initial instances and vocabulary before checking references and types. Unknown node destinations are rejected at admission. Instance definitions and references must agree with the expected entity kind. Variable expressions must match declared scope and type. Skill parameters are checked within the invocation context. A trait assignment must identify a trait present in the catalog and an admissible entity kind.

A narrative transition is not a physical move. For spatial scenes, `move_character` and `set_scene` must be consistent within the same committed transaction. A presentation region may refer to a named presentation view, but those references are validated separately from game rules.

## Author navigation

Start at [package fields](package.md), then [cards](card.md), [initial state](initial_state.md), [nodes](node.md), [scenes](scene.md), [rules](rule.md), [expressions](common.md), and [presentation](09_PRESENTATION.md). For execution authority use [Observe and Act](08_OBSERVE_ACT.md).

## Sources

- `gisela/contracts/semantic_definitions.py`, `semantic_packages.py`, `semantic_traits.py`
- `gisela/engine/scene_presence.py`, `scene_actions.py`, `initialization.py`
- `docs/architecture/ESCENAS_Y_PRESENCIA.md`
