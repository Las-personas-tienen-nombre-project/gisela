#!/usr/bin/env python3
"""Schema-level regression tests; this is not an implementation of GISELA."""
import copy
import json
import pathlib
import unittest
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

R=pathlib.Path(__file__).parent
S={p.name.removesuffix('.schema.json'):json.loads(p.read_text(encoding='utf8')) for p in R.glob('*.schema.json')}
registry=Registry().with_resources((s['$id'],Resource.from_contents(s)) for s in S.values())
V={name:Draft202012Validator(s,registry=registry,format_checker=FormatChecker()) for name,s in S.items()}
FIX=json.loads((R/'example.package.json').read_text(encoding='utf8'))

def session(status='exploring'):
 i=FIX['initial_state']
 world={k:copy.deepcopy(i.get(k,[] if k!='world_variables' else {})) for k in ['locations','characters','objects','skills','effects','capacities','relationships','world_variables']}
 out={
 'schema_version':'1.2','package_id':FIX['manifest']['id'],'package_digest':'a'*64,
 'session_id':'test_session','revision':2,'world_revision':1,'turn':1,
 'status':status,'world_time':i['world_time'],
 'rng':{'algorithm':'sha256_counter_v1','seed':'b'*64,'counter':0},
 'identity':{'used_instance_ids':['porteria','alberto','gisela','casete_01','intuicion_01'],'next_sequence':1},
 'world':world,'narrative':{'session_variables':i['session_variables']},
 'history':{'facts':[],'executions':[],'trace':[]}
 }
 if status=='exploring':out['current_scene']='porteria_noche'
 if status=='preparing':out['preparing_for']='inicio'
 if status=='node':
  out['cursor']={'node':'inicio','step':'decision','execution_id':'execution_01'}
  out['history']['executions']=[{'execution_id':'execution_01','node':'inicio','turn':1,
      'started_at':i['world_time'],'completed':False}]
 if status=='ended':out['ending']='final_positivo'
 return out

def pending():
 return {
  'origin':'voluntary',
  'source':{'kind':'scene_action','scene':'porteria_noche','action':'examinar'},
  'initiated_revision':1,
  'context':{'$actor':'alberto','$target':'gisela'},
  'answers':[{'request_id':'descarte_01','option_id':'intuicion_01'}],
  'request':{'request_id':'descarte_02','kind':'select_one','purpose':'discard_skill','options':['intuicion_01']}
 }

def view(kind='choice',status='node'):
 out={'session_id':'test_session','revision':2,'world_revision':1,'world_time':FIX['initial_state']['world_time'],
      'turn':1,'status':status,'content':{'kind':kind},'actions':[]}
 if status=='exploring':out['scene']='porteria_noche'
 if kind=='pending_transaction':out['content'].update({'request_id':'descarte_02','purpose':'discard_skill'})
 if kind=='ending':out['content']['ending']='final_positivo'
 if kind=='dialogue':out['content'].update({'speaker':'gisela','text':'Hola'})
 if kind=='narrate':out['content']['text']='Había dos guardias.'
 return out

def action(kind='choose'):
 return {'kind':kind,'action_id':kind+'_01','id':'elige_01','label':'Continuar','enabled':True}

