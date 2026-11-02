"""Presentación de texto de GLAUQUIR, sin lógica del mundo."""

from __future__ import annotations

from .color import Styler


def available(actions: list[dict]) -> list[dict]:
    return [action for action in actions if action["enabled"]]


def ordered_actions(actions: list[dict]) -> list[dict]:
    """Orden visible de las ofertas: salidas primero, luego otras acciones."""
    enabled = available(actions)
    return [a for a in enabled if a.get("role") == "exit"] + [
        a for a in enabled if a.get("role") != "exit"
    ]


def option_letter(index: int) -> str:
    """Índice cero basado en letras: A..Z, AA..AZ, BA..."""
    result = ""
    index += 1
    while index:
        index, digit = divmod(index - 1, 26)
        result = chr(65 + digit) + result
    return result


def _line(value: str, role: str, styler: Styler) -> None:
    print(styler.paint(role, value))


def _show_exploring(view: dict, styler: Styler) -> None:
    from datetime import datetime

    title = view.get("scene_title", view["scene"])
    when = view.get("world_time")
    if when:
        title += " — " + datetime.fromisoformat(when).strftime("%H:%M")
    _line("\n" + title.upper(), "scene_title", styler)
    if view.get("scene_description"):
        _line("\n" + view["scene_description"], "description", styler)
    if view.get("actors"):
        print("\nPERSONAS")
        for actor in view["actors"]:
            _line("  " + actor["name"], actor.get("color", "person"), styler)
    for role, heading in (
        ("portable_object", "OBJETOS RECOGIBLES"),
        ("fixed_object", "OBJETOS FIJOS"),
        ("element", "ELEMENTOS"),
    ):
        items = [
            item
            for item in view.get("elements", [])
            if item.get("role", "element") == role
        ]
        if items:
            print("\n" + heading)
            for item in items:
                _line(
                    "  " + item["label"],
                    item.get("color", role if role != "element" else "fixed_object"),
                    styler,
                )


def _show_content(view: dict, styler: Styler) -> None:
    content = view["content"]
    kind = content["kind"]
    if kind == "exploring":
        _show_exploring(view, styler)
    elif kind in ("narrate", "dialogue"):
        speaker = content.get("speaker", "")
        _line(
            "\n" + (speaker + ": " if speaker else "") + content["text"],
            "dialogue" if kind == "dialogue" else "description",
            styler,
        )
    elif kind == "choice":
        print("\n" + content.get("prompt", "Elija una opción:"))
    elif kind == "pending_transaction":
        print("\n" + content.get("prompt", content["purpose"]))
    elif kind == "pending_evaluation":
        evaluation(content)
    elif kind == "ending":
        print("\nFinal: " + content.get("title", content["ending"]))
    else:
        print("\n" + kind.replace("_", " ").capitalize())


def _show_actions(view: dict, styler: Styler) -> None:
    ordered = ordered_actions(view["actions"])
    exits = [a for a in ordered if a.get("role") == "exit"]
    context = [a for a in ordered if a.get("role") != "exit"]
    if exits:
        print("\nSALIDAS")
        offers(exits, styler=styler, start=0)
    if context:
        print("\nACCIONES")
        offers(context, styler=styler, start=len(exits))


def show(view: dict, developer: bool = False, styler: Styler | None = None) -> None:
    """Imprime la proyección pública y un resumen opcional de desarrollo."""
    styler = styler or Styler()
    _show_content(view, styler)
    annotations = view.get("annotations", [])
    if annotations:
        print("\n" + styler.paint("information", "INFORMACIÓN"))
        for item in annotations:
            description = item["text"]
            if item["scope"] == "action":
                offer = next(
                    (a for a in view["actions"] if a["action_id"] == item["action_id"]),
                    None,
                )
                if offer is not None:
                    description = offer["label"] + ": " + description
            _line("  " + description, "information", styler)
    _show_actions(view, styler)
    if developer:
        print(
            styler.paint(
                "debug", f"\nAcciones disponibles: {len(available(view['actions']))}"
            )
        )
        print(
            styler.paint(
                "debug",
                f"Acciones bloqueadas: {len(view['actions']) - len(available(view['actions']))}",
            )
        )
        print(
            styler.paint(
                "debug", "acciones bloqueadas — muestra identificadores y motivos"
            )
        )


def evaluation(content: dict) -> None:
    """Presenta los datos publicados por Observe, sin recomputar la tirada."""
    print("\nEvaluación de dados: " + str(content["evaluation_id"]))
    rolls = ", ".join(str(value) for value in content["rolls"])
    print("Tirada: " + (rolls or "(sin azar)"))
    print("Resultado: " + content["outcome"])
    if content.get("auxiliary_request"):
        print(content["auxiliary_request"]["prompt"])


def offers(
    actions: list[dict],
    styler: Styler | None = None,
    start: int = 0,
) -> None:
    """Presenta acciones como comandos, sin imponer un menú numérico."""
    styler = styler or Styler()
    for index, action in enumerate(available(actions), start):
        _line(
            f"  {option_letter(index)}) {action['label']}  [accion {action['id']}]",
            "exit" if action.get("role") == "exit" else "action",
            styler,
        )


def blocked(actions: list[dict], styler: Styler | None = None) -> None:
    styler = styler or Styler()
    for action in actions:
        if not action["enabled"]:
            suffix = " — " + action["reason"] if action.get("reason") else ""
            _line(f"  {action['id']} — {action['label']}{suffix}", "debug", styler)


def catalogue(items: list[dict], title: str) -> None:
    """Muestra fichas disponibles sin revelar definiciones desconocidas."""
    print("\n" + title)
    if not items:
        print("No hay elementos disponibles.")
    for item in items:
        suffix = " (" + item["zone"] + ")" if "zone" in item else ""
        print(item["title"] + suffix + " [" + item["id"] + "]")


def card(item: dict) -> None:
    """Presenta una ficha pública sin inspeccionar las estructuras de ALBERTO."""
    print("\n" + item["title"])
    print(item.get("description", "No tiene descripción pública."))
    print("Identificador: " + item["id"])


def history(entries: list[dict]) -> None:
    """Presenta la lectura acumulada por GISELA, no la traza interna."""
    print("\nHistoria de la partida")
    for item in entries:
        print("\n" + item["text"])
    if not entries:
        print("Todavía no hay pasajes registrados.")


def status(view: dict) -> None:
    """Imprime los atributos que el motor autoriza al protagonista."""
    print("\nEstado: " + str(view.get("character") or "Sin protagonista"))
    for stat in view.get("stats", []):
        print(
            f"{stat['name']}: {stat['effective']} "
            f"(base {stat['base']}, actual {stat['current']}, "
            f"modificador {stat['modifier']})"
        )


def confirmed(entries: list[dict]) -> None:
    """Muestra únicamente las decisiones confirmadas por GISELA."""
    for item in entries:
        if item["kind"] in ("action", "choice", "skill"):
            print("\nAcción confirmada: " + item["text"])
