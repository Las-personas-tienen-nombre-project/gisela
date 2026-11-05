"""E1: versión aislada, admisión estática y normalización neutra TRAITS-DICE."""

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from gisela.contracts.admit_package import admit_package
from gisela.contracts.evaluation_plan import (
    compile_package_evaluations,
    normalize_evaluation,
    profile_catalog,
)
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import GiselaSession

ROOT = Path(__file__).parent
BASE = json.loads((ROOT / "example.package.json").read_text())
PROFILE = {
    "schema_version": "dice.profile.v1",
    "id": "repair",
    "mode": "deterministic",
    "bands": [{"id": "blocked", "min": 0}, {"id": "complete", "min": 10}],
}
EVAL = {
    "id": "repair_attempt",
    "profile": "repair",
    "presentation": "hidden",
    "inputs": {"base": {"literal": 12}, "difficulty": {"literal": 2}},
    "context": {"participants": [], "tags": ["repair"]},
    "branches": [
        {"outcome": "blocked", "effects": []},
        {"outcome": "complete", "effects": []},
    ],
}


def fixture():
    package = copy.deepcopy(BASE)
    package["manifest"]["format_version"] = "1.4"
    package["dice_profiles"] = [copy.deepcopy(PROFILE)]
    package["nodes"][0]["steps"].insert(
        0, {"id": "repair_step", "op": "evaluate", "evaluation": copy.deepcopy(EVAL)}
    )
    return package


def problems(package):
    return [e for e in Validator().validate_package(package) if e.severity == "error"]


