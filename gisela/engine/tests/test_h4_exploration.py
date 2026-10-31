"""H4: exploración, acciones, consultas, CLI y garantías transaccionales."""
from __future__ import annotations
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session, restore_session
from gisela.engine.world_base import WorldError

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / 'gisela/packages/h4_exploracion.package.json'


def base():
    """Devuelve una definición modificable, no la sesión interna."""
    return admit_package_file(PACKAGE).materialize()


def start(pkg=None):
    """Inicia una entrada de escena con admisión real."""
    admitted = admit_package(pkg) if pkg else admit_package_file(PACKAGE)
    return admitted, new_session(admitted)


def send(session, identifier: str):
    """Ejecuta la acción ofertada, respetando la revisión vigente."""
    view = session.observe()
    action = next(a for a in view['actions'] if a['id'] == identifier)
    return session.act({'session_id':view['session_id'], 'revision':view['revision'],
                        'action_id':action['action_id']})


def scene_action(pkg: dict, identifier: str) -> dict:
    """Localiza una acción de escena en el paquete de prueba."""
    return next(item for item in pkg['scenes'][0]['actions'] if item['id'] == identifier)


class H41Exploration(unittest.TestCase):
    def test_scene_entry_needs_no_node_turn(self):
        _, session = start()
        view = session.observe()
        self.assertEqual((view['status'], view['scene'], view['turn']),
                         ('exploring', 'porteria_noche', 0))
        self.assertEqual(view['actors'][0]['id'], 'gisela')
        self.assertEqual(view['elements'][0]['id'], 'mesa')
        self.assertEqual(len(view['actions']), 4)

    def test_scene_entry_without_initial_scene(self):
        pkg = base()
        pkg['initial_state'].pop('current_scene', None)
        _, session = start(pkg)
        self.assertEqual(session.observe()['scene'], 'porteria_noche')

    def test_observe_is_pure_and_restore_is_identical(self):
        admitted, session = start()
        before = session.export()
        self.assertEqual(session.observe(), session.observe())
        self.assertEqual(session.export(), before)
        self.assertEqual(restore_session(admitted, before).observe(), session.observe())

    def test_hidden_element_hides_actions(self):
        pkg = base()
        pkg['scenes'][0]['elements'][0]['visible_if'] = {'constant':False}
        _, session = start(pkg)
        self.assertEqual(session.observe()['elements'], [])
        self.assertNotIn('tomar', [a['id'] for a in session.observe()['actions']])

    def test_duplicate_action_id_across_owners_is_unambiguous(self):
        pkg = base()
        scene_action(pkg, 'ir_pasillo')['id'] = 'examinar'
        _, session = start(pkg)
        actions = [a for a in session.observe()['actions'] if a['id'] == 'examinar']
        self.assertEqual(len(actions), 2)
        self.assertEqual(len({a['action_id'] for a in actions}), 2)

    def test_equal_action_names_keep_exact_provenance(self):
        pkg = base()
        scene_action(pkg, 'ir_pasillo')['id'] = 'examinar'
        _, session = start(pkg)
        scene_offer, element_offer = [a for a in session.observe()['actions']
                                      if a['id'] == 'examinar']
        current = session.observe()
        reply = session.act({'session_id':current['session_id'],
                             'revision':current['revision'],
                             'action_id':element_offer['action_id']})
        self.assertEqual(reply['status'], 'ok')
        detail = session.export()['history']['trace'][-1]['detail']
        self.assertEqual(detail['element'], 'mesa')
        self.assertEqual(detail['scene'], 'porteria_noche')
        self.assertEqual(session.observe()['scene'], 'porteria_noche')

    def test_observation_respects_schema(self):
        from gisela.contracts.semantic_validator import Validator
        _, session = start()
        self.assertTrue(Validator().check_schema('observe', session.observe()))
        send(session, 'ir_pasillo')
        self.assertTrue(Validator().check_schema('observe', session.observe()))

    def test_disabled_action_is_not_executable(self):
        _, session = start()
        self.assertEqual(send(session, 'tomar')['status'], 'ok')
        before = session.export()
        disabled = next(a for a in session.observe()['actions'] if a['id'] == 'tomar')
        self.assertFalse(disabled['enabled'])
        result = session.act({'session_id':before['session_id'], 'revision':before['revision'],
                              'action_id':disabled['action_id']})
        self.assertEqual(result['error']['code'], 'INVALID_ACTION')
        self.assertEqual(session.export(), before)


