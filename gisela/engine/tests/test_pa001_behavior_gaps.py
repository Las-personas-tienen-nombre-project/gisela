"""PA-001: pruebas comportamentales focalizadas I04, I05, I06 e I16."""
import copy
from pathlib import Path
import unittest

from gisela.contracts.admit_package import admit_package, admit_package_file, PackageRejected
from gisela.engine.runtime import new_session
from gisela.engine.conditions import predicate
from gisela.engine.world_base import WorldError

PACKAGE = Path(__file__).resolve().parents[2] / 'packages' / 'mvp_casete.package.json'


class DefinitionIsolation(unittest.TestCase):
    def test_mutating_source_after_admission_does_not_change_running_session(self):
        source = admit_package_file(PACKAGE).materialize()
        admitted = admit_package(source)
        session = new_session(admitted)
        view, snapshot = session.observe(), session.export()
        source['nodes'][0]['steps'][0]['text'] = {'text': 'ALTERADO'}
        source['cards'].clear()
        self.assertEqual(session.observe(), view)
        self.assertEqual(session.export(), snapshot)
        self.assertNotEqual(admitted.materialize()['cards'], [])

    def test_mutating_materialized_package_does_not_change_session(self):
        admitted = admit_package_file(PACKAGE)
        session = new_session(admitted)
        view = session.observe()
        external = admitted.materialize()
        external['nodes'].clear()
        external['rules'].clear()
        self.assertEqual(session.observe(), view)
        self.assertTrue(admitted.materialize()['nodes'])

    def test_exported_state_is_not_definition_alias(self):
        admitted = admit_package_file(PACKAGE)
        session = new_session(admitted)
        snapshot = session.export()
        snapshot['world']['characters'][0]['location'] = 'otro'
        self.assertNotEqual(session.export()['world']['characters'][0]['location'], 'otro')
        self.assertEqual(admitted.materialize()['initial_state']['characters'][0]['location'], 'porteria')


class ConditionPurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = new_session(admit_package_file(PACKAGE))

    def test_each_supported_world_leaf_is_read_only(self):
        state = self.session.export()
        cases = [
            {'has_fact': 'alberto_presto_casete'},
            {'knows': {'character': 'alberto', 'fact': 'alberto_presto_casete'}},
            {'believes': {'character': 'alberto', 'claim': 'algo', 'value': True}},
            {'has_skill': {'character': 'alberto', 'skill': 'ninguna', 'zone': 'either'}},
            {'has_effect': {'target': 'alberto', 'effect': 'ninguno'}},
            {'owns': {'object': 'casete_01', 'owner': 'alberto'}},
            {'at_location': {'character': 'alberto', 'location': 'porteria'}},
            {'compare': {'left': {'var': {'scope': 'session', 'key': 'casete_prestado'}},
                         'op': 'eq', 'right': {'literal': False}}},
            {'compare': {'left': {'clock': 'world_time'}, 'op': 'eq',
                         'right': {'clock': 'world_time'}}},
        ]
        for cond in cases:
            with self.subTest(cond=cond):
                before = copy.deepcopy(state)
                self.assertIsInstance(predicate(state, cond, self.session._definitions), bool)
                self.assertEqual(state, before)

    def test_invalid_world_reference_does_not_create_an_entity(self):
        state = self.session.export()
        before = copy.deepcopy(state)
        with self.assertRaises(WorldError):
            predicate(state, {'owns': {'object': 'inexistente', 'owner': 'alberto'}},
                      self.session._definitions)
        self.assertEqual(state, before)


class AuthorCodeRejection(unittest.TestCase):
    def test_python_step_is_rejected_at_admission(self):
        package = admit_package_file(PACKAGE).materialize()
        package['nodes'][0]['steps'][0] = {'id': 'intro', 'op': 'python',
                                           'code': '__import__("os").system("true")'}
        with self.assertRaises(PackageRejected):
            admit_package(package)

    def test_python_effect_is_rejected_at_admission(self):
        package = admit_package_file(PACKAGE).materialize()
        package['nodes'][0]['steps'][3]['options'][0]['effects'].append(
            {'op': 'python', 'code': '__import__("os").system("true")'})
        with self.assertRaises(PackageRejected):
            admit_package(package)

    def test_extra_executable_field_is_rejected_at_admission(self):
        package = admit_package_file(PACKAGE).materialize()
        package['nodes'][0]['steps'][0]['python'] = 'print("unexpected")'
        with self.assertRaises(PackageRejected):
            admit_package(package)


if __name__ == '__main__':
    unittest.main()
