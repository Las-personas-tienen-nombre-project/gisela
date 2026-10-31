"""Regresiones focalizadas para propiedades de consulta de PA-001."""
import copy
import unittest
from gisela.engine.conditions import predicate
from gisela.engine.world_base import WorldError


class InvariantPurityTest(unittest.TestCase):
    def test_literal_comparison_is_pure(self):
        state = {'turn': 3, 'world_time': 120}
        original = copy.deepcopy(state)
        condition = {'compare': {'left': {'turn': True}, 'op': 'eq',
                                 'right': {'literal': 3}}}
        self.assertTrue(predicate(state, condition))
        self.assertEqual(state, original)

    def test_unsupported_expression_does_not_mutate_state(self):
        state = {'turn': 3, 'world_time': 120}
        original = copy.deepcopy(state)
        condition = {'compare': {'left': {'unsupported': True}, 'op': 'eq',
                                 'right': {'literal': 3}}}
        with self.assertRaises(WorldError):
            predicate(state, condition)
        self.assertEqual(state, original)

    def test_composed_conditions_are_pure(self):
        state = {'turn': 3, 'world_time': 120}
        original = copy.deepcopy(state)
        condition = {'all': [
            {'compare': {'left': {'turn': True}, 'op': 'eq',
                         'right': {'literal': 3}}},
            {'any': [{'constant': False}, {'not': {'constant': False}}]},
        ]}
        self.assertTrue(predicate(state, condition))
        self.assertEqual(state, original)
