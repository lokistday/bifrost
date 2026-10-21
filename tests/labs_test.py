"""Execute offline labs and verify files, backups and generated teaching fixtures."""
from pathlib import Path
from datetime import datetime, timezone
import base64
import csv
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / 'labs'

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

    def test_zip_and_hashes(self):
        archives = list(LABS.glob('*.zip'))
        self.assertEqual(len(archives), 9)
        for archive in archives:
            folder = LABS / archive.stem
            with zipfile.ZipFile(archive) as z:
                for file in folder.iterdir():
                    self.assertEqual(z.read(f'{folder.name}/{file.name}'), file.read_bytes())
            for line in (folder / 'SHA256SUMS.txt').read_text().splitlines():
                expected, filename = line.split('  ', 1)
                self.assertEqual(hashlib.sha256((folder / filename).read_bytes()).hexdigest(), expected)

    def test_generators_are_repeatable(self):
        paths = [ROOT/'index.html', *ROOT.glob('tracks/*/*.html'), *LABS.glob('*/*'), *LABS.glob('*.zip')]
        before = {p: p.read_bytes() for p in paths if p.is_file()}
        subprocess.run([sys.executable, str(ROOT/'scripts/build_pages.py')], check=True, capture_output=True)
        subprocess.run([sys.executable, str(ROOT/'scripts/build_labs.py')], check=True, capture_output=True)
        self.assertEqual(before, {p: p.read_bytes() for p in before})

if __name__ == '__main__':
    unittest.main(verbosity=2)
