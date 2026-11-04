"""Rutas de operaciones declarativas en orden de admisión."""

from __future__ import annotations

if __package__:
    from .semantic_shared import pointer
else:
    from semantic_shared import pointer


def evaluation_operations(owner: dict, path: str):
    """Devuelve consecuencias declaradas en ramas, con sus rutas de origen."""
    for bi, branch in enumerate(owner.get("evaluation", {}).get("branches", [])):
        for i, op in enumerate(branch.get("effects", [])):
            yield op, pointer(path, "evaluation", "branches", bi, "effects", i)


def node_operations(pkg: dict):
    """Recorre consecuencias de pasos, opciones y evaluaciones de nodos."""
    for ni, node in enumerate(pkg["nodes"]):
        for si, step in enumerate(node["steps"]):
            p = pointer("nodes", ni, "steps", si)
            for i, op in enumerate(step.get("effects", [])):
                yield op, pointer(p, "effects", i)
            for oi, option in enumerate(step.get("options", [])):
                for i, op in enumerate(option.get("effects", [])):
                    yield op, pointer(p, "options", oi, "effects", i)
            for bi, branch in enumerate(step.get("branches", [])):
                for i, op in enumerate(branch.get("effects", [])):
                    yield op, pointer(p, "branches", bi, "effects", i)
            yield from evaluation_operations(step, p)
            for oi, option in enumerate(step.get("options", [])):
                yield from evaluation_operations(option, pointer(p, "options", oi))


def scene_operations(pkg: dict):
    """Recorre acciones de escenas y elementos en orden declarado."""
    for si, scene in enumerate(pkg["scenes"]):
        for ai, action in enumerate(scene.get("actions", [])):
            for i, op in enumerate(action.get("effects", [])):
                yield op, pointer("scenes", si, "actions", ai, "effects", i)
            yield from evaluation_operations(
                action, pointer("scenes", si, "actions", ai)
            )
        for ei, element in enumerate(scene.get("elements", [])):
            for ai, action in enumerate(element.get("actions", [])):
                for i, op in enumerate(action.get("effects", [])):
                    yield (
                        op,
                        pointer(
                            "scenes", si, "elements", ei, "actions", ai, "effects", i
                        ),
                    )
                yield from evaluation_operations(
                    action, pointer("scenes", si, "elements", ei, "actions", ai)
                )


def rule_card_operations(pkg: dict):
    """Recorre reglas y consecuencias de cartas tras los nodos y escenas."""
    for ri, rule in enumerate(pkg["rules"]):
        for i, op in enumerate(rule["effects"]):
            yield op, pointer("rules", ri, "effects", i)
    for ci, card in enumerate(pkg["cards"]):
        if card["kind"] == "skill":
            for i, op in enumerate(card["play"]["effects"]):
                yield op, pointer("cards", ci, "play", "effects", i)
            for oi, outcome in enumerate(card["play"].get("outcomes", [])):
                for i, op in enumerate(outcome["effects"]):
                    yield (
                        op,
                        pointer("cards", ci, "play", "outcomes", oi, "effects", i),
                    )
        if card["kind"] == "effect":
            for field in ("on_apply", "on_expire", "on_actor_turn_start"):
                for i, op in enumerate(card.get(field, [])):
                    yield op, pointer("cards", ci, field, i)
