"""H4.5: contratos públicos, presentación, comandos, habilidades e historial."""

from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.world_base import WorldError
from tools.cli_interactive import TextClient
from tools.cli_match import match
from tools.cli_render import show

ROOT = Path(__file__).resolve().parents[3]
FILE = ROOT / "gisela/packages/h4_exploracion.package.json"


def setup(pkg=None):
    """Devuelve paquete admitido y sesión nueva."""
    admitted = admit_package(pkg) if pkg else admit_package_file(FILE)
    return admitted, new_session(admitted)


def act(session, identifier: str):
    """Actúa únicamente sobre una oferta vigente de Observe."""
    view = session.observe()
    action = next(x for x in view["actions"] if x["id"] == identifier)
    return session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": action["action_id"],
        }
    )


class H450Contracts(unittest.TestCase):
    """Primera etapa, contratos y lectura pública."""

    def test_public_view_matches_contract(self):
        _, session = setup()
        self.assertTrue(Validator().check_schema("observe", session.observe()))
        self.assertTrue(Validator().check_schema("session", session.export()))

    def test_inventory_only_has_owned_objects(self):
        _, session = setup()
        self.assertEqual(
            [x["id"] for x in session.observe()["inventory"]], ["casete_01"]
        )
        self.assertEqual(act(session, "tomar")["status"], "ok")
        self.assertEqual(session.observe()["inventory"], [])

    def test_unknown_card_does_not_leak(self):
        _, session = setup()
        with self.assertRaises(WorldError):
            session.read_public("no_existe")
        self.assertNotIn("no_existe", str(session.observe()))

    def test_observe_and_read_are_pure(self):
        _, session = setup()
        before = session.export()
        session.read_public("casete_01")
        session.player_status()
        session.read_history()
        session.observe()
        self.assertEqual(session.export(), before)

    def test_public_status_only_for_player(self):
        _, session = setup()
        self.assertEqual(session.player_status()["character"], "alberto")
        self.assertEqual(len(session.player_status()["stats"]), 5)

    def test_history_persists_without_reexecution(self):
        admitted, session = setup()
        self.assertEqual(len(session.read_history()), 1)
        self.assertEqual(
            session.read_history(),
            restore_session(admitted, session.export()).read_history(),
        )
        self.assertEqual(len(session.read_history()), 1)

    def test_invalid_reading_sequence_rejected(self):
        admitted, session = setup()
        invalid = session.export()
        invalid["history"]["reading"][0]["sequence"] = 5
        issues = Validator().validate_session(invalid, admitted.materialize())
        self.assertIn("READING_SEQUENCE", {x.code for x in issues})


class H45APresentation(unittest.TestCase):
    """Segunda etapa, presentación y opciones."""

    def test_scene_has_title_and_description(self):
        _, session = setup()
        v = session.observe()
        self.assertEqual(v["scene_title"], "Portería en la noche")
        self.assertIn("Clasificadora", v["scene_description"])

    def test_renderer_shows_author_text(self):
        _, session = setup()
        out = StringIO()
        with redirect_stdout(out):
            show(session.observe())
        self.assertIn("La entrada a la Central Clasificadora.", out.getvalue())
        self.assertIn("Conversar con Gisela", out.getvalue())

    def test_disabled_choice_cannot_be_selected_by_number(self):
        _, session = setup()
        act(session, "tomar")
        view = session.observe()
        number = next(i for i, x in enumerate(view["actions"], 1) if x["id"] == "tomar")
        with (
            patch("builtins.input", side_effect=[str(number), "salir"]),
            redirect_stdout(StringIO()) as output,
        ):
            choice = TextClient(session).choose(view)
        self.assertIsNone(choice)
        self.assertIn("no está disponible", output.getvalue())


