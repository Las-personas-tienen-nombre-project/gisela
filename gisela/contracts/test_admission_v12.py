"""Proveniencia exacta y admisión fail-closed sin ejecutor narrativo."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from admit_package import PackageRejected, admit_package, admit_package_file, cli
from semantic_validator import Validator
from canonical import package_digest

R = Path(__file__).parent
PACKAGE = json.loads((R/'example.package.json').read_text(encoding='utf8'))
NODE = json.loads((R/'examples/session_node.json').read_text(encoding='utf8'))
PENDING = json.loads((R/'semantic_examples/session_pending_source_valid.json').read_text(encoding='utf8'))
SCENE_PACKAGE = json.loads((R/'semantic_examples/package_with_scene_action.json').read_text(encoding='utf8'))


def code(issues, expected):
    assert expected in {d.code for d in issues}, (expected, issues)


class ProvenanceContracts(unittest.TestCase):
    def valid_session(self, package, snapshot):
        snapshot = copy.deepcopy(snapshot)
        snapshot["package_digest"] = package_digest(package)
        issues = Validator().validate_session(snapshot,package)
        self.assertFalse([d for d in issues if d.severity=='error'], issues)

    def test_selected_options_qualified_by_step_and_node(self):
        sess = copy.deepcopy(NODE)
        sess['history']['executions'][0]['selected_options']=[{'step_id':'decision','option_id':'prestar'}]
        self.valid_session(PACKAGE, sess)

    def test_selected_option_with_nonexistent_step(self):
        sess=copy.deepcopy(NODE)
        sess['history']['executions'][0]['selected_options']=[{'step_id':'inexistente','option_id':'prestar'}]
        code(Validator().validate_session(sess, PACKAGE),'UNKNOWN_CHOICE_STEP')

    def test_selected_option_wrong_step_type(self):
        sess=copy.deepcopy(NODE)
        sess['history']['executions'][0]['selected_options']=[{'step_id':'saludo','option_id':'prestar'}]
        code(Validator().validate_session(sess,PACKAGE),'UNKNOWN_CHOICE_STEP')

    def test_selected_option_wrong_option(self):
        sess=copy.deepcopy(NODE)
        sess['history']['executions'][0]['selected_options']=[{'step_id':'decision','option_id':'inexistente'}]
        code(Validator().validate_session(sess,PACKAGE),'UNKNOWN_SELECTED_OPTION')

    def test_unqualified_option_strings_are_invalid_in_v12(self):
        sess=copy.deepcopy(NODE)
        sess['history']['executions'][0]['selected_options']=['prestar']
        code(Validator().validate_session(sess,PACKAGE),'SCHEMA_INVALID')

    def test_same_option_id_in_distinct_choice_steps_is_unambiguous(self):
        pkg=copy.deepcopy(PACKAGE)
        pkg['nodes'][0]['steps'].append({'id':'decision_repetida','op':'choice','options':[{'id':'prestar','label':{'text':'Repetir'}}]})
        sess=copy.deepcopy(NODE)
        sess['history']['executions'][0]['selected_options']=[
            {'step_id':'decision','option_id':'prestar'},
            {'step_id':'decision_repetida','option_id':'prestar'}]
        self.valid_session(pkg,sess)

    def test_semantic_selected_option_fixture(self):
        snapshot=json.loads((R/'semantic_examples/session_node_selected_valid.json').read_text('utf8'))
        self.valid_session(PACKAGE,snapshot)

    def test_semantic_element_action_fixture(self):
        pkg=json.loads((R/'semantic_examples/package_with_element_action.json').read_text('utf8'))
        snapshot=json.loads((R/'semantic_examples/session_pending_element_valid.json').read_text('utf8'))
        self.valid_session(pkg,snapshot)

    def test_duplicate_action_ids_across_owners_accepted(self):
        pkg=copy.deepcopy(SCENE_PACKAGE)
        pkg['scenes'][0]['elements'][0]['actions']=[{'id':'examinar','label':{'text':'Mirar escritorio'}}]
        self.assertFalse([d for d in Validator().validate_package(pkg) if d.severity=='error'])
        sess=copy.deepcopy(PENDING)
        # no element -> scene-level action
        self.valid_session(pkg,sess)
        # explicit element -> same ID, but a different, unambiguous action
        sess['pending_transaction']['source']['element']='escritorio'
        self.valid_session(pkg,sess)

    def test_element_action_requires_element_source(self):
        pkg=copy.deepcopy(SCENE_PACKAGE)
        pkg['scenes'][0]['actions']=[]
        pkg['scenes'][0]['elements'][0]['actions']=[{'id':'examinar','label':{'text':'Mirar escritorio'}}]
        sess=copy.deepcopy(PENDING)
        code(Validator().validate_session(sess,pkg),'PENDING_SOURCE')
        sess['pending_transaction']['source']['element']='escritorio'
        self.valid_session(pkg,sess)

    def test_unknown_element_rejected(self):
        sess=copy.deepcopy(PENDING)
        sess['pending_transaction']['source']['element']='un_mueble_inexistente'
        code(Validator().validate_session(sess,SCENE_PACKAGE),'PENDING_SOURCE')

    def test_action_not_owned_by_element_rejected(self):
        sess=copy.deepcopy(PENDING)
        sess['pending_transaction']['source']['element']='escritorio'
        code(Validator().validate_session(sess,SCENE_PACKAGE),'PENDING_SOURCE')

    def test_duplicate_actions_on_same_owner_rejected(self):
        pkg=copy.deepcopy(SCENE_PACKAGE)
        pkg['scenes'][0]['elements'][0]['actions']=[{'id':'mirar','label':{'text':'Mirar'}}]*2
        code(Validator().validate_package(pkg),'DUPLICATE_ID')


class PackageAdmission(unittest.TestCase):
    def test_clean_package_is_admitted(self):
        admitted=admit_package(PACKAGE)
        self.assertEqual(admitted.materialize(),PACKAGE)

    def test_admitted_copy_not_affected_by_caller_mutation(self):
        pkg=copy.deepcopy(PACKAGE)
        admitted=admit_package(pkg)
        pkg['manifest']['id']='changed'
        derived=admitted.materialize();derived['manifest']['id']='another'
        self.assertEqual(admitted.materialize()['manifest']['id'],PACKAGE['manifest']['id'])

    def test_unknown_reference_blocks_admission(self):
        pkg=copy.deepcopy(PACKAGE)
        pkg['nodes'][0]['steps'][0]['scene']='escena_ausente'
        with self.assertRaises(PackageRejected) as raised:admit_package(pkg)
        code(raised.exception.diagnostics,'UNKNOWN_SCENE')

    def test_invalid_operator_blocks_admission(self):
        pkg=copy.deepcopy(PACKAGE)
        pkg['nodes'][0]['steps'][0]['op']='python'
        with self.assertRaises(PackageRejected) as raised:admit_package(pkg)
        code(raised.exception.diagnostics,'SCHEMA_INVALID')

    def test_prior_version_is_not_auto_migrated(self):
        pkg=copy.deepcopy(PACKAGE);pkg['manifest']['format_version']='1.1'
        with self.assertRaises(PackageRejected):admit_package(pkg)

    def test_file_loader_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'duplicate.json'
            path.write_text('{"manifest":{},"manifest":{}}',encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Clave JSON duplicada'):admit_package_file(path)

    def test_file_loader_rejects_nan_not_valid_json(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'nan.json';path.write_text('{"x":NaN}',encoding='utf8')
            with self.assertRaisesRegex(ValueError,'Constante JSON no permitida'):admit_package_file(path)

    def test_cli_valid_file_exit_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'valid.json';path.write_text(json.dumps(PACKAGE),encoding='utf8')
            self.assertEqual(cli([str(path),'--json']),0)

    def test_cli_semantic_error_exit_one(self):
        with tempfile.TemporaryDirectory() as temp:
            pkg=copy.deepcopy(PACKAGE)
            pkg['nodes'][0]['steps'][0]['scene']='escena_ausente'
            path=Path(temp)/'invalid.json';path.write_text(json.dumps(pkg),encoding='utf8')
            self.assertEqual(cli([str(path),'--json']),1)

    def test_cli_invalid_json_exit_two(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'invalid.json';path.write_text('{',encoding='utf8')
            self.assertEqual(cli([str(path),'--json']),2)


if __name__=='__main__': unittest.main()
