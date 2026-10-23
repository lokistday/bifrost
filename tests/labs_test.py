"""Execute offline labs and verify files, backups and generated teaching fixtures."""
from pathlib import Path
from datetime import datetime, timezone
import base64
import csv
import contextlib
import hashlib
import hmac
import importlib.util
import io
import json
import runpy
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / 'labs'
HAS_CRYPTOGRAPHY = importlib.util.find_spec('cryptography') is not None

def run(track, script, *args, cwd=None, ok=True):
    result = subprocess.run([sys.executable, str(LABS / track / script), *args], cwd=cwd or ROOT, capture_output=True, text=True, encoding='utf-8')
    if ok and result.returncode:
        raise AssertionError(result.stderr)
    return result

class LabsTest(unittest.TestCase):
    def test_foundation(self):
        self.assertEqual(run('foundation', 'hello.py').stdout.strip(), 'Hello, Bifrost\nStudy: 30 minutes')
        self.assertEqual(run('foundation', 'summarize.py').stdout.strip(), 'events=4 denied=2\nbob\ncarol')
        with tempfile.TemporaryDirectory(prefix='bifrost-labs-') as name:
            folder = Path(name)
            shutil.copy(LABS / 'foundation' / 'summarize.py', folder)
            text = (LABS / 'foundation' / 'events.csv').read_text()
            (folder / 'events.csv').write_text(text + 'dana,denied\n')
            result = subprocess.run([sys.executable, str(folder / 'summarize.py')], cwd=ROOT, capture_output=True, text=True)
            self.assertIn('events=5 denied=3', result.stdout)

    def test_web(self):
        result = run('web', 'demo.py').stdout.splitlines()
        self.assertEqual(result, ['unsafe_rows=2 safe_rows=0', 'alice_rows=1', '&lt;b&gt;hello&lt;/b&gt;', 'own=True other=False', 'regression=PASS'])

    def test_web_ownership_fails_closed(self):
        with contextlib.redirect_stdout(io.StringIO()):
            can_read = runpy.run_path(str(LABS/'web/demo.py'))['can_read']
        self.assertTrue(can_read('alice', 'alice'))
        for user, owner in [(None, None), ('', ''), (' ', ' '), (1, 1), ([], []),
                            ('alice', 'bob'), ('alice', None), (None, 'alice')]:
            with self.subTest(user=user, owner=owner):
                self.assertFalse(can_read(user, owner))

    def test_forensic(self):
        rows = run('forensic', 'timeline.py').stdout.splitlines()
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0], '2026-10-20T00:00:00+00:00 E01 login_ok')
        self.assertEqual(rows[4], '2026-10-20T00:02:00+00:00 E05 login_ok')
        self.assertEqual(rows[-1], '2026-10-20T00:03:00+00:00 E06 file_read')

    def test_network_policy(self):
        self.assertEqual(run('network', 'evaluate.py').stdout.splitlines(), ['N01 ALLOW MATCH', 'N02 ALLOW MATCH', 'N03 DENY MATCH', 'N04 DENY MATCH', 'N05 DENY MATCH', 'N06 DENY MISMATCH'])
        self.assertEqual(run('network', 'detect.py').stdout.strip(), 'REVIEW 198.51.100.8 denied=3')
        with tempfile.TemporaryDirectory(prefix='bifrost-policy-') as name:
            folder = Path(name)
            for file in ['evaluate.py', 'flows.csv', 'policy.json']:
                shutil.copy(LABS / 'network' / file, folder)
            policy = json.loads((folder / 'policy.json').read_text())
            policy['rules'].append({'src': '10.10.10.20/32', 'dst': '203.0.113.9/32', 'port': 443, 'action': 'ALLOW'})
            (folder / 'policy.json').write_text(json.dumps(policy))
            result = subprocess.run([sys.executable, str(folder / 'evaluate.py')], capture_output=True, text=True)
            self.assertIn('N06 ALLOW MATCH', result.stdout)
            self.assertNotIn('MISMATCH', result.stdout)

    def test_crypto(self):
        expected = {
            'representation': ['426966726f7374', 'Qmlmcm9zdA==', 'Bifrost'],
            'modular': ['2 9'], 'classical': ['ELIURVW', 'BIFROST'],
            'hash': ['same= False', 'hex_length= 64'],
            'mac': ['original= True', 'changed= False'], 'nonce': ['True'],
            'password': ['same_salt= True', 'other_salt= False'],
        }
        for mode, lines in expected.items():
            with self.subTest(mode=mode):
                self.assertEqual(run('crypto', 'lab.py', mode).stdout.splitlines(), lines)

    def test_crypto_optional_package_missing_is_actionable(self):
        for script in ('aead.py', 'signature.py'):
            # Isolated + no-site deliberately removes installed third-party
            # packages, including PYTHONPATH, without modifying the machine.
            result = subprocess.run([sys.executable, '-I', '-S', str(LABS/'crypto'/script)],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('python -m pip install -r requirements.txt', result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_misc(self):
        self.assertEqual(run('misc', 'solve.py').stdout.splitlines(), ['step=1: Qmlmcm9zdA==', 'step=2: Bifrost'])
        self.assertEqual(base64.b64encode(base64.b64encode(b'Bifrost')).decode(), 'UW1sbWNtOXpkQT09')
        with tempfile.TemporaryDirectory(prefix='bifrost-puzzle-') as name:
            file = Path(name) / 'bad.txt'
            file.write_text('payload=bad!\n')
            result = run('misc', 'solve.py', str(file), ok=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Error', result.stderr)

    def test_cloud(self):
        original = run('cloud', 'review.py').stdout
        self.assertEqual(original.count('REVIEW'), 8)
        self.assertIn('passed=0/8', original)
        with tempfile.TemporaryDirectory(prefix='bifrost-cloud-') as name:
            file = Path(name) / 'config-work.json'
            config = json.loads((LABS / 'cloud' / 'config.json').read_text())
            config['storage'].update(public=False, encrypted=True)
            config['identity'].update(action='ReadObject', resource='training-notes', long_lived_key=False)
            config['network'].update(database_public=False, admin_source='192.0.2.0/24')
            config['audit'].update(enabled=True, retention_days=30)
            file.write_text(json.dumps(config))
            result = run('cloud', 'review.py', str(file)).stdout
            self.assertEqual(result.count('PASS'), 8)
            self.assertIn('passed=8/8', result)

    def test_cloud_reviewed_example(self):
        result = run('cloud', 'review.py', str(LABS/'cloud/config-reviewed.json'))
        self.assertIn('passed=8/8 review=0 invalid=0', result.stdout)
        self.assertNotIn('INVALID', result.stdout)

    def test_cloud_invalid_values_cannot_pass(self):
        good = json.loads((LABS/'cloud/config-reviewed.json').read_text())
        cases = [
            ('identity', 'action', ''), ('identity', 'resource', ''),
            ('identity', 'action', ' ReadObject'), ('identity', 'action', []),
            ('identity', 'resource', None), ('storage', 'public', 0),
            ('storage', 'encrypted', 'true'), ('identity', 'long_lived_key', 'false'),
            ('network', 'database_public', None), ('network', 'admin_source', ''),
            ('network', 'admin_source', '192.0.2.1'), ('network', 'admin_source', '192.0.2.1/24'),
            ('network', 'admin_source', '999.1.2.3/24'), ('network', 'admin_source', '::/129'),
            ('audit', 'enabled', 1), ('audit', 'retention_days', True),
            ('audit', 'retention_days', -1), ('audit', 'retention_days', 36501),
            ('audit', 'retention_days', 30.0),
        ]
        with tempfile.TemporaryDirectory(prefix='bifrost-invalid-cloud-') as name:
            file = Path(name)/'config.json'
            for section, field, value in cases:
                with self.subTest(section=section, field=field, value=value):
                    config = json.loads(json.dumps(good))
                    config[section][field] = value
                    file.write_text(json.dumps(config), encoding='utf-8')
                    result = run('cloud', 'review.py', str(file), ok=False)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('INVALID', result.stdout)
                    self.assertNotIn('passed=8/8', result.stdout)

    def test_cloud_invalid_documents_and_missing_fields(self):
        good = json.loads((LABS/'cloud/config-reviewed.json').read_text())
        documents = [[], None, 'config', {}, {**good, 'workload': ''}, {**good, 'provider': False},
                     {**good, 'identity': []}, {**good, 'audit': {'enabled': True}},
                     {**good, 'stoarge': {}}, {**good, 'storage': {**good['storage'], 'encryption': True}},
                     {**good, 'storage': {**good['storage'], 'name': ''}}]
        with tempfile.TemporaryDirectory(prefix='bifrost-cloud-document-') as name:
            file = Path(name)/'config.json'
            for config in documents:
                with self.subTest(config=config):
                    file.write_text(json.dumps(config), encoding='utf-8')
                    result = run('cloud', 'review.py', str(file), ok=False)
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn('passed=8/8', result.stdout)
                    self.assertNotIn('Traceback', result.stderr)
            file.write_text('{broken JSON', encoding='utf-8')
            self.assertEqual(run('cloud', 'review.py', str(file), ok=False).returncode, 2)
            for raw in ['{"audit":{},"audit":{}}', '{"unexpected":NaN}', '{"unexpected":Infinity}']:
                file.write_text(raw, encoding='utf-8')
                self.assertEqual(run('cloud', 'review.py', str(file), ok=False).returncode, 2)
            self.assertEqual(run('cloud', 'review.py', str(file.with_name('missing.json')), ok=False).returncode, 2)

    def test_cloud_review_is_distinct_from_invalid(self):
        good = json.loads((LABS/'cloud/config-reviewed.json').read_text())
        with tempfile.TemporaryDirectory(prefix='bifrost-cloud-review-') as name:
            file = Path(name)/'config.json'
            for section, field, value in [('network', 'admin_source', '0.0.0.0/0'),
                                          ('network', 'admin_source', '::/0'),
                                          ('identity', 'action', 'Read*'),
                                          ('identity', 'resource', 'training-?'),
                                          ('audit', 'retention_days', 29)]:
                config = json.loads(json.dumps(good))
                config[section][field] = value
                file.write_text(json.dumps(config), encoding='utf-8')
                result = run('cloud', 'review.py', str(file))
                self.assertIn('passed=7/8 review=1 invalid=0', result.stdout)
                self.assertNotIn('INVALID', result.stdout)

    def test_tls_summary_and_malformed_input(self):
        self.assertEqual(run('network', 'analyze_tls.py').stdout.splitlines(), [
            'frames=15', 'client_hello=1 server_hello=1', 'sni=bifrost.test',
            'negotiated=TLS1.3', 'encrypted_records=9', 'plaintext_http_visible=False'])
        data = (LABS/'network/tls13.pcap').read_bytes()
        with tempfile.TemporaryDirectory(prefix='bifrost-tls-invalid-') as name:
            file = Path(name)/'truncated.pcap'
            for damaged in [b'', data[:25], data[:-1], b'not a pcap']:
                file.write_bytes(damaged)
                result = run('network', 'analyze_tls.py', str(file), ok=False)
                self.assertEqual(result.returncode, 2)
                self.assertIn('INVALID fixture:', result.stdout)
                self.assertNotIn('Traceback', result.stderr)

    @unittest.skipUnless(HAS_CRYPTOGRAPHY, 'optional cryptography package; install labs/crypto/requirements.txt')
    def test_aead_real_authentication_and_known_vector(self):
        from cryptography.exceptions import InvalidTag
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        self.assertEqual(run('crypto', 'aead.py').stdout.splitlines(), [
            'original=ACCEPT message=Bifrost lesson 17', 'tampered_ciphertext=REJECT',
            'tampered_tag=REJECT', 'changed_aad=REJECT', 'changed_nonce=REJECT',
            'wrong_key=REJECT', 'fresh_round_trip=True'])
        # Independent published AES-GCM zero-key/zero-IV, one-block test vector.
        expected = bytes.fromhex('0388dace60b6a392f328c2b971b2fe78ab6e47d42cec13bdf53a67b21257bddf')
        self.assertEqual(AESGCM(bytes(16)).encrypt(bytes(12), bytes(16), None), expected)
        envelope = json.loads((LABS/'crypto/envelope.json').read_text())
        key = bytes.fromhex(json.loads((LABS/'crypto/teaching-key.json').read_text())['key_hex'])
        nonce = base64.b64decode(envelope['nonce_base64'], validate=True)
        encrypted = base64.b64decode(envelope['ciphertext_base64']) + base64.b64decode(envelope['tag_base64'])
        aad = envelope['aad_utf8'].encode()
        self.assertEqual(AESGCM(key).decrypt(nonce, encrypted, aad), b'Bifrost lesson 17')
        self.assertEqual(len(nonce), 12)
        self.assertEqual(len(base64.b64decode(envelope['tag_base64'])), 16)
        for candidate_nonce, candidate_data, candidate_aad in [(nonce, encrypted[:-1] + bytes([encrypted[-1] ^ 1]), aad),
                (nonce, encrypted, b'record-id=18'), (nonce[:-1] + b'!', encrypted, aad)]:
            with self.assertRaises(InvalidTag):
                AESGCM(key).decrypt(candidate_nonce, candidate_data, candidate_aad)

    @unittest.skipUnless(HAS_CRYPTOGRAPHY, 'optional cryptography package; install labs/crypto/requirements.txt')
    def test_signature_real_verification_and_rfc8032_vector(self):
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
        self.assertEqual(run('crypto', 'signature.py').stdout.splitlines(), [
            'original=VALID', 'tampered_message=INVALID', 'tampered_signature=INVALID',
            'wrong_key=INVALID', 'fresh_round_trip=True'])
        # RFC 8032 section 7.1, Ed25519 TEST 1 (empty message).
        private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(
            '9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60'))
        self.assertEqual(private.public_key().public_bytes_raw().hex(),
            'd75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a')
        self.assertEqual(private.sign(b'').hex(),
            'e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555f'
            'b8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b')
        fixture = json.loads((LABS/'crypto/signature.json').read_text())
        public = Ed25519PublicKey.from_public_bytes(base64.b64decode(fixture['public_key_base64']))
        signature = base64.b64decode(fixture['signature_base64'])
        message = fixture['message_utf8'].encode()
        self.assertIsNone(public.verify(signature, message))
        with self.assertRaises(InvalidSignature):
            public.verify(signature, message + b' ')

    @unittest.skipUnless(HAS_CRYPTOGRAPHY, 'optional cryptography package; install labs/crypto/requirements.txt')
    def test_crypto_changed_fixture_rejected_without_traceback(self):
        with tempfile.TemporaryDirectory(prefix='bifrost-crypto-change-') as name:
            folder = Path(name)
            for filename in ('aead.py', 'envelope.json', 'teaching-key.json'):
                shutil.copy(LABS/'crypto'/filename, folder)
            fixture = json.loads((folder/'envelope.json').read_text())
            fixture['aad_utf8'] = 'record-id=18'
            (folder/'envelope.json').write_text(json.dumps(fixture), encoding='utf-8')
            result = subprocess.run([sys.executable, str(folder/'aead.py')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout.strip(), 'fixture=REJECT reason=authentication_failed')
            self.assertNotIn('Bifrost lesson 17', result.stdout)
            self.assertNotIn('Traceback', result.stderr)
            fixture['nonce_base64'] = 'invalid!'
            (folder/'envelope.json').write_text(json.dumps(fixture), encoding='utf-8')
            result = subprocess.run([sys.executable, str(folder/'aead.py')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('fixture=INVALID', result.stdout)
            self.assertNotIn('Traceback', result.stderr)

    def test_pcap(self):
        def checksum(data):
            if len(data) % 2: data += b'\0'
            total = sum(struct.unpack('!' + 'H' * (len(data)//2), data))
            while total >> 16: total = (total & 65535) + (total >> 16)
            return (~total) & 65535
        data = (LABS / 'network' / 'traffic.pcap').read_bytes()
        self.assertEqual(struct.unpack('<IHHIIII', data[:24]), (0xa1b2c3d4, 2, 4, 0, 0, 65535, 1))
        offset = 24
        frames = []
        while offset < len(data):
            seconds, micros, size, original = struct.unpack('<IIII', data[offset:offset + 16])
            offset += 16
            frame = data[offset:offset + size]; offset += size
            self.assertEqual(len(frame), original)
            self.assertEqual(frame[12:14], b'\x08\x00')
            ip = frame[14:34]
            self.assertEqual(checksum(ip), 0)
            self.assertEqual(struct.unpack('!H', ip[2:4])[0], len(frame) - 14)
            if ip[9] == 6:
                segment = frame[34:]
                pseudo = ip[12:20] + struct.pack('!BBH', 0, 6, len(segment))
                self.assertEqual(checksum(pseudo + segment), 0)
            frames.append(frame)
        self.assertEqual(len(frames), 8)
        self.assertEqual(sum(f[23] == 17 for f in frames), 2)
        self.assertEqual(sum(f[23] == 6 for f in frames), 6)
        self.assertIn(b'GET /lesson HTTP/1.1', frames[5])
        self.assertIn(b'HTTP/1.1 200 OK', frames[6])
        self.assertTrue(frames[6].endswith(b'Bifrost\n'))

    def test_tls_pcap_transport_integrity_and_frozen_payload(self):
        def checksum(data):
            if len(data) % 2:
                data += b'\0'
            total = sum(struct.unpack('!' + 'H' * (len(data)//2), data))
            while total >> 16:
                total = (total & 65535) + (total >> 16)
            return (~total) & 65535
        data = (LABS/'network/tls13.pcap').read_bytes()
        offset, frames = 24, []
        expected_seq = {50001: 1000, 443: 9000}
        payloads = {50001: bytearray(), 443: bytearray()}
        while offset < len(data):
            _, _, size, original = struct.unpack('<IIII', data[offset:offset + 16])
            frame = data[offset + 16:offset + 16 + size]
            offset += 16 + size
            self.assertEqual(size, original)
            self.assertEqual(len(frame), size)
            self.assertEqual(frame[12:14], b'\x08\x00')
            ip, segment = frame[14:34], frame[34:]
            self.assertEqual(checksum(ip), 0)
            self.assertEqual(struct.unpack('!H', ip[2:4])[0], len(frame) - 14)
            self.assertLessEqual(len(frame) - 14, 1500)
            self.assertEqual(ip[9], 6)
            self.assertEqual(checksum(ip[12:20] + struct.pack('!BBH', 0, 6, len(segment)) + segment), 0)
            sport, dport, seq, ack = struct.unpack('!HHII', segment[:12])
            self.assertEqual({sport, dport}, {443, 50001})
            self.assertEqual(seq, expected_seq[sport])
            flags = segment[13]
            payload = segment[(segment[12] >> 4)*4:]
            if flags & 16:
                self.assertEqual(ack, expected_seq[dport])
            expected_seq[sport] += len(payload) + bool(flags & 2) + bool(flags & 1)
            payloads[sport].extend(payload)
            frames.append(frame)
        self.assertEqual(len(frames), 15)
        frozen = json.loads((ROOT/'content/lab-fixtures/tls13.json').read_text())
        for direction, port in [('client_to_server', 50001), ('server_to_client', 443)]:
            expected = b''.join(bytes.fromhex(chunk['hex']) for chunk in frozen['chunks'] if chunk['direction'] == direction)
            self.assertEqual(payloads[port], expected)
        self.assertNotIn(b'GET /lesson', data)
        self.assertNotIn(b'HTTP/1.1 200 OK', data)

    @unittest.skipUnless(HAS_CRYPTOGRAPHY, 'optional package for independent TLS authentication test')
    def test_tls13_records_authenticate_finished_signature_and_http(self):
        """Independently decrypt the PCAP using RFC 8446, not the lab parser.

        This proves the fixture is an authenticated TLS exchange rather than
        a few handwritten ClientHello-like bytes followed by random payload.
        """
        from cryptography import x509
        from cryptography.exceptions import InvalidTag
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        secrets = {}
        randoms = set()
        for line in (LABS/'network/tls13.keys').read_text().splitlines():
            if line and not line.startswith('#'):
                label, client_random, secret = line.split()
                secrets[label] = bytes.fromhex(secret)
                randoms.add(bytes.fromhex(client_random))
        self.assertEqual(len(randoms), 1)
        self.assertTrue(all(len(secret) == 48 for secret in secrets.values()))

        def expand(secret, label, size):
            label = b'tls13 ' + label
            info = size.to_bytes(2, 'big') + bytes([len(label)]) + label + b'\0'
            result, previous, counter = b'', b'', 1
            while len(result) < size:
                previous = hmac.digest(secret, previous + info + bytes([counter]), 'sha384')
                result += previous
                counter += 1
            return result[:size]

        transcript = bytearray()
        record_buffers = {50001: bytearray(), 443: bytearray()}
        handshake_buffers = {50001: bytearray(), 443: bytearray()}
        stages = {50001: 'HANDSHAKE_TRAFFIC_SECRET', 443: 'HANDSHAKE_TRAFFIC_SECRET'}
        sequences = {50001: 0, 443: 0}
        app = {50001: bytearray(), 443: bytearray()}
        seen_types, close_notify, encrypted_count = [], [], 0
        certificate = None

        def handshake_messages(port, plaintext):
            nonlocal certificate
            buffer = handshake_buffers[port]
            buffer.extend(plaintext)
            while len(buffer) >= 4:
                size = int.from_bytes(buffer[1:4], 'big')
                if len(buffer) < size + 4:
                    return
                message = bytes(buffer[:size + 4]); del buffer[:size + 4]
                kind, body = message[0], message[4:]
                if kind == 1:
                    self.assertEqual(body[2:34], next(iter(randoms)))
                    self.assertIn(b'bifrost.test', body)
                elif kind == 2:
                    index = 35 + body[34]
                    self.assertEqual(body[index:index + 2], b'\x13\x02')  # AES-256-GCM / SHA-384
                elif kind == 11:
                    self.assertEqual(port, 443)
                    self.assertEqual(body[0], 0)  # certificate_request_context
                    size = int.from_bytes(body[4:7], 'big')
                    certificate = x509.load_der_x509_certificate(body[7:7 + size])
                    self.assertEqual(certificate.subject, certificate.issuer)
                    self.assertEqual(certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                                     .value.get_values_for_type(x509.DNSName), ['bifrost.test'])
                    certificate.public_key().verify(certificate.signature, certificate.tbs_certificate_bytes,
                                                   ec.ECDSA(certificate.signature_hash_algorithm))
                elif kind == 15:
                    self.assertIsNotNone(certificate)
                    self.assertEqual(body[:2], b'\x04\x03')  # ecdsa_secp256r1_sha256
                    size = int.from_bytes(body[2:4], 'big')
                    self.assertEqual(len(body[4:]), size)
                    signed = b' ' * 64 + b'TLS 1.3, server CertificateVerify\0' + hashlib.sha384(transcript).digest()
                    certificate.public_key().verify(body[4:], signed, ec.ECDSA(hashes.SHA256()))
                elif kind == 20:
                    label = ('CLIENT_' if port == 50001 else 'SERVER_') + 'HANDSHAKE_TRAFFIC_SECRET'
                    finished_key = expand(secrets[label], b'finished', 48)
                    expected = hmac.digest(finished_key, hashlib.sha384(transcript).digest(), 'sha384')
                    self.assertEqual(body, expected)
                    stages[port] = 'TRAFFIC_SECRET_0'
                    sequences[port] = 0
                seen_types.append(kind)
                transcript.extend(message)

        data, offset = (LABS/'network/tls13.pcap').read_bytes(), 24
        while offset < len(data):
            size = struct.unpack('<I', data[offset + 8:offset + 12])[0]
            frame = data[offset + 16:offset + 16 + size]; offset += 16 + size
            segment = frame[34:]
            port = struct.unpack('!H', segment[:2])[0]
            record_buffers[port].extend(segment[(segment[12] >> 4)*4:])
            buffer = record_buffers[port]
            while len(buffer) >= 5:
                size = int.from_bytes(buffer[3:5], 'big')
                if len(buffer) < size + 5:
                    break
                header, content = bytes(buffer[:5]), bytes(buffer[5:5 + size])
                del buffer[:size + 5]
                kind = header[0]
                if kind == 20:  # middlebox compatibility ChangeCipherSpec, not a handshake message
                    self.assertEqual(content, b'\1')
                    continue
                if kind == 23:
                    encrypted_count += 1
                    label = ('CLIENT_' if port == 50001 else 'SERVER_') + stages[port]
                    secret = secrets[label]
                    key, iv = expand(secret, b'key', 32), expand(secret, b'iv', 12)
                    nonce = bytes(a ^ b for a, b in zip(iv, sequences[port].to_bytes(12, 'big')))
                    plain = AESGCM(key).decrypt(nonce, content, header)
                    # Independent negative case authenticates the actual record header and ciphertext.
                    corrupted = bytes([content[0] ^ 1]) + content[1:]
                    with self.assertRaises(InvalidTag):
                        AESGCM(key).decrypt(nonce, corrupted, header)
                    sequences[port] += 1
                    plain = plain.rstrip(b'\0')
                    kind, content = plain[-1], plain[:-1]
                if kind == 22:
                    handshake_messages(port, content)
                elif kind == 23:
                    app[port].extend(content)
                elif kind == 21:
                    self.assertEqual(content, b'\1\0')  # close_notify
                    close_notify.append(port)
                else:
                    self.fail(f'unexpected inner TLS type {kind}')
        self.assertEqual(seen_types, [1, 2, 8, 11, 15, 20, 20])
        self.assertEqual(encrypted_count, 9)
        self.assertEqual(app[50001], b'GET /lesson HTTP/1.1\r\nHost: bifrost.test\r\n\r\n')
        self.assertEqual(app[443], b'HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\nBifrost\n')
        self.assertEqual(close_notify, [50001, 443])
        self.assertTrue(all(not buffer for buffer in record_buffers.values()))
        self.assertTrue(all(not buffer for buffer in handshake_buffers.values()))

    def test_zip_and_hashes(self):
        archives = list(LABS.glob('*.zip'))
        self.assertEqual(len(archives), 9)
        for archive in archives:
            folder = LABS / archive.stem
            with zipfile.ZipFile(archive) as z:
                for file in folder.iterdir():
                    if file.is_file():
                        self.assertEqual(z.read(f'{folder.name}/{file.name}'), file.read_bytes())
            for line in (folder / 'SHA256SUMS.txt').read_text().splitlines():
                expected, filename = line.split('  ', 1)
                self.assertEqual(hashlib.sha256((folder / filename).read_bytes()).hexdigest(), expected)

    def test_zip_metadata_is_portable(self):
        for archive in LABS.glob('*.zip'):
            with zipfile.ZipFile(archive) as zipped:
                self.assertEqual(zipped.namelist(), sorted(zipped.namelist()))
                for entry in zipped.infolist():
                    self.assertEqual(entry.create_system, 3)
                    self.assertEqual(entry.external_attr, 0o100644 << 16)
                    self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual(entry.date_time, (2026, 10, 21, 0, 0, 0))
                    self.assertEqual(entry.extra, b'')
                    self.assertEqual(entry.comment, b'')
            names = [line.split('  ', 1)[1] for line in (LABS/archive.stem/'SHA256SUMS.txt').read_text().splitlines()]
            self.assertEqual(names, sorted(names))

    def test_generators_are_repeatable(self):
        paths = [ROOT/'index.html', ROOT/'sitemap.xml', ROOT/'js/curriculum.js', ROOT/'js/catalog.js',
                 ROOT/'js/visual-data.js', *ROOT.glob('js/courses/*.js'), *ROOT.glob('tracks/*/*.html'),
                 *LABS.glob('*/*'), *LABS.glob('*.zip')]
        before = {p: p.read_bytes() for p in paths if p.is_file()}
        subprocess.run([sys.executable, str(ROOT/'scripts/build_pages.py')], check=True, capture_output=True)
        subprocess.run([sys.executable, str(ROOT/'scripts/build_labs.py')], check=True, capture_output=True)
        self.assertEqual(before, {p: p.read_bytes() for p in before})

if __name__ == '__main__':
    unittest.main(verbosity=2)
