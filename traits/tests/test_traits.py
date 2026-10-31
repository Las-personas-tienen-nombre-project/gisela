"""Pruebas neutrales y sin dependencia del ejecutor de GISELA."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from traits import (TraitsError, compile_catalog, evaluate, has_trait,
                    validate_assignments)
from traits.contracts import REQUEST_SCHEMA, SCHEMA


ROOT = Path(__file__).resolve().parents[2]


def example():
    """Catálogo de objetos y personajes sin referencias al demo."""
    return {
        'schema_version': 'traits.v1', 'traits': [
            {'id': 'fragile', 'entity_kinds': ['object'], 'contributions': [
                {'id': 'handle', 'when': {'role': 'target', 'all_tags': ['handling'],
                                          'none_tags': ['protected']},
                 'add': {'slot': 'difficulty', 'amount': 2}}]},
            {'id': 'methodical', 'entity_kinds': ['character'], 'contributions': [
                {'id': 'repair', 'when': {'role': 'actor', 'all_tags': ['technical']},
                 'add': {'slot': 'skill', 'amount': 2}}]},
            {'id': 'tired', 'entity_kinds': ['character'], 'contributions': [
                {'id': 'repair', 'when': {'role': 'actor', 'all_tags': ['technical']},
                 'add': {'slot': 'skill', 'amount': -1}}]}
        ]}


def request():
    """Dos participantes con entradas tipadas y ranuras declaradas."""
    return {'schema_version': 'traits.evaluation.v1', 'tags': ['technical', 'handling'],
            'slots': ['skill', 'difficulty'], 'participants': [
                {'entity': 'mechanic', 'kind': 'character', 'role': 'actor',
                 'traits': ['methodical', 'tired']},
                {'entity': 'device', 'kind': 'object', 'role': 'target',
                 'traits': ['fragile']} ]}


class TraitsCatalogTest(unittest.TestCase):
    def test_independent_imports(self):
        script = "import traits; import sys; assert 'gisela' not in sys.modules; assert 'dice' not in sys.modules; assert 'mary' not in sys.modules"
        result = subprocess.run([sys.executable, '-c', script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_schemas_valid(self):
        Draft202012Validator.check_schema(SCHEMA)
        Draft202012Validator.check_schema(REQUEST_SCHEMA)

    def test_default_capacity_five(self):
        self.assertEqual(5, compile_catalog(example())['max_traits'])

    def test_author_configured_capacity_and_zero(self):
        data = example()
        data['max_traits'] = 0
        plan = compile_catalog(data)
        self.assertEqual((), validate_assignments(plan, 'character', []))
        with self.assertRaises(TraitsError):
            validate_assignments(plan, 'object', ['fragile'])

    def test_duplicate_trait_definition_rejected(self):
        data = example()
        data['traits'].append(copy.deepcopy(data['traits'][0]))
        with self.assertRaises(TraitsError):
            compile_catalog(data)

    def test_duplicate_rule_id_rejected(self):
        data = example()
        data['traits'][0]['contributions'].append(copy.deepcopy(data['traits'][0]['contributions'][0]))
        with self.assertRaises(TraitsError):
            compile_catalog(data)

    def test_unknown_exclusion_rejected(self):
        data = example()
        data['traits'][0]['excludes'] = ['absent']
        with self.assertRaises(TraitsError):
            compile_catalog(data)

    def test_self_exclusion_rejected(self):
        data = example()
        data['traits'][0]['excludes'] = ['fragile']
        with self.assertRaises(TraitsError):
            compile_catalog(data)

    def test_contradictory_tags_rejected(self):
        data = example()
        data['traits'][0]['contributions'][0]['when']['none_tags'].append('handling')
        with self.assertRaises(TraitsError):
            compile_catalog(data)

    def test_duplicate_assignment_rejected(self):
        with self.assertRaises(TraitsError):
            validate_assignments(compile_catalog(example()), 'object', ['fragile', 'fragile'])

    def test_unknown_or_wrong_kind_rejected(self):
        plan = compile_catalog(example())
        for kind, trait_id in [('character', 'fragile'), ('object', 'absent')]:
            with self.subTest(kind=kind, trait=trait_id), self.assertRaises(TraitsError):
                validate_assignments(plan, kind, [trait_id])

    def test_exclusion_symmetric(self):
        data = example()
        data['traits'][1]['excludes'] = ['tired']
        plan = compile_catalog(data)
        for order in (['methodical', 'tired'], ['tired', 'methodical']):
            with self.subTest(order=order), self.assertRaises(TraitsError):
                validate_assignments(plan, 'character', order)

    def test_capacity_counts_all_assigned(self):
        data = example()
        data['max_traits'] = 1
        with self.assertRaisesRegex(TraitsError, 'CAPACITY_EXCEEDED'):
            validate_assignments(compile_catalog(data), 'character', ['methodical', 'tired'])

    def test_empty_catalog_and_pure_presence(self):
        plan = compile_catalog({'schema_version': 'traits.v1', 'traits': []})
        self.assertEqual((), validate_assignments(plan, 'character', []))
        self.assertFalse(has_trait([], 'fragile'))
        self.assertTrue(has_trait(['fragile'], 'fragile'))

    def test_rejects_unknown_fields_and_wrong_version(self):
        for key, value in [('unknown', True), ('schema_version', 'traits.v2')]:
            data = example()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(TraitsError):
                compile_catalog(data)


class TraitsEvaluationTest(unittest.TestCase):
    def setUp(self):
        self.plan = compile_catalog(example())

    def test_additive_totals_with_signed_amounts(self):
        result = evaluate(self.plan, request())
        self.assertEqual({'difficulty': 2, 'skill': 1}, result['totals'])
        self.assertEqual(3, len(result['contributions']))

    def test_result_independent_of_order(self):
        data = example()
        data['traits'].reverse()
        shuffled = request()
        shuffled['participants'].reverse()
        shuffled['participants'][1]['traits'].reverse()
        self.assertEqual(evaluate(self.plan, request()), evaluate(compile_catalog(data), shuffled))

    def test_no_context_or_role_match(self):
        for variant in ('role', 'tags'):
            data = request()
            if variant == 'role':
                data['participants'][0]['role'] = 'target'
                data['participants'][1]['role'] = 'actor'
            else:
                data['tags'] = ['inspection']
            with self.subTest(variant=variant):
                self.assertEqual({}, evaluate(self.plan, data)['totals'])

    def test_negative_tag_blocks_contribution(self):
        data = request()
        data['tags'].append('protected')
        self.assertEqual({'skill': 1}, evaluate(self.plan, data)['totals'])

    def test_unaccepted_slot_is_error(self):
        data = request()
        data['slots'] = ['skill']
        with self.assertRaisesRegex(TraitsError, 'Ranura no admitida'):
            evaluate(self.plan, data)

    def test_duplicate_participant_is_error(self):
        data = request()
        data['participants'].append(copy.deepcopy(data['participants'][0]))
        with self.assertRaises(TraitsError):
            evaluate(self.plan, data)

    def test_unknown_assignment_is_error(self):
        data = request()
        data['participants'][1]['traits'] = ['absent']
        with self.assertRaises(TraitsError):
            evaluate(self.plan, data)

    def test_invalid_request_is_error(self):
        data = request()
        del data['slots']
        with self.assertRaises(TraitsError):
            evaluate(self.plan, data)

    def test_inputs_not_mutated_repeated_calls_identical(self):
        definition, data = example(), request()
        before = json.dumps([definition, data], sort_keys=True)
        plan = compile_catalog(definition)
        first = evaluate(plan, data)
        self.assertEqual(first, evaluate(plan, data))
        self.assertEqual(before, json.dumps([definition, data], sort_keys=True))

    def test_empty_participants_yield_empty_totals(self):
        data = request()
        data['participants'] = []
        self.assertEqual({'contributions': [], 'totals': {},
                          'schema_version': 'traits.result.v1'}, evaluate(self.plan, data))

    def test_slots_and_tags_produce_no_unrequested_effects(self):
        data = request()
        data['tags'] = ['technical']
        data['slots'] = ['skill']
        result = evaluate(self.plan, data)
        self.assertEqual({'skill': 1}, result['totals'])


if __name__ == '__main__':
    unittest.main()
