"""Contratos independientes de MARY; no importa GISELA ni ALBERTO."""

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from mary import MaryError, compile_plan, evaluate, initial_progress, public_quests
from narrative_conditions import compare
from narrative_conditions import evaluate as condition

ROOT = Path(__file__).resolve().parents[2]


def definitions():
    """Plan con objetivo permanente, otro reversible y misión visible."""
    return {
        "objectives": [
            {
                "id": "reconocer",
                "mode": "milestone",
                "visibility": "hidden",
                "criterion": {
                    "kind": "distinct",
                    "facts": ["pasillo", "ascensor", "puesto_b"],
                    "minimum": 2,
                },
                "yield": {"fact": "rostro_reconocido"},
            },
            {
                "id": "tiene_luz",
                "mode": "current",
                "visibility": "public",
                "title": "Conservar la luz",
                "criterion": {
                    "kind": "condition",
                    "when": {
                        "compare": {
                            "left": {"value": "session.luz"},
                            "op": "eq",
                            "right": {"literal": True},
                        }
                    },
                },
            },
        ],
        "missions": [
            {
                "id": "guardia",
                "title": "Turno de vigilancia",
                "visibility": "public",
                "objectives": ["reconocer", "tiene_luz"],
                "completion": "all",
                "yield": {"fact": "turno_listo"},
            }
        ],
    }


