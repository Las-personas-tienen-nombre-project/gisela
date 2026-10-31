#!/usr/bin/env python3
"""Regresiones semánticas: sin ejecutar el motor ni reacciones."""
import copy
import json
from pathlib import Path
import unittest

from canonical import package_digest
from semantic_validator import Validator, load_json_strict

ROOT=Path(__file__).parent
BASE=json.loads((ROOT/'example.package.json').read_text(encoding='utf8'))
NODE=json.loads((ROOT/'examples/session_node.json').read_text(encoding='utf8'))
EXPLORE=json.loads((ROOT/'examples/session_exploring.json').read_text(encoding='utf8'))


def check(pkg=BASE,session=None,digest=None):
    engine=Validator()
    return engine.validate_package(pkg) if session is None else engine.validate_session(session,pkg,digest)


def mutate(fn,pkg=BASE):
    result=copy.deepcopy(pkg);fn(result);return result


class SemanticContracts(unittest.TestCase):
    def assertCode(self,issues,code):
        self.assertIn(code,{d.code for d in issues},'Se esperaba '+code+'; obtenido: '+str(issues))
    def assertClean(self,issues):
        self.assertFalse([x for x in issues if x.severity=='error'],issues)
    def test_fixture_package(self):self.assertClean(check())
    def test_duplicate_node(self):
        p=mutate(lambda p:p['nodes'].append(copy.deepcopy(p['nodes'][0])))
        self.assertCode(check(p),'DUPLICATE_ID')
    def test_duplicate_step(self):
        p=mutate(lambda p:p['nodes'][0]['steps'].append(copy.deepcopy(p['nodes'][0]['steps'][0])))
        self.assertCode(check(p),'DUPLICATE_ID')
    def test_duplicate_option(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'].append(copy.deepcopy(p['nodes'][0]['steps'][2]['options'][0])))
        self.assertCode(check(p),'DUPLICATE_ID')
    def test_duplicate_instance_different_kinds(self):
        p=mutate(lambda p:p['initial_state']['objects'][0].update(id='gisela'))
        self.assertCode(check(p),'DUPLICATE_INSTANCE')
    def test_wrong_card_kind(self):
        p=mutate(lambda p:p['initial_state']['objects'][0].update(card='gisela'))
        self.assertCode(check(p),'UNKNOWN_CARD')
    def test_wrong_owner(self):
        p=mutate(lambda p:p['initial_state']['objects'][0].update(owner='porteria'))
        self.assertCode(check(p),'INVALID_OWNER')
    def test_unknown_location(self):
        p=mutate(lambda p:p['initial_state']['characters'][0].update(location='pasillo'))
        self.assertCode(check(p),'UNKNOWN_LOCATION')
    def test_unknown_scene(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][0].update(scene='inventada'))
        self.assertCode(check(p),'UNKNOWN_SCENE')
    def test_unknown_ending(self):
        p=mutate(lambda p:p['nodes'][1]['steps'][0].update(ending='desconocido'))
        self.assertCode(check(p),'UNKNOWN_ENDING')
    def test_invalid_step_target(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][4].update(next={'step':'otro_nodo'}))
        self.assertCode(check(p),'UNKNOWN_STEP')
    def test_invalid_node_target(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][6].update(then={'node':'inventado'}))
        self.assertCode(check(p),'UNKNOWN_NODE')
    def test_unknown_fact(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'][0]['effects'][1].update(fact='fantasma'))
        self.assertCode(check(p),'UNKNOWN_FACT')
    def test_transferring_character_as_object(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'][0]['effects'][0].update(object='gisela'))
        self.assertCode(check(p),'WRONG_ENTITY_KIND')
    def test_query_candidate_context_allowed(self):
        def change(p):
            p['scenes'][0]['actors'][0]['character']={'query':{'kind':'character','selection':'one',
                'where':{'at_location':{'character':'$candidate','location':'porteria'}}}}
        self.assertClean(check(mutate(change)))
    def test_exists_plural_query_allowed(self):
        def change(p):
            p['nodes'][0]['steps'][6]['test']={'exists':{'query':{'kind':'object','selection':'all',
                'where':{'constant':True}}}}
        self.assertClean(check(mutate(change)))
    def test_plural_query_disallowed_as_singular_speaker(self):
        def change(p):
            p['nodes'][0]['steps'][1]['speaker']={'query':{'kind':'character','selection':'all',
                'where':{'constant':True}}}
        self.assertCode(check(mutate(change)),'PLURAL_REFERENCE')
    def test_unknown_session_variable(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'][0]['effects'][2]['target']['var'].update(key='sin_declarar'))
        self.assertCode(check(p),'UNKNOWN_VARIABLE')
    def test_incompatible_assignment(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'][0]['effects'][2].update(value={'literal':'sí'}))
        self.assertCode(check(p),'TYPE_MISMATCH')
    def test_add_boolean(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'][0]['effects'][2].update(op='add',value={'literal':1}))
        self.assertCode(check(p),'TYPE_MISMATCH')
    def test_incompatible_condition(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][6].update(test={'compare':{'left':{'literal':True},'op':'eq','right':{'literal':'false'}}}))
        self.assertCode(check(p),'INCOMPATIBLE_COMPARISON')
    def test_clock_compare_valid_iso_datetime(self):
        def change(p):
            p['nodes'][0]['steps'][6]['test']={'compare':{'left':{'clock':'world_time'},
                'op':'gte','right':{'literal':'1998-08-13T19:00:00-04:00'}}}
        self.assertClean(check(mutate(change)))
    def test_clock_compare_invalid_string(self):
        def change(p):
            p['nodes'][0]['steps'][6]['test']={'compare':{'left':{'clock':'world_time'},
                'op':'gte','right':{'literal':'mañana'}}}
        self.assertCode(check(mutate(change)),'INCOMPATIBLE_COMPARISON')
    def test_property_default_range(self):
        def change(p):
            p['cards'][0]['properties']=[{'id':'energia','type':'integer','initial':12,'min':0,'max':10}]
        self.assertCode(check(mutate(change)),'PROPERTY_RANGE')
    def test_unknown_relationship(self):
        p=mutate(lambda p:p['initial_state'].update(relationships=[{'from':'alberto','to':'gisela','key':'confianza','value':1}]))
        self.assertCode(check(p),'UNKNOWN_RELATION')
    def test_duplicate_capacities(self):
        p=mutate(lambda p:p['initial_state']['capacities'].append(copy.deepcopy(p['initial_state']['capacities'][0])))
        self.assertCode(check(p),'DUPLICATE_CAPACITY')
    def test_capacity_exceeded(self):
        p=mutate(lambda p:p['initial_state']['capacities'][0].update(hand=0))
        self.assertCode(check(p),'CAPACITY_EXCEEDED')
    def test_stat_outside_scale(self):
        p=mutate(lambda p:p['initial_state']['characters'][0].update(stats={'strength':11}))
        self.assertCode(check(p),'STAT_RANGE')
    def test_declared_variable_bad_initial(self):
        p=mutate(lambda p:p['manifest']['variables'][0].update(initial=10))
        self.assertCode(check(p),'TYPE_MISMATCH')
    def test_duplicate_property_declaration(self):
        def change(p):
            p['cards'][0]['properties']=[{'id':'cansancio','type':'integer','initial':2}]*2
        self.assertCode(check(mutate(change)),'DUPLICATE_ID')
    def test_unknown_instance_property(self):
        p=mutate(lambda p:p['initial_state']['objects'][0].update(properties={'precio':200}))
        self.assertCode(check(p),'UNKNOWN_PROPERTY')
    def test_localization_key_absent(self):
        p=mutate(lambda p:p['cards'][0].update(title={'text_key':'alberto_title'}))
        self.assertCode(check(p),'MISSING_TEXT')
    def test_undeclared_language(self):
        p=mutate(lambda p:p.update(strings={'en':{'x':'text'}}))
        self.assertCode(check(p),'UNDECLARED_LANGUAGE')
    def test_same_scene_action_id_on_different_owners_is_valid(self):
        def change(p):
            p['scenes'][0]['actions']=[{'id':'mirar','label':{'text':'Mirar'}}]
            p['scenes'][0]['elements'][0]['actions']=[{'id':'mirar','label':{'text':'Mirar'}}]
        self.assertClean(check(mutate(change)))
    def test_unknown_context_name(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][1].update(speaker='$prince'))
        self.assertCode(check(p),'UNSUPPORTED_CONTEXT')
    def test_candidate_unbound(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][1].update(speaker='$candidate'))
        self.assertCode(check(p),'UNBOUND_CONTEXT')
    def test_dynamic_cycle_not_rejected_as_story_quality(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][4].update(next={'step':'fondo'}))
        self.assertClean(check(p))
    def test_unknown_signal(self):
        p=mutate(lambda p:p['rules'].append({'id':'señal_no_valida','trigger':{'on':'signal','id':'desconocida'},'effects':[{'op':'record_fact','fact':'alberto_presto_casete'}]}))
        self.assertCode(check(p),'SCHEMA_INVALID') # non-ascii ID rejected by schema
    def test_unknown_signal_valid_id(self):
        p=mutate(lambda p:p['rules'].append({'id':'regla_senal','trigger':{'on':'signal','id':'desconocida'},'effects':[{'op':'record_fact','fact':'alberto_presto_casete'}]}))
        self.assertCode(check(p),'UNKNOWN_SIGNAL')
    def test_create_object_without_holder(self):
        p=mutate(lambda p:p['nodes'][0]['steps'][2]['options'][0]['effects'].append({'op':'create_instance','card':'casete','instance_id':'casete_02'}))
        self.assertCode(check(p),'AMBIGUOUS_LOCATION')
    def test_session_node(self):self.assertClean(check(session=copy.deepcopy(NODE)))
    def test_session_exploring(self):
        s=copy.deepcopy(EXPLORE);s['turn']=0
        self.assertClean(check(session=s))
    def test_structural_fixture_truncated_history_rejected(self):
        self.assertCode(check(session=copy.deepcopy(EXPLORE)),'TURN_COUNT')
    def test_session_missing_used_id(self):
        s=copy.deepcopy(NODE);s['identity']['used_instance_ids'].remove('gisela')
        self.assertCode(check(session=s),'UNRECORDED_ID')
    def test_session_duplicate_used_id(self):
        s=copy.deepcopy(NODE);s['identity']['used_instance_ids'].append('alberto')
        self.assertCode(check(session=s),'SCHEMA_INVALID') # ya lo impide JSON Schema
    def test_session_cursor_wrong_node(self):
        s=copy.deepcopy(NODE);s['cursor']['node']='final_compartido'
        self.assertCode(check(session=s),'CURSOR_MISMATCH')
    def test_session_cursor_wrong_execution(self):
        s=copy.deepcopy(NODE);s['cursor']['execution_id']='false_id'
        self.assertCode(check(session=s),'ACTIVE_EXECUTION')
    def test_session_multiple_active_executions(self):
        s=copy.deepcopy(NODE);second=copy.deepcopy(s['history']['executions'][0]);second['execution_id']='execution_02';s['history']['executions'].append(second)
        self.assertCode(check(session=s),'ACTIVE_EXECUTION')
    def test_session_duplicate_turn(self):
        s=copy.deepcopy(NODE);second=copy.deepcopy(s['history']['executions'][0]);second['execution_id']='execution_02';s['history']['executions'].append(second)
        self.assertCode(check(session=s),'DUPLICATE_TURN')
    def test_session_duplicate_fact_sequence(self):
        s=copy.deepcopy(NODE);e={'sequence':0,'fact':'alberto_presto_casete','source':'decidir'};s['history']['facts']=[e,e]
        self.assertCode(check(session=s),'DUPLICATE_SEQUENCE')
    def test_session_package_mismatch(self):
        s=copy.deepcopy(NODE);s['package_id']='otro_paquete'
        self.assertCode(check(session=s),'PACKAGE_MISMATCH')
    def test_session_digest_mismatch_against_trusted(self):
        self.assertCode(check(session=copy.deepcopy(NODE),digest='c'*64),'TRUSTED_DIGEST_MISMATCH')
    def test_session_digest_matches_package(self):
        issues=check(session=copy.deepcopy(NODE))
        self.assertFalse([x for x in issues if x.code=='DIGEST_MISMATCH'])
    def test_session_duplicate_pending_answers(self):
        s=copy.deepcopy(EXPLORE);s['pending_transaction']={'origin':'mandatory', 'source':{'kind':'node_start','node':'inicio'},'initiated_revision':1,'context':{},'answers':[{'request_id':'a','option_id':'b'},{'request_id':'a','option_id':'c'}],'request':{'request_id':'c','kind':'select_one','purpose':'discard_skill','options':['b']}}
        self.assertCode(check(session=s),'DUPLICATE_PENDING_ANSWER')
    def test_session_pending_current_id_repeated(self):
        s=copy.deepcopy(EXPLORE);s['pending_transaction']={'origin':'mandatory', 'source':{'kind':'node_start','node':'inicio'},'initiated_revision':1,'context':{},'answers':[{'request_id':'a','option_id':'b'}],'request':{'request_id':'a','kind':'select_one','purpose':'discard_skill','options':['b']}}
        self.assertCode(check(session=s),'PENDING_REQUEST_REUSED')
    def test_choice_pending_must_match_cursor(self):
        s=copy.deepcopy(EXPLORE);s['turn']=0
        s['pending_transaction']={'origin':'voluntary',
            'source':{'kind':'choice_option','node':'inicio','step':'decision','option':'prestar'},
            'initiated_revision':1,'context':{},'answers':[],
            'request':{'request_id':'a','kind':'select_one','purpose':'discard_skill','options':['intuicion_01']}}
        self.assertCode(check(session=s),'PENDING_CURSOR')
    def test_session_unknown_pending_origin(self):
        s=copy.deepcopy(EXPLORE);s['pending_transaction']={'origin':'voluntary', 'source':{'kind':'scene_action','scene':'porteria_noche','action':'inexistente'},'initiated_revision':1,'context':{},'answers':[],'request':{'request_id':'a','kind':'select_one','purpose':'discard_skill','options':['b']}}
        self.assertCode(check(session=s),'PENDING_SOURCE')
    def test_session_pending_context_wrong(self):
        s=copy.deepcopy(EXPLORE);s['pending_transaction']={'origin':'mandatory', 'source':{'kind':'node_start','node':'inicio'},'initiated_revision':1,'context':{'$actor':'nadie'},'answers':[],'request':{'request_id':'a','kind':'select_one','purpose':'discard_skill','options':['b']}}
        self.assertCode(check(session=s),'UNBOUND_CONTEXT')
    def test_action_against_view_valid(self):
        view={'session_id':'test_session','revision':2,'world_revision':1,'world_time':'1998-08-13T19:00:00-04:00','turn':1,'status':'node','content':{'kind':'choice'},'actions':[{'kind':'choose','action_id':'elegir','id':'prestar','label':'Prestar','enabled':True}]}
        act={'session_id':'test_session','revision':2,'action_id':'elegir'}
        self.assertClean(Validator().validate_act_against_observe(act,view))
    def test_action_unoffered(self):
        view={'session_id':'test_session','revision':2,'world_revision':1,'world_time':'1998-08-13T19:00:00-04:00','turn':1,'status':'node','content':{'kind':'choice'},'actions':[]}
        self.assertCode(Validator().validate_act_against_observe({'session_id':'test_session','revision':2,'action_id':'inventada'},view),'ACTION_NOT_OFFERED')
    def test_action_stale(self):
        view={'session_id':'test_session','revision':2,'world_revision':1,'world_time':'1998-08-13T19:00:00-04:00','turn':1,'status':'node','content':{'kind':'choice'},'actions':[]}
        self.assertCode(Validator().validate_act_against_observe({'session_id':'test_session','revision':1,'action_id':'inventada'},view),'STALE_PROJECTION')


    def test_var_ref_instance_property_type(self):
        def change(p):
            p['cards'][0]['properties']=[{'id':'cansancio','type':'integer','initial':0}]
            p['nodes'][0]['steps'][2]['options'][0]['effects'].append({
                'op':'set', 'target':{'var':{'scope':'character','entity':'alberto','key':'cansancio'}},
                'value':{'literal':'erróneo'}})
        self.assertCode(check(mutate(change)),'TYPE_MISMATCH')
    def test_var_ref_instance_unknown_field(self):
        def change(p):
            p['nodes'][0]['steps'][2]['options'][0]['effects'].append({
                'op':'set', 'target':{'var':{'scope':'character','entity':'alberto','key':'ninguna'}},
                'value':{'literal':1}})
        self.assertCode(check(mutate(change)),'UNKNOWN_PROPERTY')
    def test_sofia_effect_requires_character(self):
        def change(p):
            p['nodes'][0]['steps'][2]['options'][0]['effects'].append({
                'op':'apply_effect','effect':'inspiracion','target':'porteria'})
        self.assertCode(check(mutate(change)),'WRONG_ENTITY_KIND')
    def test_incompatible_return_policy(self):
        def change(p):
            p['cards'][4]['return_policy']['when']=[
                {'if':{'constant':True},'to':'hand'}, {'if':{'constant':True},'to':'reserve'}]
        self.assertCode(check(mutate(change)),'RETURN_POLICY_CONFLICT')
    def test_strict_json_parser_rejects_duplicate_keys(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'dup.json';path.write_text('{"id":"uno","id":"dos"}',encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Clave JSON duplicada'):
                load_json_strict(path)
    def test_semantic_exploring_example_passes(self):
        data=json.loads((ROOT/'semantic_examples/session_exploring_valid.json').read_text(encoding='utf8'))
        self.assertClean(check(session=data))
    def test_semantic_ended_example_passes(self):
        data=json.loads((ROOT/'semantic_examples/session_ended_valid.json').read_text(encoding='utf8'))
        self.assertClean(check(session=data))
    def test_semantic_pending_example_source_passes(self):
        pkg=json.loads((ROOT/'semantic_examples/package_with_scene_action.json').read_text(encoding='utf8'))
        data=json.loads((ROOT/'semantic_examples/session_pending_source_valid.json').read_text(encoding='utf8'))
        self.assertClean(check(pkg,session=data))
        self.assertCode(check(pkg,session=data),'REPLAY_UNVERIFIED')

if __name__=='__main__':unittest.main()
