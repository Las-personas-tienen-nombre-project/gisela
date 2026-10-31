"""H3.4c: vida de efectos, límites y atomicidad causal de GISELA."""
from __future__ import annotations
import unittest
from gisela.contracts.admit_package import admit_package, PackageRejected
from gisela.engine.errors import EngineFailure
from gisela.engine.runtime import restore_session
from gisela.engine.tests.test_h34a_values import load, ready, send
from gisela.engine.conditions import predicate


def package(expiration=None, stacking='additive', behavior=None):
    """Prepara una vertical desde un paquete ya admitido por H3.4a."""
    behavior = behavior or {}
    pkg = load()
    pkg['rules'] = []
    pkg['manifest']['facts'].extend(['valor_termino', 'despedida', 'cierre_reactivo', 'aplicado'])
    pkg['cards'].append({'id':'valor', 'kind':'effect', 'title':{'text':'Valor'},
                         'modifiers':[{'stat':'strength','amount':2}], 'stacking':stacking,
                         **({'expiration':expiration} if expiration else {}),
                         'on_apply':behavior.get('apply', []), 'on_expire':behavior.get('expire', [])})
    return pkg


def chosen(pkg, operations):
    """Agrega consecuencias a la opción de prueba, sin tocar su texto."""
    step = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
    next(o for o in step['options'] if o['id']=='prestar')['effects'] = operations
    return pkg


def grant(instance=None):
    """Declara un efecto con identidad determinista cuando se especifica."""
    result = {'op':'apply_effect', 'effect':'valor', 'target':'alberto'}
    if instance:
        result['instance_id'] = instance
    return result


def end(identifier='valor_01'):
    """Declara la terminación explícita de una instancia."""
    return {'op':'end_effect', 'effect_instance':identifier}


def row(session):
    """Obtiene la fuerza calculada sin escribir en el mundo."""
    return session.scoresheet('alberto')['stats'][0]


def finish(session):
    """Recorre los pasos observables hasta el desenlace."""
    for _ in range(20):
        if session.export()['status'] == 'ended':
            return
        result = send(session)
        if result['status'] != 'ok':
            raise AssertionError(result)
    raise AssertionError('La vertical no terminó')


