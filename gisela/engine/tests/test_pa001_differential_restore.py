"""PA-001 PT-02R: equivalencia diferencial entre ejecución continua y restaurada."""
import copy
import json
import unittest

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.tests.test_h2_closure import PACKAGE, SEED, with_roll, send, reach_choice


def roundtrip(admitted, session):
    return restore_session(admitted, json.loads(json.dumps(session.export(), ensure_ascii=False)))


class DifferentialRestore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = admit_package_file(PACKAGE).materialize()

    def assert_equivalent(self, uninterrupted, restored):
        self.assertEqual(uninterrupted.export(), restored.export())
        self.assertEqual(uninterrupted.observe(), restored.observe())

    def test_reaction_pending_roll_restore_and_exact_once(self):
        admitted = admit_package(with_roll(self.base))
        continuous = new_session(admitted, seed=SEED)
        reach_choice(continuous)
        resumed = roundtrip(admitted, continuous)
        self.assert_equivalent(continuous, resumed)
        for action in ('choose_prestar', 'resolve_hab_02'):
            for session in (continuous, resumed):
                self.assertEqual(send(session, action)['status'], 'ok')
            resumed = roundtrip(admitted, resumed)
            self.assert_equivalent(continuous, resumed)
        state = continuous.export()
        self.assertEqual(state['rng']['counter'], 1)
        self.assertEqual(len(state['history']['facts']), 1)
        self.assertEqual(len(state['history']['trace']), 2)
        self.assertNotIn('pending_transaction', state)

    def test_cancel_then_retry_after_restore_matches_continuous(self):
        admitted = admit_package(with_roll(self.base))
        continuous = new_session(admitted, seed=SEED)
        reach_choice(continuous)
        resumed = roundtrip(admitted, continuous)
        base = continuous.export()
        for action in ('choose_prestar', 'cancel_pending', 'choose_prestar', 'resolve_hab_01'):
            for session in (continuous, resumed):
                self.assertEqual(send(session, action)['status'], 'ok')
            resumed = roundtrip(admitted, resumed)
            self.assert_equivalent(continuous, resumed)
            if action == 'cancel_pending':
                self.assertEqual(continuous.export()['rng'], base['rng'])
                self.assertEqual(continuous.export()['history'], base['history'])
        self.assertEqual(continuous.export()['rng']['counter'], 1)

    def test_conflicting_reactions_rollback_both_execution_paths(self):
        package = with_roll(self.base)
        package['manifest']['variables'].append({'scope':'session','id':'choque',
                                                   'type':'boolean','initial':False})
        package['initial_state']['session_variables']['choque'] = False
        for idx, value in enumerate((True, False)):
            package['rules'].append({'id':f'choque_{idx}',
                'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                'effects':[{'op':'set','target':{'var':{'scope':'session','key':'choque'}},
                            'value':{'literal':value}}]})
        admitted = admit_package(package)
        continuous = new_session(admitted, seed=SEED)
        reach_choice(continuous)
        resumed = roundtrip(admitted, continuous)
        before = copy.deepcopy(continuous.export())
        for session in (continuous, resumed):
            result = send(session, 'choose_prestar')
            self.assertEqual(result['status'], 'error')
            self.assertEqual(result['error']['code'], 'REACTION_CONFLICT')
            self.assertEqual(session.export(), before)
        self.assert_equivalent(continuous, roundtrip(admitted, resumed))
