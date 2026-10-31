"""Cierre de H2: inicio suspendido, RNG en borrador y restauración.

No hay llamadas a Ren'Py ni efectos externos. Todas las observaciones
se obtienen de la API pública y los snapshots exportados por GISELA.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.contracts.rng import RNGState, draw
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import EngineFailure, new_session, restore_session

PACKAGE = Path(__file__).resolve().parents[2] / 'packages' / 'h2_descarte.package.json'
SEED = '0123456789abcdef' * 4


def send(session, action_id: str) -> dict:
    view = session.observe()
    return session.act({'session_id': view['session_id'],
                        'revision': view['revision'], 'action_id': action_id})


def reach_choice(session):
    for _ in range(2):
        assert send(session, 'advance')['status'] == 'ok'
    assert session.observe()['content']['kind'] == 'choice'


def with_roll(pkg: dict, *, key: str = 'dado', sides: int = 6) -> dict:
    pkg = copy.deepcopy(pkg)
    pkg['manifest']['variables'].append({'scope': 'session', 'id': key,
                                         'type': 'integer', 'initial': 0})
    pkg['initial_state']['session_variables'][key] = 0
    pkg['nodes'][0]['steps'][3]['options'][0]['effects'].insert(0, {
        'op': 'roll', 'sides': sides,
        'store': {'var': {'scope': 'session', 'key': key}}})
    return pkg


class H2ClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = admit_package_file(PACKAGE).materialize()

    def starting_package(self, roll_first=True) -> object:
        pkg = copy.deepcopy(self.base)
        effects = []
        if roll_first:
            pkg['manifest']['variables'].append({'scope':'session', 'id':'dado',
                                                  'type':'integer', 'initial':0})
            pkg['initial_state']['session_variables']['dado'] = 0
            effects.append({'op':'roll','sides':6,
                            'store':{'var':{'scope':'session','key':'dado'}}})
        effects.append({'op':'grant_skill','character':'gisela',
                        'skill':'habilidad_c','overflow':'require_choice'})
        pkg['rules'].append({'id':'iniciar_con_eleccion',
                             'trigger':{'on':'turn_started'},
                             'effects':effects})
        return admit_package(pkg)

    def test_initial_mandatory_request_keeps_confirmed_base(self):
        package = self.starting_package()
        session = new_session(package, seed=SEED)
        state = session.export()
        self.assertEqual(state['status'], 'exploring')
        self.assertEqual(state['turn'], 0)
        self.assertEqual(state['history']['executions'], [])
        self.assertEqual(state['rng']['counter'], 0)
        self.assertEqual(state['narrative']['session_variables']['dado'], 0)
        self.assertEqual(state['revision'], 1)
        self.assertEqual(state['world_revision'], 0)
        self.assertEqual(state['pending_transaction']['source'], {'kind':'session_start'})
        self.assertEqual(state['pending_transaction']['origin'], 'mandatory')
        self.assertEqual({a['kind'] for a in session.observe()['actions']}, {'resolve_pending'})
        self.assertFalse(list(Validator().schemas['session'].iter_errors(state)))
        self.assertFalse(list(Validator().schemas['observe'].iter_errors(session.observe())))
        self.assertEqual(send(session,'cancel_pending')['error']['code'], 'INVALID_ACTION')

    def test_initial_request_restores_and_commits_once(self):
        admitted = self.starting_package()
        session = new_session(admitted, seed=SEED)
        restored = restore_session(admitted, json.loads(json.dumps(session.export())))
        self.assertEqual(restored.observe(), session.observe())
        original, _ = draw(RNGState(seed=SEED), 6)
        for s in (session, restored):
            self.assertEqual(send(s,'resolve_hab_01')['status'],'ok')
            state = s.export()
            self.assertNotIn('pending_transaction', state)
            self.assertEqual(state['turn'], 1)
            self.assertEqual(len(state['history']['executions']), 1)
            self.assertEqual(state['rng']['counter'], 1)
            self.assertEqual(state['narrative']['session_variables']['dado'], original)
            self.assertEqual(state['identity']['next_sequence'], 2)
            self.assertEqual(state['world_revision'], 1)
            self.assertEqual(state['revision'], 2)
        self.assertEqual(session.export(), restored.export())
        self.assertEqual(session.observe()['content']['kind'], 'narrate')

    def test_invalid_initial_response_is_atomic(self):
        admitted = self.starting_package()
        session = new_session(admitted)
        previous = session.export()
        self.assertEqual(send(session,'resolve_fantasma')['error']['code'], 'INVALID_ACTION')
        self.assertEqual(session.export(),previous)
        forged = copy.deepcopy(previous)
        forged['pending_transaction']['answers'] = [
            {'request_id':'auxiliar_0001','option_id':'fantasma'}]
        forged['pending_transaction']['request']['request_id'] = 'auxiliar_0002'
        with self.assertRaises(EngineFailure):
            restore_session(admitted, forged)

    def test_initial_pending_without_scene_uses_preparing_and_restores(self):
        pkg = self.starting_package().materialize()
        pkg['initial_state'].pop('current_scene')
        admitted = admit_package(pkg)
        session = new_session(admitted, seed=SEED)
        saved = session.export()
        self.assertEqual(saved['status'], 'preparing')
        self.assertEqual(saved['preparing_for'], pkg['manifest']['entry']['node'])
        self.assertNotIn('current_scene', saved)
        self.assertEqual(saved['turn'], 0)
        restored = restore_session(admitted, json.loads(json.dumps(saved)))
        self.assertEqual(restored.observe(), session.observe())
        for target in (session, restored):
            self.assertEqual(send(target, 'resolve_hab_01')['status'], 'ok')
        self.assertEqual(session.export(), restored.export())
        self.assertEqual(session.export()['status'], 'node')
        self.assertNotIn('preparing_for', session.export())

    def test_roll_while_pending_and_cancel_is_not_consumed(self):
        admitted = admit_package(with_roll(self.base))
        session = new_session(admitted, seed=SEED)
        reach_choice(session)
        baseline = session.export()
        self.assertEqual(send(session,'choose_prestar')['status'],'ok')
        pending = session.export()
        self.assertEqual(pending['rng'], baseline['rng'])
        self.assertEqual(pending['narrative'],baseline['narrative'])
        self.assertEqual(send(session,'cancel_pending')['status'],'ok')
        self.assertEqual(session.export()['rng'],baseline['rng'])
        self.assertEqual(session.export()['narrative'],baseline['narrative'])
        # Reintentar consume exactamente el primer sorteo, no el segundo.
        self.assertEqual(send(session,'choose_prestar')['status'],'ok')
        self.assertEqual(send(session,'resolve_hab_01')['status'],'ok')
        number,_ = draw(RNGState(seed=SEED), 6)
        self.assertEqual(session.export()['narrative']['session_variables']['dado'],number)
        self.assertEqual(session.export()['rng']['counter'],1)

    def test_roll_pending_restores_and_commits_identically(self):
        admitted = admit_package(with_roll(self.base))
        original = new_session(admitted,seed=SEED)
        reach_choice(original)
        send(original,'choose_prestar')
        restored = restore_session(admitted,json.loads(json.dumps(original.export())))
        self.assertEqual(restored.observe(),original.observe())
        for s in (original,restored):
            self.assertEqual(send(s,'resolve_hab_02')['status'],'ok')
        self.assertEqual(restored.export(), original.export())
        self.assertEqual(original.export()['rng']['counter'],1)

    def test_reaction_conflict_after_roll_rolls_back_rng(self):
        pkg=with_roll(self.base)
        pkg['manifest']['variables'].append({'scope':'session','id':'choque',
                                             'type':'boolean','initial':False})
        pkg['initial_state']['session_variables']['choque']=False
        # Ambas reglas disparadas en la misma ronda intentan escribir el mismo campo.
        for index, v in enumerate((True,False)):
            pkg['rules'].append({'id':f'choque_{index}',
                'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                'effects':[{'op':'set',
                  'target':{'var':{'scope':'session','key':'choque'}},
                  'value':{'literal':v}}]})
        admitted=admit_package(pkg)
        session=new_session(admitted,seed=SEED)
        reach_choice(session)
        state=session.export()
        response=send(session,'choose_prestar')
        self.assertEqual(response['error']['code'],'REACTION_CONFLICT')
        self.assertEqual(session.export(), state)

    def test_two_rolls_on_same_target_conflict_without_consumption(self):
        pkg=with_roll(self.base)
        for name in ('a_roll','z_roll'):
            pkg['rules'].append({'id':name,
                'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                'effects':[{'op':'roll','sides':6,
                    'store':{'var':{'scope':'session','key':'dado'}}}]})
        admitted=admit_package(pkg)
        session=new_session(admitted,seed=SEED)
        reach_choice(session)
        state=session.export()
        response=send(session,'choose_prestar')
        self.assertEqual(response['error']['code'],'REACTION_CONFLICT')
        self.assertEqual(session.export(),state)

    def test_random_round_order_uses_rule_ids_not_file_order(self):
        pkg=copy.deepcopy(self.base)
        for key in ('dado_a','dado_z'):
            pkg['manifest']['variables'].append({'scope':'session','id':key,
                                                 'type':'integer','initial':0})
            pkg['initial_state']['session_variables'][key]=0
        for name,key in (('zeta','dado_z'),('alfa','dado_a')):
            pkg['rules'].append({'id':name,
                'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                'effects':[{'op':'roll','sides':17,
                    'store':{'var':{'scope':'session','key':key}}}]})
        reversed_pkg=copy.deepcopy(pkg)
        reversed_pkg['rules'].reverse()
        observed=[]
        for definition in (pkg,reversed_pkg):
            session=new_session(admit_package(definition),seed=SEED)
            reach_choice(session)
            send(session,'choose_prestar')
            # La reacción concede otra habilidad y suspende la transacción.
            send(session,'resolve_hab_01')
            snap=session.export()
            observed.append((snap['narrative']['session_variables']['dado_a'],
                             snap['narrative']['session_variables']['dado_z'],
                             snap['rng']['counter']))
        self.assertEqual(observed[0],observed[1])
        first,next_state=draw(RNGState(seed=SEED),17)
        second,_=draw(next_state,17)
        self.assertEqual(observed[0],(first,second,2))

    def test_roll_invalid_target_fails_without_rng_consumption(self):
        pkg=with_roll(self.base)
        # Se declara como booleano, pero el schema de operación roll exige tipo numérico.
        for var in pkg['manifest']['variables']:
            if var['id']=='dado': var['type']='boolean'; var['initial']=False
        pkg['initial_state']['session_variables']['dado']=False
        with self.assertRaises(ValueError):
            admit_package(pkg)


if __name__=='__main__':
    unittest.main()
