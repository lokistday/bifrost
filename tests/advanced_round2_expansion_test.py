"""Round-two protocol, workload-boundary, and cryptographic-record regressions."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'labs'  # Test the actual published modules with their shared helpers.
HAS_CRYPTO = importlib.util.find_spec('cryptography') is not None
NEW = {
    'network': {'ipv6-boundaries', 'stream-reassembly', 'dns-cache', 'path-mtu', 'event-time-windows'},
    'cloud': {'effective-permissions', 'kubernetes-rbac', 'metadata-credentials', 'private-endpoint-paths', 'breakglass-access'},
    'crypto': {'aad-record-binding', 'verifier-migration', 'envelope-keywrap', 'signature-authorization', 'unbiased-randomness'},
}
OPTIONAL = {'crypto.aad-record-binding', 'crypto.envelope-keywrap', 'crypto.signature-authorization'}


def module(track, name):
    sys.path.insert(0, str(SOURCES / track))
    spec = importlib.util.spec_from_file_location(f'round2_{track}', SOURCES / track / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


network = module('network', 'protocol_models.py')
cloud = module('cloud', 'boundary_models.py')
crypto = module('crypto', 'record_crypto.py')


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

    def test_every_new_example_and_worked_step_has_literal_expected_output(self):
        for track, suffixes in NEW.items():
            course = json.loads((ROOT / 'content' / 'courses' / f'{track}.json').read_text(encoding='utf-8'))
            selected = [lesson for section in course['modules'] for lesson in section['lessons'] if lesson['id'].split('.')[1] in suffixes]
            self.assertEqual(len(selected), 5)
            for lesson in selected:
                if lesson['id'] in OPTIONAL and not HAS_CRYPTO:
                    with self.subTest(lesson=lesson['id']):
                        self.skipTest('optional existing cryptography dependency unavailable')
                    continue
                with self.subTest(lesson=lesson['id'], step='main'):
                    self.assertEqual(self.run_snippet(track, lesson['code']), lesson['expected'])
                for step in lesson['walkthrough']:
                    with self.subTest(lesson=lesson['id'], step=step['title']):
                        self.assertEqual(self.run_snippet(track, step['code']), step['expected'])

    def test_optional_crypto_missing_is_actionable_without_affecting_stdlib_modes(self):
        script = str(SOURCES / 'crypto' / 'record_crypto.py')
        for mode in ('aad', 'envelope', 'context'):
            result = subprocess.run([sys.executable, '-E', '-S', script, mode], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('python -m pip install -r requirements.txt', result.stderr)
            self.assertNotIn('Traceback', result.stderr)
        for mode in ('migration', 'sampling'):
            result = subprocess.run([sys.executable, '-E', '-S', script, mode], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


class ProtocolBoundaries(unittest.TestCase):
    def setUp(self):
        self.data = network.load()

    def test_ipv4_allow_does_not_include_ipv6_or_link_scope(self):
        rows, rules = self.data['family_requests'], self.data['family_rules']
        self.assertEqual(network.family_policy(rows[0], rules), 'ALLOW')
        self.assertEqual(network.family_policy(rows[1], rules), 'DENY')
        self.assertEqual(network.family_policy(rows[2], rules), 'SCOPE_REQUIRED')
        self.assertEqual(network.family_policy({**rows[2], 'interface': 'lab0'}, rules), 'DENY')
        self.assertEqual(network.family_policy(rows[1], rules + [dict(network='2001:db8:20::/64', port=443)]), 'ALLOW')
        self.assertEqual(network.scope('::1'), 'loopback')
        self.assertEqual(network.scope('fd00::5'), 'unique-local')

    def test_stream_reorders_deduplicates_and_refuses_gaps_and_conflicts(self):
        streams = self.data['stream']
        self.assertEqual(network.reassemble(streams['complete'], 8), (b'BIFROST!', [], [], 8))
        self.assertEqual(network.reassemble(streams['gap'], 8), (None, [3, 4], [], 6))
        self.assertEqual(network.reassemble(streams['conflict'], 8), (None, [], [2], 8))
        repaired = copy.deepcopy(streams['conflict'])
        repaired[-1]['hex'] = '46'
        self.assertEqual(network.reassemble(repaired, 8), (b'BIFROST!', [], [], 8))

    def test_stream_rejects_out_of_range_or_invalid_offsets(self):
        for offset in (-1, 8, True):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                network.reassemble([dict(offset=offset, hex='41')], 8)

    def test_dns_expiry_has_exact_boundary_and_negative_minimum(self):
        rows = self.data['dns_records']
        self.assertEqual(network.dns_lookup(rows, 'LEARN.EXAMPLE.', 'a', 29.999), ('HIT', '192.0.2.7'))
        self.assertEqual(network.dns_lookup(rows, 'learn.example', 'A', 30), ('MISS', None))
        self.assertEqual(network.dns_lookup(rows, 'absent.example', 'AAAA', 29.999), ('NEGATIVE_NXDOMAIN', None))
        self.assertEqual(network.dns_lookup(rows, 'absent.example', 'AAAA', 30), ('MISS', None))
        short = copy.deepcopy(rows)
        short[1]['soa_minimum'] = 5
        self.assertEqual(network.dns_lookup(short, 'absent.example', 'A', 15), ('MISS', None))
        self.assertEqual(network.dns_lookup(short, 'absent.example', 'A', 14.999), ('NEGATIVE_NXDOMAIN', None))

    def test_nodata_does_not_negate_other_record_types(self):
        rows = self.data['dns_records']
        self.assertEqual(network.dns_lookup(rows, 'v6only.example', 'A', 10), ('NEGATIVE_NODATA', None))
        self.assertEqual(network.dns_lookup(rows, 'v6only.example', 'AAAA', 10), ('MISS', None))
        self.assertEqual(network.dns_lookup(rows, 'absent.example', 'A', 9), ('MISS', None))

    def test_mtu_accounts_for_family_options_and_ipv6_minimum(self):
        self.assertEqual(network.tcp_budget(1500, 4), 1460)
        self.assertEqual(network.tcp_budget(1500, 6), 1440)
        self.assertEqual(network.tcp_budget(1280, 6, 12), 1208)
        for args in ((1000, 6), (1280, 6, -1), (10, 4), (1500, 7)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                network.tcp_budget(*args)

    def test_late_event_at_watermark_is_accepted_and_sessions_can_merge(self):
        events = self.data['events']
        accepted, late = network.accept_late(events, 5)
        self.assertEqual([r['id'] for r in late], ['E4'])
        self.assertEqual(len(network.sessions(accepted, 10)), 2)
        accepted, late = network.accept_late(events, 8)
        self.assertEqual((len(accepted), len(late), len(network.sessions(accepted, 10))), (4, 0, 1))
        self.assertEqual(len(network.sessions([dict(event_time=0), dict(event_time=9.999)], 10)), 1)
        self.assertEqual(len(network.sessions([dict(event_time=0), dict(event_time=10)], 10)), 2)

    def test_invalid_time_values_do_not_silently_make_sessions(self):
        for value in (float('nan'), float('inf'), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                network.accept_late([dict(event_time=value)], 5)
        for timeout in (0, -1, float('inf')):
            with self.assertRaises(ValueError):
                network.sessions([], timeout)


class CloudBoundaryModels(unittest.TestCase):
    def setUp(self):
        self.data = cloud.load()

    def test_boundary_does_not_grant_and_deny_precedes_allow(self):
        d = self.data
        self.assertEqual(cloud.effective_permission(d['permission_requests'][1], d['identity_allow'], d['boundary_allow']), 'DENY_BOUNDARY')
        self.assertEqual(cloud.effective_permission(dict(action='DeleteNotes'), [], ['DeleteNotes']), 'DENY_NO_IDENTITY_ALLOW')
        self.assertEqual(cloud.effective_permission(dict(action='ReadNotes', explicit_deny=True, resource_policy_grant=True), ['ReadNotes'], ['ReadNotes']), 'DENY_EXPLICIT')
        self.assertEqual(cloud.effective_permission(d['permission_requests'][3], d['identity_allow'], d['boundary_allow']), 'UNMODELED_RESOURCE_POLICY')

    def test_rbac_checks_subject_namespace_and_target_namespace(self):
        d = self.data
        self.assertTrue(cloud.rbac_allowed(d['rbac_requests'][0], d['role'], d['binding']))
        for row in d['rbac_requests'][1:]:
            self.assertFalse(cloud.rbac_allowed(row, d['role'], d['binding']))
        binding = {**d['binding'], 'subject': dict(namespace='other', name='viewer')}
        self.assertFalse(cloud.rbac_allowed(d['rbac_requests'][0], d['role'], binding))
        self.assertTrue(cloud.rbac_allowed(d['rbac_requests'][3], d['role'], binding))
        self.assertFalse(cloud.rbac_allowed({**d['rbac_requests'][0], 'api_group': 'apps'}, d['role'], d['binding']))

    def test_metadata_layers_do_not_override_each_other(self):
        d = self.data
        self.assertEqual(cloud.metadata_access(d['metadata_requests'][0], d['metadata_options']), 'DENY_TOKEN')
        self.assertEqual(cloud.metadata_access(d['metadata_requests'][0], {**d['metadata_options'], 'tokens_required': False}), 'REACHABLE_MODEL')
        self.assertEqual(cloud.metadata_access(d['metadata_requests'][2], {**d['metadata_options'], 'tokens_required': False}), 'BLOCKED_NETWORK')
        self.assertEqual(cloud.metadata_access(d['metadata_requests'][1], {**d['metadata_options'], 'endpoint_enabled': False}), 'DISABLED')

    def test_private_dns_does_not_grant_identity_permission(self):
        d = self.data
        self.assertEqual(cloud.private_access(d['private_requests'][0]), 'ALLOW_MODEL')
        self.assertEqual(cloud.private_access(d['private_requests'][1]), 'PUBLIC_PATH')
        self.assertEqual(cloud.private_access(d['private_requests'][2]), 'DENY_IDENTITY')
        self.assertEqual(cloud.private_access(d['private_requests'][3]), 'DENY_ENDPOINT_POLICY')
        self.assertEqual(cloud.private_access({**d['private_requests'][0], 'network_path': False}), 'NO_NETWORK_PATH')

    def test_breakglass_exact_expiry_revocation_and_subject_scope(self):
        lease, rows = self.data['lease'], self.data['lease_requests']
        self.assertEqual(cloud.lease_decision(rows[0], lease), 'ALLOW_MODEL')
        self.assertEqual(cloud.lease_decision(rows[1], lease), 'DENY_TIME')
        self.assertEqual(cloud.lease_decision({**rows[0], 'at': lease['start']}, lease), 'ALLOW_MODEL')
        self.assertEqual(cloud.lease_decision({**rows[0], 'at': '2026-10-26T10:14:59.999999Z'}, lease), 'ALLOW_MODEL')
        self.assertEqual(cloud.lease_decision(rows[0], {**lease, 'revoked': True}), 'DENY_REVOKED')
        self.assertEqual(cloud.lease_decision(rows[2], lease), 'DENY_SCOPE')
        self.assertEqual(cloud.lease_decision({**rows[0], 'resource': 'other'}, lease), 'DENY_SCOPE')
        self.assertEqual(cloud.lease_decision(rows[0], {**lease, 'approved_by': ' '}), 'DENY_IDENTITY_OR_APPROVAL')

    def test_lease_rejects_unzoned_or_reversed_intervals(self):
        lease, row = self.data['lease'], self.data['lease_requests'][0]
        with self.assertRaises(ValueError):
            cloud.lease_decision({**row, 'at': '2026-10-26T10:00:00'}, lease)
        with self.assertRaises(ValueError):
            cloud.lease_decision(row, {**lease, 'expires': lease['start']})


class StdlibCryptoRecords(unittest.TestCase):
    def test_password_migration_requires_success_and_never_downgrades(self):
        record = crypto.load()['password_record']
        self.assertEqual(crypto.verify_and_plan('wrong', record), (False, False))
        self.assertEqual(crypto.verify_and_plan('training-pass', record), (True, True))
        stronger = crypto.verifier('training-pass', bytes(16), 3000)
        self.assertEqual(crypto.verify_and_plan('training-pass', stronger, 2000), (True, False))

    def test_password_format_and_cost_validation_precede_unbounded_work(self):
        record = crypto.load()['password_record']
        for update in (dict(format_version=True), dict(format_version=2), dict(algorithm='unknown'),
                       dict(iterations=True), dict(iterations=100001), dict(iterations=0),
                       dict(salt_hex='00'), dict(verifier_hex='aa')):
            with self.subTest(update=update), self.assertRaises(ValueError):
                crypto.verify_and_plan('training-pass', {**record, **update})

    def test_semantic_authorization_requires_complete_claim_and_exact_request(self):
        claim = dict(context='review', action='approve', resource='note-17')
        self.assertTrue(crypto.semantic_authorization(True, claim, claim, ['approve']))
        self.assertFalse(crypto.semantic_authorization(False, claim, claim, ['approve']))
        self.assertFalse(crypto.semantic_authorization(True, claim, {**claim, 'action': 'publish'}, ['approve', 'publish']))
        self.assertFalse(crypto.semantic_authorization(True, claim, {**claim, 'resource': 'note-18'}, ['approve']))
        self.assertFalse(crypto.semantic_authorization(True, claim, claim, []))
        self.assertFalse(crypto.semantic_authorization(True, dict(action='approve'), dict(action='approve'), ['approve']))

    def test_rejection_sampling_has_equal_preimages_and_boundary_behavior(self):
        self.assertEqual([sum(value % 10 == r for value in range(250)) for r in range(10)], [25] * 10)
        source = iter([250, 251, 249])
        self.assertEqual(crypto.rejection_sample(lambda: next(source)), (9, 2))
        self.assertEqual(crypto.rejection_sample(lambda: 255, 16), (15, 0))
        self.assertEqual(crypto.rejection_sample(lambda: 0, 1), (0, 0))
        with self.assertRaises(ValueError):
            crypto.rejection_sample(lambda: 250, 10, 3)
        for bound in (0, 257, True):
            with self.assertRaises(ValueError):
                crypto.rejection_sample(lambda: 1, bound)


@unittest.skipUnless(HAS_CRYPTO, 'optional existing cryptography dependency unavailable')
class ActualCryptoRecords(unittest.TestCase):
    def test_aad_binds_tenant_document_and_version_without_releasing_plaintext(self):
        InvalidTag, *_ = crypto.optional_crypto()
        fixture = crypto.load()['record']
        self.assertEqual(crypto.decrypt_record(fixture, 'blue', '17', '1'), b'training note')
        for tenant, document, version in [('red', '17', '1'), ('blue', '18', '1'), ('blue', '17', '2')]:
            with self.subTest(tenant=tenant, document=document, version=version), self.assertRaises(InvalidTag):
                crypto.decrypt_record(fixture, tenant, document, version)

    def test_rewrap_returns_new_metadata_preserves_payload_and_decrypts(self):
        _, _, _, AESGCM, _, unwrap, InvalidUnwrap = crypto.optional_crypto()
        d = crypto.load()
        old, new = bytes.fromhex(d['wrapping']['old_kek_hex']), bytes.fromhex(d['wrapping']['new_kek_hex'])
        envelope = dict(ciphertext_hex=d['record']['ciphertext_hex'], nonce_hex=d['record']['nonce_hex'],
                        wrapped_dek_hex=d['wrapping']['wrapped_dek_hex'], kek_id='kek-v1')
        original = dict(envelope)
        rotated = crypto.rewrap_envelope(envelope, old, new, 'kek-v2')
        self.assertEqual(envelope, original)
        self.assertIsNot(rotated, envelope)
        self.assertEqual(rotated['ciphertext_hex'], original['ciphertext_hex'])
        self.assertEqual(rotated['nonce_hex'], original['nonce_hex'])
        self.assertNotEqual(rotated['wrapped_dek_hex'], original['wrapped_dek_hex'])
        dek = unwrap(new, bytes.fromhex(rotated['wrapped_dek_hex']))
        self.assertEqual(AESGCM(dek).decrypt(bytes.fromhex(rotated['nonce_hex']), bytes.fromhex(rotated['ciphertext_hex']), crypto.record_aad('blue', '17', '1')), b'training note')
        with self.assertRaises(InvalidUnwrap):
            unwrap(old, bytes.fromhex(rotated['wrapped_dek_hex']))

    def test_modified_wrap_and_modified_ciphertext_are_rejected(self):
        InvalidTag, _, _, AESGCM, _, unwrap, InvalidUnwrap = crypto.optional_crypto()
        d = crypto.load()
        wrapped = bytearray.fromhex(d['wrapping']['wrapped_dek_hex'])
        wrapped[0] ^= 1
        with self.assertRaises(InvalidUnwrap):
            unwrap(bytes.fromhex(d['wrapping']['old_kek_hex']), bytes(wrapped))
        payload = bytearray.fromhex(d['record']['ciphertext_hex'])
        payload[0] ^= 1
        with self.assertRaises(InvalidTag):
            AESGCM(bytes.fromhex(d['record']['dek_hex'])).decrypt(bytes.fromhex(d['record']['nonce_hex']), bytes(payload), crypto.record_aad('blue', '17', '1'))

    def test_real_ed25519_binds_context_action_resource_and_key(self):
        _, InvalidSignature, Private, *_ = crypto.optional_crypto()
        key = Private.from_private_bytes(bytes.fromhex(crypto.load()['signing_seed_hex']))
        signed = crypto.signed_claim('review', 'approve', 'note-17')
        signature = key.sign(signed)
        key.public_key().verify(signature, signed)
        for values in [('deploy', 'approve', 'note-17'), ('review', 'publish', 'note-17'), ('review', 'approve', 'note-18')]:
            with self.subTest(values=values), self.assertRaises(InvalidSignature):
                key.public_key().verify(signature, crypto.signed_claim(*values))
        with self.assertRaises(InvalidSignature):
            Private.generate().public_key().verify(signature, signed)


if __name__ == '__main__':
    unittest.main()
