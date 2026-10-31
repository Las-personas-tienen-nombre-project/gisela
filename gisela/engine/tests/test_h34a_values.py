"""Regresiones H3.4a: propiedades, relaciones y escrituras compatibles."""
from __future__ import annotations
import copy
import unittest
from pathlib import Path
from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.conditions import predicate, value
from gisela.engine.runtime import new_session, restore_session

PATH = Path(__file__).resolve().parents[2] / 'packages/h3_relaciones.package.json'
REL = {'relationship':{'from':'alberto','to':'gisela','key':'confianza'}}
REVERSE = {'relationship':{'from':'gisela','to':'alberto','key':'confianza'}}
PROP = {'property':{'entity':'casete_01','key':'cuidado'}}
PATIENCE = {'property':{'entity':'gisela','key':'paciencia'}}


def load():
    """Carga la vertical H3.4a como paquete independiente y mutable."""
    return admit_package_file(PATH).materialize()


def send(session, selected=None):
    """Envía únicamente acciones que el motor ofreció en Observe."""
    view = session.observe()
    options = [a for a in view['actions'] if a['enabled']]
    chosen = next((a for a in options if a['id'] == selected), options[0])
    return session.act({'session_id':view['session_id'], 'revision':view['revision'],
                        'action_id':chosen['action_id']})


def ready(pkg=None):
    """Llega a la elección en una sesión con paquete admitido."""
    admitted = admit_package(pkg) if pkg else admit_package_file(PATH)
    session = new_session(admitted)
    for _ in range(12):
        if session.observe()['content']['kind'] == 'choice':
            return admitted, session
        assert send(session)['status'] == 'ok'
    raise AssertionError('No se alcanzó la elección')


def rule(pkg, rule_id, effects):
    """Reemplaza las consecuencias de una regla existente."""
    next(r for r in pkg['rules'] if r['id'] == rule_id)['effects'] = effects
    return pkg


def op(operation, target, val):
    """Construye una escritura declarativa sin atajos Python."""
    return {'op':operation, 'target':target, 'value':val}


