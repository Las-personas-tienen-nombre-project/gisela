"""Registro narrativo confirmado, diferente de la traza técnica causal.

Se almacena en history.reading dentro de la misma sesión. Consultar el registro
nunca reevalúa una escena contra un mundo que ya pudo haber cambiado.
"""

from __future__ import annotations


def _display(session, state: dict) -> tuple[str, str, str] | None:
    """Resuelve el texto de la posición narrativa confirmada."""
    from .projection import text

    kind = state["status"]
    if kind == "exploring":
        scene = session._scenes[state["current_scene"]]
        name = text(scene.get("title", scene["id"]), session)
        description = (
            text(scene["description"], session) if "description" in scene else ""
        )
        return "scene", scene["id"], "\n\n".join(x for x in (name, description) if x)
    if kind == "ended":
        end = next(
            (e for e in session._package["endings"] if e["id"] == state["ending"]), None
        )
        name = (
            text(end["title"], session) if end and "title" in end else state["ending"]
        )
        return "ending", state["ending"], name
    if kind == "node":
        step = session._current_step(state)
        if step["op"] in ("narrate", "dialogue"):
            body = text(step["text"], session)
            if step["op"] == "dialogue":
                body = step["speaker"] + ": " + body
            return step["op"], state["cursor"]["node"] + "." + step["id"], body
    return None


def append(state: dict, record: tuple[str, str, str]) -> None:
    """Anexa un texto tras la confirmación de la acción que lo origina."""
    kind, source, text = record
    if not text:
        return
    reading = state["history"].setdefault("reading", [])
    reading.append(
        {
            "sequence": len(reading) + 1,
            "kind": kind,
            "source": source,
            "text": text,
            "turn": state["turn"],
        }
    )


def entry(session, state: dict, previous: dict | None = None) -> None:
    """Captura una nueva presentación, sin duplicar una posición sin cambios."""
    present = _display(session, state)
    if (
        not present
        or state.get("pending_transaction")
        or state.get("pending_evaluation")
    ):
        return
    old = _display(session, previous) if previous else None
    if present != old:
        append(state, present)


def action(session, state: dict, source: dict) -> None:
    """Conserva la elección o interacción confirmada con su etiqueta pública."""
    from .projection import text

    kind = source["kind"]
    if kind == "choice_option":
        step = next(
            s
            for s in session._nodes[source["node"]]["steps"]
            if s["id"] == source["step"]
        )
        option = next(o for o in step["options"] if o["id"] == source["option"])
        append(state, ("choice", source["step"], text(option["label"], session)))
    elif kind == "scene_action":
        from .scene_actions import definition

        item = definition(session, source)
        append(state, ("action", source["action"], text(item["label"], session)))
    elif kind == "skill_play":
        previous = next(
            (
                e
                for e in state["history"]["trace"][::-1]
                if e["kind"] == "skill_played"
                and e["source"] == source["skill_instance"]
            ),
            None,
        )
        if previous:
            card = session._cards[previous["detail"]["card"]]
            append(
                state, ("skill", source["skill_instance"], text(card["title"], session))
            )


def history(session, limit: int | None = None) -> list[dict]:
    """Devuelve una copia pública, nunca eventos causales ni borradores."""
    if limit is not None and (type(limit) is not int or limit < 1):
        raise ValueError("El límite de history debe ser positivo")
    entries = session._state["history"].get("reading", [])
    return [item.copy() for item in (entries[-limit:] if limit else entries)]
