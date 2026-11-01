"""H4.6: aventura ajena al canon; pruebas desde el contrato público."""

from __future__ import annotations

import json
import unittest

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.authorized_gateway import ExecutionGateway, GatewayError, Principal
from gisela.engine.runtime import new_session, restore_session
from tools.h46_walkthrough import PACKAGE, ROUTES, admitted_package, advance, run

SEED = "0" * 64


def fresh(seed=SEED):
    admitted = admitted_package()
    return admitted, new_session(admitted, seed=seed)


def facts(session):
    return [item["fact"] for item in session.export()["history"]["facts"]]


def follow(session, actions):
    for name in actions:
        advance(session, name)


class H46Faro(unittest.TestCase):
    def test_01_admission_and_public_entry(self):
        admitted, session = fresh()
        self.assertEqual(admitted.materialize()["manifest"]["format_version"], "1.5")
        view = session.observe()
        self.assertEqual((view["status"], view["scene"]), ("exploring", "muelle"))
        self.assertEqual(session.export()["turn"], 0)
        self.assertNotIn("faro_seguro", json.dumps(view))

    def test_02_three_real_endings(self):
        expected = {
            "completa": "faro_encendido",
            "parcial": "luz_intermitente",
            "sin_preparacion": "noche_cerrada",
        }
        for route, ending in expected.items():
            with self.subTest(route=route):
                session = run(route, SEED, check_restores=True)["session"]
                self.assertEqual(session.export()["ending"], ending)
                self.assertEqual(session.observe()["content"]["kind"], "ending")

    def test_03_relationships_inventory_and_knowledge(self):
        session = run("completa", SEED)["session"]
        state = session.export()
        self.assertEqual(state["world"]["relationships"][0]["value"], 4)
        self.assertEqual(
            next(o for o in state["world"]["objects"] if o["id"] == "prisma_uno")[
                "owner"
            ],
            "lara",
        )
        self.assertIn("plano_leido", state["world"]["characters"][0]["knowledge"])
        self.assertIs(state["world"]["characters"][0]["beliefs"]["faro_seguro"], False)
        self.assertIn("ruta_aprendida", facts(session))
        self.assertEqual(facts(session).count("ruta_visible"), 1)

    def test_04_mary_milestone_yields_once(self):
        prepared = run("completa", SEED)["session"].export()
        rushed = run("sin_preparacion", SEED)["session"].export()
        self.assertEqual(prepared["mary"]["missions"]["salvar_navegantes"], "completed")
        self.assertEqual(rushed["mary"]["missions"]["salvar_navegantes"], "active")
        self.assertEqual(
            [i["fact"] for i in prepared["history"]["facts"]].count(
                "diagnostico_completo"
            ),
            1,
        )

    def test_05_skill_traits_and_effect_expiration(self):
        session = run("completa", SEED)["session"]
        char = session.export()["world"]["characters"][0]
        self.assertEqual(char["stats"]["intelligence"], 8)
        self.assertIn("meticulosa", char["traits"])
        self.assertIn("afinacion_usada", facts(session))
        self.assertIn("temple_agotado", facts(session))
        self.assertNotIn(
            "oido_uno", [s["id"] for s in session.export()["world"]["skills"]]
        )

    def test_06_independent_route_assigns_trait(self):
        session = run("sin_preparacion", SEED)["session"]
        self.assertIn("audaz", session.export()["world"]["characters"][0]["traits"])
        self.assertNotIn("apoyo_mutuo", facts(session))
        self.assertEqual(session.export()["world"]["relationships"][0]["value"], -1)

    def test_07_pending_is_fixed_and_restorable(self):
        admitted, session = fresh()
        index = ROUTES["completa"].index("reparar_motor") + 1
        follow(session, ROUTES["completa"][:index])
        view = session.observe()
        self.assertEqual(view["content"]["kind"], "pending_evaluation")
        frozen = session.export()
        self.assertEqual(restore_session(admitted, frozen).export(), frozen)
        self.assertEqual(session.observe(), view)
        self.assertNotIn("reparacion_lograda", facts(session))
        self.assertNotIn("reparacion_fallida", facts(session))
        clone = restore_session(admitted, frozen)
        advance(session, "continue")
        advance(clone, "continue")
        self.assertEqual(session.export(), clone.export())

    def test_08_hidden_does_not_consume_random(self):
        admitted, session = fresh()
        follow(session, ROUTES["completa"][:5])
        self.assertIn("pronostico_confirmado", facts(session))
        self.assertEqual(session.export()["rng"]["counter"], 0)
        self.assertEqual(
            restore_session(admitted, session.export()).export(), session.export()
        )

    def test_09_stale_action_and_unoffered_do_not_mutate(self):
        _, session = fresh()
        before = session.export()
        view = session.observe()
        req = {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": "continue_evaluation",
        }
        self.assertEqual(session.act(req)["error"]["code"], "INVALID_ACTION")
        self.assertEqual(session.export(), before)
        advance(session, "escuchar_aviso")
        self.assertEqual(session.act(req)["error"]["code"], "STALE_PROJECTION")

    def test_10_gateway_nonhuman_exactly_once(self):
        _, session = fresh()
        g = ExecutionGateway(
            session,
            {"server": Principal("server", frozenset({"act", "observe_player"}))},
        )
        client = g.bind("server")
        view = client.observe()
        req = {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": view["actions"][0]["action_id"],
        }
        first = client.act(req, "cmd_01")
        self.assertEqual(first, client.act(req, "cmd_01"))
        self.assertEqual(client.act(req, "cmd_02")["error"]["code"], "STALE_PROJECTION")
        with self.assertRaises(GatewayError):
            g.bind("intruso")

    def test_11_rollback_of_invalid_evaluation_branch(self):
        pkg = admit_package_file(PACKAGE).materialize()
        action = next(
            a for a in pkg["scenes"][2]["actions"] if a["id"] == "reparar_motor"
        )
        for branch in action["evaluation"]["branches"]:
            branch["effects"].append(
                {"op": "transfer", "object": "prisma_uno", "from": "elio", "to": "lara"}
            )
        admitted = admit_package(pkg)
        session = new_session(admitted, seed=SEED)
        follow(
            session, ROUTES["completa"][: ROUTES["completa"].index("reparar_motor") + 1]
        )
        before = session.export()
        view = session.observe()
        action = view["actions"][0]
        reply = session.act(
            {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": action["action_id"],
            }
        )
        self.assertEqual(reply["status"], "error")
        self.assertEqual(session.export(), before)

    def test_12_seed_determinism_and_stress(self):
        for value in range(4):
            seed = f"{value:064x}"
            a = run("completa", seed)["session"].export()
            b = run("completa", seed)["session"].export()
            self.assertEqual(a, b)
            self.assertIn(
                a["ending"], ("faro_encendido", "luz_intermitente", "noche_cerrada")
            )

    def test_13_different_order_changes_world_time(self):
        _, session = fresh()
        follow(session, ROUTES["completa"][:5])
        for _ in range(5):
            advance(session, "entrar_archivo")
            advance(session, "volver_muelle")
        self.assertEqual(session.export()["world_time"], "2026-10-30T19:40:00-03:00")
        follow(session, ["subir_cupula", "emitir_senal"])
        self.assertIn("marea_alta", facts(session))

    def test_14_presentation_never_leaks_private_modifiers(self):
        _, session = fresh()
        prefix = ROUTES["completa"][: ROUTES["completa"].index("reparar_motor") + 1]
        follow(session, prefix)
        content = session.observe()["content"]
        serialized = json.dumps(content)
        self.assertEqual(content["presentation"], "visible")
        self.assertNotIn("intelligence", serialized)
        self.assertNotIn("meticulosa", serialized)
        self.assertNotIn("bonus", serialized)

    def test_15_glauquir_prints_public_dice(self):
        import io
        from contextlib import redirect_stdout

        from tools.cli_render import show

        _, session = fresh()
        follow(
            session, ROUTES["completa"][: ROUTES["completa"].index("reparar_motor") + 1]
        )
        output = io.StringIO()
        with redirect_stdout(output):
            show(session.observe())
        text = output.getvalue()
        self.assertIn("Evaluación de dados:", text)
        self.assertIn("Resultado:", text)
        self.assertNotIn("intelligence", text)


if __name__ == "__main__":
    unittest.main()
