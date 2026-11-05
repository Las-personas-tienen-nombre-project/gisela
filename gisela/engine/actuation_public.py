"""Public projection of authorial actuation onto the standard Observe/Act boundary."""

from __future__ import annotations

from .actuation import current
from .conditions import predicate
from .projection import text


def project(session, view, language=None):
    state = session._state
    clock = state["actuation"]
    actor = current(state)
    recent = clock["events"][-12:]
    messages, rolls = _history(state)
    contests = _contests(state)
    from .causal_trace import project as causal_project

    view["actuation"] = {
        "round": clock["round"],
        "actor": actor,
        "remaining": clock["remaining"],
        "order": list(clock["order"]),
        "initiative": [
            {"actor": x["actor"], "die": x["die"], "score": x["score"]}
            for x in clock["initiative"]
        ],
        "outcome": clock.get("outcome"),
        "messages": messages[-12:],
        "rolls": [
            {
                "source": item["source"],
                "sides": item["detail"]["sides"],
                "result": item["detail"]["result"],
                "store": item["detail"]["store"],
            }
            for item in rolls[-12:]
        ],
        "contests": contests[-12:],
        "causal": causal_project(state),
        "participants": _participants(session),
        "resources": _resources(session),
        "effects": _effects(clock),
        "events": [
            {"kind": event["kind"], "detail": str(event["detail"])[:300]}
            for event in recent
        ],
    }
    view["actions"] = []
    if clock["complete"]:
        view["status"] = "ended"
        view["content"] = {
            "kind": "ending",
            "ending": clock["outcome"] or "encounter_complete",
        }
        return
    view["content"] = {
        "kind": "choice",
        "prompt": f"Ronda {clock['round']}: {actor} ({clock['remaining']} acciones)",
    }
    view["actions"] = _actions(session, actor, language)


def _actions(session, actor, language):
    state = session._state
    actions = []
    if actor == state.get("player_character"):
        for skill in state["world"]["skills"]:
            if skill["character"] != actor or skill["zone"] != "hand":
                continue
            card = session._cards[skill["card"]]
            if (
                card["kind"] != "skill"
                or card.get("passive_traits")
                or card["play"].get("parameters")
            ):
                continue
            enabled = predicate(
                state,
                card["play"].get("requires", {"constant": True}),
                session._definitions,
            )
            actions.append(
                {
                    "kind": "actuation_skill",
                    "action_id": "actturn_" + skill["id"],
                    "id": skill["id"],
                    "label": text(card["title"], session, language),
                    "enabled": enabled,
                }
            )
        person = next(
            p
            for p in session._package["actuation"]["participants"]
            if p["character"] == actor
        )
        if person.get("allow_pass", False):
            actions.append(
                {
                    "kind": "actuation_pass",
                    "action_id": "actturn_pass",
                    "id": "pasar",
                    "label": "Pasar",
                    "enabled": True,
                }
            )
    else:
        actions.append(
            {
                "kind": "actuation_advance",
                "action_id": "actturn_advance",
                "id": "continuar",
                "label": f"Actuar: {actor}",
                "enabled": True,
            }
        )
    return _label_targets(session, actions)


def _label_targets(session, actions):
    mappings = {
        entry["skill"]: entry["target"]
        for entry in session._package.get("presentation", {}).get("action_targets", [])
    }
    for action in actions:
        target = mappings.get(action["id"])
        if target:
            action["target"] = target
            action["label"] += " -> " + target
    return actions


def _participants(session):
    return [
        {"id": person["character"]}
        for person in session._package["actuation"]["participants"]
    ]


def _resources(session):
    variables = session._state["narrative"]["session_variables"]
    result = []
    for entry in session._package["actuation"].get("public_resources", []):
        item = {
            "entity": entry["entity"],
            "id": entry["id"],
            "value": variables[entry["current"]],
        }
        if "maximum" in entry:
            item["maximum"] = variables[entry["maximum"]]
        result.append(item)
    return result


def _effects(clock):
    return [
        {
            "id": effect["id"],
            "beneficiary": effect["beneficiary"],
            "remaining": effect["remaining"],
        }
        for effect in clock["effects"][:64]
    ]


def _history(state):
    messages = [
        item["detail"]["text"]
        for item in state["history"]["trace"]
        if item["kind"] == "author_message"
        and isinstance(item.get("detail", {}).get("text"), str)
    ]
    rolls = [item for item in state["history"]["trace"] if item["kind"] == "dice_roll"]
    return messages, rolls


def _contests(state):
    """Publica resultados DICE ya confirmados sin reejecutar evaluaciones."""
    entries = []
    for item in state["history"]["trace"]:
        if item["kind"] != "contest_resolved":
            continue
        detail = item["detail"]
        entries.append(
            {
                "source": item["source"],
                "profile": detail["profile"],
                "winner": detail["winner"],
                "left": _contest_side(detail["left"]),
                "right": _contest_side(detail["right"]),
            }
        )
    return entries


def _contest_side(dice):
    """Expone datos del dado, no contexto privado de participantes o TRAITS."""
    return {
        name: dice[name] for name in ("rolls", "die_value", "base", "bonus", "total")
    }