class MaryIndependent(unittest.TestCase):
    def setUp(self):
        self.plan = compile_plan(definitions())

    def context(self, facts=(), light=False):
        return {"facts": list(facts), "values": {"session.luz": light}}

    def test_source_definitions_not_modified(self):
        src = definitions()
        compile_plan(src)["objectives"]["reconocer"]["mode"] = "current"
        self.assertEqual(src, definitions())

    def test_first_evaluation_is_pure(self):
        before = initial_progress(self.plan)
        result = evaluate(self.plan, self.context(["pasillo"]), before)
        self.assertEqual(before, initial_progress(self.plan))
        self.assertEqual(result["progress"]["missions"]["guardia"], "active")

    def test_two_distinct_experiences(self):
        current = evaluate(self.plan, self.context(["pasillo", "pasillo"]))
        self.assertFalse(current["progress"]["objectives"]["reconocer"])
        current = evaluate(
            self.plan, self.context(["pasillo", "ascensor"]), current["progress"]
        )
        self.assertTrue(current["progress"]["objectives"]["reconocer"])
        self.assertEqual(len(current["yields"]), 1)

    def test_yield_occurs_once(self):
        first = evaluate(self.plan, self.context(["pasillo", "ascensor"]))
        second = evaluate(
            self.plan, self.context(["pasillo", "ascensor"]), first["progress"]
        )
        self.assertEqual(second["yields"], [])
        self.assertEqual(second["transitions"], [])

    def test_milestone_latches_and_current_reverses(self):
        first = evaluate(self.plan, self.context(["pasillo", "ascensor"], True))
        self.assertEqual(first["progress"]["missions"]["guardia"], "completed")
        second = evaluate(self.plan, self.context([], False), first["progress"])
        self.assertTrue(second["progress"]["objectives"]["reconocer"])
        self.assertFalse(second["progress"]["objectives"]["tiene_luz"])
        self.assertEqual(second["progress"]["missions"]["guardia"], "completed")

    def test_hidden_objective_never_leaks(self):
        snapshot = evaluate(self.plan, self.context())["progress"]
        public = public_quests(self.plan, snapshot)
        self.assertEqual(
            public[0]["objectives"], [{"title": "Conservar la luz", "completed": False}]
        )
        self.assertNotIn("reconocer", json.dumps(public))

    def test_weighted_progress_is_unique(self):
        plan = compile_plan(
            {
                "objectives": [
                    {
                        "id": "donativos",
                        "mode": "milestone",
                        "criterion": {
                            "kind": "weighted",
                            "weights": {"comida": 2, "oro": 3},
                            "minimum": 4,
                        },
                    }
                ],
                "missions": [],
            }
        )
        self.assertFalse(
            evaluate(plan, self.context(["comida", "comida"]))["progress"][
                "objectives"
            ]["donativos"]
        )
        self.assertTrue(
            evaluate(plan, self.context(["comida", "oro"]))["progress"]["objectives"][
                "donativos"
            ]
        )

    def test_failure_precedes_completion(self):
        src = definitions()
        src["missions"][0]["fail_when"] = {"has_fact": "tarde"}
        plan = compile_plan(src)
        outcome = evaluate(plan, self.context(["pasillo", "ascensor", "tarde"], True))
        self.assertEqual(outcome["progress"]["missions"]["guardia"], "failed")
        self.assertFalse(
            any(x["source"] == "mission:guardia" for x in outcome["yields"])
        )

    def test_snapshot_json_roundtrip(self):
        state = evaluate(self.plan, self.context(["pasillo", "ascensor"]))["progress"]
        restored = json.loads(json.dumps(state))
        self.assertEqual(
            evaluate(self.plan, self.context(["pasillo", "ascensor"]), restored)[
                "yields"
            ],
            [],
        )

    def test_unknown_progress_and_types_rejected(self):
        progress = initial_progress(self.plan)
        progress["objectives"]["otro"] = True
        with self.assertRaises(MaryError):
            evaluate(self.plan, self.context(), progress)
        progress = initial_progress(self.plan)
        progress["objectives"]["reconocer"] = 1
        with self.assertRaises(MaryError):
            evaluate(self.plan, self.context(), progress)

    def test_decimal_and_integer_compare(self):
        from decimal import Decimal

        self.assertTrue(compare(Decimal("2.0"), 2, "eq"))
        self.assertTrue(compare(Decimal("2.5"), 2, "gt"))

    def test_boolean_and_integer_not_equal(self):
        self.assertFalse(compare(True, 1, "eq"))
        with self.assertRaises(ValueError):
            compare(True, 1, "gt")
        self.assertTrue(
            condition(
                {"all": [{"constant": True}, {"not": {"constant": False}}]},
                lambda x: False,
            )
        )

    def test_invalid_mission_reference_rejected(self):
        src = definitions()
        src["missions"][0]["objectives"] = ["no_existe"]
        with self.assertRaises(MaryError):
            compile_plan(src)

    def test_duplicate_ids_rejected(self):
        src = definitions()
        src["objectives"].append(copy.deepcopy(src["objectives"][0]))
        with self.assertRaises(MaryError):
            compile_plan(src)

    def test_unreachable_threshold_rejected(self):
        src = definitions()
        src["objectives"][0]["criterion"]["minimum"] = 4
        with self.assertRaises(MaryError):
            compile_plan(src)

    def test_reversible_yield_rejected(self):
        src = definitions()
        src["objectives"][1]["yield"] = {"fact": "falso"}
        with self.assertRaises(MaryError):
            compile_plan(src)

    def test_independent_imports(self):
        script = (
            "import mary\nimport sys\n"
            "unexpected = [name for name in ('gisela', 'alberto') "
            "if name in sys.modules]\n"
            "if unexpected:\n"
            "    raise SystemExit(f'Unexpected imports: {unexpected}')\n"
        )
        outcome = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(outcome.returncode, 0, outcome.stderr)

    def test_deterministic_order(self):
        result = evaluate(self.plan, self.context(["pasillo", "ascensor"], True))
        self.assertEqual(
            [x["source"] for x in result["yields"]],
            ["objective:reconocer", "mission:guardia"],
        )

    def test_no_effects_outside_results(self):
        context = self.context(["pasillo", "ascensor"], True)
        before = copy.deepcopy(context)
        result = evaluate(self.plan, context)
        result["progress"]["objectives"]["reconocer"] = False
        self.assertEqual(context, before)

    def test_many_objectives_within_budget(self):
        src = {
            "objectives": [
                {
                    "id": f"goal_{i}",
                    "mode": "milestone",
                    "criterion": {"kind": "condition", "when": {"has_fact": "a"}},
                }
                for i in range(256)
            ],
            "missions": [],
        }
        result = evaluate(compile_plan(src), {"facts": ["a"], "values": {}})
        self.assertEqual(len(result["transitions"]), 256)

    def test_ambiguous_condition_rejected(self):
        src = definitions()
        src["objectives"][0]["criterion"] = {
            "kind": "condition",
            "when": {"all": [], "any": []},
        }
        with self.assertRaises(MaryError):
            compile_plan(src)


if __name__ == "__main__":
    unittest.main()
