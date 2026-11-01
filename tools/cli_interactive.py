"""GLAUQUIR: interacción MUD de texto. No accede a los atributos privados de GISELA."""

from __future__ import annotations

import json
from pathlib import Path

from . import cli_render as render
from .cli_commands import inspect, instructions
from .cli_match import match, normalize, select


class TextClient:
    """Traduce comandos y números a acciones ya publicadas por Observe."""

    def __init__(self, session, developer: bool = False):
        self.session = session
        self.developer = developer

    def choose(self, view: dict):
        """Atiende consultas sin consumir acciones hasta recibir una selección."""
        while True:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSesión terminada por el jugador.")
                return None
            if not raw:
                continue
            answer = self._command(view, raw)
            if answer is not False:
                return answer

    def _command(self, view: dict, raw: str):
        """Resuelve consultas o envía acciones únicamente desde Observe."""
        name, _, rest = raw.partition(" ")
        name = normalize(name)
        handled, answer = self._basic(view, name, rest)
        if handled:
            return answer
        if name in ("ficha", "leer") and self._card(view, rest):
            return False
        if name in ("depurar", "consultar"):
            if self.developer:
                inspect(self.session, rest.split())
            else:
                print("Active --developer para consultar datos internos.")
            return False
        if name in ("ver", "mirar", "look") and rest and self._element(view, rest):
            return False
        candidates = match(view["actions"], name, rest)
        if (
            not candidates
            and name == "examinar"
            and (self._element(view, rest) or self._card(view, rest))
        ):
            return False
        if not candidates:
            candidates = select(view["actions"], raw)
        return self._choose_candidates(candidates)

    def _basic(self, view: dict, name: str, rest: str) -> tuple[bool, object]:
        """Atiende comandos universales que no provocan acciones del juego."""
        if name.isdecimal():
            number = int(name)
            if 1 <= number <= len(view["actions"]):
                action = view["actions"][number - 1]
                if action["enabled"]:
                    return True, action
                print("Esa acción no está disponible.")
                return True, False
            print("Número fuera de las opciones.")
            return True, False
        if name in ("salir", "quit"):
            return True, None
        if name in ("cargar", "load"):
            return True, {"command": "load", "path": rest.strip()}
        if name in ("guardar", "save"):
            return True, self._save(rest)
        if name in ("ver", "mirar", "look") and not rest:
            render.show(view)
            return True, False
        if name in ("ayuda", "help"):
            instructions()
            return True, False
        if name in ("acciones", "actions"):
            return True, self._actions(view, rest)
        if name in (
            "inventario",
            "inventory",
            "cartas",
            "cards",
            "habilidades",
            "skills",
        ):
            self._catalogue(view, name)
            return True, False
        return self._other_queries(name, rest)

    def _catalogue(self, view: dict, name: str) -> None:
        """Presenta una colección pública, sin manipular inventarios."""
        alias = {"inventario": "inventory", "cartas": "cards", "habilidades": "skills"}
        translation = {
            "inventory": "Inventario",
            "cards": "Cartas conocidas",
            "skills": "Habilidades",
        }
        key = alias.get(name, name)
        render.catalogue(view.get(key, []), translation[key])

    def _other_queries(self, name: str, rest: str) -> tuple[bool, object]:
        """Resuelve el estado y el historial usando únicamente API públicas."""
        if name in ("quests", "misiones", "objetivos"):
            self._show_quests()
            return True, False
        if name in ("estado", "status"):
            render.status(self.session.player_status())
            return True, False
        if name in ("history", "historia"):
            return True, self._history(rest)
        return False, False

    def _show_quests(self):
        """Presenta solo las misiones publicadas por Observe."""
        entries = self.session.observe().get("quests", [])
        if not entries:
            print("No hay misiones visibles.")
            return
        for quest in entries:
            print(f"{quest['title']} ({quest['status']})")
            for objective in quest["objectives"]:
                mark = "x" if objective["completed"] else " "
                print(f"  [{mark}] {objective['title']}")

    def _card(self, view: dict, value: str) -> bool:
        """Examina solo cartas visibles, por ID o título inequívoco."""
        requested = normalize(value)
        if not requested:
            print("Indique el objeto o la carta que desea leer.")
            return True
        matches = [
            item
            for item in view.get("cards", [])
            if requested in (normalize(item["id"]), normalize(item["title"]))
        ]
        if len(matches) == 1:
            render.card(self.session.read_public(matches[0]["id"]))
        elif matches:
            print("Nombre ambiguo. Use el identificador de la carta.")
        else:
            return False
        return True

    def _element(self, view: dict, value: str) -> bool:
        """Inspecciona únicamente elementos de la proyección pública actual."""
        requested = normalize(value)
        matches = [
            item
            for item in view.get("elements", [])
            if requested in (normalize(item["id"]), normalize(item["label"]))
        ]
        if not matches:
            return False
        if len(matches) != 1:
            print("Elemento ambiguo. Use su identificador.")
            return True
        item = matches[0]
        print("\n" + item["label"])
        if "description" in item:
            print(item["description"])
        elif "entity" in item:
            render.card(self.session.read_public(item["entity"]))
        else:
            print("No tiene descripción pública.")
        return True

    def _actions(self, view: dict, value: str):
        """Enumera todas las acciones o las vinculadas a un elemento visible."""
        if not value:
            render.offers(view["actions"])
            return False
        matches = [
            item
            for item in view.get("elements", [])
            if normalize(value) in (normalize(item["id"]), normalize(item["label"]))
        ]
        if len(matches) == 1:
            render.offers(matches[0]["actions"])
        else:
            print("No existe un elemento único con ese nombre.")
        return False

    def _history(self, argument: str):
        """Muestra el registro confirmado sin modificar la partida."""
        try:
            limit = None if argument in ("", "all", "todo") else int(argument)
            render.history(self.session.read_history(limit))
        except ValueError:
            print("Uso: history, history 20 o history all.")
        return False

    def _save(self, value: str):
        """Exporta mediante la API de sesión, nunca por lectura del mundo."""
        if not value:
            print("Uso: guardar RUTA")
            return False
        try:
            path = Path(value)
            path.write_text(
                json.dumps(self.session.export(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print("Sesión guardada en " + str(path))
        except OSError as exc:
            print("No se pudo guardar la sesión: " + str(exc))
        return False

    def _choose_candidates(self, candidates: list[dict]):
        """Rechaza elecciones ambiguas; permite seleccionarlas por número global."""
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            print("Hay varias acciones posibles:")
            for item in candidates:
                print(item["action_id"] + ": " + item["label"])
            print("Seleccione el número correspondiente en la lista de acciones.")
        else:
            print("Acción no disponible. Escriba acciones para ver las opciones.")
        return False
