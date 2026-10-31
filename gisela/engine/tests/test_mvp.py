"""Pruebas de contratos observables, reacción, rollback y restauración."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import unittest
from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import new_session, restore_session, EngineFailure

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT/'gisela'/'packages'/'mvp_casete.package.json'


def submit(session, wanted=None):
    view=session.observe()
    options=[a for a in view['actions'] if a['enabled']]
    action=next((a for a in options if a['id']==wanted), options[0])
    return session.act({'session_id':view['session_id'], 'revision':view['revision'],
                        'action_id':action['action_id']})


def follow(session, choice='prestar'):
    for _ in range(16):
        if session.observe()['status']=='ended':return session
        response=submit(session,choice if session.observe()['content']['kind']=='choice' else None)
        if response['status']!='ok':raise AssertionError(response)
    raise AssertionError('El recorrido no terminó')


class MvpTest(unittest.TestCase):
    def test_ejemplo_documentacion_api(self):
        """El recorrido mínimo publicado admite, observa, actúa y restaura."""
        from pathlib import Path
        from gisela.contracts.admit_package import admit_package_file
        from gisela.engine.runtime import new_session, restore_session

        package = admit_package_file(Path('gisela/packages/mvp_casete.package.json'))
        session = new_session(package, session_id='ejemplo_documentacion', seed='0' * 64)
        view = session.observe()
        action = next(item for item in view['actions'] if item['enabled'])
        result = session.act({
            'session_id': view['session_id'],
            'revision': view['revision'],
            'action_id': action['action_id'],
        })
        self.assertEqual(result['status'], 'ok')
        restored = restore_session(package, session.export())
        self.assertEqual(restored.observe(), session.observe())

    @classmethod
    def setUpClass(cls):
        cls.admitted=admit_package_file(PACKAGE)

    def setUp(self):
        self.session=new_session(self.admitted)

    def test_admission_and_observe(self):
        view=self.session.observe()
        self.assertEqual(view['content']['kind'],'narrate')
        self.assertFalse(list(Validator().schemas['observe'].iter_errors(view)))
        self.assertEqual(self.session.export()['turn'],1)

    def test_both_endings(self):
        a=follow(new_session(self.admitted),'prestar')
        b=follow(new_session(self.admitted),'guardar')
        self.assertEqual(a.export()['ending'],'compartido')
        self.assertEqual(b.export()['ending'],'solo')
        self.assertTrue(a.export()['narrative']['session_variables']['gisela_reacciono'])
        self.assertFalse(b.export()['narrative']['session_variables']['gisela_reacciono'])
        self.assertEqual(a.export()['world']['objects'][0]['owner'],'gisela')
        self.assertEqual(b.export()['world']['objects'][0]['owner'],'alberto')
        self.assertEqual(len(a.export()['history']['facts']),1)
        self.assertEqual(len(b.export()['history']['facts']),0)
        self.assertEqual(len(a.export()['history']['trace']),1)
        self.assertEqual(len(a.export()['history']['executions']),2)

    def test_guardado_restaurado_equivalente(self):
        original=new_session(self.admitted)
        submit(original)
        saved=json.loads(json.dumps(original.export(),ensure_ascii=False))
        restored=restore_session(self.admitted,saved)
        self.assertEqual(restored.observe(),original.observe())
        follow(original,'prestar');follow(restored,'prestar')
        self.assertEqual(restored.export(),original.export())

    def test_export_defensive_copy(self):
        snap=self.session.export();snap['world']['objects'].clear()
        self.assertEqual(len(self.session.export()['world']['objects']),1)

    def test_stale_action_does_not_modify_session(self):
        saved=self.session.export()
        result=self.session.act({'session_id':'mvp_session','revision':0,'action_id':'advance'})
        self.assertEqual(result['error']['code'],'STALE_PROJECTION')
        self.assertEqual(self.session.export(),saved)

    def test_parameters_rejected(self):
        view=self.session.observe()
        result=self.session.act({'session_id':view['session_id'],'revision':view['revision'],
                                 'action_id':'advance','parameters':{'injected':1}})
        self.assertEqual(result['error']['code'],'INVALID_ACTION')

    def test_disabled_option_is_never_executed(self):
        s=new_session(self.admitted)
        submit(s);submit(s)
        self.assertEqual(s.observe()['content']['kind'],'choice')
        draft=s.export();draft['world']['objects'][0]['owner']='gisela'
        draft['world_revision']+=1;draft['revision']+=1
        s=restore_session(self.admitted,draft)
        snap=s.export()
        self.assertFalse(next(a for a in s.observe()['actions'] if a['id']=='prestar')['enabled'])
        result=s.act({'session_id':snap['session_id'],'revision':snap['revision'],
                      'action_id':'choose_prestar'})
        self.assertEqual(result['error']['code'],'INVALID_ACTION')
        self.assertEqual(s.export(),snap)

    def test_tampered_digest_rejected(self):
        draft=self.session.export();draft['package_digest']='0'*64
        with self.assertRaises(EngineFailure) as error:
            restore_session(self.admitted,draft)
        self.assertEqual(error.exception.code,'RESTORE_MISMATCH')

    def test_unsupported_step_rejected(self):
        obj=self.admitted.materialize()
        obj['nodes'][0]['steps'].insert(0, {'id':'preparacion','op':'prepare_hand'})
        admitted=admit_package(obj)
        with self.assertRaises(EngineFailure) as failure:
            new_session(admitted)
        self.assertEqual(failure.exception.code,'UNSUPPORTED_FORMAT')

    def test_reactive_conflict_rolls_back(self):
        obj=self.admitted.materialize()
        obj['rules'].append({'id':'segunda_reaccion','trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                             'effects':[{'op':'set','target':{'var':{'scope':'session','key':'gisela_reacciono'}},
                                         'value':{'literal':False}}]})
        admitted=admit_package(obj)
        s=new_session(admitted)
        submit(s);submit(s)
        before=s.export()
        result=submit(s,'prestar')
        self.assertEqual(result['error']['code'],'REACTION_CONFLICT')
        self.assertEqual(s.export(),before)

    def test_reactive_cycle_rolls_back(self):
        obj=self.admitted.materialize()
        obj['manifest']['variables'].append({'scope':'session','id':'vuelta','type':'integer','initial':0})
        obj['initial_state']['session_variables']['vuelta']=0
        obj['rules'].append({'id':'repetir_hecho','trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                             'effects':[{'op':'record_fact','fact':'alberto_presto_casete'}]})
        admitted=admit_package(obj)
        s=new_session(admitted)
        submit(s);submit(s)
        before=s.export();r=submit(s,'prestar')
        self.assertIn(r['error']['code'],('REACTION_CYCLE','BUDGET_EXCEEDED'))
        self.assertEqual(s.export(),before)

    def test_result_matches_contract(self):
        view=self.session.observe()
        result=submit(self.session)
        v=Validator().schemas['result']
        self.assertFalse(list(v.iter_errors(result)))
        err=self.session.act({'session_id':'mvp_session','revision':0,'action_id':'advance'})
        self.assertFalse(list(v.iter_errors(err)))

    def test_saved_states_semantically_valid(self):
        s=new_session(self.admitted)
        for _ in range(8):
            issues=Validator().validate_session(s.export(), self.admitted.materialize())
            self.assertFalse([i for i in issues if i.severity=='error'],issues)
            if s.observe()['status']=='ended':break
            submit(s,'prestar' if s.observe()['content']['kind']=='choice' else None)

    def test_another_package_is_not_accepted_for_restore(self):
        obj=self.admitted.materialize();obj['manifest']['id']='otro_paquete'
        different=admit_package(obj)
        with self.assertRaises(EngineFailure):restore_session(different,self.session.export())

    def test_observe_is_read_only_and_independent(self):
        before=self.session.export()
        v=self.session.observe()
        v['content']['text']='texto_manipulado'
        v['actions'][0]['enabled']=False
        self.assertEqual(self.session.export(),before)
        self.assertNotEqual(self.session.observe()['content']['text'],'texto_manipulado')
        self.assertTrue(self.session.observe()['actions'][0]['enabled'])

    def test_unknown_action_does_not_modify_world(self):
        before=self.session.export()
        request={'session_id':'mvp_session','revision':1,'action_id':'choose_prestar'}
        response=self.session.act(request)
        self.assertEqual(response['error']['code'],'INVALID_ACTION')
        self.assertEqual(self.session.export(),before)

    def test_invalid_json_act_does_not_modify_world(self):
        before=self.session.export()
        response=self.session.act({'session_id':'mvp_session','revision':True,'action_id':'advance'})
        self.assertEqual(response['error']['code'],'INVALID_ACTION')
        self.assertEqual(self.session.export(),before)

    def test_rules_observe_the_same_base_in_a_round(self):
        package=self.admitted.materialize()
        package['manifest']['variables'].append({'scope':'session','id':'otra_reaccion','type':'boolean','initial':False})
        package['initial_state']['session_variables']['otra_reaccion']=False
        package['rules'].append({'id':'observa_el_estado_inicial',
            'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
            'when':{'compare':{
                'left':{'var':{'scope':'session','key':'gisela_reacciono'}},
                'op':'eq','right':{'literal':False}}},
            'effects':[{'op':'set','target':{'var':{'scope':'session','key':'otra_reaccion'}},
                        'value':{'literal':True}}]})
        s=follow(new_session(admit_package(package)))
        self.assertTrue(s.export()['narrative']['session_variables']['otra_reaccion'])
        self.assertEqual(len(s.export()['history']['trace']),2)

    def test_no_op_does_not_produce_state_changed(self):
        package=self.admitted.materialize()
        package['manifest']['variables'].append({'scope':'session','id':'efecto_fantasma','type':'boolean','initial':False})
        package['initial_state']['session_variables']['efecto_fantasma']=False
        package['rules'].append({'id':'cambio_variable',
            'trigger':{'on':'state_changed','target':{'var':{'scope':'session','key':'casete_prestado'}}},
            'effects':[{'op':'set','target':{'var':{'scope':'session','key':'efecto_fantasma'}},
                        'value':{'literal':True}}]})
        option=package['nodes'][0]['steps'][3]['options'][1]
        option['effects']=[{'op':'set','target':{'var':{'scope':'session','key':'casete_prestado'}},
                            'value':{'literal':False}}]
        s=follow(new_session(admit_package(package)),'guardar')
        self.assertFalse(s.export()['narrative']['session_variables']['efecto_fantasma'])
        self.assertFalse(s.export()['history']['trace'])

    def test_invalid_cursor_fails_restoration(self):
        s=self.session.export()
        s['cursor']['step']='paso_inexistente'
        with self.assertRaises(EngineFailure):restore_session(self.admitted,s)

    def test_repeat_node_counts_new_turn(self):
        package=self.admitted.materialize()
        package['nodes'][1]['steps'][0]={'id':'regresar','op':'transition','next':{'node':'inicio'}}
        s=new_session(admit_package(package))
        for _ in range(8):
            if s.export()['turn'] == 3: break
            view=s.observe()
            action='prestar' if view['content']['kind']=='choice' else None
            self.assertEqual(submit(s,action)['status'],'ok')
        self.assertEqual(s.export()['turn'],3)
        self.assertEqual(s.export()['cursor']['node'],'inicio')
        self.assertEqual(len(s.export()['history']['executions']),3)
        self.assertTrue(s.export()['history']['executions'][0]['completed'])
        self.assertTrue(s.export()['history']['executions'][1]['completed'])
        self.assertFalse(s.export()['history']['executions'][2]['completed'])


if __name__=='__main__':unittest.main()
