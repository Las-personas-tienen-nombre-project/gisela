"""Pruebas H3 de ALBERTO: operaciones, invariantes y guardados."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from gisela.contracts.admit_package import admit_package, admit_package_file, PackageRejected
from gisela.engine.runtime import new_session, restore_session, EngineFailure
from gisela.engine.conditions import predicate

PACKAGES = Path(__file__).resolve().parents[2] / 'packages'


def base(name='mvp_casete'):
    """Devuelve una copia modificable de un paquete narrativo admitido."""
    return admit_package_file(PACKAGES / (name + '.package.json')).materialize()


def add_effects(pkg, *effects):
    """Añade efectos a la opción prestar sin modificar el paquete original."""
    step = next(step for node in pkg['nodes'] for step in node['steps'] if step['op'] == 'choice')
    option = next(item for item in step['options'] if item['id'] == 'prestar')
    option.setdefault('effects', []).extend(effects)
    return pkg


def send(session, selected=None):
    """Ejecuta una acción realmente ofrecida por la sesión."""
    view = session.observe()
    actions = [item for item in view['actions'] if item['enabled']]
    action = next((x for x in actions if x['id'] == selected), actions[0])
    return session.act({'session_id':view['session_id'], 'revision':view['revision'],
                        'action_id':action['action_id']})


def ready(pkg):
    """Abre la historia y la adelanta hasta la primera elección."""
    admitted = admit_package(pkg)
    session = new_session(admitted)
    for _ in range(12):
        if session.observe()['content']['kind'] == 'choice':
            return admitted, session
        assert send(session)['status'] == 'ok'
    raise AssertionError('No se alcanzó la elección')


def character(state, identifier='gisela'):
    """Busca un personaje en un snapshot exportado."""
    return next(x for x in state['world']['characters'] if x['id'] == identifier)


class WorldH3Test(unittest.TestCase):
    def test_move_character_and_location_condition(self):
        pkg = base()
        pkg['cards'].append({'id':'patio', 'kind':'location', 'title':{'text':'Patio'}})
        pkg['initial_state']['locations'].append({'id':'patio', 'card':'patio'})
        add_effects(pkg, {'op':'move_character', 'character':'gisela', 'location':'patio'})
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        self.assertEqual(character(snapshot)['location'], 'patio')
        self.assertTrue(predicate(snapshot, {'at_location':{'character':'gisela', 'location':'patio'}}))
        self.assertEqual(snapshot['current_scene'], 'porteria_noche')

    def test_learn_and_believe_do_not_register_new_historical_fact(self):
        pkg = base()
        pkg['manifest']['facts'].append('conocio_secreto')
        pkg['manifest']['claims'].append('confia_en_alberto')
        add_effects(pkg, {'op':'learn_fact', 'character':'gisela', 'fact':'conocio_secreto'},
                    {'op':'set_belief', 'character':'gisela', 'claim':'confia_en_alberto', 'value':True})
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        self.assertTrue(predicate(snapshot, {'knows':{'character':'gisela', 'fact':'conocio_secreto'}}))
        self.assertTrue(predicate(snapshot, {'believes':{'character':'gisela', 'claim':'confia_en_alberto','value':True}}))
        self.assertFalse(predicate(snapshot, {'has_fact':'conocio_secreto'}))
        self.assertNotIn('conocio_secreto', character(before).get('knowledge', []))
        self.assertEqual(restore_session(admitted, snapshot).export(), snapshot)

    def test_creating_and_removing_retains_used_identity(self):
        pkg = add_effects(base(), {'op':'create_instance', 'card':'casete',
                                  'instance_id':'casete_extra', 'owner':'gisela'},
                          {'op':'remove_instance', 'instance':'casete_extra'})
        admitted, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        self.assertIn('casete_extra', snapshot['identity']['used_instance_ids'])
        self.assertNotIn('casete_extra', [x['id'] for x in snapshot['world']['objects']])
        self.assertEqual(restore_session(admitted, snapshot).export(), snapshot)

    def test_removed_id_reuse_rolls_back_all(self):
        pkg = add_effects(base(), {'op':'create_instance', 'card':'casete',
                                  'instance_id':'casete_extra','owner':'gisela'},
                          {'op':'remove_instance','instance':'casete_extra'},
                          {'op':'create_instance','card':'casete',
                           'instance_id':'casete_extra','owner':'gisela'})
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'INSTANCE_COLLISION')
        self.assertEqual(session.export(), before)

    def test_auto_id_generated_only_on_commit(self):
        pkg = add_effects(base(), {'op':'create_instance', 'card':'casete','owner':'gisela'})
        admitted, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        self.assertIn('object_000001', [x['id'] for x in snapshot['world']['objects']])
        self.assertIn('object_000001', snapshot['identity']['used_instance_ids'])
        self.assertEqual(restore_session(admitted, json.loads(json.dumps(snapshot))).export(), snapshot)

    def test_removing_referenced_character_is_atomic(self):
        _, session = ready(add_effects(base(), {'op':'remove_instance','instance':'gisela'}))
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'ENTITY_IN_USE')
        self.assertEqual(session.export(), before)

    def test_creation_then_failure_does_not_consume_id(self):
        effects = ({'op':'create_instance','card':'casete','owner':'gisela'},
                   {'op':'remove_instance','instance':'gisela'})
        _, session = ready(add_effects(base(), *effects))
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'ENTITY_IN_USE')
        self.assertEqual(session.export()['identity'], before['identity'])
        self.assertEqual(session.export(), before)

    def test_move_skill_rejects_full_hand(self):
        pkg = add_effects(base('h2_descarte'), {'op':'move_skill', 'character':'gisela',
                                               'skill_instance':'hab_02', 'to':'hand'})
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'CAPACITY_EXCEEDED')
        self.assertEqual(session.export(), before)

    def test_move_and_discard_skill(self):
        pkg = base('h2_descarte')
        pkg['initial_state']['capacities'][0]['hand'] = 2
        add_effects(pkg, {'op':'move_skill','character':'gisela',
                          'skill_instance':'hab_02','to':'hand'},
                    {'op':'discard_skill','character':'gisela','skill_instance':'hab_01'})
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        skills = session.export()['world']['skills']
        self.assertNotIn('hab_01', [item['id'] for item in skills])
        self.assertEqual(next(x['zone'] for x in skills if x['id']=='hab_02'), 'hand')
        self.assertTrue(predicate(session.export(),
            {'has_skill':{'character':'gisela','skill':'habilidad_b','zone':'hand'}}))

    def test_advance_time_is_explicit_and_restorable(self):
        pkg = add_effects(base(), {'op':'advance_time', 'minutes':45})
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        after = session.export()
        self.assertNotEqual(before['world_time'], after['world_time'])
        self.assertEqual(after['world_revision'], before['world_revision'] + 1)
        self.assertEqual(restore_session(admitted, after).export(), after)

    def test_conflicting_moves_reject_entire_round(self):
        pkg = base()
        for name in ('mover_a', 'mover_b'):
            pkg['rules'].append({'id':name,
                'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
                'effects':[{'op':'move_character','character':'gisela','location':'porteria'}]})
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), before)

    def test_transfer_between_person_and_location(self):
        pkg = base()
        option = next(x for n in pkg['nodes'] for st in n['steps'] if st['op']=='choice'
                      for x in st['options'] if x['id']=='prestar')
        option['effects'][0]['to'] = 'porteria'
        admitted, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        obj = next(x for x in snapshot['world']['objects'] if x['id']=='casete_01')
        self.assertEqual(obj['location'], 'porteria')
        self.assertNotIn('owner', obj)
        self.assertEqual(restore_session(admitted, snapshot).export(), snapshot)

    def test_wrong_transfer_origin_is_atomic(self):
        pkg = base()
        option = next(x for n in pkg['nodes'] for st in n['steps'] if st['op']=='choice'
                      for x in st['options'] if x['id']=='prestar')
        option['effects'][0]['from'] = 'porteria'
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'INVALID_STATE')
        self.assertEqual(session.export(), before)

    def test_remove_and_transfer_conflict_across_rules(self):
        pkg = base()
        pkg['rules'].extend([
            {'id':'a_retirar', 'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
             'effects':[{'op':'remove_instance','instance':'casete_01'}]},
            {'id':'b_trasladar', 'trigger':{'on':'fact_recorded','fact':'alberto_presto_casete'},
             'effects':[{'op':'transfer','object':'casete_01','from':'gisela','to':'alberto'}]},
        ])
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), before)

    def test_unknown_location_rejects_movement_atomically(self):
        pkg = add_effects(base(), {'op':'move_character', 'character':'gisela',
                                  'location':'ubicacion_no_existente'})
        with self.assertRaises(PackageRejected):
            ready(pkg)

    def test_admission_rejects_object_without_holder(self):
        pkg = add_effects(base(), {'op':'create_instance','card':'casete'})
        with self.assertRaises(PackageRejected):
            ready(pkg)

    def test_admission_rejects_character_without_location(self):
        pkg = add_effects(base(), {'op':'create_instance','card':'gisela'})
        with self.assertRaises(PackageRejected):
            ready(pkg)

    def test_unsupported_context_is_rejected_before_play(self):
        pkg = add_effects(base(), {'op':'move_character',
                                  'character':'$actor','location':'porteria'})
        with self.assertRaises(EngineFailure):
            new_session(admit_package(pkg))


if __name__ == '__main__':
    unittest.main()
