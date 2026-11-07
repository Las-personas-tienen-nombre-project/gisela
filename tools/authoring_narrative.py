"""Pure narrative-step constructors for GISELA's existing JSON contract.

No execution, I/O, schema substitution or package-specific references.
Admission remains the authority for complete compiled packages.
"""

from copy import deepcopy


def _name(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Narrative identifier must be a nonempty string")
    return value


def text(value):
    return {"text": _name(value)}


def step(identifier, op, **fields):
    if "id" in fields or "op" in fields:
        raise ValueError("Reserved narrative step property")
    return {"id": _name(identifier), "op": _name(op), **deepcopy(fields)}


def narrate(identifier, content):
    return step(identifier, "narrate", text=text(content))


def dialogue(identifier, speaker, content):
    return step(identifier, "dialogue", speaker=_name(speaker), text=text(content))


def show_scene(identifier, scene_id):
    return step(identifier, "scene", scene=_name(scene_id))


def target_step(identifier):
    return {"step": _name(identifier)}


def target_node(identifier):
    return {"node": _name(identifier)}


def owns(owner, object_id):
    return {"owns": {"owner": _name(owner), "object": _name(object_id)}}


def has_fact(identifier):
    return {"has_fact": _name(identifier)}


def negated(condition):
    return {"not": deepcopy(condition)}


def record_fact(identifier):
    return {"op": "record_fact", "fact": _name(identifier)}


def transfer(object_id, origin, destination):
    return {
        "op": "transfer",
        "object": _name(object_id),
        "from": _name(origin),
        "to": _name(destination),
    }


def option(identifier, label, details):
    """Build a choice option from next/effects/enabled_if fields."""
    if not isinstance(details, dict) or "next" not in details:
        raise ValueError("Option requires a next target")
    if set(details) - {"next", "effects", "enabled_if"}:
        raise ValueError("Unsupported option property")
    if not isinstance(details["next"], dict):
        raise ValueError("Option next target must be a dictionary")  # noqa: TRY004
    return {"id": _name(identifier), "label": text(label), **deepcopy(details)}


def choice(identifier, options):
    if not isinstance(options, (list, tuple)) or not options:
        raise ValueError("Choice requires options")
    ids = [_name(item["id"]) for item in options]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate option IDs")
    return step(identifier, "choice", options=list(options))


def transition(identifier, destination):
    return step(identifier, "transition", next=destination)


def condition(identifier, test, branches):
    if not isinstance(branches, (tuple, list)) or len(branches) != 2:
        raise ValueError("Condition requires then/else targets")
    return step(
        identifier, "condition", test=test, then=branches[0], **{"else": branches[1]}
    )


def ending(identifier, ending_id):
    return step(identifier, "ending", ending=_name(ending_id))


def node(identifier, steps):
    if not isinstance(steps, (list, tuple)) or not steps:
        raise ValueError("Node requires steps")
    ids = [_name(item["id"]) for item in steps]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate step IDs")
    return {"id": _name(identifier), "steps": deepcopy(list(steps))}


def fact_reaction(identifier, fact, details):
    """Build a fact-triggered reaction from guard and effects."""
    if not isinstance(details, dict) or set(details) != {"when", "effects"}:
        raise ValueError("Reaction requires guard and effects")
    effects = details["effects"]
    if not isinstance(effects, (list, tuple)) or not effects:
        raise ValueError("Reaction requires effects")
    return {
        "id": _name(identifier),
        "trigger": {"on": "fact_recorded", "fact": _name(fact)},
        "when": deepcopy(details["when"]),
        "effects": deepcopy(list(effects)),
    }
