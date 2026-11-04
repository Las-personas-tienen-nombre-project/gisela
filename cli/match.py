"""Traductor textual de acciones ofrecidas; nunca crea operaciones nuevas."""

from __future__ import annotations

import re
import unicodedata

VERBS = {
    "ir": ("ir", "entrar", "regresar", "volver", "salir"),
    "hablar": ("hablar", "conversar", "preguntar"),
    "tomar": ("tomar", "recoger", "coger"),
    "dar": ("dar", "entregar", "prestar"),
    "dejar": ("dejar", "soltar"),
    "usar": ("usar", "utilizar", "encender", "activar"),
    "jugar": ("usar", "jugar", "activar"),
    "examinar": ("examinar", "mirar", "inspeccionar", "revisar"),
}
ARTICLES = {"el", "la", "los", "las", "de", "del", "al", "un", "una", "con", "a"}


def normalize(value: str) -> str:
    """Normaliza acentos, puntuación y mayúsculas sin realizar inferencias."""
    plain = unicodedata.normalize("NFD", value.casefold())
    plain = "".join(char for char in plain if unicodedata.category(char) != "Mn")
    return " ".join(re.findall(r"[a-z0-9_]+", plain))


def words(value: str) -> set[str]:
    """Extrae términos significativos de un identificador o etiqueta."""
    return set(normalize(value).split()) - ARTICLES


def match(actions: list[dict], verb: str, subject: str) -> list[dict]:
    """Filtra solo acciones publicadas, sin adivinar la intención del autor."""
    options = []
    wanted = words(subject)
    for action in actions:
        if not action["enabled"]:
            continue
        if verb == "jugar" and action["kind"] != "play_skill":
            continue
        if verb != "jugar" and action["kind"] == "play_skill":
            continue
        labels = words(action["label"])
        verbs = set(VERBS.get(verb, (verb,)))
        if not labels.intersection(verbs):
            continue
        if wanted and not wanted.issubset(labels | words(action["id"])):
            continue
        options.append(action)
    return options


def select(actions: list[dict], value: str) -> list[dict]:
    """Permite elegir por etiqueta o ID exacto sin tomar la primera coincidencia."""
    needle = normalize(value)
    return [
        item
        for item in actions
        if item["enabled"]
        and needle
        in (
            normalize(item["label"]),
            normalize(item["id"]),
            normalize(item["action_id"]),
        )
    ]