class H45BObjects(unittest.TestCase):
    """Tercera etapa, fichas, inventario y comandos contextuales."""

    def test_card_read_does_not_act(self):
        _, session = setup()
        before = session.export()
        with redirect_stdout(StringIO()) as output:
            TextClient(session)._command(session.observe(), "ficha casete")
        self.assertIn("Casete", output.getvalue())
        self.assertEqual(session.export(), before)

    def test_inventory_command_is_pure(self):
        _, session = setup()
        before = session.export()
        with redirect_stdout(StringIO()) as output:
            TextClient(session)._command(session.observe(), "inventario")
        self.assertIn("casete_01", output.getvalue())
        self.assertEqual(session.export(), before)

    def test_command_matches_only_offered_actions(self):
        _, session = setup()
        actions = session.observe()["actions"]
        self.assertEqual(
            [x["id"] for x in match(actions, "hablar", "gisela")], ["conversar"]
        )
        self.assertEqual(match(actions, "jugar", "gesto"), [])

    def test_examine_prefers_author_action(self):
        _, session = setup()
        offered = TextClient(session)._command(session.observe(), "examinar casete")
        self.assertEqual(offered["id"], "examinar")

    def test_ambiguous_selection_never_guesses(self):
        _, session = setup()
        view = session.observe()
        action = view["actions"][0]
        with redirect_stdout(StringIO()):
            result = TextClient(session)._choose_candidates(
                [action, view["actions"][1]]
            )
        self.assertIs(result, False)


class H45CSkills(unittest.TestCase):
    """Cuarta etapa, uso de habilidades desde escenas cuando están autorizadas."""

    def _permitted(self):
        pkg = admit_package_file(FILE).materialize()
        pkg["scenes"][0]["allow_skill_play"] = True
        return setup(pkg)

    def test_exploration_skill_is_offered_and_consumed(self):
        _, session = self._permitted()
        self.assertIn("gesto_01", [x["id"] for x in session.observe()["actions"]])
        self.assertEqual(act(session, "gesto_01")["status"], "ok")
        self.assertNotIn("gesto_01", [x["id"] for x in session.observe()["skills"]])
        self.assertEqual(session.read_history()[-1]["kind"], "skill")

    def test_skill_cannot_be_played_in_unpermitted_scene(self):
        _, session = setup()
        before = session.export()
        result = session.act(
            {
                "session_id": before["session_id"],
                "revision": before["revision"],
                "action_id": "play_gesto_01",
            }
        )
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.export(), before)

    def test_skill_restore_matches_uninterrupted(self):
        admitted, session = self._permitted()
        restored = restore_session(admitted, session.export())
        self.assertEqual(act(session, "gesto_01"), act(restored, "gesto_01"))
        self.assertEqual(session.export(), restored.export())


class H45DHistory(unittest.TestCase):
    """Quinta etapa, registro autoritativo y herramientas de depuración."""

    def test_history_of_scene_and_conversation(self):
        admitted, session = setup()
        act(session, "conversar")
        self.assertEqual(session.read_history()[-1]["kind"], "narrate")
        self.assertEqual(session.read_history(1)[0]["kind"], "narrate")
        self.assertEqual(
            restore_session(admitted, session.export()).read_history(),
            session.read_history(),
        )

    def test_history_command_is_read_only(self):
        _, session = setup()
        before = session.export()
        with redirect_stdout(StringIO()) as output:
            TextClient(session)._command(session.observe(), "history all")
        self.assertIn("Portería en la noche", output.getvalue())
        self.assertEqual(session.export(), before)

    def test_developer_mode_is_explicit(self):
        _, session = setup()
        with redirect_stdout(StringIO()) as output:
            TextClient(session)._command(session.observe(), "depurar hechos")
        self.assertIn("--developer", output.getvalue())
        with redirect_stdout(StringIO()) as output:
            TextClient(session, True)._command(session.observe(), "depurar hechos")
        self.assertIn("facts", output.getvalue())

    def test_pending_does_not_publish_a_draft(self):
        pkg = admit_package_file(FILE).materialize()
        pkg["scenes"][0]["actions"][0]["effects"] = [
            {
                "op": "grant_skill",
                "skill": "reserva",
                "character": "alberto",
                "overflow": "require_choice",
            }
        ]
        pkg["initial_state"]["capacities"][0]["hand"] = 1
        # Con la mano y la reserva llenas, el descarte necesita respuesta.
        _, session = setup(pkg)
        previous = session.export()["history"]["reading"]
        reply = act(session, "ir_pasillo")
        self.assertEqual(reply["status"], "ok")
        self.assertEqual(session.export()["history"]["reading"], previous)


