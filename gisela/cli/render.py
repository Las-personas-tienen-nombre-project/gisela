"""Presentación de texto de GLAUQUIR, sin lógica del mundo."""

from __future__ import annotations

from .color import Styler
from .render_table import show_table


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
        show_presentation(view["presentation"], styler)
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


def show_causal(
    events: list[dict], indent: str = "", styler: Styler | None = None
) -> None:
    """Presenta solo el historial confirmado provisto por Observe."""
    from gisela.engine.presentation_semantics import LABELS, clean

    styler = styler or Styler()
    colors = {
        "damage": "red",
        "healing": "green",
        "buff": "cyan",
        "debuff": "magenta",
        "neutral": "default",
    }
    for item in events:
        role = item.get("semantic_role")
        label = LABELS.get(role)
        detail = item.get("display_text")
        if detail is None:
            detail = _causal_description(item)
        text = (label + ": " if label else "") + clean(detail)
        print(
            indent
            + styler.paint(colors.get(role, "default"), f"  #{item['sequence']} {text}")
        )


def _causal_description(item: dict) -> str:
    detail = item.get("detail", {})
    kind = item["kind"]
    if kind == "initiative":
        return "Orden de actuación: " + str(detail.get("order", "?"))
    if kind == "event_triggered":
        return "Acontecimiento: " + str(detail.get("event", "?"))
    if kind == "encounter_completed":
        return "Desenlace: " + str(detail.get("outcome", "?"))
    if kind == "dice_roll":
        return f"Tirada d{detail.get('sides', '?')}: {detail.get('result', '?')} ({detail.get('store', '?')})"
    if kind == "contest_resolved":
        return (
            f"Concurso {detail.get('profile', '?')}: {detail.get('left_total', '?')} frente a "
            f"{detail.get('right_total', '?')} · {detail.get('winner', '?')}"
        )
    if kind == "variable_changed":
        return f"{detail.get('variable', '?')}: {detail.get('before', '?')} → {detail.get('after', '?')}"
    if kind in ("skill_started", "skill_played"):
        return str(detail.get("actor", "?")) + " · " + str(detail.get("card", "?"))
    return str(detail.get("text", kind))


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
        label = action["label"]
        if action.get("target") and " → " not in label:
            label += " → " + str(action["target"])
        _line(
            f"  {option_letter(index)}) {label}  [accion {action['id']}]",
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


def show_presentation(presentation: dict, styler: Styler | None = None) -> None:
    """Render generic regions; action offers retain original Observe IDs."""
    for region in presentation["regions"]:
        _show_region(region, 0, styler or Styler())


def _show_region(region: dict, depth: int, styler: Styler) -> None:
    if region.get("visible") is False:
        return
    indent = "  " * depth
    label = region.get("label") or region["id"].replace("_", " ")
    print("\n" + indent + label.upper())
    if region.get("missing"):
        print(indent + "  " + _display_text(region.get("text", "No disponible")))
        return
    for child in region.get("children", []):
        _show_region(child, depth + 1, styler)
    handlers = {
        "choice_list": _region_choices,
        "event_log": _region_events,
        "table": _region_table,
        "initiative_order": _region_initiative,
        "entity_collection": _region_collection,
    }
    handlers.get(region["component"], _region_value)(region, indent, styler)


def _display_text(value) -> str:
    from gisela.engine.presentation_semantics import clean

    if isinstance(value, dict):
        for field in ("label", "name", "actor", "id", "kind"):
            if field in value:
                return clean(value[field])
    text = clean(value)
    return "Pendiente de confirmación" if text == "No disponible" else text


def _region_choices(region, indent, styler):
    items = region.get("items", [])
    if items:
        print(indent + "  Elija una letra o escriba: accion <id>")
        offers(items, styler)
    else:
        print(indent + "  No hay acciones disponibles.")


def _region_events(region, indent, styler):
    items = region.get("items", [])
    if not items:
        print(indent + "  Todavía no hay acontecimientos confirmados.")
    elif "count" in region:
        print(indent + f"  {len(items)} de {region['count']} registros seleccionados")
        if "blocks" in region:
            _show_causal_blocks(region["blocks"], indent, styler)
        else:
            show_causal(items, indent, styler)
    else:
        if len(items) > 10:
            print(indent + f"  Últimos 10 de {len(items)} registros publicados")
        show_causal(items[-10:], indent, styler)


def _show_causal_blocks(blocks, indent, styler):
    for block in blocks:
        if block["kind"] == "event":
            show_causal([block["event"]], indent, styler)
        else:
            print(indent + "  Acción confirmada:")
            show_causal(block["events"][:1], indent, styler)
            if len(block["events"]) > 1:
                print(indent + "    Resultados y registros correlacionados:")
                show_causal(block["events"][1:], indent + "    ", styler)


def _region_table(region, indent, styler):
    show_table(region, indent)


def _region_initiative(region, indent, styler):
    for index, item in enumerate(region.get("items", []), 1):
        print(f"{indent}  {index}. {_display_text(item)}")


def _region_value(region, indent, styler):
    if "items" in region:
        for item in region["items"]:
            print(indent + "  " + _display_text(item))
    elif "value" in region:
        print(indent + "  " + _display_text(region["value"]))
    elif "text" in region:
        print(indent + "  " + _display_text(region["text"]))


def _region_collection(region, indent, styler):
    items = region.get("items", [])
    if not items:
        print(indent + "  Ningún elemento vigente.")
    elif all(
        isinstance(item, dict) and {"entity", "id", "value"} <= item.keys()
        for item in items
    ):
        _show_resources(items, indent)
    else:
        for item in items:
            print(indent + "  " + _collection_text(item))


def _show_resources(items, indent):
    grouped = {}
    for item in items:
        grouped.setdefault(item["entity"], []).append(item)
    for entity, resources in grouped.items():
        print(indent + "  " + _display_text(entity).upper())
        for item in resources:
            measure = str(item["value"])
            if "maximum" in item:
                measure += "/" + str(item["maximum"])
            print(indent + "    " + _display_text(item["id"]) + ": " + measure)


def _collection_text(item):
    if isinstance(item, dict) and {"id", "beneficiary", "remaining"} <= item.keys():
        return f"{item['beneficiary']} · {item['id']} ({item['remaining']} restantes)"
    if isinstance(item, dict) and {"actor", "die", "score"} <= item.keys():
        return f"{item['actor']}: {item['die']} → {item['score']}"
    return _display_text(item)
