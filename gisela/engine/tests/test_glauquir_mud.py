"""Regresiones de la presentación y comandos MUD."""

import os
import re
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from gisela.cli.color import Styler
from gisela.cli.interactive import TextClient
from gisela.cli.render import show
from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session

PRODUCT = (
    Path(__file__).resolve().parents[4]
    / "las-personas-tienen-nombre/renpy/game/data/stories/central_clasificadora_cards_v1.package.json"
)


class MudTest(unittest.TestCase):
    def test_unknown_actor_name_and_card_are_public_aliases(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "packages/h46b_central_clasificadora.package.json"
        )
        package = admit_package_file(source).materialize()
        actor = package["scenes"][0]["actors"][0]
        actor["unknown_name"] = {"text": "Persona desconocida"}
        actor["known_if"] = {"constant": False}
        session = new_session(admit_package(package))
        view = session.observe()
        self.assertEqual(view["actors"][0]["name"], "Persona desconocida")
        card = next(c for c in view["cards"] if c["id"] == view["actors"][0]["id"])
        self.assertEqual(card["title"], "Persona desconocida")
        self.assertNotIn("description", card)

    def test_auto_color_respects_redirection_and_no_color(self):
        with redirect_stdout(StringIO()):
            self.assertFalse(Styler("auto").enabled)
        prior = os.environ.get("NO_COLOR")
        try:
            os.environ["NO_COLOR"] = ""
            self.assertFalse(Styler("auto").enabled)
            self.assertTrue(Styler("always").enabled)
        finally:
            if prior is None:
                os.environ.pop("NO_COLOR", None)
            else:
                os.environ["NO_COLOR"] = prior

    def test_large_productive_scene(self):
        if not PRODUCT.exists():
            self.skipTest("El paquete productivo externo no está instalado")
        session = new_session(admit_package_file(PRODUCT))
        view = session.observe()
        self.assertEqual(
            (len(view["actions"]), sum(a["enabled"] for a in view["actions"])), (278, 1)
        )
        output = StringIO()
        with redirect_stdout(output):
            show(view, styler=Styler("never"))
            TextClient(session)._command(view, "acciones")
        self.assertIn("accion tomar_turno", output.getvalue())
        self.assertNotIn("night_1_handover_000", output.getvalue())
        self.assertEqual(TextClient(session)._command(view, "1")["id"], "tomar_turno")
        with redirect_stdout(StringIO()):
            self.assertIs(
                TextClient(session)._command(view, "accion night_1_handover_000"), False
            )

    def test_explicit_diagnostics_and_color(self):
        view = {
            "scene": "porteria",
            "scene_title": "Portería",
            "world_time": "1998-07-24T18:45:00-04:00",
            "content": {"kind": "exploring"},
            "actions": [
                {
                    "id": "go",
                    "action_id": "go",
                    "kind": "interact",
                    "label": "Salir",
                    "enabled": True,
                    "role": "exit",
                },
                {
                    "id": "locked",
                    "action_id": "locked",
                    "kind": "interact",
                    "label": "Cerrado",
                    "enabled": False,
                    "reason": "Falta llave",
                },
                {
                    "id": "silent",
                    "action_id": "silent",
                    "kind": "interact",
                    "label": "Oculto",
                    "enabled": False,
                },
            ],
            "actors": [],
            "elements": [],
        }
        client = TextClient(None, True)
        output = StringIO()
        with redirect_stdout(output):
            show(view, True, Styler("never"))
        self.assertIn("Acciones bloqueadas: 2", output.getvalue())
        self.assertNotIn("accion locked", output.getvalue())
        with redirect_stdout(output):
            client._command(view, "acciones bloqueadas")
        self.assertIn("locked — Cerrado — Falta llave", output.getvalue())
        self.assertIn("silent — Oculto", output.getvalue())
        with redirect_stdout(StringIO()):
            self.assertIs(client._command(view, "accion locked"), False)
        for mode, colored in (("never", False), ("always", True)):
            output = StringIO()
            with redirect_stdout(output):
                show(view, styler=Styler(mode))
            self.assertEqual("\x1b[" in output.getvalue(), colored)
            self.assertIn(
                "PORTERÍA — 18:45", re.sub(r"\x1b\[[0-9;]*m", "", output.getvalue())
            )


if __name__ == "__main__":
    unittest.main()
