"""Regresiones para base, current, effective y Scoresheet de S.O.F.I.A."""

from __future__ import annotations

import unittest

from gisela.contracts.admit_package import admit_package
from gisela.engine.conditions import predicate, value
from gisela.engine.runtime import restore_session
from gisela.engine.tests.test_h34a_values import load, ready, send
from gisela.engine.world_base import WorldError

STAT = {"character": "alberto", "name": "strength", "component": "current"}


def ref(component="current"):
    """Construye una referencia sin duplicar literales entre pruebas."""
    return {"stat": {**STAT, "component": component}}


def change(pkg, amount, operation="set"):
    """Modifica la opción de una vertical autónoma para probar escrituras."""
    choice = next(s for n in pkg["nodes"] for s in n["steps"] if s["op"] == "choice")
    opt = next(o for o in choice["options"] if o["id"] == "prestar")
    opt.setdefault("effects", []).append(
        {"op": operation, "target": ref(), "value": {"literal": amount}}
    )
    return pkg


class SofiaH34bTests(unittest.TestCase):
    def test_baseline_read_does_not_materialize_current(self):
        _, session = ready()
        before = session.export()
        self.assertEqual(value(before, ref("base"), session._definitions), 6)
        self.assertEqual(value(before, ref(), session._definitions), 6)
        self.assertEqual(value(before, ref("effective"), session._definitions), 6)
        self.assertEqual(session.export(), before)
        self.assertNotIn(
            "stats",
            next(x for x in before["world"]["characters"] if x["id"] == "alberto"),
        )

    def test_scoresheet_schema_and_purity(self):
        _, session = ready()
        before = session.export()
        sheet = session.scoresheet("alberto")
        self.assertEqual(
            sheet["stats"][0],
            {
                "name": "strength",
                "base": 6,
                "current": 6,
                "modifier": 0,
                "effective": 6,
            },
        )
        self.assertTrue(session._admitted)
        from gisela.contracts.semantic_validator import Validator

        self.assertTrue(Validator().check_schema("scoresheet", sheet))
        self.assertEqual(session.export(), before)

    def test_write_current_and_restore(self):
        pkg = change(load(), 4)
        admitted, session = ready(pkg)
        self.assertEqual(send(session, "prestar")["status"], "ok")
        state = session.export()
        self.assertEqual(value(state, ref("base"), session._definitions), 6)
        self.assertEqual(value(state, ref("current"), session._definitions), 4)
        self.assertEqual(session.scoresheet("alberto")["stats"][0]["effective"], 4)
        self.assertEqual(
            restore_session(admitted, state).scoresheet("alberto"),
            session.scoresheet("alberto"),
        )

    def test_add_and_compare_effective(self):
        pkg = change(load(), -2, "add")
        _, session = ready(pkg)
        self.assertEqual(send(session, "prestar")["status"], "ok")
        test = {
            "compare": {"left": ref("effective"), "op": "eq", "right": {"literal": 4}}
        }
        self.assertTrue(predicate(session.export(), test, session._definitions))

    def test_out_of_range_rolls_back(self):
        _, session = ready(change(load(), 11))
        before = session.export()
        self.assertEqual(send(session, "prestar")["error"]["code"], "STAT_RANGE")
        self.assertEqual(session.export(), before)

    def test_boolean_is_not_an_integer(self):
        from gisela.engine.sofia import write

        _, session = ready()
        with self.assertRaises(WorldError):
            write(session.export(), {"ref": STAT, "value": True}, session._definitions)

    def test_effects_modify_effective_without_changing_current(self):
        pkg = load()
        pkg["cards"].append(
            {
                "id": "estimulo",
                "kind": "effect",
                "title": {"text": "Estímulo"},
                "modifiers": [{"stat": "strength", "amount": 3}],
            }
        )
        pkg["initial_state"]["effects"].append(
            {
                "id": "estimulo_01",
                "card": "estimulo",
                "target": "alberto",
                "started_turn": 0,
                "started_at": pkg["initial_state"]["world_time"],
            }
        )
        _, session = ready(pkg)
        before = session.export()
        row = session.scoresheet("alberto")["stats"][0]
        self.assertEqual(
            (row["base"], row["current"], row["modifier"], row["effective"]),
            (6, 6, 3, 9),
        )
        self.assertEqual(session.export(), before)

    def test_active_effect_can_exceed_scale(self):
        pkg = load()
        pkg["cards"].append(
            {
                "id": "impulso",
                "kind": "effect",
                "title": {"text": "Impulso"},
                "modifiers": [{"stat": "strength", "amount": 8}],
            }
        )
        pkg["initial_state"]["effects"].append(
            {
                "id": "impulso_01",
                "card": "impulso",
                "target": "alberto",
                "started_turn": 0,
                "started_at": pkg["initial_state"]["world_time"],
            }
        )
        _, session = ready(pkg)
        self.assertEqual(session.scoresheet("alberto")["stats"][0]["effective"], 14)

    def test_no_sofia_character_does_not_gain_stats(self):
        pkg = load()
        del next(card for card in pkg["cards"] if card["id"] == "gisela")["sofia"]
        _, session = ready(pkg)
        with self.assertRaises(WorldError):
            session.scoresheet("gisela")

    def test_reset_to_base_does_not_persist_override(self):
        pkg = change(change(load(), 4), 6)
        _, session = ready(pkg)
        self.assertEqual(send(session, "prestar")["status"], "ok")
        actor = next(
            x for x in session.export()["world"]["characters"] if x["id"] == "alberto"
        )
        self.assertNotIn("stats", actor)

    def test_set_base_and_effective_are_not_writable(self):
        """El contrato permite modificar únicamente current."""
        from gisela.contracts.admit_package import PackageRejected

        for component in ("base", "effective"):
            pkg = change(load(), 5)
            choice = next(
                s for n in pkg["nodes"] for s in n["steps"] if s["op"] == "choice"
            )
            choice["options"][0]["effects"][-1]["target"] = ref(component)
            with self.assertRaises(PackageRejected):
                admit_package(pkg)

    def test_stat_write_rolls_back_after_later_failure(self):
        """Una consecuencia posterior inválida revierte el cambio de atributo."""
        pkg = change(load(), 4)
        choice = next(
            s for n in pkg["nodes"] for s in n["steps"] if s["op"] == "choice"
        )
        choice["options"][0]["effects"].append(
            {"op": "remove_instance", "instance": "gisela"}
        )
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, "prestar")["status"], "error")
        self.assertEqual(session.export(), before)

    def test_reactive_stat_additions_are_combined(self):
        """Dos sumas de una misma ronda leen el mismo valor base."""
        pkg = load()
        for name, increment in (("confianza_2", -1), ("confianza_3", -2)):
            next(r for r in pkg["rules"] if r["id"] == name)["effects"] = [
                {"op": "add", "target": ref(), "value": {"literal": increment}}
            ]
        _, session = ready(pkg)
        self.assertEqual(send(session, "prestar")["status"], "ok")
        self.assertEqual(value(session.export(), ref(), session._definitions), 3)

    def test_reactive_stat_set_add_conflict_rolls_back(self):
        """La combinación contradictoria no altera la sesión."""
        pkg = load()
        for name, op in (("confianza_2", "set"), ("confianza_3", "add")):
            next(r for r in pkg["rules"] if r["id"] == name)["effects"] = [
                {"op": op, "target": ref(), "value": {"literal": 3}}
            ]
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, "prestar")["error"]["code"], "REACTION_CONFLICT")
        self.assertEqual(session.export(), before)

    def test_scoresheet_reads_confirmed_state_during_wait(self):
        """Scoresheet no filtra modificaciones provisionales de una espera."""
        from gisela.engine.tests.test_h3_world import base

        _, session = ready(base("h2_descarte"))
        before = session.scoresheet("gisela")
        self.assertEqual(send(session, "prestar")["status"], "ok")
        self.assertEqual(session.observe()["content"]["kind"], "pending_transaction")
        self.assertEqual(session.scoresheet("gisela")["stats"], before["stats"])

    def test_unknown_character_is_rejected(self):
        """No hay atributos implícitos para instancias inexistentes."""
        _, session = ready()
        with self.assertRaises(WorldError):
            session.scoresheet("fantasma")

    def test_invalid_stats_without_sofia_are_rejected_on_admission(self):
        """La validación semántica detecta incoherencias de definición."""
        from gisela.contracts.admit_package import PackageRejected

        pkg = load()
        del next(c for c in pkg["cards"] if c["id"] == "gisela")["sofia"]
        actor = next(
            c for c in pkg["initial_state"]["characters"] if c["id"] == "gisela"
        )
        actor["stats"] = {"strength": 2}
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_modifier_without_sofia_is_rejected_on_admission(self):
        """Un modificador S.O.F.I.A. requiere una carta apropiada."""
        from gisela.contracts.admit_package import PackageRejected

        pkg = load()
        del next(c for c in pkg["cards"] if c["id"] == "gisela")["sofia"]
        pkg["cards"].append(
            {
                "id": "estimulo",
                "kind": "effect",
                "title": {"text": "Estímulo"},
                "modifiers": [{"stat": "strength", "amount": 2}],
            }
        )
        pkg["initial_state"]["effects"].append(
            {
                "id": "estimulo_01",
                "card": "estimulo",
                "target": "gisela",
                "started_turn": 0,
                "started_at": pkg["initial_state"]["world_time"],
            }
        )
        with self.assertRaises(PackageRejected):
            admit_package(pkg)


if __name__ == "__main__":
    unittest.main()
