"""Presentación de texto de GLAUQUIR, sin lógica del mundo."""

from __future__ import annotations


def show(view: dict) -> None:
    """Imprime la proyección narrativa y las acciones de GISELA."""
    content = view["content"]
    kind = content["kind"]
    if kind == "exploring":
        print("\nEscena: " + view["scene"])
        print("\n" + view.get("scene_title", view["scene"]))
        if view.get("scene_description"):
            print("\n" + view["scene_description"])
        for title, group, key in [
            ("Personas", "actors", "name"),
            ("Elementos", "elements", "label"),
        ]:
            if view.get(group):
                print(
                    title + ": " + ", ".join(o.get(key, o["id"]) for o in view[group])
                )
    elif kind in ("narrate", "dialogue"):
        speaker = content.get("speaker", "")
        print("\n" + (speaker + ": " if speaker else "") + content["text"])
    elif kind == "choice":
        print("\n" + content.get("prompt", "Elija una opción:"))
    elif kind == "pending_transaction":
        print("\n" + content.get("prompt", content["purpose"]))
    elif kind == "pending_evaluation":
        evaluation(content)
    elif kind == "ending":
        print("\nFinal: " + content["ending"])
    else:
        print("\n" + kind.replace("_", " ").capitalize())
    offers(view["actions"])


def evaluation(content: dict) -> None:
    """Presenta los datos publicados por Observe, sin recomputar la tirada."""
    print("\nEvaluación de dados: " + str(content["evaluation_id"]))
    rolls = ", ".join(str(value) for value in content["rolls"])
    print("Tirada: " + (rolls or "(sin azar)"))
    print("Resultado: " + content["outcome"])
    if content.get("auxiliary_request"):
        print(content["auxiliary_request"]["prompt"])


def offers(actions: list[dict]) -> None:
    """Enumera las acciones publicadas y sus estados."""
    for index, action in enumerate(actions, 1):
        suffix = "" if action["enabled"] else " (no disponible)"
        print(f"{index}. {action['label']}{suffix}")


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
