"""PA-001 PT-02R: frontera pública Act durante transacciones pendientes."""
import copy
import unittest

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session
from gisela.engine.tests.test_h2_closure import PACKAGE, SEED, with_roll, reach_choice, send
from gisela.engine.tests.test_pa001_differential_restore import roundtrip


class MalformedAuxiliary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admitted = admit_package(with_roll(admit_package_file(PACKAGE).materialize()))

    def sessions(self):
        a = new_session(self.admitted, seed=SEED)
        reach_choice(a)
        self.assertEqual(send(a, 'choose_prestar')['status'], 'ok')
        return a, roundtrip(self.admitted, a)

    def test_malformed_envelopes_never_change_pending_snapshot(self):
        a, b = self.sessions()
        initial = copy.deepcopy(a.export())
        view = a.observe()
        valid = {'session_id':view['session_id'], 'revision':view['revision'],
                 'action_id':'resolve_hab_01'}
        invalid = [None, [], 'resolve_hab_01', {},
                   {**valid, 'revision':'invalid'},
                   {**valid, 'action_id':None},
                   {**valid, 'parameters':{'unexpected':1}},
                   {**valid, 'unexpected':True},
                   {k:v for k,v in valid.items() if k!='session_id'}]
        for session in (a,b):
            for request in invalid:
                result = session.act(copy.deepcopy(request))
                self.assertEqual(result['status'], 'error', request)
                self.assertIn(result['error']['code'], ('INVALID_ACTION', 'STALE_PROJECTION'))
                self.assertEqual(session.export(), initial, request)
        for session in (a,b):
            self.assertEqual(send(session,'resolve_hab_01')['status'], 'ok')
        self.assertEqual(a.export(), b.export())

    def test_stale_and_foreign_envelopes_rejected_without_mutation(self):
        a, b = self.sessions()
        before = copy.deepcopy(a.export())
        view = a.observe()
        for session in (a,b):
            for request in ({'session_id':'foreign', 'revision':view['revision'], 'action_id':'resolve_hab_01'},
                            {'session_id':view['session_id'], 'revision':view['revision']-1, 'action_id':'resolve_hab_01'}):
                result = session.act(request)
                self.assertEqual(result['error']['code'], 'STALE_PROJECTION')
                self.assertEqual(session.export(), before)
        self.assertEqual(a.observe(),b.observe())
