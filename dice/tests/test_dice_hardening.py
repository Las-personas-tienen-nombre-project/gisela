"""E0-D01..D06: perfiles son unívocos, totales cubiertos sin reroll."""
import copy
import unittest
from dice import DiceError, compile_profile, evaluate
from dice.tests.test_dice import profile


class DiceHardening(unittest.TestCase):
    def test_e0_d01_reject_duplicate_result_names(self):
        data = profile()
        data['bands'][2]['id'] = data['bands'][1]['id']
        with self.assertRaises(DiceError):
            compile_profile(data)

    def test_e0_d02_first_band_is_lower_fallback(self):
        data = profile('deterministic')
        data['bands'] = [{'id':'blocked', 'min':10}]
        result = evaluate(compile_profile(data), {'base':0,'bonus':0,'difficulty':1})
        self.assertEqual(result['outcome'],'blocked')

    def test_e0_d03_minimum_allowed_totals_are_covered(self):
        data = profile('deterministic')
        result = evaluate(compile_profile(data),
                          {'base':-1000000, 'bonus':-1000000, 'difficulty':1000000})
        self.assertEqual(result['outcome'],'failure')

    def test_e0_d04_above_highest_threshold_is_last_band(self):
        data = profile('deterministic')
        result = evaluate(compile_profile(data),
                          {'base':1000000,'bonus':1000000,'difficulty':-1000000})
        self.assertEqual(result['outcome'],'success')

    def test_e0_d05_rejection_preserves_profile_and_rng(self):
        data = profile()
        data['bands'][2]['id'] = data['bands'][1]['id']
        initial = copy.deepcopy(data)
        called = []
        with self.assertRaises(DiceError):
            evaluate(compile_profile(data), {'base':0,'bonus':0,'difficulty':0},
                     lambda _: called.append(True))
        self.assertEqual(data, initial)
        self.assertEqual(called, [])

    def test_e0_d06_direct_evaluate_rejects_uncompiled_bad_profile(self):
        data = profile()
        data['bands'][2]['id'] = data['bands'][1]['id']
        draws = []
        with self.assertRaises(DiceError):
            evaluate(data, {'base':0,'bonus':0,'difficulty':0}, lambda _:draws.append(1))
        self.assertEqual(draws, [])

    def test_e0_d07_profile_does_not_import_game_engine(self):
        import dice.core
        self.assertNotIn('gisela', dice.core.__dict__)
        self.assertNotIn('traits', dice.core.__dict__)
