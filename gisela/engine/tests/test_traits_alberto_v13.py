"""Regresión: TRAITS integrado con ALBERTO sin romper paquetes v1.2."""
from __future__ import annotations
import copy
import unittest
from gisela.contracts.admit_package import admit_package, PackageRejected
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.conditions import predicate
from gisela.engine.tests.test_h34a_values import load, ready, send


def catalog(maximum=5):
    """Definiciones ajenas al argumento del juego."""
    return {'schema_version':'traits.v1', 'max_traits':maximum, 'traits':[
        {'id':'steady', 'entity_kinds':['character'], 'contributions':[]},
        {'id':'curious', 'entity_kinds':['character'], 'contributions':[]},
        {'id':'fragile', 'entity_kinds':['object'], 'contributions':[]}]}


def fixture():
    """Construye una vertical v1.3 con herencia y sobreescritura."""
    pkg = load()
    pkg['manifest']['format_version'] = '1.3'
    pkg['traits'] = catalog()
    next(c for c in pkg['cards'] if c['id']=='alberto')['traits'] = ['steady']
    next(c for c in pkg['cards'] if c['kind']=='object')['traits'] = ['fragile']
    next(c for c in pkg['initial_state']['characters'] if c['id']=='gisela')['traits'] = []
    return pkg


def effects(pkg, operations):
    """Reemplaza una elección admitida para ensayar operaciones."""
    pkg['rules'] = []
    choice = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
    next(o for o in choice['options'] if o['id']=='prestar')['effects'] = operations
    return pkg


class TraitsAlbertoV13(unittest.TestCase):
    def test_v12_remains_unchanged(self):
        _, session = ready()
        self.assertEqual(session.export()['schema_version'], '1.2')
        self.assertNotIn('traits', session.export()['world']['characters'][0])

    def test_initial_inheritance_and_empty_override(self):
        admitted, session = ready(fixture())
        world = session.export()['world']
        self.assertEqual(world['characters'][0]['traits'], ['steady'])
        self.assertEqual(world['characters'][1]['traits'], [])
        self.assertEqual(world['objects'][0]['traits'], ['fragile'])
        self.assertEqual(world['locations'][0]['traits'], [])
        self.assertEqual(restore_session(admitted, session.export()).export(), session.export())

    def test_assignment_removal_and_restore(self):
        pkg = effects(fixture(), [{'op':'remove_trait','entity':'alberto','trait':'steady'},
                                  {'op':'assign_trait','entity':'alberto','trait':'curious'}])
        admitted, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        snapshot = session.export()
        self.assertEqual(snapshot['world']['characters'][0]['traits'], ['curious'])
        self.assertTrue(predicate(snapshot, {'has_trait':{'entity':'alberto','trait':'curious'}}, session._definitions))
        self.assertFalse(predicate(snapshot, {'has_trait':{'entity':'alberto','trait':'steady'}}, session._definitions))
        self.assertEqual(restore_session(admitted, snapshot).export(), snapshot)

    def test_capacity_violation_rolls_back(self):
        pkg = effects(fixture(), [{'op':'assign_trait','entity':'alberto','trait':'curious'}])
        pkg['traits']['max_traits'] = 1
        _, session = ready(pkg)
        previous = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'CAPACITY_EXCEEDED')
        self.assertEqual(session.export(), previous)

    def test_unknown_trait_rejected_at_admission(self):
        pkg = fixture()
        next(c for c in pkg['cards'] if c['id']=='alberto')['traits'] = ['unlisted']
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_no_catalog_rejects_assigned(self):
        pkg = fixture()
        del pkg['traits']
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_v12_rejects_traits_without_migration(self):
        pkg = fixture()
        pkg['manifest']['format_version'] = '1.2'
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_duplicated_or_unsorted_snapshot_rejected(self):
        admitted, session = ready(fixture())
        snap = session.export()
        snap['world']['characters'][0]['traits'] = ['steady','steady']
        with self.assertRaises(Exception):
            restore_session(admitted, snap)

    def test_create_instance_inherits_card(self):
        pkg = effects(fixture(), [{'op':'create_instance','card':'alberto',
                                    'instance_id':'another', 'location':'base'}])
        # El lugar corresponde a las definiciones declaradas por el juego.
        loc = pkg['initial_state']['locations'][0]['id']
        choice = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        next(o for o in choice['options'] if o['id']=='prestar')['effects'][0]['location'] = loc
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        created = next(c for c in session.export()['world']['characters'] if c['id']=='another')
        self.assertEqual(created['traits'], ['steady'])

    def test_idempotent_removal(self):
        pkg = effects(fixture(), [{'op':'remove_trait','entity':'gisela','trait':'steady'}])
        _, session = ready(pkg)
        self.assertEqual(send(session, 'prestar')['status'], 'ok')
        self.assertEqual(session.export()['world']['characters'][1]['traits'], [])

    def test_reaction_conflict_same_entity(self):
        pkg = fixture()
        for rule in pkg['rules']:
            if rule['id'] in ('confianza_2','confianza_3'):
                rule['effects'] = [{'op':'assign_trait','entity':'alberto','trait':'curious'}]
        _, session = ready(pkg)
        previous = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), previous)

    def test_unknown_condition_trait_rejected_at_admission(self):
        pkg = fixture()
        choice = next(s for n in pkg['nodes'] for s in n['steps'] if s['op']=='choice')
        choice['options'][0]['visible_if'] = {'has_trait':{'entity':'alberto','trait':'not_registered'}}
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_invalid_target_category_rejected_at_admission(self):
        pkg = effects(fixture(), [{'op':'assign_trait','entity':'casete_01','trait':'steady'}])
        # La referencia existe, pero 'steady' se restringe a personajes.
        _, session = ready(pkg)
        previous = session.export()
        self.assertEqual(send(session, 'prestar')['error']['code'],'INVALID_REFERENCE')
        self.assertEqual(session.export(), previous)

    def test_noncanonical_snapshot_rejected(self):
        admitted, session = ready(fixture())
        snapshot = session.export()
        snapshot['world']['characters'][0]['traits'] = ['steady', 'curious']
        with self.assertRaises(Exception):
            restore_session(admitted, snapshot)

    def test_v13_without_catalog_is_valid_when_no_traits(self):
        pkg = fixture()
        del pkg['traits']
        for card in pkg['cards']:
            card.pop('traits',None)
        _, session = ready(pkg)
        self.assertEqual(session.export()['world']['characters'][0]['traits'],[])
