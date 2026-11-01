"""E2: casos independientes del relato sobre evaluación oculta transaccional."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from gisela.contracts.admit_package import admit_package
from gisela.engine.authorized_gateway import ExecutionGateway, GatewayError, Principal
from gisela.engine.errors import EngineFailure
from gisela.engine.runtime import new_session, restore_session

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "packages/e1_reparacion_sin_jugador.package.json"
)


def fixture(mode="dice_sum"):
    """Paquete neutral sin protagonista, TRAITS ni S.O.F.I.A."""
    pkg = json.loads(SOURCE.read_text())
    profile = pkg["dice_profiles"][0]
    profile["mode"] = mode
    profile["count"] = 2
    profile["sides"] = 6
    if mode == "deterministic":
        profile.pop("count")
        profile.pop("sides")
    pkg["nodes"][0]["steps"][0]["evaluation"]["presentation"] = "hidden"
    return pkg


def evaluate(pkg):
    """Accede al contrato de evaluación de un paso, sin ejecución."""
    return pkg["nodes"][0]["steps"][0]["evaluation"]


def send(session, name):
    """Utiliza la revisión y la oferta auténtica de Observe."""
    view = session.observe()
    return session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": name,
        }
    )


def set_result(pkg, *, base=12, difficulty=0):
    """Configura las entradas efectivas de una evaluación."""
    evaluate(pkg)["inputs"] = {
        "base": {"literal": base},
        "difficulty": {"literal": difficulty},
    }


def fact(pkg):
    """Confirma solo la rama de éxito; el caso de fallo permanece vacío."""
    return pkg["nodes"][0]["steps"][0]["evaluation"]["branches"][1]


def simple_node(pkg):
    """Crea un nodo observable después de las evaluaciones automáticas."""
    pkg["nodes"][0]["steps"].append(
        {"id": "observar", "op": "narrate", "text": {"text": "Resultado de la tarea"}}
    )
    return pkg


def character(pkg):
    """Añade una entidad de prueba con atributos, sin personaje jugador."""
    pkg["cards"] = [
        {"id": "taller", "kind": "location", "title": {"text": "Taller"}},
        {
            "id": "tecnico",
            "kind": "character",
            "title": {"text": "Técnico"},
            "sofia": {
                "strength": 2,
                "openness": 3,
                "fortune": 4,
                "intelligence": 7,
                "awareness": 1,
            },
        },
    ]
    pkg["initial_state"]["locations"] = [{"id": "taller", "card": "taller"}]
    pkg["initial_state"]["characters"] = [
        {"id": "tecnico", "card": "tecnico", "location": "taller", "status": {}}
    ]
    return pkg


def catalog(pkg, *, amount=3, slot="bonus"):
    """Aporta un rasgo que el evaluador resolverá en el momento de actuar."""
    character(pkg)
    pkg["traits"] = {
        "schema_version": "traits.v1",
        "traits": [
            {
                "id": "experto",
                "entity_kinds": ["character"],
                "contributions": [
                    {
                        "id": "aptitud",
                        "when": {"role": "actor", "all_tags": ["repair"]},
                        "add": {"slot": slot, "amount": amount},
                    }
                ],
            }
        ],
    }
    pkg["cards"][1]["traits"] = ["experto"]
    evaluate(pkg)["context"] = {
        "participants": [{"entity": "tecnico", "role": "actor"}],
        "tags": ["repair"],
    }
    return pkg


def pending_game():
    """Evaluación de opción que solicita descarte sin fijar el RNG."""
    path = Path(__file__).resolve().parents[2] / "contracts/example.package.json"
    pkg = json.loads(path.read_text())
    pkg["manifest"]["format_version"] = "1.4"
    pkg["dice_profiles"] = fixture()["dice_profiles"]
    spec = evaluate(fixture())
    spec["inputs"] = {"base": {"literal": 12}}
    spec["branches"][1]["effects"] = [
        {
            "op": "grant_skill",
            "character": "gisela",
            "skill": "intuicion",
            "overflow": "require_choice",
        }
    ]
    spec["branches"][1]["next"] = {"step": "entrega"}
    spec["branches"][0]["next"] = {"step": "despedida"}
    choice = pkg["nodes"][0]["steps"][2]["options"][0]
    choice.pop("effects")
    choice.pop("next")
    choice["evaluation"] = spec
    for number, zone in enumerate(("hand", "hand", "reserve"), 1):
        pkg["initial_state"]["skills"].append(
            {
                "id": f"hab_{number:02d}",
                "card": "intuicion",
                "character": "gisela",
                "zone": zone,
            }
        )
    return pkg


class E2Hidden(unittest.TestCase):
    def test_e2_01_hidden_step_commits_branch_and_restores(self):
        pkg = simple_node(fixture("deterministic"))
        set_result(pkg, base=13)
        admitted = admit_package(pkg)
        session = new_session(admitted)
        self.assertEqual(session.observe()["content"]["kind"], "narrate")
        self.assertEqual(
            [x["fact"] for x in session.export()["history"]["facts"]],
            ["maquina_reparada"],
        )
        self.assertEqual(session.export()["turn"], 1)
        self.assertEqual(session.export()["rng"]["counter"], 0)
        self.assertEqual(
            restore_session(admitted, session.export()).export(), session.export()
        )

    def test_e2_02_random_dice_sum_is_reproducible(self):
        admitted = admit_package(simple_node(fixture()))
        a = new_session(admitted, seed="1" * 64)
        b = new_session(admitted, seed="1" * 64)
        self.assertEqual(a.export(), b.export())
        self.assertEqual(a.export()["rng"]["counter"], 2)
        self.assertEqual(a.observe()["content"]["kind"], "narrate")
        self.assertNotIn("dice", json.dumps(a.observe()))

    def test_e2_03_deterministic_negative_difficulty(self):
        pkg = simple_node(fixture("deterministic"))
        set_result(pkg, base=-900000, difficulty=900000)
        state = new_session(admit_package(pkg)).export()
        self.assertEqual(state["history"]["facts"], [])
        self.assertEqual(state["rng"]["counter"], 0)

    def test_e2_04_multiple_profiles_are_isolated(self):
        pkg = fixture("deterministic")
        pkg["dice_profiles"].append(
            {
                "schema_version": "dice.profile.v1",
                "id": "second",
                "mode": "dice_sum",
                "count": 2,
                "sides": 6,
                "bands": [{"id": "bad", "min": 0}, {"id": "good", "min": 5}],
            }
        )
        second = copy.deepcopy(pkg["nodes"][0]["steps"][0])
        second["id"] = "second_evaluation"
        second["evaluation"]["profile"] = "second"
        second["evaluation"]["branches"] = [{"outcome": "bad"}, {"outcome": "good"}]
        pkg["nodes"][0]["steps"].append(second)
        session = new_session(admit_package(simple_node(pkg)))
        self.assertEqual(session.export()["rng"]["counter"], 2)

    def test_e2_05_choice_runs_branch_after_authorization(self):
        pkg = fixture("deterministic")
        check = pkg["nodes"][0]["steps"].pop(0)["evaluation"]
        pkg["nodes"][0]["steps"] = [
            {
                "id": "elegir",
                "op": "choice",
                "options": [
                    {
                        "id": "intentar",
                        "label": {"text": "Intentar"},
                        "evaluation": check,
                    }
                ],
            }
        ]
        pkg["nodes"][0]["steps"].append(
            {"id": "despues", "op": "narrate", "text": {"text": "Después"}}
        )
        session = new_session(admit_package(pkg))
        self.assertEqual(session.export()["history"]["facts"], [])
        self.assertEqual(send(session, "choose_intentar")["status"], "ok")
        self.assertEqual(session.observe()["content"]["kind"], "narrate")
        self.assertEqual(
            len(session.export()["history"]["executions"][0]["selected_options"]), 1
        )

    def test_e2_06_scene_action_is_atomic(self):
        pkg = fixture("deterministic")
        check = pkg["nodes"][0]["steps"][0]["evaluation"]
        pkg["manifest"]["entry"] = {"scene": "taller"}
        pkg["scenes"] = [
            {
                "id": "taller",
                "title": {"text": "Taller"},
                "actions": [
                    {
                        "id": "trabajar",
                        "label": {"text": "Trabajar"},
                        "evaluation": check,
                    }
                ],
            }
        ]
        session = new_session(admit_package(pkg))
        self.assertEqual(session.export()["rng"]["counter"], 0)
        self.assertEqual(send(session, "interact_0_0")["status"], "ok")
        self.assertEqual(len(session.export()["history"]["trace"]), 1)
        self.assertEqual(session.export()["turn"], 0)

    def test_e2_07_element_action_resolves_independently(self):
        pkg = fixture("deterministic")
        check = pkg["nodes"][0]["steps"][0]["evaluation"]
        pkg["manifest"]["entry"] = {"scene": "taller"}
        pkg["scenes"] = [
            {
                "id": "taller",
                "title": {"text": "Taller"},
                "elements": [
                    {
                        "id": "mesa",
                        "label": {"text": "Mesa"},
                        "actions": [
                            {
                                "id": "revisar",
                                "label": {"text": "Revisar"},
                                "evaluation": check,
                            }
                        ],
                    }
                ],
            }
        ]
        session = new_session(admit_package(pkg))
        self.assertEqual(send(session, "interact_1_0")["status"], "ok")
        self.assertEqual(
            session.export()["history"]["trace"][0]["detail"]["element"], "mesa"
        )

    def test_e2_08_invalid_branch_rolls_back_rng(self):
        pkg = fixture()
        set_result(pkg, base=12)
        fact(pkg)["effects"].append(
            {
                "op": "transfer",
                "object": "pieza_01",
                "from": "receptor",
                "to": "tecnico",
            }
        )
        pkg["cards"] = [
            {"id": "pieza", "kind": "object", "title": {"text": "Pieza"}},
            {"id": "receptor", "kind": "character", "title": {"text": "Receptor"}},
            {"id": "tecnico", "kind": "character", "title": {"text": "Técnico"}},
            {"id": "taller", "kind": "location", "title": {"text": "Taller"}},
        ]
        pkg["initial_state"]["locations"] = [{"id": "taller", "card": "taller"}]
        pkg["initial_state"]["characters"] = [
            {"id": n, "card": n, "location": "taller", "status": {}}
            for n in ("receptor", "tecnico")
        ]
        pkg["initial_state"]["objects"] = [
            {"id": "pieza_01", "card": "pieza", "owner": "tecnico"}
        ]
        # La transferencia desde receptor es válida en autoría, pero no en estado.
        pkg["nodes"][0]["steps"].insert(
            0, {"id": "intro", "op": "narrate", "text": {"text": "Preparación"}}
        )
        session = new_session(admit_package(pkg))
        old = session.export()
        self.assertEqual(send(session, "advance")["status"], "error")
        self.assertEqual(session.export(), old)

    def test_e2_09_stat_is_read_from_effective_world(self):
        pkg = character(simple_node(fixture("deterministic")))
        evaluate(pkg)["inputs"]["base"] = {
            "stat": {
                "character": "tecnico",
                "name": "intelligence",
                "component": "effective",
            }
        }
        evaluate(pkg)["inputs"]["difficulty"] = {"literal": 0}
        session = new_session(admit_package(pkg))
        self.assertEqual(session.export()["history"]["facts"], [])

    def test_e2_10_non_hidden_is_reserved_for_e3(self):
        pkg = fixture()
        evaluate(pkg)["presentation"] = "visible"
        with self.assertRaises(EngineFailure) as error:
            new_session(admit_package(pkg))
        self.assertEqual(error.exception.code, "UNSUPPORTED_FORMAT")

    def test_e2_11_unknown_client_cannot_act(self):
        pkg = fixture("deterministic")
        pkg["nodes"][0]["steps"] = [
            {"id": "intro", "op": "narrate", "text": {"text": "Inicio"}},
            {"id": "final", "op": "narrate", "text": {"text": "Final"}},
        ]
        session = new_session(admit_package(pkg))
        controller = Principal("bot", frozenset({"act", "observe_player"}))
        gateway = ExecutionGateway(session, {"bot": controller})
        with self.assertRaises(GatewayError):
            gateway.bind("outsider")
        client = gateway.bind("bot")
        self.assertEqual(
            client.act(
                {
                    "session_id": "mvp_session",
                    "revision": session.export()["revision"],
                    "action_id": "advance",
                },
                "c1",
            )["status"],
            "ok",
        )

    def test_e2_12_different_seed_can_change_outcome_without_violating_contract(self):
        admitted = admit_package(simple_node(fixture()))
        a = new_session(admitted, seed="0" * 64)
        b = new_session(admitted, seed="a" * 64)
        self.assertNotEqual(a.export()["rng"]["seed"], b.export()["rng"]["seed"])

    def test_e2_13_restore_rejects_wrong_digest(self):
        admitted = admit_package(simple_node(fixture()))
        session = new_session(admitted)
        forged = session.export()
        forged["package_digest"] = "a" * 64
        with self.assertRaises(EngineFailure):
            restore_session(admitted, forged)


class E2Hardening(unittest.TestCase):
    def test_e2_14_traits_and_sofia_resolve_together(self):
        pkg = catalog(simple_node(fixture("deterministic")))
        evaluate(pkg)["inputs"] = {
            "base": {
                "stat": {
                    "character": "tecnico",
                    "name": "intelligence",
                    "component": "effective",
                }
            }
        }
        state = new_session(admit_package(pkg)).export()
        self.assertEqual(
            [x["fact"] for x in state["history"]["facts"]], ["maquina_reparada"]
        )
        self.assertEqual(state["world"]["characters"][0]["traits"], ["experto"])

    def test_e2_15_current_stat_after_prior_effect_is_used(self):
        pkg = character(simple_node(fixture("deterministic")))
        evaluate(pkg)["inputs"] = {
            "base": {
                "stat": {
                    "character": "tecnico",
                    "name": "intelligence",
                    "component": "effective",
                }
            }
        }
        pkg["nodes"][0]["steps"].insert(
            0,
            {
                "id": "modificar",
                "op": "effect",
                "effects": [
                    {
                        "op": "set",
                        "target": {
                            "stat": {
                                "character": "tecnico",
                                "name": "intelligence",
                                "component": "current",
                            }
                        },
                        "value": {"literal": 10},
                    }
                ],
            },
        )
        state = new_session(admit_package(pkg)).export()
        self.assertEqual(
            [x["fact"] for x in state["history"]["facts"]], ["maquina_reparada"]
        )
        self.assertEqual(state["world"]["characters"][0]["stats"]["intelligence"], 10)

    def test_e2_16_preflight_overflow_does_not_draw(self):
        pkg = catalog(fixture(), amount=100, slot="difficulty")
        set_result(pkg, base=1, difficulty=1000000)
        pkg["nodes"][0]["steps"].insert(
            0, {"id": "intro", "op": "narrate", "text": {"text": "Inicio"}}
        )
        session = new_session(admit_package(pkg))
        old = session.export()
        response = send(session, "advance")
        self.assertEqual(response["error"]["code"], "INVALID_STATE")
        self.assertEqual(session.export(), old)
        self.assertEqual(old["rng"]["counter"], 0)

    def test_e2_17_pending_replay_restores_same_dice(self):
        admitted = admit_package(pending_game())
        session = new_session(admitted, seed="2" * 64)
        self.assertEqual(send(session, "advance")["status"], "ok")
        self.assertEqual(send(session, "choose_prestar")["status"], "ok")
        pending = session.export()
        self.assertEqual(pending["rng"]["counter"], 0)
        self.assertEqual(
            pending["pending_transaction"]["source"]["kind"], "choice_option"
        )
        restored = restore_session(admitted, pending)
        for target in (session, restored):
            self.assertEqual(send(target, "resolve_hab_01")["status"], "ok")
        self.assertEqual(session.export(), restored.export())
        self.assertEqual(session.export()["rng"]["counter"], 2)

    def test_e2_18_pending_cancel_preserves_world_and_rng(self):
        admitted = admit_package(pending_game())
        session = new_session(admitted, seed="2" * 64)
        send(session, "advance")
        before = session.export()
        send(session, "choose_prestar")
        self.assertEqual(send(session, "cancel_pending")["status"], "ok")
        after = session.export()
        self.assertEqual(after["rng"], before["rng"])
        self.assertEqual(after["world"], before["world"])
        self.assertEqual(after["history"], before["history"])

    def test_e2_19_mary_yield_is_exactly_once(self):
        pkg = simple_node(fixture("deterministic"))
        set_result(pkg, base=12)
        pkg["manifest"]["facts"].append("objetivo_cumplido")
        pkg["mary"] = {
            "objectives": [
                {
                    "id": "tarea",
                    "mode": "milestone",
                    "visibility": "hidden",
                    "criterion": {
                        "kind": "condition",
                        "when": {"has_fact": "maquina_reparada"},
                    },
                    "yield": {"fact": "objetivo_cumplido"},
                }
            ],
            "missions": [],
        }
        admitted = admit_package(pkg)
        session = new_session(admitted)
        restored = restore_session(admitted, session.export())
        self.assertEqual(len(restored.export()["history"]["facts"]), 2)
        self.assertEqual(restored.export()["mary"], session.export()["mary"])

    def test_e2_20_all_dice_modes_keep_rng_reproducible(self):
        for mode in ("deterministic", "single_die", "dice_sum", "dice_pool"):
            pkg = fixture(mode)
            if mode == "single_die":
                pkg["dice_profiles"][0]["count"] = 1
            admitted = admit_package(simple_node(pkg))
            a = new_session(admitted, seed="e" * 64)
            b = new_session(admitted, seed="e" * 64)
            self.assertEqual(a.export(), b.export())
            self.assertEqual(
                a.export()["rng"]["counter"],
                0 if mode == "deterministic" else (1 if mode == "single_die" else 2),
            )

    def test_e2_21_atomic_transition_into_invalid_node(self):
        pkg = character(fixture())
        set_result(pkg, base=12)
        fact(pkg)["next"] = {"node": "otro"}
        pkg["nodes"][0]["steps"].insert(
            0, {"id": "intro", "op": "narrate", "text": {"text": "Comienzo"}}
        )
        pkg["cards"].append(
            {"id": "pieza", "kind": "object", "title": {"text": "Pieza"}}
        )
        pkg["initial_state"]["characters"].append(
            {"id": "receptor", "card": "tecnico", "location": "taller", "status": {}}
        )
        pkg["initial_state"]["objects"] = [
            {"id": "pieza_01", "card": "pieza", "owner": "tecnico"}
        ]
        pkg["nodes"].append(
            {
                "id": "otro",
                "steps": [
                    {
                        "id": "invalidar",
                        "op": "effect",
                        "effects": [
                            {
                                "op": "transfer",
                                "object": "pieza_01",
                                "from": "receptor",
                                "to": "tecnico",
                            }
                        ],
                    },
                    {"id": "fin", "op": "narrate", "text": {"text": "Fin"}},
                ],
            }
        )
        session = new_session(admit_package(pkg))
        before = session.export()
        self.assertEqual(send(session, "advance")["status"], "error")
        self.assertEqual(session.export(), before)
        self.assertFalse(before["history"]["executions"][0]["completed"])

    def test_e2_22_wrong_revision_cannot_repeat_branch(self):
        pkg = fixture("deterministic")
        pkg["nodes"][0]["steps"] = [
            {"id": "intro", "op": "narrate", "text": {"text": "Intro"}},
            {"id": "evaluar", "op": "evaluate", "evaluation": evaluate(pkg)},
            {"id": "outro", "op": "narrate", "text": {"text": "Outro"}},
        ]
        session = new_session(admit_package(pkg))
        old = session.observe()
        req = {
            "session_id": old["session_id"],
            "revision": old["revision"],
            "action_id": "advance",
        }
        self.assertEqual(session.act(req)["status"], "ok")
        state = session.export()
        self.assertEqual(session.act(req)["error"]["code"], "STALE_PROJECTION")
        self.assertEqual(session.export(), state)

    def test_e2_23_future_evaluation_is_not_public_before_act(self):
        pkg = fixture("dice_sum")
        pkg["nodes"][0]["steps"].insert(
            0, {"id": "intro", "op": "narrate", "text": {"text": "Inicio"}}
        )
        session = new_session(admit_package(pkg))
        before = json.dumps(session.observe())
        self.assertNotIn("reparacion", before)
        self.assertNotIn("bonus", before)
        self.assertEqual(session.export()["rng"]["counter"], 0)