class H42World(unittest.TestCase):
    def test_inspect_transfer_move_and_dialogue(self):
        admitted, session = start()
        self.assertEqual(send(session, 'examinar')['status'], 'ok')
        self.assertEqual(send(session, 'tomar')['status'], 'ok')
        self.assertEqual(session.debug_query({'kind':'entity','entity':'casete_01'})['owner'], 'gisela')
        self.assertEqual(send(session, 'ir_pasillo')['status'], 'ok')
        self.assertEqual(session.observe()['scene'], 'pasillo')
        self.assertEqual(send(session, 'regresar')['status'], 'ok')
        self.assertEqual(send(session, 'conversar')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'narrate')
        self.assertEqual(restore_session(admitted, session.export()).export(), session.export())

    def test_stale_action_rejected_after_movement(self):
        _, session = start()
        before = session.observe()
        selected = before['actions'][0]
        self.assertEqual(send(session, 'ir_pasillo')['status'], 'ok')
        result = session.act({'session_id':before['session_id'], 'revision':before['revision'],
                              'action_id':selected['action_id']})
        self.assertEqual(result['error']['code'], 'STALE_PROJECTION')

    def test_failure_rolls_back_transfer(self):
        pkg = base()
        scene_action(pkg, 'ir_pasillo')['effects'] = [
            {'op':'transfer', 'object':'casete_01','from':'alberto','to':'gisela'},
            {'op':'add', 'target':{'stat':{'character':'alberto','name':'strength',
                                        'component':'current'}}, 'value':{'literal':1000}}]
        _, session = start(pkg)
        before = session.export()
        self.assertEqual(send(session, 'ir_pasillo')['status'], 'error')
        self.assertEqual(session.export(), before)

    def test_unknown_scene_rolls_back(self):
        pkg = base()
        scene_action(pkg, 'ir_pasillo')['effects'] = [
            {'op':'set_scene','scene':'desconocida'}]
        # El admisor rechaza la referencia antes de crear la sesión.
        from gisela.contracts.admit_package import PackageRejected
        with self.assertRaises(PackageRejected):
            start(pkg)

    def test_scene_actions_can_suspend_cancel_and_restore(self):
        pkg = base()
        scene_action(pkg, 'ir_pasillo')['effects'] = [
            {'op':'grant_skill', 'character':'alberto','skill':'gesto',
             'overflow':'require_choice'}]
        pkg['initial_state']['capacities'][0]['hand'] = 1
        admitted, session = start(pkg)
        before = session.export()
        self.assertEqual(send(session, 'ir_pasillo')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'pending_transaction')
        self.assertEqual(session.export()['world'], before['world'])
        restored = restore_session(admitted, session.export())
        self.assertEqual(send(restored, 'cancelar')['status'], 'ok')
        self.assertEqual(restored.export()['world'], before['world'])
        self.assertEqual(send(session, 'gesto_01')['status'], 'ok')
        self.assertEqual(session.observe()['content']['kind'], 'exploring')


class H43Queries(unittest.TestCase):
    def test_properties_relations_knowledge_and_skills(self):
        _, session = start()
        character = session.debug_query({'kind':'character','character':'alberto'})
        self.assertEqual(character['id'], 'alberto')
        self.assertIn('skills', character)
        relationship = session.debug_query({'kind':'relationship','from':'alberto',
                                            'to':'gisela','key':'confianza'})
        self.assertEqual(relationship['value'], 0)
        prop = session.debug_query({'kind':'property','entity':'casete_01','key':'estado'})
        self.assertEqual(prop['value'], 'guardado')
        sheet = session.debug_query({'kind':'scoresheet','character':'alberto'})
        self.assertEqual(sheet['character'], 'alberto')
        self.assertEqual(sheet['stats'][0]['base'], 6)

    def test_queries_do_not_modify_world(self):
        _, session = start()
        before = session.export()
        session.debug_query({'kind':'character','character':'gisela'})
        session.debug_query({'kind':'relationship','from':'gisela','to':'alberto','key':'confianza'})
        session.debug_query({'kind':'facts'})
        self.assertEqual(session.export(), before)
        with self.assertRaises(WorldError):
            session.debug_query({'kind':'property','entity':'gisela','key':'no_existe'})

    def test_queries_reject_unknown_fields(self):
        _, session = start()
        with self.assertRaises(WorldError):
            session.debug_query({'kind':'character','character':'alberto','debug':True})


class H44Console(unittest.TestCase):
    def test_console_autoplay_scene(self):
        result = subprocess.run([sys.executable, 'tools/play_mvp.py', '--auto', '--package',
                                 str(PACKAGE), '--choose', 'conversar'], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Escena: porteria_noche', result.stdout)
        self.assertIn('Final:', result.stdout)

    def test_console_save_load_and_inspect(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'sesion.json'
            lines = f'consultar scoresheet alberto\nguardar {target}\n1\ncargar {target}\n2\nsalir\n'
            result = subprocess.run([sys.executable, 'tools/play_mvp.py', '--developer',
                                     '--package', str(PACKAGE)], cwd=ROOT, input=lines,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.exists())
            self.assertIn('"character": "alberto"', result.stdout)
            self.assertGreaterEqual(result.stdout.count('Escena: porteria_noche'), 2)
            reload = subprocess.run([sys.executable, 'tools/play_mvp.py', '--package',
                                     str(PACKAGE), '--restore', str(target), '--auto',
                                     '--choose', 'conversar'], cwd=ROOT,
                                    capture_output=True, text=True)
            self.assertEqual(reload.returncode, 0, reload.stderr)


if __name__ == '__main__':
    unittest.main()
