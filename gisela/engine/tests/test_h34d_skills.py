"""H3.4d: uso autorizado, resultados, consumo, retorno y replay."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.errors import EngineFailure
from gisela.engine.tests.test_h34a_values import send

PATH = Path(__file__).resolve().parents[2] / 'packages/h3_habilidades.package.json'


def fixture():
    """Usa una historia corta y validable como origen de las variaciones."""
    return admit_package_file(PATH).materialize()


def window(pkg=None):
    """Abre la ventana después del primer paso visible."""
    admission = admit_package(pkg) if pkg else admit_package_file(PATH)
    session = new_session(admission)
    for _ in range(1):
        assert send(session)['status'] == 'ok'
    assert session.observe()['content']['kind'] == 'skill_window'
    return admission, session


def card(pkg, identifier='gesto'):
    """Ubica una carta existente por identificador."""
    return next(x for x in pkg['cards'] if x['id'] == identifier)


def skill(pkg, ident='gesto_01'):
    """Ubica la instancia inicial de habilidad."""
    return next(x for x in pkg['initial_state']['skills'] if x['id'] == ident)


class H34dSkillsTest(unittest.TestCase):
    def test_play_discards_and_records_outcome_once(self):
        admitted, session = window()
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        saved = session.export()
        self.assertNotIn('gesto_01', [s['id'] for s in saved['world']['skills']])
        self.assertEqual(saved['history']['facts'][-2]['fact'], 'habilidad_utilizada')
        self.assertEqual(saved['history']['facts'][-1]['fact'], 'habilidad_resultado')
        self.assertEqual(saved['history']['trace'][-1]['kind'], 'skill_played')
        self.assertEqual(session.observe()['content']['kind'], 'ending')
        self.assertEqual(restore_session(admitted, saved).export(), saved)

    def test_skip_window_does_not_consume(self):
        _, session = window()
        original = session.export()['world']['skills']
        self.assertEqual(send(session, 'continue')['status'], 'ok')
        self.assertEqual(session.export()['world']['skills'], original)
        self.assertEqual(session.observe()['content']['kind'], 'ending')

    def test_requires_false_disables_action(self):
        pkg = fixture()
        card(pkg)['play']['requires'] = {'constant':False}
        _, session = window(pkg)
        self.assertFalse(session.observe()['actions'][0]['enabled'])
        before = session.export()
        request = {'session_id':before['session_id'], 'revision':before['revision'],
                   'action_id':'play_gesto_01'}
        self.assertEqual(session.act(request)['error']['code'], 'INVALID_ACTION')
        self.assertEqual(session.export(), before)

    def test_reserve_skill_cannot_be_played(self):
        _, session = window()
        self.assertNotIn('play_reserva_01', [x['action_id'] for x in session.observe()['actions']])
        before = session.export()
        request = {'session_id':before['session_id'], 'revision':before['revision'],
                   'action_id':'play_reserva_01'}
        self.assertEqual(session.act(request)['error']['code'], 'INVALID_ACTION')
        self.assertEqual(session.export(), before)

    def test_playing_return_to_hand_preserves_identity(self):
        pkg = fixture()
        card(pkg)['return_policy']['default'] = 'hand'
        _, session = window(pkg)
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(next(s for s in session.export()['world']['skills']
                              if s['id'] == 'gesto_01')['zone'], 'hand')
        self.assertEqual(len(session.export()['history']['trace']), 1)

    def test_return_to_reserve(self):
        pkg = fixture()
        card(pkg)['return_policy']['default'] = 'reserve'
        pkg['initial_state']['capacities'][0]['reserve'] = 2
        _, session = window(pkg)
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(next(s for s in session.export()['world']['skills']
                              if s['id'] == 'gesto_01')['zone'], 'reserve')

    def test_conditioned_return_and_default(self):
        pkg = fixture()
        card(pkg)['return_policy'] = {'default':'discard', 'when':[
            {'if':{'has_fact':'habilidad_utilizada'}, 'to':'hand'}]}
        _, session = window(pkg)
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertIn('gesto_01', [s['id'] for s in session.export()['world']['skills']])

    def test_incompatible_return_rolls_back(self):
        pkg = fixture()
        card(pkg)['return_policy'] = {'default':'discard', 'when':[
            {'if':{'has_fact':'habilidad_utilizada'},'to':'hand'},
            {'if':{'constant':True},'to':'reserve'}]}
        _, session = window(pkg)
        before = session.export()
        result = send(session, 'gesto_01')
        self.assertEqual(result['error']['code'], 'RETURN_POLICY_CONFLICT')
        self.assertEqual(session.export(), before)

    def test_play_requires_decision_and_restores(self):
        pkg = fixture()
        card(pkg)['play']['effects'] = [{'op':'grant_skill', 'character':'alberto',
            'skill':'gesto','overflow':'require_choice'}]
        card(pkg)['play']['outcomes'] = []
        card(pkg)['return_policy']['default'] = 'hand'
        pkg['initial_state']['capacities'][0]['hand'] = 1
        admitted, session = window(pkg)
        base = session.export()
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'pending_transaction')
        saved = session.export()
        self.assertEqual(saved['world'], base['world'])
        self.assertEqual(saved['history'], base['history'])
        self.assertEqual(saved['rng'], base['rng'])
        self.assertEqual(saved['pending_transaction']['source']['kind'], 'skill_play')
        restored = restore_session(admitted, json.loads(json.dumps(saved)))
        self.assertEqual(send(restored, 'skill_000001')['status'], 'ok')
        self.assertEqual(send(session, 'skill_000001')['status'], 'ok')
        self.assertEqual(restored.export(), session.export())
        self.assertIn('gesto_01', [s['id'] for s in restored.export()['world']['skills']])

    def test_cancel_pending_play_preserves_world(self):
        pkg = fixture()
        card(pkg)['play']['effects'] = [{'op':'grant_skill','character':'alberto',
            'skill':'gesto', 'overflow':'require_choice'}]
        card(pkg)['return_policy']['default'] = 'hand'
        pkg['initial_state']['capacities'][0]['hand'] = 1
        _, session = window(pkg)
        initial = session.export()
        send(session, 'gesto_01')
        self.assertEqual(send(session, 'cancelar')['status'], 'ok')
        self.assertEqual(session.export()['world'], initial['world'])
        self.assertEqual(session.export()['history'], initial['history'])
        self.assertEqual(session.observe()['content']['kind'], 'skill_window')

    def test_full_reserve_return_asks_and_replays(self):
        pkg = fixture()
        card(pkg)['return_policy']['default'] = 'reserve'
        admitted, session = window(pkg)
        baseline = session.export()
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'pending_transaction')
        self.assertEqual(session.export()['world'], baseline['world'])
        restored = restore_session(admitted, session.export())
        self.assertEqual(send(restored, 'reserva_01')['status'], 'ok')
        self.assertEqual(send(session, 'reserva_01')['status'], 'ok')
        self.assertEqual(restored.export(), session.export())
        self.assertEqual(next(s for s in session.export()['world']['skills']
                              if s['id'] == 'gesto_01')['zone'], 'reserve')

    def test_matching_return_destinations_do_not_conflict(self):
        pkg = fixture()
        card(pkg)['return_policy'] = {'default':'discard', 'when':[
            {'if':{'constant':True}, 'to':'hand'},
            {'if':{'has_fact':'habilidad_utilizada'}, 'to':'hand'}]}
        _, session = window(pkg)
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertIn('gesto_01', [s['id'] for s in session.export()['world']['skills']])

    def test_failed_result_still_consumes_attempt(self):
        pkg = fixture()
        card(pkg)['play']['outcomes'] = [{'when':{'constant':False}, 'effects':[
            {'op':'record_fact','fact':'habilidad_resultado'}]}]
        _, session = window(pkg)
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertNotIn('gesto_01', [s['id'] for s in session.export()['world']['skills']])
        self.assertFalse(any(f['fact']=='habilidad_resultado' for f in session.export()['history']['facts']))
        self.assertEqual(session.export()['history']['trace'][-1]['kind'],'skill_played')

    def test_technical_error_does_not_consume(self):
        pkg = fixture()
        card(pkg)['play']['effects'] = [{'op':'transfer', 'object':'casete_01',
                                         'from':'gisela', 'to':'alberto'}]
        _, session = window(pkg)
        before = session.export()
        self.assertEqual(send(session, 'gesto_01')['status'], 'error')
        self.assertEqual(session.export(), before)

    def test_second_play_when_limit_allows(self):
        pkg = fixture()
        card(pkg)['return_policy']['default'] = 'hand'
        window_step = next(s for s in pkg['nodes'][0]['steps'] if s['op']=='skill_window')
        window_step['max_plays'] = 2
        admitted, session = window(pkg)
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'skill_window')
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'ending')
        restored = restore_session(admitted, session.export())
        self.assertEqual(restored.export(), session.export())

    def test_playing_skill_outside_window_is_rejected(self):
        _, session = window()
        send(session, 'continue')
        before = session.export()
        forged = {'session_id':before['session_id'], 'revision':before['revision'],
                  'action_id':'play_gesto_01'}
        self.assertEqual(session.act(forged)['error']['code'], 'INVALID_ACTION')
        self.assertEqual(session.export(), before)

    def test_missing_player_rejected_before_start(self):
        pkg = fixture()
        pkg['initial_state'].pop('player_character')
        with self.assertRaises(EngineFailure):
            new_session(admit_package(pkg))


if __name__ == '__main__':
    unittest.main()