class H45EIntegration(unittest.TestCase):
    """Sexta etapa, recorridos completos y controles negativos."""

    def test_cli_script_can_finish_world(self):
        import subprocess

        commands = (
            "mirar\ninventario\nficha casete\nacciones\njugar gesto\n"
            "ir pasillo\nir porteria\ndar casete\nhistory all\n"
            "hablar gisela\n1\n1\n"
        )
        run = subprocess.run(
            [
                sys.executable,
                "tools/play_mvp.py",
                "--package",
                "gisela/packages/h45_cli.package.json",
            ],
            cwd=ROOT,
            input=commands,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        for required in (
            "Historia de la partida",
            "Pasillo",
            "Acción confirmada:",
            "Final: solo",
            "Inventario",
        ):
            self.assertIn(required, run.stdout)

    def test_eof_exits_cleanly(self):
        import subprocess

        run = subprocess.run(
            [
                sys.executable,
                "tools/play_mvp.py",
                "--package",
                "gisela/packages/h45_cli.package.json",
            ],
            cwd=ROOT,
            input="",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)

    def test_hidden_character_does_not_leak(self):
        pkg = admit_package_file(FILE).materialize()
        pkg["scenes"][0]["actors"][0]["visible_if"] = {"constant": False}
        _, session = setup(pkg)
        self.assertNotIn("gisela", [x["id"] for x in session.observe()["cards"]])
        with self.assertRaises(WorldError):
            session.read_public("gisela")

    def test_rejected_action_does_not_add_history(self):
        _, session = setup()
        before = session.read_history()
        result = session.act(
            {
                "session_id": "mvp_session",
                "revision": 0,
                "action_id": "interact_900_900",
            }
        )
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.read_history(), before)

    def test_public_history_is_defensive_copy(self):
        _, session = setup()
        previous = session.export()
        session.read_history()[0]["text"] = "Falsificación"
        self.assertEqual(previous, session.export())

    def test_cli_save_and_load_preserve_history(self):
        import subprocess
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as folder:
            save = Path(folder) / "partida.json"
            commands = (
                f"guardar {save}\nir pasillo\ncargar {save}\nhistory all\nsalir\n"
            )
            run = subprocess.run(
                [
                    sys.executable,
                    "tools/gisela_cli.py",
                    "--package",
                    "gisela/packages/h45_cli.package.json",
                ],
                cwd=ROOT,
                input=commands,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(save.is_file())
            self.assertIn("Historia de la partida", run.stdout)
            self.assertEqual(run.stdout.count("La radio descansaba"), 0)

    def test_history_rejects_invalid_limit_without_writing(self):
        _, session = setup()
        before = session.export()
        with redirect_stdout(StringIO()) as output:
            TextClient(session)._command(session.observe(), "history -3")
        self.assertIn("Uso: history", output.getvalue())
        self.assertEqual(session.export(), before)

    def test_package_is_admitted_and_cli_schemas_hold(self):
        admitted = admit_package_file(ROOT / "gisela/packages/h45_cli.package.json")
        session = new_session(admitted)
        self.assertTrue(Validator().check_schema("session", session.export()))
        self.assertTrue(Validator().check_schema("observe", session.observe()))


if __name__ == "__main__":
    unittest.main()
