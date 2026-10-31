"""E3: suspensión determinista y confirmación diferida de resultados DICE."""
from __future__ import annotations
import copy
import json
import unittest

from gisela.contracts.admit_package import admit_package
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.errors import EngineFailure
from gisela.engine.authorized_gateway import ExecutionGateway, Principal, GatewayError
from gisela.engine.tests.test_e2_evaluations import (
    fixture, evaluate, simple_node, fact, send, character, catalog, pending_game, set_result)


def v15(pkg, presentation='visible'):
    pkg['manifest']['format_version'] = '1.5'
    evaluate(pkg)['presentation'] = presentation
    return pkg


def from_choice(presentation='visible'):
    pkg = v15(fixture(), presentation)
    spec = pkg['nodes'][0]['steps'].pop(0)['evaluation']
    pkg['nodes'][0]['steps'] = [{'id':'elegir','op':'choice','options':[
        {'id':'intentar','label':{'text':'Intentar'},'evaluation':spec}]},
        {'id':'despues','op':'narrate','text':{'text':'Después'}}]
    return pkg


def from_scene(element=False):
    pkg = v15(fixture())
    spec = evaluate(pkg)
    pkg['manifest']['entry'] = {'scene':'taller'}
    action={'id':'trabajar','label':{'text':'Trabajar'},'evaluation':spec}
    if element:
        pkg['scenes'] = [{'id':'taller','title':{'text':'Taller'},'elements':[
            {'id':'mesa','label':{'text':'Mesa'},'actions':[action]}]}]
    else:
        pkg['scenes'] = [{'id':'taller','title':{'text':'Taller'},'actions':[action]}]
    return pkg


