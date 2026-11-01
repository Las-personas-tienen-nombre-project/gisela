"""DICE debe funcionar sin importar GISELA, TRAITS ni S.O.F.I.A."""

import copy
import unittest

from dice import DiceError, compile_profile, evaluate


def profile(mode="dice_sum"):
    return {
        "schema_version": "dice.profile.v1",
        "id": "repair",
        "mode": mode,
        **({} if mode == "deterministic" else {"count": 2, "sides": 6}),
        "bands": [
            {"id": "failure", "min": -1000000},
            {"id": "partial", "min": 5},
            {"id": "success", "min": 10},
        ],
    }


class DiceIndependent(unittest.TestCase):
    def test_deterministic_without_rng(self):
        p = compile_profile(profile("deterministic"))
        result = evaluate(p, {"base": 8, "bonus": 3, "difficulty": 1})
        self.assertEqual(result["outcome"], "success")
        self.assertEqual(result["rolls"], [])

    def test_injected_rng_and_full_trace(self):
        p = compile_profile(profile())
        sequence = iter([3, 5])
        result = evaluate(
            p, {"base": 1, "bonus": 1, "difficulty": 2}, lambda _: next(sequence)
        )
        self.assertEqual((result["rolls"], result["total"]), ([3, 5], 8))
        self.assertEqual(result["outcome"], "partial")

    def test_pool_uses_max_not_sum(self):
        p = compile_profile(profile("dice_pool"))
        self.assertEqual(
            evaluate(p, {"base": 0, "bonus": 0, "difficulty": 0}, lambda _: 4)["total"],
            4,
        )

    def test_rejects_bad_roll_no_mutation_of_profile(self):
        p = compile_profile(profile())
        before = copy.deepcopy(p)
        with self.assertRaises(DiceError):
            evaluate(p, {"base": 0, "bonus": 0, "difficulty": 0}, lambda _: 7)
        self.assertEqual(p, before)

    def test_no_rng_provider_rejected(self):
        with self.assertRaises(DiceError):
            evaluate(
                compile_profile(profile()), {"base": 1, "bonus": 1, "difficulty": 1}
            )

    def test_invalid_profile(self):
        invalid = profile()
        invalid["bands"][1]["min"] = -1000000
        with self.assertRaises(DiceError):
            compile_profile(invalid)

    def test_invalid_number_types(self):
        p = compile_profile(profile("deterministic"))
        with self.assertRaises(DiceError):
            evaluate(p, {"base": True, "bonus": 2, "difficulty": 1})

    def test_same_inputs_and_dice_same_result(self):
        p = compile_profile(profile())
        arg = {"base": 3, "bonus": 2, "difficulty": 6}
        a = evaluate(p, arg, lambda _: 4)
        b = evaluate(p, arg, lambda _: 4)
        self.assertEqual(a, b)