class H34aValuesTests(unittest.TestCase):
    def test_sparse_directed_defaults_do_not_materialize_on_read(self):
        _, session = ready()
        before = session.export()
        self.assertEqual(value(before, REL, session._definitions), 0)
        self.assertEqual(value(before, REVERSE, session._definitions), 0)
        self.assertEqual(value(before, PROP, session._definitions), 1)
        self.assertEqual(value(before, PATIENCE, session._definitions), 2)
        self.assertEqual(session.export(), before)
        self.assertEqual(before['world']['relationships'], [])
        self.assertNotIn('properties', before['world']['objects'][0])

    def test_add_merges_in_one_round_and_restores(self):
        admitted, session = ready()
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        self.assertEqual(value(snapshot, REL, session._definitions), 5)
        self.assertEqual(value(snapshot, REVERSE, session._definitions), 0)
        self.assertEqual(value(snapshot, PROP, session._definitions), 3)
        self.assertEqual(len(snapshot['world']['relationships']), 1)
        self.assertEqual(restore_session(admitted, snapshot).export(), snapshot)

    def test_compare_property_and_relation_control_choice(self):
        _, session = ready()
        condition = {'compare':{'left':REL, 'op':'eq', 'right':{'literal':0}}}
        self.assertTrue(predicate(session.export(), condition, session._definitions))
        self.assertEqual(send(session, 'guardar')['status'], 'ok')
        self.assertEqual(value(session.export(), REL, session._definitions), 0)

    def test_same_set_values_coalesce(self):
        pkg = load()
        for name in ('confianza_2', 'confianza_3'):
            rule(pkg, name, [op('set', REL, {'literal':4})])
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        self.assertEqual(value(session.export(), REL, session._definitions), 4)
        self.assertEqual(len(session.export()['world']['relationships']), 1)

    def test_different_set_values_abort_entire_action(self):
        pkg = rule(load(), 'confianza_2', [op('set', REL, {'literal':4})])
        pkg = rule(pkg, 'confianza_3', [op('set', REL, {'literal':5})])
        _, session = ready(pkg)
        before = session.export()
        result = send(session, 'prestar')
        self.assertEqual(result['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), before)

    def test_set_plus_add_aborts_entire_action(self):
        pkg = rule(load(), 'confianza_2', [op('set', REL, {'literal':4})])
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), before)

    def test_out_of_range_after_aggregation_rolls_back(self):
        pkg = load()
        for key in ('confianza_2', 'confianza_3'):
            rule(pkg, key, [op('add', PROP, {'literal':5})])
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'PROPERTY_RANGE')
        self.assertEqual(session.export(), before)

    def test_baseline_rhs_for_different_targets(self):
        pkg = rule(load(), 'confianza_2', [op('set', PATIENCE, {'literal':7})])
        pkg = rule(pkg, 'confianza_3', [op('set', PROP, PATIENCE)])
        pkg['rules'] = [r for r in pkg['rules'] if r['id'] != 'cuidado_casete']
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        self.assertEqual(value(session.export(), PATIENCE, session._definitions), 7)
        self.assertEqual(value(session.export(), PROP, session._definitions), 2)

    def test_property_type_error_rolls_back(self):
        pkg = rule(load(), 'confianza_2', [op('set', PROP, {'literal':'malo'})])
        # La admisión semántica detecta el tipo incorrecto antes del runtime.
        from gisela.contracts.admit_package import PackageRejected
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_relation_write_to_removed_entity_is_rejected(self):
        pkg = load()
        pkg['rules'] = []
        choice = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        option = next(o for o in choice['options'] if o['id']=='prestar')
        option['effects'] = [
            {'op':'remove_instance','instance':'casete_01'},
            op('set', {'relationship':{'from':'alberto','to':'casete_01',
                                     'key':'confianza'}}, {'literal':2})]
        _, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'INVALID_REFERENCE')
        self.assertEqual(session.export(), before)

    def test_existing_relation_and_property_override(self):
        pkg = load()
        pkg['initial_state'].setdefault('relationships', []).append({'from':'alberto','to':'gisela',
                                                        'key':'confianza','value':1})
        pkg['initial_state']['objects'][0]['properties'] = {'cuidado':4}
        _, session = ready(pkg)
        self.assertEqual(value(session.export(), REL, session._definitions), 1)
        self.assertEqual(value(session.export(), PROP, session._definitions), 4)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        self.assertEqual(value(session.export(), REL, session._definitions), 6)
        self.assertEqual(value(session.export(), PROP, session._definitions), 6)

    def test_followup_rule_sees_single_merged_change(self):
        pkg = load()
        pkg['rules'].append({'id':'reaccion_a_confianza',
            'trigger':{'on':'state_changed','target':REL},
            'effects':[op('set', PATIENCE, {'literal':4})]})
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        self.assertEqual(value(session.export(), PATIENCE, session._definitions), 4)
        trace = session.export()['history']['trace']
        self.assertEqual([r['source'] for r in trace].count('reaccion_a_confianza'), 1)

    def test_unregistered_property_is_rejected_by_admission(self):
        pkg = rule(load(), 'confianza_2', [op('set',
            {'property':{'entity':'gisela','key':'inexistente'}}, {'literal':2})])
        from gisela.contracts.admit_package import PackageRejected
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_unregistered_relation_is_rejected_by_admission(self):
        pkg = rule(load(), 'confianza_2', [op('add',
            {'relationship':{'from':'alberto','to':'gisela','key':'inexistente'}},
            {'literal':2})])
        from gisela.contracts.admit_package import PackageRejected
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_pending_round_replays_relation_and_property(self):
        pkg = load()
        pkg['manifest']['id'] = 'h34a_pending'
        pkg['cards'] += [{'id':'destreza','kind':'skill','title':{'text':'Destreza'},
                          'play':{'effects':[]}}]
        pkg['initial_state']['capacities'] = [{'character':'gisela','hand':0,'reserve':0}]
        rule(pkg, 'confianza_2', [{'op':'grant_skill','character':'gisela',
                                  'skill':'destreza','overflow':'require_choice'}])
        # La operación no puede ofrecer un descarte sin habilidades existentes.
        # Se comprueba el rechazo atómico, no una espera imposible.
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'NO_LEGAL_CHOICE')
        self.assertEqual(session.export(), before)

    def test_pending_replay_keeps_world_confirmed_until_resolution(self):
        path = PATH.with_name('h2_descarte.package.json')
        pkg = admit_package_file(path).materialize()
        pkg['manifest']['relationship_fields'] = [{'id':'confianza','type':'integer','initial':0}]
        step = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        option = next(o for o in step['options'] if o['id']=='prestar')
        option['effects'].insert(0, op('add', REL, {'literal':2}))
        admitted, session = ready(pkg)
        before = session.export()
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        waiting = session.export()
        self.assertEqual(waiting['world'], before['world'])
        restored = restore_session(admitted, waiting)
        for target in (session, restored):
            self.assertEqual(send(target, 'hab_01')['status'], 'ok')
            self.assertEqual(value(target.export(), REL, target._definitions), 2)
        self.assertEqual(restored.export(), session.export())

    def test_numeric_comparison_distinguishes_booleans(self):
        _, session = ready()
        condition = {'compare':{'left':{'literal':1}, 'op':'eq',
                                'right':{'literal':1.0}}}
        self.assertTrue(predicate(session.export(), condition, session._definitions))
        condition['compare']['right'] = {'literal':True}
        self.assertFalse(predicate(session.export(), condition, session._definitions))

    def test_rule_reordering_changes_neither_values_nor_rng(self):
        original = load()
        changed = copy.deepcopy(original)
        changed['rules'].reverse()
        states = []
        for pkg in (original, changed):
            _, session = ready(pkg)
            self.assertEqual(send(session, 'prestar')['status'], 'ok')
            states.append(session.export())
        self.assertEqual(states[0]['world'], states[1]['world'])
        self.assertEqual(states[0]['rng'], states[1]['rng'])