class SchemaContracts(unittest.TestCase):
 def good(self,name,item):
  errs=list(V[name].iter_errors(item));self.assertFalse(errs,f'{name}: '+ '; '.join(e.message for e in errs[:2]))
 def bad(self,name,item):
  self.assertFalse(V[name].is_valid(item),f'{name}: invalid fixture was accepted')
 def test_metaschemas(self):
  self.assertEqual(len(S),13)
  for spec in S.values():Draft202012Validator.check_schema(spec)
 def test_package_fixture(self):self.good('package',FIX)
 def test_package_legacy_version_rejected(self):
  d=copy.deepcopy(FIX);d['manifest']['format_version']='1.0';self.bad('package',d)
 def test_unknown_operator_rejected(self):
  d=copy.deepcopy(FIX);d['nodes'][0]['steps'][0]['op']='python';self.bad('package',d)
 def test_implicit_first_by_id_rejected(self):
  data={'query':{'kind':'character','where':{'constant':True},'selection':'one','on_multiple':'first_by_id'}}
  self.bad('package',self.with_scene_query(data))
 def with_scene_query(self,q):
  d=copy.deepcopy(FIX);d['scenes'][0]['actors'][0]['character']=q;return d
 def test_expiration_all_differed(self):
  d=copy.deepcopy(FIX)
  e=next(x for x in d['cards'] if x['kind']=='effect');e['expiration']['mode']='all';self.bad('package',d)
 def test_literal_objects_not_operations(self):
  d=copy.deepcopy(FIX);d['nodes'][0]['steps'].append({'id':'unsafe','op':'condition','test':{'compare':{
   'left':{'literal':{'op':'python'}},'op':'eq','right':{'literal':'x'}}}});self.bad('package',d)
 def test_states_valid(self):
  for s in ['preparing','node','exploring','ended']:
   with self.subTest(s=s):self.good('session',session(s))
 def test_node_requires_cursor(self):
  d=session('node');d.pop('cursor');self.bad('session',d)
 def test_exploring_requires_scene(self):
  d=session();d.pop('current_scene');self.bad('session',d)
 def test_ended_requires_ending(self):
  d=session('ended');d.pop('ending');self.bad('session',d)
 def test_preparing_requires_preparing_for(self):
  d=session('preparing');d.pop('preparing_for');self.bad('session',d)
 def test_exploring_forbids_cursor(self):
  d=session();d['cursor']={'node':'inicio','step':'decision','execution_id':'execution_01'};self.bad('session',d)
 def test_ended_forbids_pending(self):
  d=session('ended');d['pending_transaction']=pending();self.bad('session',d)
 def test_pending_is_allowed_and_structural(self):
  d=session();d['pending_transaction']=pending();self.good('session',d)
 def test_pending_on_node(self):
  d=session('node');d['pending_transaction']=pending();self.good('session',d)
 def test_pending_without_context_rejected(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction'].pop('context');self.bad('session',d)
 def test_pending_without_answers_rejected(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction'].pop('answers');self.bad('session',d)
 def test_pending_without_request_rejected(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction'].pop('request');self.bad('session',d)
 def test_pending_empty_candidates_rejected(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction']['request']['options']=[];self.bad('session',d)
 def test_pending_duplicate_candidates_rejected(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction']['request']['options']=['a','a'];self.bad('session',d)
 def test_pending_draft_world_rejected(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction']['draft_world']={};self.bad('session',d)
 def test_pending_source_discriminated(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction']['source']={'kind':'scene_action','node':'inicio'};self.bad('session',d)
 def test_pending_context_cannot_be_query(self):
  d=session();d['pending_transaction']=pending();d['pending_transaction']['context']['$actor']={'query':{}};self.bad('session',d)
 def test_nonunique_allocated_ids_rejected(self):
  d=session();d['identity']['used_instance_ids']=['alberto','alberto'];self.bad('session',d)
 def test_rng_format_bounded(self):
  d=session();d['rng']['seed']='not_hex';self.bad('session',d)
 def test_completed_requires_timestamp(self):
  d=session('node');d['history']['executions'][0]['completed']=True;self.bad('session',d)
 def test_incomplete_forbids_timestamp(self):
  d=session('node');d['history']['executions'][0]['completed_at']=FIX['initial_state']['world_time'];self.bad('session',d)
 def test_choice_without_prompt_is_valid(self):self.good('observe',view())
 def test_embedded_choice_options_rejected(self):
  d=view();d['content']['options']=[action()];self.bad('observe',d)
 def test_pending_view_actions(self):
  d=view('pending_transaction','exploring');d['actions']=[action('resolve_pending'),action('cancel_pending')];self.good('observe',d)
 def test_pending_view_rejects_normal_actions(self):
  d=view('pending_transaction','exploring');d['actions']=[action('choose')];self.bad('observe',d)
 def test_pending_view_requires_some_action(self):
  d=view('pending_transaction','exploring');self.bad('observe',d)
 def test_normal_view_rejects_pending_actions(self):
  d=view();d['actions']=[action('resolve_pending')];self.bad('observe',d)
 def test_exploring_view_requires_scene(self):
  d=view('exploring','exploring');d.pop('scene');self.bad('observe',d)
 def test_exploring_view_requires_exploring_content(self):
  d=view('choice','exploring');self.bad('observe',d)
 def test_ended_view_no_actions(self):
  d=view('ending','ended');self.good('observe',d);d['actions']=[action('choose')];self.bad('observe',d)
 def test_act_valid(self):self.good('act',{'session_id':'test_session','revision':2,'action_id':'choose_01'})
 def test_act_rejects_arbitrary_ops(self):
  d={'session_id':'test_session','revision':2,'action_id':'choose_01','parameters':{'danger':{'op':'grant_skill'}}};self.bad('act',d)
 def test_result_ok_and_error(self):
  d={'status':'ok','revision':2,'view':view()};self.good('result',d)
  self.good('result',{'status':'error','revision':2,'error':{'code':'STALE_PROJECTION','message':'Old revision'}})
 def test_errors_cannot_embed_draft_state(self):
  d={'status':'error','revision':2,'error':{'code':'INVALID_STATE','message':'x','detail':{'draft_world':{'secret':1}}}};self.bad('result',d)

if __name__=='__main__':unittest.main(verbosity=2)