class E3Visible(unittest.TestCase):
    def test_01_entry_pending_no_world_or_turn_and_restore(self):
        pkg = v15(simple_node(fixture()))
        adm = admit_package(pkg)
        s = new_session(adm,seed='a'*64)
        p=s.export()
        self.assertEqual(p['turn'],0)
        self.assertEqual(p['world_revision'],0)
        self.assertEqual(p['rng']['counter'],2)
        self.assertEqual(p['history']['facts'],[])
        self.assertEqual(p['status'],'preparing')
        self.assertNotIn('cursor',p)
        self.assertEqual(s.observe()['content']['kind'],'pending_evaluation')
        self.assertNotIn('total',s.observe()['content'])
        self.assertNotIn('base',json.dumps(s.observe()))
        restored=restore_session(adm,p)
        self.assertEqual(restored.export(),p)
        self.assertEqual(send(s,'continue_evaluation'),send(restored,'continue_evaluation'))
        self.assertEqual(s.export(),restored.export())

    def test_02_acknowledged_same_command_and_no_automatic_commit(self):
        pkg=v15(simple_node(fixture('deterministic')),'acknowledged')
        s=new_session(admit_package(pkg))
        self.assertEqual(s.observe()['content']['presentation'],'acknowledged')
        self.assertEqual(s.export()['rng']['counter'],0)
        self.assertEqual(len(s.export()['history']['facts']),0)
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')

    def test_03_choice_uncommitted_before_continue(self):
        s=new_session(admit_package(from_choice()))
        before=s.export()
        self.assertEqual(send(s,'choose_intentar')['status'],'ok')
        p=s.export()
        self.assertEqual(p['history']['executions'],before['history']['executions'])
        self.assertEqual(p['world_revision'],before['world_revision'])
        self.assertEqual(p['turn'],before['turn'])
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        self.assertEqual(len(s.export()['history']['executions'][0]['selected_options']),1)

    def test_04_scene_and_element_routes(self):
        for element in (False,True):
            with self.subTest(element=element):
                a=admit_package(from_scene(element))
                s=new_session(a)
                self.assertEqual(send(s,'interact_1_0' if element else 'interact_0_0')['status'],'ok')
                self.assertEqual(s.export()['history']['trace'],[])
                self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
                trace=s.export()['history']['trace']
                self.assertEqual(len(trace),1)
                self.assertEqual('element' in trace[0]['detail'],element)

    def test_05_effects_before_visible_remain_uncommitted(self):
        pkg=v15(simple_node(fixture()))
        pkg['nodes'][0]['steps'].insert(0, {'id':'antes','op':'effect','effects':[
            {'op':'record_fact','fact':'maquina_reparada'}]})
        s=new_session(admit_package(pkg))
        self.assertEqual(s.export()['history']['facts'],[])
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        self.assertIn('maquina_reparada',[x['fact'] for x in s.export()['history']['facts']])

    def test_06_visible_chain_replays_both_without_partial_world(self):
        pkg=v15(simple_node(fixture()))
        other=copy.deepcopy(pkg['nodes'][0]['steps'][0]);other['id']='second'
        pkg['nodes'][0]['steps'].insert(1,other)
        adm=admit_package(pkg)
        s=new_session(adm)
        one=s.export();self.assertEqual(len(one['pending_evaluation']['fixed']),1)
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        two=s.export()
        self.assertEqual(len(two['pending_evaluation']['fixed']),2)
        self.assertEqual(two['history']['facts'],[])
        self.assertEqual(two['world_revision'],0)
        self.assertEqual(two['turn'],0)
        self.assertEqual(two['rng']['counter'],4)
        re=restore_session(adm,two)
        self.assertEqual(send(re,'continue_evaluation')['status'],'ok')
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        self.assertEqual(s.export(),re.export())
        self.assertEqual(s.export()['rng']['counter'],4)

    def test_07_auxiliary_after_fixed_does_not_reroll(self):
        pkg=pending_game();pkg['manifest']['format_version']='1.5'
        spec=pkg['nodes'][0]['steps'][2]['options'][0]['evaluation']
        spec['presentation']='visible'
        adm=admit_package(pkg)
        s=new_session(adm,seed='2'*64)
        self.assertEqual(send(s,'advance')['status'],'ok')
        self.assertEqual(send(s,'choose_prestar')['status'],'ok')
        rng=s.export()['rng']
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        p=s.export()
        self.assertIn('auxiliary_request',p['pending_evaluation'])
        self.assertEqual(p['rng'],rng)
        self.assertEqual(len(p['pending_evaluation']['fixed']),1)
        restored=restore_session(adm,p)
        self.assertEqual(send(restored,'resolve_hab_01')['status'],'ok')
        self.assertEqual(send(s,'resolve_hab_01')['status'],'ok')
        self.assertEqual(restored.export(),s.export())
        self.assertEqual(s.export()['rng'],rng)

    def test_08_preflight_failure_before_roll(self):
        pkg=v15(catalog(fixture(),amount=100,slot='difficulty'))
        set_result(pkg,base=1,difficulty=1000000)
        pkg['nodes'][0]['steps'].insert(0, {'id':'inicio','op':'narrate','text':{'text':'Inicio'}})
        s=new_session(admit_package(pkg));before=s.export()
        self.assertEqual(send(s,'advance')['status'],'error')
        self.assertEqual(s.export(),before)

    def test_09_reject_stale_foreign_and_unoffered(self):
        s=new_session(admit_package(v15(simple_node(fixture()))))
        old=s.observe()
        for key in ('advance','cancel_pending','choose_fake'):
            self.assertEqual(send(s,key)['error']['code'],'INVALID_ACTION')
        self.assertEqual(s.observe(),old)
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        self.assertEqual(s.act({'session_id':old['session_id'],'revision':old['revision'],
            'action_id':'continue_evaluation'})['error']['code'],'STALE_PROJECTION')

    def test_10_restore_rejects_forged_result_and_rng(self):
        adm=admit_package(v15(simple_node(fixture())))
        s=new_session(adm)
        for change in ('result','rng','source','fixed','id'):
            p=s.export()
            if change=='result':p['pending_evaluation']['fixed'][-1]['result']['outcome']='exito'
            if change=='rng':p['rng']['counter']+=1
            if change=='source':p['pending_evaluation']['source']['kind']='session_start';p['pending_evaluation']['source']['fake']='extra'
            if change=='fixed':p['pending_evaluation']['fixed'][0]['rng_before']['counter']=4
            if change=='id':p['pending_evaluation']['evaluation_id']='bad'
            with self.subTest(change=change),self.assertRaises(EngineFailure):
                restore_session(adm,p)

    def test_11_traits_and_sofia_opaque(self):
        pkg=v15(catalog(simple_node(fixture())))
        evaluate(pkg)['inputs']={'base':{'stat':{'character':'tecnico',
            'name':'intelligence','component':'effective'}}}
        s=new_session(admit_package(pkg))
        v=json.dumps(s.observe())
        for word in ('experto','intelligence','bonus','tecnico'):
            self.assertNotIn(word,v)
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')

    def test_12_gateway_nonhuman_idempotent(self):
        a=admit_package(from_choice())
        session=new_session(a)
        principal=Principal('bot',frozenset({'act','observe_player'}))
        g=ExecutionGateway(session,{'bot':principal})
        client=g.bind('bot')
        v=client.observe()
        req={'session_id':v['session_id'],'revision':v['revision'],'action_id':'choose_intentar'}
        first=client.act(req,'command_one')
        self.assertEqual(first['status'],'ok')
        self.assertEqual(client.act(req,'command_one'),first)
        self.assertEqual(client.act(req,'command_two')['error']['code'],'STALE_PROJECTION')
        v=client.observe();req={'session_id':v['session_id'],'revision':v['revision'],'action_id':'continue_evaluation'}
        success=client.act(req,'command_three')
        self.assertEqual(success['status'],'ok')
        self.assertEqual(client.act(req,'command_three'),success)
        with self.assertRaises(GatewayError):g.bind('intruso')

    def test_13_v14_still_rejects_visible(self):
        pkg=fixture();evaluate(pkg)['presentation']='visible'
        with self.assertRaises(EngineFailure):new_session(admit_package(pkg))

    def test_14_schema_snapshot_and_observe(self):
        s=new_session(admit_package(v15(simple_node(fixture()))))
        v=Validator();v.use_version('1.5')
        self.assertEqual(list(v.schemas['session'].iter_errors(s.export())),[])
        self.assertEqual(list(v.schemas['observe'].iter_errors(s.observe())),[])
        self.assertEqual(list(v.schemas['act'].iter_errors({'session_id':'mvp_session',
            'revision':s.export()['revision'],'action_id':'continue_evaluation'})),[])

    def test_15_branch_error_preserves_pending_and_rng(self):
        pkg=v15(character(fixture('deterministic')))
        set_result(pkg,base=12)
        pkg['cards'].append({'id':'pieza','kind':'object','title':{'text':'Pieza'}})
        pkg['initial_state']['characters'].append({'id':'receptor','card':'tecnico',
            'location':'taller','status':{}})
        pkg['initial_state']['objects']=[{'id':'pieza_01','card':'pieza','owner':'tecnico'}]
        fact(pkg)['effects'].append({'op':'transfer','object':'pieza_01',
                                     'from':'receptor','to':'tecnico'})
        s=new_session(admit_package(pkg))
        before=s.export()
        self.assertEqual(send(s,'continue_evaluation')['status'],'error')
        self.assertEqual(s.export(),before)
        self.assertEqual(s.observe()['content']['kind'],'pending_evaluation')

    def test_16_hidden_before_visible_and_between_results(self):
        pkg=v15(simple_node(fixture()))
        hidden=copy.deepcopy(pkg['nodes'][0]['steps'][0]);hidden['id']='hidden'
        hidden['evaluation']['presentation']='hidden'
        pkg['nodes'][0]['steps'].insert(0,hidden)
        extra=copy.deepcopy(hidden);extra['id']='hidden_between'
        pkg['nodes'][0]['steps'].insert(2,extra)
        second=copy.deepcopy(pkg['nodes'][0]['steps'][1]);second['id']='visible_second'
        pkg['nodes'][0]['steps'].insert(3,second)
        admitted=admit_package(pkg)
        s=new_session(admitted)
        self.assertEqual(s.export()['rng']['counter'],4)
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        self.assertEqual(s.export()['rng']['counter'],8)
        restored=restore_session(admitted,s.export())
        self.assertEqual(send(s,'continue_evaluation')['status'],'ok')
        self.assertEqual(send(restored,'continue_evaluation')['status'],'ok')
        self.assertEqual(s.export(),restored.export())
        self.assertEqual(s.export()['rng']['counter'],8)

    def test_17_mary_applied_once_after_continue(self):
        pkg=v15(simple_node(fixture('deterministic')))
        set_result(pkg,base=12)
        pkg['manifest']['facts'].append('objetivo_cumplido')
        pkg['mary']={'objectives':[{'id':'tarea','mode':'milestone',
            'visibility':'hidden','criterion':{'kind':'condition',
                'when':{'has_fact':'maquina_reparada'}},
            'yield':{'fact':'objetivo_cumplido'}}], 'missions':[]}
        admitted=admit_package(pkg)
        session=new_session(admitted)
        self.assertEqual(session.export()['history']['facts'],[])
        req=session.observe()
        self.assertEqual(send(session,'continue_evaluation')['status'],'ok')
        self.assertEqual(len(session.export()['history']['facts']),2)
        old={'session_id':req['session_id'],'revision':req['revision'],
             'action_id':'continue_evaluation'}
        self.assertEqual(session.act(old)['error']['code'],'STALE_PROJECTION')
        self.assertEqual(len(session.export()['history']['facts']),2)

    def test_18_restore_rejects_forged_auxiliary_offer(self):
        pkg=pending_game();pkg['manifest']['format_version']='1.5'
        pkg['nodes'][0]['steps'][2]['options'][0]['evaluation']['presentation']='visible'
        admitted=admit_package(pkg)
        s=new_session(admitted,seed='2'*64)
        send(s,'advance');send(s,'choose_prestar');send(s,'continue_evaluation')
        p=s.export()
        self.assertIn('auxiliary_request',p['pending_evaluation'])
        p['pending_evaluation']['auxiliary_request']['options']=['inventado']
        with self.assertRaises(EngineFailure):restore_session(admitted,p)

    def test_19_transition_to_another_node_remains_atomic(self):
        pkg=v15(character(fixture('deterministic')))
        set_result(pkg,base=12)
        fact(pkg)['next']={'node':'otro'}
        pkg['cards'].append({'id':'pieza','kind':'object','title':{'text':'Pieza'}})
        pkg['initial_state']['characters'].append({'id':'receptor','card':'tecnico',
            'location':'taller','status':{}})
        pkg['initial_state']['objects']=[{'id':'pieza_01','card':'pieza','owner':'tecnico'}]
        pkg['nodes'].append({'id':'otro','steps':[{'id':'fallo','op':'effect',
            'effects':[{'op':'transfer','object':'pieza_01','from':'receptor','to':'tecnico'}]},
            {'id':'salida','op':'narrate','text':{'text':'Salida'}}]})
        session=new_session(admit_package(pkg))
        before=session.export()
        self.assertEqual(send(session,'continue_evaluation')['status'],'error')
        self.assertEqual(session.export(),before)
        self.assertEqual(session.export()['turn'],0)

    def test_20_restore_requires_exact_package_digest(self):
        pkg=v15(simple_node(fixture()))
        admitted=admit_package(pkg);s=new_session(admitted)
        other=copy.deepcopy(pkg)
        other['nodes'][0]['steps'][-1]['text']['text']='No es el mismo paquete'
        with self.assertRaises(EngineFailure):
            restore_session(admit_package(other),s.export())


    def test_21_checkpoint_gateway_recovers_frozen_result_and_receipt(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from gisela.engine.checkpoint_store import JsonCheckpointStore
        adm=admit_package(from_choice())
        principal=Principal('servicio',frozenset({'act','observe_player'}))
        with TemporaryDirectory() as folder:
            path=Path(folder)/'session.json'
            g=ExecutionGateway(new_session(adm),{'servicio':principal},
                               store=JsonCheckpointStore(path))
            client=g.bind('servicio')
            view=client.observe()
            cmd={'session_id':view['session_id'],'revision':view['revision'],
                 'action_id':'choose_intentar'}
            response=client.act(cmd,'prepare')
            self.assertEqual(response['status'],'ok')
            fixed=client.observe()['content']
            g.close()
            g2=ExecutionGateway(new_session(adm),{'servicio':principal},
                                store=JsonCheckpointStore(path))
            client=g2.bind('servicio')
            self.assertEqual(client.observe()['content'],fixed)
            self.assertEqual(client.act(cmd,'prepare'),response)
            view=client.observe()
            continuation={'session_id':view['session_id'],'revision':view['revision'],
                          'action_id':'continue_evaluation'}
            self.assertEqual(client.act(continuation,'continue')['status'],'ok')
            self.assertEqual(client.act(continuation,'continue')['status'],'ok')
            g2.close()

    def test_22_v15_hidden_retains_single_atomic_commit(self):
        pkg=simple_node(fixture())
        pkg['manifest']['format_version']='1.5'
        pkg['nodes'][0]['steps'][0]['evaluation']['presentation']='hidden'
        admitted=admit_package(pkg)
        session=new_session(admitted)
        self.assertNotIn('pending_evaluation',session.export())
        self.assertEqual(session.export()['rng']['counter'],2)
        self.assertEqual(session.export()['turn'],1)
        self.assertEqual(session.observe()['content']['kind'],'narrate')
        self.assertEqual(session.export(),restore_session(admitted,session.export()).export())


if __name__=='__main__':unittest.main()
