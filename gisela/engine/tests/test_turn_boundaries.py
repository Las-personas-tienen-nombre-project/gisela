"""Pruebas de frontera ADR-007/008 sin añadir fases públicas al runtime.

Se utilizan nodos de un fixture existente, pero las condiciones y efectos
son genéricos y válidos para cualquier juego que utilice GISELA.
"""
from __future__ import annotations

import copy
import unittest
from pathlib import Path

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.runtime import new_session

PACKAGE = Path(__file__).resolve().parents[2] / 'packages' / 'mvp_casete.package.json'
VAR = lambda name: {'var': {'scope': 'session', 'key': name}}


def declare(pkg, name, options=None):
    options = options or {}
    initial = options.get('initial', 0)
    kind = options.get('kind', 'integer')
    pkg['manifest']['variables'].append({'scope': 'session', 'id': name,
                                         'type': kind, 'initial': initial})
    pkg['initial_state']['session_variables'][name] = initial


def setting(name, value):
    return {'op': 'set', 'target': VAR(name), 'value': {'literal': value}}


def adding(name, amount):
    return {'op': 'add', 'target': VAR(name), 'value': {'literal': amount}}


def equals(name, value):
    return {'compare': {'left': VAR(name), 'op': 'eq', 'right': {'literal': value}}}


def send(session, identifier):
    view = session.observe()
    available = [a for a in view['actions'] if a['action_id'] == identifier or a['id'] == identifier]
    if len(available) != 1:
        raise AssertionError(f'{identifier}: {available}')
    return session.act({'session_id': view['session_id'],
                        'revision': view['revision'],
                        'action_id': available[0]['action_id']})


def reach_transition(session):
    """Alcanza un nodo que termina en transición, sin cerrarlo todavía."""
    assert send(session, 'advance')['status'] == 'ok'
    assert send(session, 'advance')['status'] == 'ok'
    assert send(session, 'guardar')['status'] == 'ok'
    assert session.export()['cursor']['step'] == 'despedida'


class TurnBoundariesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = admit_package_file(PACKAGE).materialize()

    def _base_with_paused_destination(self):
        pkg = copy.deepcopy(self.base)
        # El nodo B debe exponer un paso para inspeccionar el salto confirmado.
        b = next(n for n in pkg['nodes'] if n['id'] == 'final_solitario')
        b['steps'] = [
            {'id': 'observacion_b', 'op': 'narrate',
             'text': {'text': 'El siguiente nodo está activo.'}},
            {'id': 'terminar', 'op': 'ending', 'ending': 'solo'},
        ]
        return pkg

    def _pkg_with_phase_rules(self):
        pkg = self._base_with_paused_destination()
        declare(pkg, 'phase_count')
        declare(pkg, 'entered_b', {'kind':'boolean', 'initial':False})
        pkg['rules'] += [
            {'id': 'close_a_1',
             'trigger': {'on': 'node_completed', 'node': 'inicio'},
             'effects': [adding('phase_count', 1)]},
            {'id': 'close_a_2',
             'trigger': {'on': 'turn_ended'},
             'effects': [adding('phase_count', 1)]},
            {'id': 'start_b',
             'trigger': {'on': 'turn_started'},
             'when': equals('phase_count', 2),
             'effects': [setting('entered_b', True)]},
        ]
        return pkg

    def test_T04_closed_node_and_started_node_share_single_commit(self):
        pkg = self._pkg_with_phase_rules()
        session = new_session(admit_package(pkg))
        reach_transition(session)
        before = session.export()
        response = send(session, 'advance')
        self.assertEqual(response['status'], 'ok')
        after = session.export()
        self.assertEqual(after['revision'], before['revision'] + 1)
        self.assertEqual(after['turn'], before['turn'] + 1)
        self.assertEqual(after['narrative']['session_variables']['phase_count'], 2)
        self.assertTrue(after['narrative']['session_variables']['entered_b'])
        self.assertTrue(after['history']['executions'][-2]['completed'])
        self.assertFalse(after['history']['executions'][-1]['completed'])
        self.assertEqual(after['cursor']['node'], 'final_solitario')
        self.assertEqual(after['cursor']['step'], 'observacion_b')
        trace = [x['source'] for x in after['history']['trace'] if x['kind'] == 'rule_fired']
        self.assertLess(trace.index('close_a_1'), trace.index('start_b'))
        self.assertLess(trace.index('close_a_2'), trace.index('start_b'))

    def test_T05_failure_starting_B_rolls_back_whole_jump(self):
        pkg = self._pkg_with_phase_rules()
        declare(pkg, 'conflict', {'kind':'boolean', 'initial':False})
        pkg['rules'] += [
            {'id': 'start_b_conflict_1',
             'trigger': {'on': 'turn_started'},
             'when': equals('phase_count', 2),
             'effects': [setting('conflict', True)]},
            {'id': 'start_b_conflict_2',
             'trigger': {'on': 'turn_started'},
             'when': equals('phase_count', 2),
             'effects': [setting('conflict', False)]},
        ]
        session = new_session(admit_package(pkg))
        reach_transition(session)
        before = session.export()
        response = send(session, 'advance')
        self.assertEqual(response['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), before)
        self.assertEqual(before['cursor']['step'], 'despedida')
        self.assertEqual(before['turn'], 1)

    def test_T06_conflicting_close_event_writes_rollback(self):
        pkg = self._base_with_paused_destination()
        declare(pkg, 'conflict', {'kind':'boolean', 'initial':False})
        pkg['rules'] += [
            {'id': 'node_completed_conflict',
             'trigger': {'on': 'node_completed', 'node': 'inicio'},
             'effects': [setting('conflict', True)]},
            {'id': 'turn_ended_conflict',
             'trigger': {'on': 'turn_ended'},
             'effects': [setting('conflict', False)]},
        ]
        session = new_session(admit_package(pkg))
        reach_transition(session)
        before = session.export()
        response = send(session, 'advance')
        self.assertEqual(response['error']['code'], 'REACTION_CONFLICT')
        self.assertEqual(session.export(), before)

    def test_T08_idempotent_set_does_not_emit_state_changed(self):
        pkg = self._base_with_paused_destination()
        declare(pkg, 'unchanged', {'kind':'boolean', 'initial':False})
        declare(pkg, 'spuriously_changed', {'kind':'boolean', 'initial':False})
        pkg['rules'] += [
            {'id': 'idempotent',
             'trigger': {'on': 'turn_started'},
             'effects': [setting('unchanged', False)]},
            {'id': 'would_fire_only_for_effective_change',
             'trigger': {'on': 'state_changed', 'target': VAR('unchanged')},
             'effects': [setting('spuriously_changed', True)]},
        ]
        session = new_session(admit_package(pkg))
        self.assertFalse(session.export()['narrative']['session_variables']['spuriously_changed'])
        trace = [x['source'] for x in session.export()['history']['trace'] if x['kind'] == 'rule_fired']
        self.assertIn('idempotent', trace)
        self.assertNotIn('would_fire_only_for_effective_change', trace)


if __name__ == '__main__':
    unittest.main()