class E1Contracts(unittest.TestCase):
    def assert_rejected(self, package, code=None):
        issues = problems(package)
        self.assertTrue(issues, "Paquete inválido admitido")
        if code:
            self.assertIn(code, [e.code for e in issues], issues)

    def test_e1_01_thirteen_v14_schemas_are_valid(self):
        schemas = list((ROOT / "v1_4").glob("*.schema.json"))
        self.assertEqual(len(schemas), 13)
        for path in schemas:
            with self.subTest(path=path.name):
                Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_e1_02_admission_and_digest(self):
        package = fixture()
        self.assertEqual([], problems(package))
        admitted = admit_package(package)
        self.assertEqual(admitted.materialize(), package)
        package["dice_profiles"][0]["bands"][0]["id"] = "different"
        self.assertEqual(
            admitted.materialize()["dice_profiles"][0]["bands"][0]["id"], "blocked"
        )

    def test_e1_03_normalized_request_is_exact_bridge_input(self):
        package = fixture()
        plan = compile_package_evaluations(package)["/nodes/0/steps/0"]
        self.assertEqual(
            plan["request"],
            {
                "profile": PROFILE,
                "base": 12,
                "difficulty": 2,
                "participants": [],
                "tags": ["repair"],
            },
        )
        self.assertEqual(set(plan["branches"]), {"blocked", "complete"})
        plan["request"]["profile"]["bands"].clear()
        self.assertEqual(PROFILE["bands"][0]["id"], "blocked")

    def test_e1_04_does_not_consume_rng_or_mutate_world(self):
        package = fixture()
        original = copy.deepcopy(package)
        compile_package_evaluations(package)
        self.assertEqual(original, package)

    def test_e1_05_rejects_duplicate_profile_ids(self):
        package = fixture()
        package["dice_profiles"].append(copy.deepcopy(PROFILE))
        self.assert_rejected(package, "DICE_PROFILE_INVALID")

    def test_e1_06_rejects_invalid_dice_profile(self):
        package = fixture()
        package["dice_profiles"][0]["bands"][1]["id"] = "blocked"
        self.assert_rejected(package, "DICE_PROFILE_INVALID")

    def test_e1_07_rejects_missing_profile(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["profile"] = "unknown"
        self.assert_rejected(package, "EVALUATION_INVALID")

    def test_e1_08_rejects_missing_branch(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["branches"].pop()
        self.assert_rejected(package, "EVALUATION_INVALID")

    def test_e1_09_rejects_duplicate_branch(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["branches"][1]["outcome"] = (
            "blocked"
        )
        self.assert_rejected(package, "EVALUATION_INVALID")

    def test_e1_10_rejects_unexpected_branch(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["branches"][1]["outcome"] = (
            "other"
        )
        self.assert_rejected(package, "EVALUATION_INVALID")

    def test_e1_11_rejects_invalid_branch_effect(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["branches"][1]["effects"] = [
            {"op": "record_fact", "fact": "unknown"}
        ]
        self.assert_rejected(package, "UNKNOWN_FACT")

    def test_e1_12_rejects_bad_branch_destination(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["branches"][1]["next"] = {
            "node": "missing"
        }
        self.assert_rejected(package, "UNKNOWN_NODE")

    def test_e1_13_rejects_missing_stat_card(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["inputs"]["base"] = {
            "stat": {
                "character": "gisela",
                "name": "openness",
                "component": "effective",
            }
        }
        for card in package["cards"]:
            if card["kind"] == "character" and card["id"] == "gisela":
                card.pop("sofia", None)
        self.assert_rejected(package, "MISSING_SOFIA")

    def test_e1_14_rejects_unknown_stat_actor(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["inputs"]["base"] = {
            "stat": {
                "character": "unknown",
                "name": "awareness",
                "component": "effective",
            }
        }
        self.assert_rejected(package, "UNKNOWN_ENTITY")

    def test_e1_15_rejects_duplicate_participants(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["context"]["participants"] = [
            {"entity": "gisela", "role": "actor"}
        ] * 2
        self.assert_rejected(package, "DUPLICATE_PARTICIPANT")

    def test_e1_16_rejects_participant_wrong_kind(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["context"]["participants"] = [
            {"entity": "intuicion_01", "role": "actor"}
        ]
        self.assert_rejected(package, "WRONG_ENTITY_KIND")

    def test_e1_17_rejects_choice_evaluation_with_effects(self):
        package = fixture()
        option = package["nodes"][0]["steps"][3]["options"][0]
        option["evaluation"] = copy.deepcopy(EVAL)
        self.assert_rejected(package, "SCHEMA_INVALID")

    def test_e1_18_choice_evaluation_and_scene_action_supported(self):
        package = fixture()
        option = package["nodes"][0]["steps"][3]["options"][0]
        option.pop("effects", None)
        option.pop("next", None)
        option["evaluation"] = copy.deepcopy(EVAL)
        scene_action = {"id": "repair_action", "label": {"text": "Reparar"}}
        package["scenes"][0].setdefault("actions", []).append(scene_action)
        scene_action.pop("effects", None)
        scene_action.pop("next", None)
        scene_action["evaluation"] = copy.deepcopy(EVAL)
        self.assertEqual([], problems(package))
        plan = compile_package_evaluations(package)
        self.assertEqual(len(plan), 3)

    def test_e1_19_scene_local_destination_is_rejected(self):
        package = fixture()
        action = {"id": "repair_action", "label": {"text": "Reparar"}}
        package["scenes"][0].setdefault("actions", []).append(action)
        action.pop("effects", None)
        action.pop("next", None)
        action["evaluation"] = copy.deepcopy(EVAL)
        action["evaluation"]["branches"][0]["next"] = {"step": "decision"}
        self.assert_rejected(package, "INVALID_SCENE_DESTINATION")

    def test_e1_20_v12_rejects_evaluation(self):
        package = copy.deepcopy(BASE)
        package["nodes"][0]["steps"].insert(
            0, {"id": "repair_step", "op": "evaluate", "evaluation": EVAL}
        )
        self.assert_rejected(package, "SCHEMA_INVALID")

    def test_e1_21_runtime_executes_hidden_v14(self):
        admitted = admit_package(fixture())
        session = GiselaSession.new_session(admitted)
        self.assertEqual(session.export()["schema_version"], "1.4")

    def test_e1_22_v14_snapshot_is_restorable_with_matching_digest(self):
        admitted = admit_package(fixture())
        session = GiselaSession.new_session(admitted)
        snapshot = session.export()
        self.assertFalse(
            [
                i
                for i in Validator().validate_session(
                    snapshot, admitted.materialize(), expected_digest=admitted.digest
                )
                if i.severity == "error"
            ]
        )
        self.assertEqual(
            GiselaSession.restore_session(admitted, snapshot).export(), snapshot
        )

    def test_e1_23_no_missing_dice_dependencies_for_literal(self):
        package = fixture()
        self.assertNotIn("traits", package)
        self.assertEqual([], problems(package))
        self.assertNotIn(
            "stat", normalize_evaluation(EVAL, profile_catalog(package))["request"]
        )

    def test_e1_24_rejects_invalid_literal_bound(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["inputs"]["base"] = {
            "literal": 1000001
        }
        self.assert_rejected(package, "SCHEMA_INVALID")

    def test_e1_25_rejects_duplicate_tags(self):
        package = fixture()
        package["nodes"][0]["steps"][0]["evaluation"]["context"]["tags"] = [
            "repair",
            "repair",
        ]
        self.assert_rejected(package, "SCHEMA_INVALID")

    def test_e1_26_rejects_missing_catalog(self):
        package = fixture()
        package.pop("dice_profiles")
        self.assert_rejected(package, "EVALUATION_INVALID")

    def test_e1_27_rejects_math_profiles_with_excessive_bands(self):
        package = fixture()
        package["dice_profiles"][0]["bands"] = [
            {"id": f"out_{i}", "min": i} for i in range(17)
        ]
        self.assert_rejected(package, "SCHEMA_INVALID")

    def test_e1_28_differs_for_dice_modes_without_rolling(self):
        package = fixture()
        profile = package["dice_profiles"][0]
        profile.update(mode="dice_sum", count=2, sides=6)
        plan = compile_package_evaluations(package)["/nodes/0/steps/0"]
        self.assertEqual(plan["request"]["profile"]["count"], 2)
        self.assertNotIn("rng_after", plan)

    def test_e1_29_generic_package_without_player_is_admitted(self):
        """La autoría no presupone protagonista, Ren'Py ni TRAITS/S.O.F.I.A."""
        path = ROOT.parent / "packages/e1_reparacion_sin_jugador.package.json"
        package = json.loads(path.read_text())
        self.assertNotIn("player_character", package["initial_state"])
        self.assertNotIn("traits", package)
        self.assertEqual([], problems(package))
        result = compile_package_evaluations(package)
        self.assertEqual(len(result), 1)
        self.assertEqual(next(iter(result.values()))["request"]["base"], 3)


if __name__ == "__main__":
    unittest.main()
