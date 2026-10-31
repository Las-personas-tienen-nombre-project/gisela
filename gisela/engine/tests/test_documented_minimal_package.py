"""Comprueba que el primer paquete documentado admite sus dos recorridos."""
from pathlib import Path
import unittest

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session


PACKAGE = Path(__file__).resolve().parents[2] / 'packages' / 'ejemplo_minimo.package.json'


class DocumentedMinimalPackageTest(unittest.TestCase):
    def test_both_endings(self):
        admitted = admit_package_file(PACKAGE)
        for choice, ending in (('abrir', 'adentro'), ('seguir', 'afuera')):
            with self.subTest(choice=choice):
                session = new_session(admitted)
                seen_choice = False
                for _ in range(4):
                    view = session.observe()
                    if view['status'] == 'ended':
                        break
                    if view['content']['kind'] == 'choice':
                        seen_choice = True
                    action = next((item for item in view['actions'] if item['id'] == choice),
                                  view['actions'][0])
                    result = session.act({
                        'session_id': view['session_id'],
                        'revision': view['revision'],
                        'action_id': action['action_id'],
                    })
                    self.assertEqual(result['status'], 'ok')
                self.assertTrue(seen_choice)
                self.assertEqual(session.observe()['status'], 'ended')
                self.assertEqual(session.export()['ending'], ending)


if __name__ == '__main__':
    unittest.main()
