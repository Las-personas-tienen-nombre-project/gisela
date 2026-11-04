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
    if "actuation" in view and "presentation" not in view:
        clock = view["actuation"]
        print(
            f"\nACTUACIÓN · ronda {clock['round']} · {clock['actor'] or 'final'} · acciones {clock['remaining']}"
        )
        if clock["round"] == 1 and clock["actor"] == clock["order"][0]:
            print(
                "  Iniciativa: "
                + ", ".join(
                    f"{x['actor']} {x['die']} → {x['score']}"
                    for x in clock["initiative"]
                )
            )
        if clock.get("causal"):
            show_causal(clock["causal"][-10:])
        else:
            for roll in clock.get("rolls", [])[-3:]:
                print(f"  Dado d{roll['sides']}: {roll['result']} ({roll['store']})")
            for message in clock["messages"][-5:]:
                print("  " + message)
        for event in clock["events"][-3:]:
            print("  " + event["kind"] + ": " + event["detail"])
    if "presentation" in view:
        show_presentation(view["presentation"])
    else:
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


def show_causal(events: list[dict]) -> None:
    """Presenta solo el historial confirmado provisto por Observe."""
    for item in events:
        detail = item["detail"]
        kind = item["kind"]
        if kind == "initiative":
            result = "Iniciativa: " + detail["order"]
        elif kind == "event_triggered":
            result = "Acontecimiento: " + detail["event"]
        elif kind == "encounter_completed":
            result = "Desenlace: " + detail["outcome"]
        elif kind == "dice_roll":
            result = f"d{detail['sides']} = {detail['result']} ({detail['store']})"
        elif kind == "contest_resolved":
            result = (
                f"{detail['profile']}: {detail['left_total']} vs "
                f"{detail['right_total']} ({detail['winner']})"
            )
        elif kind == "variable_changed":
            result = f"{detail['variable']}: {detail['before']} → {detail['after']}"
        elif kind in ("skill_started", "skill_played"):
            result = f"{detail['actor']} · {detail['card']}"
        else:
            result = detail.get("text", "")
        print(f"  #{item['sequence']} {kind}: {result}")


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


def show_presentation(presentation: dict) -> None:
    """Render declarative regions without changing Observe or action order."""
    for region in presentation["regions"]:
        _show_region(region)


def _show_region(region: dict, depth: int = 0) -> None:
    if region.get("visible") is False:
        return
    indent = "  " * depth
    label = region.get("label") or region["id"].replace("_", " ")
    print("\n" + indent + label.upper())
    if region.get("missing"):
        print(indent + "  " + region.get("text", "No disponible"))
        return
    for child in region.get("children", []):
        _show_region(child, depth + 1)
    kind = region["component"]
    if kind == "choice_list":
        items = region.get("items", [])
        if items:
            offers(items)
        else:
            print(indent + "  No hay acciones disponibles.")
    elif kind == "event_log":
        items = region.get("items", [])
        if items:
            show_causal(items[-10:], indent)
        else:
            print(indent + "  Todavía no hay acontecimientos confirmados.")
    elif kind == "initiative_order":
        for index, item in enumerate(region.get("items", []), 1):
            print(f"{indent}  {index}. {_display_text(item)}")
    elif kind == "entity_collection":
        _show_collection(region.get("items", []), indent)
    elif "items" in region:
        for item in region["items"]:
            print(indent + "  " + _display_text(item))
    elif "value" in region:
        print(indent + "  " + _display_text(region["value"]))
    elif "text" in region:
        print(indent + "  " + region["text"])


def _display_text(value) -> str:
    """Provide a readable fallback for generic public values."""
    if isinstance(value, dict):
        for field in ("label", "name", "actor", "id", "kind"):
            if field in value:
                return str(value[field])
    return str(value)


def _show_collection(items: list, indent: str) -> None:
    """Group public resources; never interpret their domain semantics."""
    if not items:
        print(indent + "  Ningún elemento vigente.")
        return
    if all(
        isinstance(item, dict) and {"entity", "id", "value"} <= item.keys()
        for item in items
    ):
        grouped = {}
        for item in items:
            grouped.setdefault(item["entity"], []).append(item)
        for entity, resources in grouped.items():
            print(indent + "  " + str(entity).upper())
            for item in resources:
                measure = str(item["value"])
                if "maximum" in item:
                    measure += "/" + str(item["maximum"])
                print(indent + "    " + str(item["id"]) + ": " + measure)
        return
    for item in items:
        if isinstance(item, dict) and {"id", "beneficiary", "remaining"} <= item.keys():
            print(
                indent + "  " + str(item["beneficiary"]) + " · " + str(item["id"])
                + " (" + str(item["remaining"]) + " restantes)"
            )
        elif isinstance(item, dict) and {"actor", "die", "score"} <= item.keys():
            print(
                indent + "  " + str(item["actor"]) + ": "
                + str(item["die"]) + " → " + str(item["score"])
            )
        else:
            print(indent + "  " + _display_text(item))


def _causal_description(item: dict) -> str:
    """Format only confirmed fields already projected into Observe."""
    detail = item["detail"]
    kind = item["kind"]
    if kind == "initiative":
        return "Orden de actuación: " + str(detail["order"])
    if kind == "event_triggered":
        return "Acontecimiento: " + str(detail["event"])
    if kind == "encounter_completed":
        return "Desenlace: " + str(detail["outcome"])
    if kind == "dice_roll":
        return f"Tirada d{detail['sides']}: {detail['result']} ({detail['store']})"
    if kind == "contest_resolved":
        return (
            f"Concurso {detail['profile']}: {detail['left_total']} frente a "
            f"{detail['right_total']} · {detail['winner']}"
        )
    if kind == "variable_changed":
        return f"{detail['variable']}: {detail['before']} → {detail['after']}"
    if kind in ("skill_started", "skill_played"):
        return str(detail["actor"]) + " · " + str(detail["card"])
    return str(detail.get("text", kind))


def show_causal(events: list[dict], indent: str = "") -> None:
    """Show a bounded window of confirmed causal records in original order."""
    for item in events:
        print(indent + f"  #{item['sequence']} " + _causal_description(item))


def evaluation(content: dict) -> None:
    """Present published evaluation values without recalculating dice."""
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
    """Present authorized actions with exactly the current Observe identifiers."""
    styler = styler or Styler()
    for index, action in enumerate(available(actions), start):
        label = action["label"]
        if action.get("target") and " → " not in label:
            label += " → " + str(action["target"])
        _line(
            f"  {option_letter(index)}) {label}  [accion {action['id']}]",
            "exit" if action.get("role") == "exit" else "action",
            styler,
        )


def blocked(actions: list[dict], styler: Styler | None = None) -> None:
    """Report disabled offers without treating them as executable choices."""
    styler = styler or Styler()
    for action in actions:
        if not action["enabled"]:
            suffix = " — " + action["reason"] if action.get("reason") else ""
            _line(f"  {action['id']} — {action['label']}{suffix}", "debug", styler)

