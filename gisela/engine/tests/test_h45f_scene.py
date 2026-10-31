"""H4.5f: escenas físicas, presencia, inspección y autorización de GLAUQUIR."""
from __future__ import annotations
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest
from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.contracts.semantic_validator import Validator
from gisela.engine.runtime import new_session, restore_session, EngineFailure
from gisela.engine.world_base import WorldError
from tools.cli_interactive import TextClient

FILE = 'gisela/packages/h4_exploracion.package.json'


def base():
    """Copia profunda de las definiciones de H4, sin mutar el paquete real."""
    return admit_package_file(Path(FILE)).materialize()


def remote(pkg: dict) -> dict:
    """Añade otro lugar físico y una escena para probar traslados."""
    pkg['initial_state']['locations'].append({'id':'patio', 'card':'porteria'})
    pkg['scenes'].append({'id':'patio_escena', 'location':'patio',
                          'title':{'text':'Patio'}, 'actions':[]})
    return pkg


def start(pkg: dict):
    """Exige admisión real y una sesión nueva."""
    admitted = admit_package(pkg)
    return admitted, new_session(admitted)


def offer(session, identifier: str) -> dict:
    """Construye Act únicamente con una acción publicada."""
    view = session.observe()
    action = next(a for a in view['actions'] if a['id'] == identifier)
    return {'session_id':view['session_id'], 'revision':view['revision'],
            'action_id':action['action_id']}


def scene_action(pkg: dict, identifier: str, effects: list) -> None:
    """Añade una acción sencilla a la primera escena del paquete."""
    pkg['scenes'][0]['actions'].append({'id':identifier, 'label':{'text':identifier},
                                        'effects':effects})


def element(pkg: dict, identifier: str, entity: str | None = None) -> dict:
    """Inserta un elemento con descripción y acción verificable."""
    entry = {'id':identifier, 'label':{'text':identifier},
             'description':{'text':'Descripción visible de ' + identifier},
             'actions':[{'id':'inspeccionar_' + identifier,
                         'label':{'text':'Inspeccionar ' + identifier},
                         'effects':[{'op':'record_fact','fact':'mesa_examinada'}]}]}
    if entity is not None:
        entry['entity'] = entity
    pkg['scenes'][0]['elements'].append(entry)
    return entry


class H45F1Location(unittest.TestCase):
    """La escena es contexto de GISELA, el lugar pertenece a ALBERTO."""
    def test_unknown_scene_location_rejected_by_admission(self):
        pkg = base()
        pkg['scenes'][0]['location'] = 'lugar_inexistente'
        codes = {i.code for i in Validator().validate_package(pkg)}
        self.assertIn('UNKNOWN_ENTITY', codes)

    def test_dynamic_scene_location_rejected(self):
        pkg = base()
        pkg['scenes'][0]['location'] = '$actor'
        codes = {i.code for i in Validator().validate_package(pkg)}
        self.assertIn('UNBOUND_SCENE_LOCATION', codes)

    def test_initial_scene_and_player_location_must_match(self):
        pkg = remote(base())
        pkg['initial_state']['characters'][0]['location'] = 'patio'
        codes = {i.code for i in Validator().validate_package(pkg)}
        self.assertIn('SCENE_LOCATION_MISMATCH', codes)

    def test_invalid_restore_is_rejected_before_observe(self):
        pkg = remote(base())
        admitted, session = start(pkg)
        snapshot = session.export()
        snapshot['world']['characters'][0]['location'] = 'patio'
        errors = {i.code for i in Validator().validate_session(snapshot, pkg)}
        self.assertIn('SCENE_LOCATION_MISMATCH', errors)
        with self.assertRaises(EngineFailure):
            restore_session(admitted, snapshot)

    def test_set_scene_without_movement_rolls_back_atomically(self):
        pkg = remote(base())
        scene_action(pkg, 'ir_sin_mover', [{'op':'set_scene', 'scene':'patio_escena'}])
        _, session = start(pkg)
        before = session.export()
        result = session.act(offer(session, 'ir_sin_mover'))
        self.assertEqual(result['status'], 'error')
        self.assertEqual(session.export(), before)

    def test_coordinated_move_and_scene_survive_restore(self):
        pkg = remote(base())
        scene_action(pkg, 'ir_con_mover', [
            {'op':'move_character', 'character':'alberto', 'location':'patio'},
            {'op':'set_scene', 'scene':'patio_escena'}])
        admitted, session = start(pkg)
        self.assertEqual(session.act(offer(session, 'ir_con_mover'))['status'], 'ok')
        self.assertEqual(session.observe()['scene'], 'patio_escena')
        self.assertEqual(restore_session(admitted, session.export()).observe(), session.observe())

    def test_scene_without_place_uses_declarative_visibility(self):
        pkg = remote(base())
        pkg['scenes'][0].pop('location')
        pkg['initial_state']['characters'][1]['location'] = 'patio'
        _, session = start(pkg)
        self.assertIn('gisela', [a['id'] for a in session.observe()['actors']])


