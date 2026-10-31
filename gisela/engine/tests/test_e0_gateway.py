"""E0-G: autoridad, idempotencia, concurrencia, checkpoint y privacidad."""
from concurrent.futures import ThreadPoolExecutor
from tempfile import TemporaryDirectory
from pathlib import Path
from threading import Barrier
from unittest import TestCase
from gisela.engine.authorized_gateway import ExecutionGateway, Principal, GatewayError
from gisela.engine.checkpoint_store import JsonCheckpointStore, StoreFailure
from gisela.engine.tests.test_h34a_values import ready
from gisela.engine.runtime import new_session


CONTROLLER = Principal('glauquir', frozenset({'act','observe_player'}))
READER = Principal('reporter', frozenset({'observe_player'}))
BOT = Principal('bot', frozenset({'act'}))
ADMIN = Principal('admin', frozenset({'export_private','debug_private'}))
REGISTRY = {p.identifier:p for p in (CONTROLLER,READER,BOT,ADMIN)}


def command(view, action='choose_guardar'):
    return {'session_id':view['session_id'], 'revision':view['revision'],
            'action_id':action}


class GatewayHardening(TestCase):
    def setUp(self):
        self.admitted, session = ready()
        self.session = session
        self.gateway = ExecutionGateway(session, REGISTRY)
        self.client = self.gateway.bind('glauquir')

    def test_e0_g01_command_is_idempotent(self):
        req = command(self.client.observe())
        first = self.client.act(req, 'c001')
        state = self.session.export()
        second = self.client.act(req, 'c001')
        self.assertEqual(first, second)
        self.assertEqual(self.session.export(), state)

    def test_e0_g02_command_id_cannot_change_payload(self):
        req = command(self.client.observe())
        self.client.act(req, 'c001')
        with self.assertRaises(GatewayError):
            self.client.act(dict(req, action_id='choose_prestar'), 'c001')

    def test_e0_g03_revision_rejects_distinct_command(self):
        req = command(self.client.observe())
        self.assertEqual(self.client.act(req, 'c001')['status'], 'ok')
        self.assertEqual(self.client.act(req, 'c002')['error']['code'], 'STALE_PROJECTION')

    def test_e0_g04_no_permission_escalation_from_request(self):
        reader = self.gateway.bind('reporter')
        req = command(reader.observe())
        with self.assertRaises(GatewayError):
            reader.act(dict(req, principal='glauquir'), 'c001')
        with self.assertRaises(GatewayError):
            self.gateway.bind('intruso')
        self.assertEqual(self.session.export()['revision'], req['revision'])

    def test_e0_g05_player_projection_requires_permission(self):
        bot = self.gateway.bind('bot')
        with self.assertRaises(GatewayError):
            bot.observe()
        with self.assertRaises(GatewayError):
            bot.export()
        with self.assertRaises(GatewayError):
            self.client.export()
        self.assertIn('world', self.gateway.bind('admin').export())

    def test_e0_g06_writer_without_player_view_is_redacted(self):
        bot = self.gateway.bind('bot')
        req = command(self.client.observe())
        result = bot.act(req, 'b001')
        self.assertEqual(result['status'],'ok')
        self.assertNotIn('view', result)

    def test_e0_g07_raw_session_mutation_is_blocked(self):
        req = command(self.client.observe())
        self.assertEqual(self.session.act(req)['error']['code'], 'INVALID_ACTION')
        self.assertEqual(self.session.export()['revision'],req['revision'])

    def test_e0_g08_race_same_revision_single_commit(self):
        initial = command(self.client.observe())
        barrier = Barrier(2)
        def run(cid):
            barrier.wait()
            return self.client.act(initial, cid)
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(run, ('race1','race2')))
        self.assertEqual([r['status'] for r in replies].count('ok'),1)
        self.assertEqual([r['status'] for r in replies].count('error'),1)
        self.assertEqual(self.session.export()['revision'],initial['revision'] + 1)

    def test_e0_g09_observe_does_not_mutate_state(self):
        snap = self.session.export()
        self.client.observe()
        self.client.observe()
        self.assertEqual(self.session.export(), snap)

    def test_e0_g10_durable_receipt_survives_restore(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'gateway.json'
            a = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))
            client = a.bind('glauquir')
            req = command(client.observe(), 'advance')
            first = client.act(req, 'replay1')
            a.close()
            b = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))
            self.assertEqual(b.bind('glauquir').act(req, 'replay1'), first)
            self.assertEqual(b.bind('glauquir').observe(), first['view'])
            b.close()

    def test_e0_g11_disk_lock_prevents_second_writer(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'gateway.json'
            first = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                     JsonCheckpointStore(path))
            with self.assertRaises(StoreFailure):
                ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))
            first.close()

    def test_e0_g12_tampered_checkpoint_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'gateway.json'
            first = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                     JsonCheckpointStore(path))
            first.close()
            import json
            doc = json.loads(path.read_text())
            doc['package_digest'] = '0' * 64
            path.write_text(json.dumps(doc))
            with self.assertRaises(GatewayError):
                ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))

    def test_e0_g13_same_command_from_other_principal_distinct(self):
        req = command(self.client.observe())
        self.client.act(req,'same')
        result = self.gateway.bind('bot').act(req,'same')
        self.assertEqual(result['status'],'error')
        self.assertEqual(result['error']['code'],'STALE_PROJECTION')
        self.assertEqual(result['error']['message'],'Operación rechazada')

    def test_e0_g14_result_is_defensively_copied(self):
        req = command(self.client.observe())
        result = self.client.act(req,'same')
        result['view']['actions'].clear()
        self.assertNotEqual(self.client.act(req,'same'),result)

    def test_e0_g15_invalid_id_does_not_mutate(self):
        snapshot = self.session.export()
        with self.assertRaises(GatewayError):
            self.client.act(command(self.client.observe()),'Invalid ID')
        self.assertEqual(self.session.export(),snapshot)
    def test_e0_g18_pending_replay_durable_and_rng_unchanged(self):
        from gisela.engine.tests.test_pending import PACKAGE, before_choice
        from gisela.contracts.admit_package import admit_package_file
        admitted = admit_package_file(PACKAGE)
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'pending.json'
            initial = new_session(admitted)
            before_choice(initial)
            gateway = ExecutionGateway(initial, REGISTRY, JsonCheckpointStore(path))
            client = gateway.bind('glauquir')
            req = command(client.observe(), 'choose_prestar')
            first = client.act(req, 'pending1')
            pending = initial.export()
            gateway.close()
            restored = ExecutionGateway(new_session(admitted), REGISTRY,
                                        JsonCheckpointStore(path))
            client2 = restored.bind('glauquir')
            self.assertEqual(client2.act(req, 'pending1'), first)
            self.assertEqual(restored._session.export()['rng'], pending['rng'])
            self.assertEqual(client2.observe()['content']['kind'],'pending_transaction')
            resolved = client2.act(command(client2.observe(), 'resolve_hab_01'), 'answer1')
            self.assertEqual(resolved['status'],'ok')
            self.assertNotIn('pending_transaction', restored._session.export())
            restored.close()

    def test_e0_g19_corrupt_receipt_rejected_on_restore(self):
        import json
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'bad_receipt.json'
            first = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                     JsonCheckpointStore(path))
            first.close()
            checkpoint = json.loads(path.read_text())
            checkpoint['receipts']['glauquir:bad'] = {'fingerprint':'abc', 'response':{}}
            path.write_text(json.dumps(checkpoint))
            with self.assertRaises(GatewayError):
                ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))
    def test_e0_g20_revoked_principal_cannot_use_existing_binding(self):
        req = command(self.client.observe())
        self.gateway._principals['glauquir'] = Principal('glauquir', frozenset({'act'}))
        with self.assertRaises(GatewayError):
            self.client.act(req, 'revoked')
        with self.assertRaises(GatewayError):
            self.client.observe()
        self.assertEqual(self.session.export()['revision'],req['revision'])

    def test_e0_g21_replayed_receipt_obeys_current_audience(self):
        req = command(self.client.observe())
        self.assertIn('view', self.client.act(req, 'first'))
        self.gateway._principals['glauquir'] = Principal('glauquir', frozenset({'act'}))
        new_binding = self.gateway.bind('glauquir')
        duplicate = new_binding.act(req, 'first')
        self.assertEqual(duplicate['status'],'ok')
        self.assertNotIn('view',duplicate)

    def test_e0_g22_checkpoint_with_duplicate_json_keys_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'duplicate.json'
            first = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                     JsonCheckpointStore(path))
            first.close()
            content = path.read_text()
            path.write_text('{' + '"format":"gisela.gateway.v1",' + content[1:])
            with self.assertRaises(StoreFailure):
                ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))

    def test_e0_g23_mismatched_session_id_in_snapshot_rejected(self):
        import json
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'wrong_session.json'
            first = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                     JsonCheckpointStore(path))
            first.close()
            checkpoint = json.loads(path.read_text())
            checkpoint['state']['session_id'] = 'another_session'
            path.write_text(json.dumps(checkpoint))
            with self.assertRaises(GatewayError):
                ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))
    def test_e0_g24_receipt_future_revision_rejected(self):
        import json
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'receipt_future.json'
            first = ExecutionGateway(new_session(self.admitted), REGISTRY,
                                     JsonCheckpointStore(path))
            req = command(first.bind('glauquir').observe(),'advance')
            first.bind('glauquir').act(req,'receipt1')
            first.close()
            checkpoint = json.loads(path.read_text())
            checkpoint['receipts']['glauquir:receipt1']['response']['revision'] += 100
            path.write_text(json.dumps(checkpoint))
            with self.assertRaises(GatewayError):
                ExecutionGateway(new_session(self.admitted), REGISTRY,
                                 JsonCheckpointStore(path))


class StorageFailures(TestCase):
    def test_e0_g16_failed_save_rolls_back(self):
        _, session = ready()
        class FailingStore:
            def __init__(self): self.count = 0
            def claim(self): pass
            def release(self): pass
            def load(self): return None
            def save(self, _: dict):
                self.count += 1
                if self.count == 2: raise StoreFailure('falló', uncertain=False)
        gateway = ExecutionGateway(session, REGISTRY, FailingStore())
        client = gateway.bind('glauquir')
        before = session.export()
        with self.assertRaises(GatewayError):
            client.act(command(client.observe()),'fail1')
        self.assertEqual(session.export(),before)

    def test_e0_g17_uncertain_save_fences_gateway(self):
        _, session = ready()
        class UncertainStore:
            def __init__(self): self.count = 0
            def claim(self): pass
            def release(self): pass
            def load(self): return None
            def save(self, _: dict):
                self.count += 1
                if self.count == 2: raise StoreFailure('indeterminado', uncertain=True)
        gateway = ExecutionGateway(session, REGISTRY, UncertainStore())
        client = gateway.bind('glauquir')
        with self.assertRaises(GatewayError):
            client.act(command(client.observe()),'fail1')
        with self.assertRaises(GatewayError):
            client.observe()
