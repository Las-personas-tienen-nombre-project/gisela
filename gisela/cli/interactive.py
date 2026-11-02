"""GLAUQUIR: interacción MUD de texto. No accede a los atributos privados de GISELA."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from gisela.engine.world_base import WorldError

from . import render
from .color import Styler
from .commands import inspect, instructions
from .match import match, normalize, select

DISPOSITION_COLORS = {
    "hostile": "red",
    "unfriendly": "yellow",
    "neutral": "white",
    "friendly": "green",
    "very_friendly": "cyan",
}


class TextClient:
    """Traduce comandos de texto a acciones publicadas por Observe."""

    def __init__(self, session, developer: bool = False, styler: Styler | None = None):
        self.session = session
        self.developer = developer
        self.styler = styler or Styler()
        self._history_started = False

    def choose(self, view: dict):
        """Atiende consultas sin consumir acciones hasta recibir una selección."""
        while True:
            try:
                raw = self._read_command(view).strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSesión terminada por el jugador.")
                return None
            if not raw:
                continue
            answer = self._command(view, raw)
            if answer is not False:
                return answer

    def _read_command(self, view: dict) -> str:
        """Edita líneas en terminales y registra el comando expandido."""
        line_editor = None
        if sys.stdin.isatty() and sys.stdout.isatty():
            try:
                import readline

                line_editor = readline
            except ImportError:
                pass
        if line_editor and not self._history_started:
            line_editor.clear_history()
            self._history_started = True
        before = line_editor.get_current_history_length() if line_editor else 0
        raw = input("> ")
        if line_editor and raw.strip():
            command = raw.strip()
            selected = self._letter_action(view, command)
            if selected is not None:
                command = "accion " + selected["id"]
            after = line_editor.get_current_history_length()
            if after > before:
                line_editor.replace_history_item(after - 1, command)
            else:
                line_editor.add_history(command)
        return raw

    @staticmethod
    def _letter_action(view: dict, raw: str):
        """Resuelve exclusivamente letras ofrecidas en la observación actual."""
        if not raw.isascii() or not raw.isalpha():
            return None
        for index, action in enumerate(render.ordered_actions(view["actions"])):
            if raw.upper() == render.option_letter(index):
                return action
        return None

    def display(self, view: dict) -> None:
        """Añade color diagnóstico solo a una copia local de la observación."""
        if not self.developer:
            render.show(view, styler=self.styler)
            return
        shown = dict(view)
        shown["actors"] = [dict(actor) for actor in view.get("actors", [])]
        for actor in shown["actors"]:
            if "color" not in actor:
                result = self.session.debug_query(
                    {"kind": "disposition", "actor": actor["id"]}
                )
                actor["color"] = DISPOSITION_COLORS.get(result["category"], "person")
        render.show(shown, True, self.styler)

    def _command(self, view: dict, raw: str):
        """Resuelve consultas o envía acciones únicamente desde Observe."""
        name, _, rest = raw.partition(" ")
        name = normalize(name)
        handled, answer = self._basic(view, name, rest)
        if handled:
            return answer
        if name in ("accion", "action"):
            return self._choose_candidates(select(view["actions"], rest))
        if name in ("ficha", "leer") and self._card(view, rest):
            return False
        if name in ("depurar", "consultar"):
            if self.developer:
                inspect(self.session, rest.split())
            else:
                print("Active --developer para consultar datos internos.")
            return False
        if name in ("hechos", "relacion", "propiedad"):
            if self.developer:
                inspect(self.session, [name, *rest.split()])
            else:
                print("Active --developer para consultar datos internos.")
            return False
        if name == "disposicion":
            if not self.developer:
                print("Active --developer para consultar la disposición.")
            else:
                try:
                    print(
                        json.dumps(
                            self.session.debug_query(
                                {"kind": "disposition", "actor": rest.strip()}
                            ),
                            ensure_ascii=False,
                            indent=2,
                        )
                    )
                except WorldError as exc:
                    print("Consulta rechazada: " + str(exc))
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
        letter_action = self._letter_action(view, name) if not rest else None
        if letter_action is not None:
            return True, letter_action
        if name.isdecimal():
            number = int(name)
            choices = render.ordered_actions(view["actions"])
            if 1 <= number <= len(choices):
                return True, choices[number - 1]
            print("Número fuera de las opciones.")
            return True, False
        if name in ("salir", "quit"):
            return True, None
        if name in ("cargar", "load"):
            return True, {"command": "load", "path": rest.strip()}
        if name in ("guardar", "save"):
            return True, self._save(rest)
        if name in ("ver", "mirar", "look") and not rest:
            self.display(view)
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
        if value in ("bloqueadas", "todas"):
            if not self.developer:
                print("Active --developer para inspeccionar acciones bloqueadas.")
            elif value == "bloqueadas":
                render.blocked(view["actions"], self.styler)
            else:
                print("DISPONIBLES")
                render.offers(view["actions"], self.styler)
                print("BLOQUEADAS")
                render.blocked(view["actions"], self.styler)
            return False
        if not value:
            render.offers(render.ordered_actions(view["actions"]), self.styler)
            return False
        matches = [
            item
            for item in view.get("elements", [])
            if normalize(value) in (normalize(item["id"]), normalize(item["label"]))
        ]
        if len(matches) == 1:
            indices = {
                action["id"]: index
                for index, action in enumerate(render.ordered_actions(view["actions"]))
            }
            for action in render.ordered_actions(matches[0]["actions"]):
                index = indices.get(action["id"])
                if index is not None:
                    render.offers([action], self.styler, start=index)
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
        """Rechaza elecciones ambiguas y muestra comandos inequívocos."""
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            print("Hay varias acciones posibles:")
            for item in candidates:
                print("  accion " + item["id"] + " — " + item["label"])
            print("Escriba uno de los comandos indicados.")
        else:
            print("Acción no disponible. Escriba acciones para ver las opciones.")
        return False