class H34cEffectsTest(unittest.TestCase):
    def test_apply_and_explicit_end_restore(self):
        pkg = chosen(package(), [grant('valor_01')])
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session,'prestar')['status'], 'ok')
        self.assertEqual(row(session)['effective'], 8)
        self.assertEqual(row(session)['current'], 6)
        self.assertEqual(restore_session(admitted, session.export()).scoresheet('alberto'),
                         session.scoresheet('alberto'))
        self.assertEqual(len(session.export()['world']['effects']), 1)
        self.assertEqual(before['world']['effects'], [])

    def test_explicit_end_executes_on_expire_once(self):
        pkg = package(behavior={'expire':[{'op':'record_fact', 'fact':'valor_termino'}]})
        pkg = chosen(pkg, [grant('valor_01'), end()])
        _, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'], 'ok')
        self.assertEqual(row(session)['effective'], 6)
        self.assertEqual([f['fact'] for f in session.export()['history']['facts']].count('valor_termino'),1)
        self.assertEqual(session.export()['world']['effects'], [])

    def test_additive_stack_and_unique_rejection(self):
        pkg = chosen(package(), [grant('valor_01'), grant('valor_02')])
        _, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'], 'ok')
        self.assertEqual(row(session)['modifier'], 4)
        pkg = chosen(package(stacking='unique_per_target'), [grant('valor_01'), grant('valor_02')])
        _, session = ready(pkg)
        previous = session.export()
        self.assertEqual(send(session,'prestar')['error']['code'], 'EFFECT_ALREADY_ACTIVE')
        self.assertEqual(session.export(), previous)

    def test_after_minutes_with_chained_expiration_event(self):
        expiry = {'mode':'any', 'clauses':[{'after_minutes':5}]}
        pkg = package(expiry, behavior={'expire':[{'op':'record_fact','fact':'valor_termino'}]})
        pkg = chosen(pkg, [grant('valor_01'), {'op':'advance_time','minutes':5}])
        _, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'], 'ok')
        self.assertEqual(row(session)['modifier'], 0)
        self.assertTrue(predicate(session.export(), {'has_fact':'valor_termino'}))

    def test_on_fact_expiration_and_rule_effect_expired(self):
        expiry = {'mode':'any', 'clauses':[{'on_fact':'despedida'}]}
        pkg = package(expiry, behavior={'expire':[{'op':'record_fact','fact':'valor_termino'}]})
        pkg['rules'].append({'id':'cierre_valor','trigger':{'on':'effect_expired','effect':'valor'},
                             'effects':[{'op':'record_fact','fact':'cierre_reactivo'}]})
        pkg = chosen(pkg,[grant('valor_01'),{'op':'record_fact','fact':'despedida'}])
        _, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'],'ok')
        facts = [f['fact'] for f in session.export()['history']['facts']]
        self.assertEqual(facts.count('valor_termino'),1)
        self.assertEqual(facts.count('cierre_reactivo'),1)

    def test_when_clause_uses_confirmed_changes(self):
        expiry = {'mode':'any', 'clauses':[{'when':{'has_fact':'despedida'}}]}
        pkg = chosen(package(expiry), [grant('valor_01'),{'op':'record_fact','fact':'despedida'}])
        _, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'], 'ok')
        self.assertEqual(row(session)['modifier'],0)

    def test_turn_expiration_does_not_end_same_turn(self):
        expiry = {'mode':'any','clauses':[{'after_turns':1}]}
        pkg = chosen(package(expiry),[grant('valor_01')])
        _, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'],'ok')
        self.assertEqual(row(session)['modifier'],2)
        finish(session)
        self.assertEqual(row(session)['modifier'],0)

    def test_failed_expiration_rolls_back_clock_and_ids(self):
        expiry = {'mode':'any','clauses':[{'after_minutes':5}]}
        pkg = chosen(package(expiry, behavior={'expire':[{'op':'remove_instance','instance':'alberto'}]}),
                     [grant('valor_01'), {'op':'advance_time','minutes':5}])
        _, session = ready(pkg)
        previous = session.export()
        self.assertEqual(send(session,'prestar')['status'],'error')
        self.assertEqual(session.export(),previous)

    def test_effect_reference_and_unknown_target_rejected(self):
        pkg = chosen(package(),[{'op':'apply_effect','effect':'valor','target':'inexistente'}])
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_restore_pending_with_provisional_effect(self):
        from gisela.engine.tests.test_h3_world import base
        pkg = base('h2_descarte')
        pkg['cards'].append({'id':'valor','kind':'effect','title':{'text':'Valor'},
                              'modifiers':[{'stat':'strength','amount':2}]})
        step = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        option = next(o for o in step['options'] if o['id']=='prestar')
        option['effects'].insert(0,grant('valor_01'))
        admitted, session = ready(pkg)
        self.assertEqual(send(session,'prestar')['status'],'ok')
        self.assertEqual(session.observe()['content']['kind'],'pending_transaction')
        self.assertEqual(session.export()['world']['effects'],[])
        recovered = restore_session(admitted,session.export())
        self.assertEqual(recovered.export(),session.export())
        self.assertEqual(row(recovered)['modifier'],0)

    def test_has_effect_condition_without_state_mutation(self):
        pkg = chosen(package(), [grant('valor_01')])
        _, session = ready(pkg)
        query = {'has_effect':{'target':'alberto','effect':'valor'}}
        before = session.export()
        self.assertFalse(predicate(before,query))
        self.assertEqual(send(session,'prestar')['status'],'ok')
        self.assertTrue(predicate(session.export(),query))
        self.assertNotEqual(before,session.export())

    def test_on_apply_suspends_and_restores_pending(self):
        from gisela.engine.tests.test_h3_world import base
        pkg = base('h2_descarte')
        pkg['cards'].append({'id':'valor','kind':'effect','title':{'text':'Valor'},
              'on_apply':[{'op':'grant_skill','character':'gisela',
                           'skill':'habilidad_c','overflow':'require_choice'}]})
        step = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        choice = next(o for o in step['options'] if o['id']=='prestar')
        choice['effects'] = [grant('valor_01')]
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session,'prestar')['status'],'ok')
        snapshot = session.export()
        self.assertEqual(snapshot['world'],before['world'])
        session = restore_session(admitted,snapshot)
        response = next(a['id'] for a in session.observe()['actions']
                        if a['kind']=='resolve_pending')
        self.assertEqual(send(session,response)['status'],'ok')
        self.assertEqual(len(session.export()['world']['effects']),1)
        self.assertNotIn('pending_transaction',session.export())

    def test_expiration_suspends_and_replays_once(self):
        from gisela.engine.tests.test_h3_world import base
        pkg = base('h2_descarte')
        pkg['manifest']['facts'].append('despedida')
        pkg['cards'].append({'id':'valor','kind':'effect','title':{'text':'Valor'},
              'expiration':{'mode':'any','clauses':[{'on_fact':'despedida'}]},
              'on_expire':[{'op':'grant_skill','character':'gisela',
                            'skill':'habilidad_c','overflow':'require_choice'}]})
        step = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        choice = next(o for o in step['options'] if o['id']=='prestar')
        choice['effects'] = [grant('valor_01'),{'op':'record_fact','fact':'despedida'}]
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session,'prestar')['status'],'ok')
        snapshot = session.export()
        self.assertEqual(snapshot['world'],before['world'])
        session = restore_session(admitted,snapshot)
        answer = next(a['id'] for a in session.observe()['actions']
                      if a['kind']=='resolve_pending')
        self.assertEqual(send(session,answer)['status'],'ok')
        self.assertEqual(session.export()['world']['effects'],[])
        self.assertEqual(len(session.export()['world']['skills']),2)

    def test_recursion_is_rejected_before_session(self):
        pkg = package(behavior={'apply':[grant()]})
        with self.assertRaises(EngineFailure):
            ready(pkg)

    def test_nested_reactive_writes_conflict_without_order_priority(self):
        stat = {'stat':{'character':'alberto','name':'strength','component':'current'}}
        pkg = package(behavior={'apply':[{'op':'add','target':stat,
                                         'value':{'literal':2}}]})
        pkg['rules'] = [
            {'id':'a','trigger':{'on':'fact_recorded','fact':'despedida'},
             'effects':[grant('valor_01')]},
            {'id':'b','trigger':{'on':'fact_recorded','fact':'despedida'},
             'effects':[{'op':'add','target':stat,'value':{'literal':1}}]},
        ]
        pkg = chosen(pkg,[{'op':'record_fact','fact':'despedida'}])
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session,'prestar')['error']['code'],'REACTION_CONFLICT')
        self.assertEqual(session.export(),before)

    def test_initial_effects_do_not_execute_on_apply(self):
        pkg = package(behavior={'apply':[{'op':'record_fact','fact':'aplicado'}]})
        pkg['initial_state']['effects'].append({'id':'valor_01','card':'valor',
            'target':'alberto','started_turn':0,'started_at':pkg['initial_state']['world_time']})
        _, session = ready(pkg)
        self.assertFalse(predicate(session.export(),{'has_fact':'aplicado'}))
        self.assertEqual(row(session)['modifier'],2)

if __name__ == '__main__':
    unittest.main()
