"""Pruebas de la frontera neutral TRAITS–DICE con RNG transaccional."""
from __future__ import annotations
import copy
import unittest
from gisela.engine.tests.test_traits_alberto_v13 import fixture
from gisela.engine.tests.test_h34a_values import ready
from gisela.engine.traits_dice_bridge import resolve


def setup():
    pkg = fixture()
    pkg['traits']['traits'][0]['contributions'] = [
        {'id':'repair', 'when':{'role':'actor','all_tags':['repair']},
         'add':{'slot':'bonus','amount':2}}]
    pkg['traits']['traits'].append({'id':'fragile_machine','entity_kinds':['object'],
        'contributions':[{'id':'difficult', 'when':{'role':'target','all_tags':['repair']},
                          'add':{'slot':'difficulty','amount':2}}]})
    next(c for c in pkg['cards'] if c['kind']=='object')['traits'] = ['fragile_machine']
    return ready(pkg)[1]


def spec(mode):
    return {'participants':[{'entity':'alberto','role':'actor'},
                            {'entity':'casete_01','role':'target'}],
            'tags':['repair'], 'base':0,'difficulty':4,
            'stat':{'character':'alberto','name':'openness','component':'effective'},
            'profile':{'schema_version':'dice.profile.v1','id':'repair','mode':mode,
                       **({} if mode=='deterministic' else {'count':2,'sides':6}),
                       'bands':[{'id':'failure','min':-1000000},
                                {'id':'partial','min':0},{'id':'success','min':5}]}}


class TraitsDiceBridge(unittest.TestCase):
    def test_traits_sofia_and_dice_compose_without_mutation(self):
        session = setup()
        before = session.export()
        result = resolve(before,spec('deterministic'),session._definitions)
        self.assertEqual(result['traits']['totals'], {'bonus':2, 'difficulty':2})
        self.assertEqual(result['dice']['total'], -1)
        self.assertEqual(result['dice']['outcome'],'failure')
        self.assertEqual(session.export(),before)
        self.assertEqual(result['rng_after'],before['rng'])

    def test_rng_is_proposed_not_committed(self):
        session = setup()
        before = session.export()
        a = resolve(before,spec('dice_sum'),session._definitions)
        b = resolve(before,spec('dice_sum'),session._definitions)
        self.assertEqual(a,b)
        self.assertGreater(a['rng_after']['counter'],before['rng']['counter'])
        self.assertEqual(session.export(),before)

    def test_different_tags_do_not_apply_rasgos(self):
        session = setup()
        request = spec('deterministic')
        request['tags'] = ['another_context']
        result = resolve(session.export(),request,session._definitions)
        self.assertEqual(result['traits']['totals'], {})

    def test_no_sofia_needed_for_traits_dice(self):
        session = setup()
        request = spec('deterministic')
        request.pop('stat')
        result = resolve(session.export(),request,session._definitions)
        self.assertEqual(result['dice']['base'],0)

    def test_dice_also_works_without_traits_catalog(self):
        pkg = __import__('gisela.engine.tests.test_traits_alberto_v13',fromlist=['fixture']).fixture()
        del pkg['traits']
        for card in pkg['cards']:
            card.pop('traits',None)
        from gisela.engine.tests.test_h34a_values import ready
        session = ready(pkg)[1]
        args = spec('deterministic')
        args.pop('stat')
        self.assertEqual(resolve(session.export(),args,session._definitions)['traits']['totals'],{})
