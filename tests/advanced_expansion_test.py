"""Regression cases for the network/cloud/crypto expansion's real lab behavior."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'scripts' / 'lab_sources'
NEW = {
    'network': {'routing', 'nat-correlation', 'connection-state', 'detection-metrics', 'incident-correlation'},
    'cloud': {'workload-trust', 'iac-review', 'container-supply-chain', 'audit-coverage', 'recovery-exercise'},
    'crypto': {'key-lifecycle', 'hkdf-context', 'certificate-trust', 'replay-protection', 'message-encoding'},
}


def module(track, name):
    spec = importlib.util.spec_from_file_location(f'advanced_{track}', SOURCES / track / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


network = module('network', 'defense_models.py')
cloud = module('cloud', 'operations.py')
crypto = module('crypto', 'design_checks.py')


class PublishedExamples(unittest.TestCase):
    def run_snippet(self, track, snippet):
        output = []
        for line in snippet.splitlines():
            args = shlex.split(line)
            self.assertEqual(args[0], 'python3')
            result = subprocess.run([sys.executable, *args[1:]], cwd=SOURCES / track,
                                    capture_output=True, text=True, encoding='utf-8',
                                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            self.assertEqual(result.returncode, 0, result.stderr)
            output.append(result.stdout.rstrip('\n'))
        return '\n'.join(output)

    def test_all_new_main_examples_and_worked_steps(self):
        for track, suffixes in NEW.items():
            data = json.loads((ROOT / 'content' / 'courses' / f'{track}.json').read_text(encoding='utf-8'))
            selected = [lesson for section in data['modules'] for lesson in section['lessons']
                        if lesson['id'].split('.')[1] in suffixes]
            self.assertEqual(len(selected), 5)
            for lesson in selected:
                with self.subTest(lesson=lesson['id'], step='main'):
                    self.assertEqual(self.run_snippet(track, lesson['code']), lesson['expected'])
                for step in lesson['walkthrough']:
                    with self.subTest(lesson=lesson['id'], step=step['title']):
                        self.assertEqual(self.run_snippet(track, step['code']), step['expected'])


class NetworkBoundaryCases(unittest.TestCase):
    def setUp(self):
        self.data = network.load()

    def test_longest_prefix_default_and_no_route(self):
        self.assertEqual(network.route('10.20.1.7', self.data['routes'])[1], 'app')
        self.assertEqual(network.route('10.30.1.7', self.data['routes'])[1], 'core')
        self.assertEqual(network.route('203.0.113.1', self.data['routes'])[1], 'wan')
        self.assertIsNone(network.route('203.0.113.1', self.data['routes'][1:]))

    def test_nat_requires_destination_port_and_half_open_interval(self):
        observation = copy.deepcopy(self.data['observations'][0])
        self.assertEqual(network.correlate_nat(observation, self.data['nat']), ['10.20.1.7'])
        observation['destination'] = '203.0.113.21:443'
        self.assertEqual(network.correlate_nat(observation, self.data['nat']), [])
        observation = copy.deepcopy(self.data['observations'][0])
        observation['public_port'] = 40002
        self.assertEqual(network.correlate_nat(observation, self.data['nat']), ['10.20.1.8'])
        observation['time'] = self.data['nat'][1]['end']
        self.assertEqual(network.correlate_nat(observation, self.data['nat']), [])
        observation['time'] = self.data['nat'][1]['start']
        self.assertEqual(network.correlate_nat(observation, self.data['nat']), ['10.20.1.8'])

    def test_nat_does_not_silently_choose_one_ambiguous_mapping(self):
        rows = [self.data['nat'][0], {**self.data['nat'][0], 'private_ip': '10.20.1.9'}]
        self.assertEqual(network.correlate_nat(self.data['observations'][0], rows), ['10.20.1.7', '10.20.1.9'])

    def test_state_requires_reply_and_key_and_closes(self):
        events = self.data['state_events']
        results = network.track(events)
        self.assertFalse(results[4][1])
        self.assertEqual(results[5][2], 'none')
        self.assertFalse(results[6][1])
        missing_reply = network.track([row for row in events if row['id'] != 'S2'])
        self.assertEqual(missing_reply[1:3], [('S3', False, 'pending'), ('S4', False, 'pending')])
        wrong = copy.deepcopy(events[:4])
        wrong[-1]['direction'] = 'unknown'
        self.assertFalse(network.track(wrong)[-1][1])

    def test_metrics_report_zero_denominators_and_threshold_tradeoff(self):
        counts, precision, recall = network.metrics(self.data['detections'], 3)
        self.assertEqual(counts, dict(TP=2, FP=2, FN=1, TN=3))
        self.assertEqual(precision, 0.5)
        self.assertAlmostEqual(recall, 2 / 3)
        counts, precision, recall = network.metrics(self.data['detections'], 6)
        self.assertEqual(counts, dict(TP=1, FP=0, FN=2, TN=5))
        self.assertEqual(precision, 1)
        self.assertAlmostEqual(recall, 1 / 3)
        self.assertIsNone(network.metrics(self.data['detections'], 99)[1])
        self.assertIsNone(network.metrics([dict(score=1, attack=False)], 0)[2])

    def test_missing_incident_observation_cannot_keep_complete_conclusion(self):
        self.data['response'] = [r for r in self.data['response'] if not (r['request_id'] == 'R-17' and r['source'] == 'app')]
        with tempfile.TemporaryDirectory() as folder:
            fixture = Path(folder) / 'copy.json'
            fixture.write_text(json.dumps(self.data), encoding='utf-8')
            result = subprocess.run([sys.executable, str(SOURCES / 'network' / 'defense_models.py'), 'response', '--input', str(fixture)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('correlated=2 conclusion=insufficient_evidence', result.stdout)
        self.assertNotIn('attempt_observed', result.stdout)


class CloudBoundaryCases(unittest.TestCase):
    def setUp(self):
        self.data = cloud.load()

    def test_trust_requires_all_exact_authenticated_conditions(self):
        self.assertTrue(cloud.trust_matches(self.data['claims'][0], self.data['trust']))
        self.assertFalse(cloud.trust_matches(self.data['claims'][1], self.data['trust']))
        self.assertFalse(cloud.trust_matches(self.data['claims'][2], self.data['trust']))
        missing = {**self.data['claims'][0]}
        del missing['aud']
        self.assertFalse(cloud.trust_matches(missing, self.data['trust']))
        for replacement in (None, [], '*', 'bifrost-deploy '):
            self.assertFalse(cloud.trust_matches({**self.data['claims'][0], 'aud': replacement}, self.data['trust']))

    def test_delete_and_public_admin_need_distinct_reviews(self):
        self.assertEqual(cloud.review_changes(self.data['changes']), [
            ('admin-ingress', 'PUBLIC_ADMIN_REVIEW'), ('notes-data', 'DATA_LOSS_REVIEW'), ('web-replicas', 'CHANGE_REVIEW')])

    def test_pinning_does_not_make_runtime_privilege_checks_pass(self):
        image = {**self.data['images'][1], 'uid': 0, 'privileged': True}
        result = cloud.review_image(image)
        self.assertTrue(result['pinned'])
        self.assertFalse(result['non_root'])
        self.assertFalse(result['privileged_disabled'])
        self.assertFalse(cloud.review_image({**image, 'reference': 'a@sha256:not-a-digest'})['pinned'])
        self.assertFalse(cloud.review_image({**image, 'uid': True})['non_root'])

    def test_audit_keeps_other_accounts_and_regions(self):
        self.assertEqual(cloud.audit_summary(self.data['audit'], self.data['enabled_categories']), (2, 1, ['object-read']))
        rows = self.data['audit'] + [{**self.data['audit'][0], 'region': 'lab-2'}]
        self.assertEqual(cloud.audit_summary(rows, self.data['enabled_categories'])[0], 3)

    def test_recovery_uses_exact_seconds_at_objective_boundaries(self):
        record = {**self.data['recovery'], 'latest_verified_backup': '2026-10-20T09:45:00Z', 'service_verified': '2026-10-20T11:00:00Z'}
        self.assertEqual(cloud.recovery(record), (15.0, 60.0, True, True))
        record['latest_verified_backup'] = '2026-10-20T09:44:59Z'
        record['service_verified'] = '2026-10-20T11:00:01Z'
        loss, elapsed, rpo, rto = cloud.recovery(record)
        self.assertGreater(loss, 15)
        self.assertGreater(elapsed, 60)
        self.assertFalse(rpo)
        self.assertFalse(rto)

    def test_rto_includes_waiting_before_recovery_starts(self):
        record = {**self.data['recovery'], 'recovery_started': '2026-10-20T10:20:00Z', 'service_verified': '2026-10-20T10:50:00Z'}
        self.assertEqual(cloud.recovery(record)[1], 50)

    def test_recovery_rejects_invalid_chronology_or_goals(self):
        for update in [dict(latest_verified_backup='2026-10-20T10:01:00Z'),
                       dict(recovery_started='2026-10-20T09:59:00Z'),
                       dict(service_verified='2026-10-20T09:59:00Z'),
                       dict(incident='2026-10-20T10:00:00'),
                       dict(rpo_minutes=-1), dict(rpo_minutes=True), dict(rto_minutes=float('inf'))]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                cloud.recovery({**self.data['recovery'], **update})

    def test_backup_hash_checks_actual_fixture_bytes(self):
        record = self.data['recovery']
        contents = (SOURCES / 'cloud' / record['backup_file']).read_bytes()
        self.assertEqual(hashlib.sha256(contents).hexdigest(), record['backup_sha256'])
        self.assertNotEqual(hashlib.sha256(contents + b'!').hexdigest(), record['backup_sha256'])


class CryptoBoundaryCases(unittest.TestCase):
    def test_hkdf_matches_published_rfc5869_case_one(self):
        expected = bytes.fromhex('3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865')
        self.assertEqual(crypto.hkdf(bytes.fromhex('0b' * 22), bytes(range(13)), bytes(range(240, 250)), 42), expected)
        self.assertNotEqual(crypto.hkdf(b'ikm', b'salt', b'client', 32), crypto.hkdf(b'ikm', b'salt', b'server', 32))
        for length in (-1, 0, 8161):
            with self.assertRaises(ValueError):
                crypto.hkdf(b'ikm', b'salt', b'info', length)

    def test_key_retirement_and_compromise_are_different(self):
        self.assertTrue(crypto.key_allowed('retired', 'decrypt'))
        self.assertFalse(crypto.key_allowed('retired', 'encrypt'))
        self.assertFalse(crypto.key_allowed('compromised', 'decrypt'))
        self.assertFalse(crypto.key_allowed('unknown', 'encrypt'))

    def test_certificate_metadata_name_date_and_root_are_independent(self):
        cert = dict(dns_names=['learn.example'], not_before='2026-01-01', not_after='2026-12-31', root='Training Root')
        self.assertFalse(crypto.certificate_metadata(cert, 'learn.example.other', '2026-10-20')['name_match'])
        self.assertFalse(crypto.certificate_metadata(cert, 'learn.example', '2027-01-01')['time_match'])
        result = crypto.certificate_metadata({**cert, 'root': 'Unknown'}, 'learn.example', '2026-10-20')
        self.assertEqual(result, dict(name_match=True, time_match=True, root_in_training_store=False))

    def test_replay_invalid_mac_does_not_advance_state_and_fields_are_bound(self):
        tag = crypto.sign_request(1, b'POST', b'/notes', b'hello')
        self.assertEqual(crypto.accept(1, b'POST', b'/notes', b'hello', tag, 0), ('ACCEPT', 1))
        self.assertEqual(crypto.accept(1, b'POST', b'/notes', b'hello', tag, 1), ('REPLAY', 1))
        for seq, method, path, body in [(2, b'POST', b'/notes', b'hello'), (1, b'GET', b'/notes', b'hello'),
                                       (1, b'POST', b'/admin', b'hello'), (1, b'POST', b'/notes', b'changed')]:
            self.assertEqual(crypto.accept(seq, method, path, body, tag, 1), ('BAD_TAG', 1))
        self.assertEqual(crypto.accept(1, b'POST', b'/notes', b'hello', tag, 0), ('ACCEPT', 1))

    def test_framing_distinguishes_equal_naive_inputs_and_counts_utf8_bytes(self):
        self.assertEqual(b''.join([b'ab', b'c']), b''.join([b'a', b'bc']))
        self.assertNotEqual(crypto.encode_fields([b'ab', b'c']), crypto.encode_fields([b'a', b'bc']))
        self.assertEqual(crypto.encode_fields([chr(0xAC00).encode('utf-8')]).hex(), '00000003eab080')
        with self.assertRaises(TypeError):
            crypto.encode_fields(['not-bytes'])


if __name__ == '__main__':
    unittest.main()