class H45F2Presence(unittest.TestCase):
    """La información física debe estar presente y autorizada."""
    def test_departed_actor_disappears_from_actors_and_cards(self):
        pkg = remote(base())
        scene_action(pkg, 'mover_gisela', [
            {'op':'move_character', 'character':'gisela', 'location':'patio'}])
        admitted, session = start(pkg)
        self.assertIn('gisela', [a['id'] for a in session.observe()['actors']])
        self.assertEqual(session.act(offer(session, 'mover_gisela'))['status'], 'ok')
        self.assertNotIn('gisela', [a['id'] for a in session.observe()['actors']])
        self.assertNotIn('gisela', [c['id'] for c in session.observe()['cards']])
        self.assertEqual(restore_session(admitted, session.export()).observe(), session.observe())

    def test_owned_object_is_visible_but_foreign_inventory_is_not(self):
        pkg = base()
        element(pkg, 'casete_visible', 'casete_01')
        pkg['initial_state']['objects'].append({'id':'casete_gisela',
                'card':'casete', 'owner':'gisela'})
        element(pkg, 'casete_ajeno', 'casete_gisela')
        _, session = start(pkg)
        ids = [e['id'] for e in session.observe()['elements']]
        self.assertIn('casete_visible', ids)
        self.assertNotIn('casete_ajeno', ids)
        with self.assertRaises(WorldError):
            session.read_public('casete_gisela')

    def test_transfer_hides_object_actions_and_read_public(self):
        pkg = base()
        element(pkg, 'casete_visible', 'casete_01')
        element(pkg, 'cuadro')
        _, session = start(pkg)
        offers = session.observe()['actions']
        previous = next(a for a in offers if a['id'] == 'inspeccionar_casete_visible')
        other = next(a for a in offers if a['id'] == 'inspeccionar_cuadro')
        self.assertEqual(session.act(offer(session, 'tomar'))['status'], 'ok')
        after = session.observe()
        self.assertNotIn('casete_visible', [e['id'] for e in after['elements']])
        self.assertEqual(next(a for a in after['actions'] if a['id'] == 'inspeccionar_cuadro')['action_id'], other['action_id'])
        forged = {'session_id':after['session_id'], 'revision':after['revision'],
                  'action_id':previous['action_id']}
        before = session.export()
        self.assertEqual(session.act(forged)['status'], 'error')
        self.assertEqual(session.export(), before)
        with self.assertRaises(WorldError):
            session.read_public('casete_01')

    def test_duplicate_literal_actor_rejected(self):
        pkg = base()
        pkg['scenes'][0]['actors'].append({'character':'gisela'})
        codes = {i.code for i in Validator().validate_package(pkg)}
        self.assertIn('DUPLICATE_ACTOR', codes)

    def test_dynamic_actor_contract_is_not_silently_executed(self):
        pkg = base()
        pkg['scenes'][0]['actors'][0]['character'] = {'query':{
            'kind':'character', 'selection':'one', 'where':{'constant':True}}}
        issues = Validator().validate_package(pkg)
        self.assertEqual([i for i in issues if i.severity == 'error'], [])
        admitted = admit_package(pkg)
        with self.assertRaises(EngineFailure):
            new_session(admitted)

    def test_actor_element_follows_character_location(self):
        pkg = remote(base())
        element(pkg, 'gisela_visible', 'gisela')
        scene_action(pkg, 'mover_gisela', [
            {'op':'move_character', 'character':'gisela', 'location':'patio'}])
        _, session = start(pkg)
        self.assertEqual(session.act(offer(session, 'mover_gisela'))['status'], 'ok')
        self.assertNotIn('gisela_visible', [e['id'] for e in session.observe()['elements']])
        self.assertNotIn('inspeccionar_gisela_visible', [a['id'] for a in session.observe()['actions']])

    def test_unbound_entity_and_remote_location_rejected(self):
        pkg = remote(base())
        element(pkg, 'objetivo_indirecto', '$actor')
        element(pkg, 'otro_lugar', 'patio')
        codes = {i.code for i in Validator().validate_package(pkg)}
        self.assertIn('UNBOUND_SCENE_ENTITY', codes)
        self.assertIn('SCENE_REMOTE_LOCATION', codes)


class H45F3Inspection(unittest.TestCase):
    """GLAUQUIR lee textos de elementos sin mutar el mundo."""
    def test_element_description_is_authorized_and_conforms(self):
        pkg = base()
        element(pkg, 'lavamanos')
        admitted, session = start(pkg)
        item = next(e for e in session.observe()['elements'] if e['id'] == 'lavamanos')
        self.assertEqual(item['description'], 'Descripción visible de lavamanos')
        self.assertTrue(Validator().check_schema('observe', session.observe()))
        self.assertEqual(restore_session(admitted, session.export()).observe(), session.observe())

    def test_element_inspection_does_not_run_authored_action(self):
        pkg = base()
        element(pkg, 'lavamanos')
        _, session = start(pkg)
        before = session.export()
        with redirect_stdout(StringIO()) as output:
            result = TextClient(session)._command(session.observe(), 'mirar lavamanos')
        self.assertIs(result, False)
        self.assertIn('Descripción visible de lavamanos', output.getvalue())
        self.assertEqual(session.export(), before)

    def test_examinar_prefers_authored_interaction(self):
        pkg = base()
        element(pkg, 'lavamanos')
        _, session = start(pkg)
        answer = TextClient(session)._command(session.observe(), 'examinar lavamanos')
        self.assertEqual(answer['id'], 'inspeccionar_lavamanos')

    def test_hidden_element_description_never_reaches_client(self):
        pkg = base()
        entry = element(pkg, 'lavamanos')
        entry['visible_if'] = {'constant':False}
        _, session = start(pkg)
        view = session.observe()
        self.assertNotIn('lavamanos', [e['id'] for e in view['elements']])
        with redirect_stdout(StringIO()) as output:
            TextClient(session)._command(view, 'examinar lavamanos')
        self.assertNotIn('Descripción visible', output.getvalue())

    def test_element_without_description_uses_public_card(self):
        pkg = base()
        entry = element(pkg, 'casete_visible', 'casete_01')
        entry.pop('description')
        _, session = start(pkg)
        before = session.export()
        with redirect_stdout(StringIO()) as output:
            result = TextClient(session)._command(session.observe(), 'mirar casete_visible')
        self.assertIs(result, False)
        self.assertIn('Casete', output.getvalue())
        self.assertEqual(session.export(), before)


if __name__ == '__main__':
    unittest.main()
