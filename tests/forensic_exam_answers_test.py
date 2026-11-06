"""Source coverage and independent executable checks for 150 forensic questions.

Source membership proves scope, not semantic correctness. See the editorial
audit for the separate question/answer/distractor review.
"""
import collections
import contextlib
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import sqlite3
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zlib

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'labs/forensic'


def module(name):
    spec = importlib.util.spec_from_file_location('exam_' + name, LAB / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class ForensicExamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course = json.loads((ROOT / 'content/courses/forensic.json').read_text(encoding='utf-8'))
        cls.banks = [json.loads((ROOT / f'content/exams/forensic-{n:02}.json').read_text(encoding='utf-8')) for n in range(1, 7)]
        cls.questions = {q['id']: q for bank in cls.banks for q in bank['questions']}
        cls.casework, cls.artifacts, cls.signature = (module(n) for n in ['casework', 'artifacts_round2', 'signature_lab'])

    def choice(self, bank, number):
        q = self.questions[f'forensic-m{bank:02}-q{number:02}']
        return q['options'][q['answer']]

    def output(self, action, source=None):
        stream = io.StringIO()
        connections = []
        connect = sqlite3.connect
        def tracked_connect(*args, **kwargs):
            connection = connect(*args, **kwargs)
            connections.append(connection)
            return connection
        try:
            with patch.object(sqlite3, 'connect', tracked_connect), contextlib.redirect_stdout(stream):
                action(source)
        finally:
            for connection in connections:
                connection.close()
        return stream.getvalue().strip()

    def test_scope_and_exact_lesson_evidence(self):
        evidence = json.loads((ROOT / 'developer-notes/forensic-exam-evidence-2026-11-06.json').read_text(encoding='utf-8'))
        self.assertEqual(len(self.questions), 150)
        self.assertEqual(set(evidence), set(self.questions))
        seen = set()
        expected_counts = [[8, 9, 8], [13, 12], [8, 8, 9], [15, 5, 5], [9, 8, 8], [12, 13]]
        for number, bank in enumerate(self.banks, 1):
            lessons = {l['id']: l for l in self.course['modules'][number - 1]['lessons']}
            self.assertEqual((bank['course'], bank['module'], bank['version']), ('forensic', number, 2))
            self.assertEqual(len(bank['questions']), 25)
            counts = collections.Counter(q['lesson'] for q in bank['questions'])
            self.assertEqual(set(counts), set(lessons))
            self.assertEqual([counts[key] for key in lessons], expected_counts[number - 1])
            self.assertEqual(sorted(collections.Counter(q['answer'] for q in bank['questions']).values()), [6, 6, 6, 7])
            for q in bank['questions']:
                with self.subTest(question=q['id']):
                    normalized = re.sub(r'\s+', ' ', q['prompt']).strip()
                    self.assertNotIn(normalized, seen)
                    seen.add(normalized)
                    self.assertEqual(len(q['options']), 4)
                    self.assertEqual(len({re.sub(r'\s+', ' ', o).strip() for o in q['options']}), 4)
                    self.assertIs(type(q['answer']), int)
                    self.assertIn(q['answer'], range(4))
                    self.assertGreater(len(q['explanation']), 30)
                    e = evidence[q['id']]
                    self.assertEqual(e['lesson'], q['lesson'])
                    source = lessons[q['lesson']]
                    for part in e['section'].split('.'):
                        source = source[part]
                    self.assertIn(e['quote'], source)

    def test_hash_logs_and_time_answers(self):
        original = (LAB / 'evidence.txt').read_bytes()
        digest = hashlib.sha256(original).digest()
        with tempfile.TemporaryDirectory(prefix='bifrost-exam-hash-') as directory:
            copy = Path(directory) / 'copy.txt'
            copy.write_bytes(original)
            self.assertEqual(hashlib.sha256(copy.read_bytes()).digest(), digest)
            copy.write_bytes(original + b'!')
            self.assertNotEqual(hashlib.sha256(copy.read_bytes()).digest(), digest)
        self.assertEqual((LAB / 'evidence.txt').read_bytes(), original)
        self.assertEqual(self.choice(1, 4), '원본 해시는 유지되고 사본 해시는 바뀐다.')
        with (LAB / 'auth.csv').open(encoding='utf-8', newline='') as file:
            rows = list(csv.DictReader(file))
        denied = [r for r in rows if r['event'] == 'login_denied']
        self.assertEqual([r['id'] for r in denied], ['E02', 'E03', 'E04'])
        self.assertEqual({(r['user'], r['source']) for r in denied}, {('bob', '198.51.100.8')})
        stamps = [datetime.fromisoformat(r['time']) for r in denied]
        self.assertEqual([(b - a).total_seconds() for a, b in zip(stamps, stamps[1:])], [10, 10])
        self.assertEqual(self.choice(1, 11), '10초')
        for n, text in [(1, '2026-10-20T09:00:00+09:00'), (2, '2026-10-20T01:30:00+09:00'), (8, '2026-10-20T09:02:00+09:00')]:
            self.assertEqual(datetime.fromisoformat(text).astimezone(timezone.utc).isoformat(), self.choice(2, n))
        chosen = self.choice(2, 10)
        self.assertLess(datetime.fromisoformat('2026-10-20T09:00:00+09:00'), datetime.fromisoformat('2026-10-20T00:30:00+00:00'))
        self.assertEqual(chosen, '09:00+09:00의 사건')
        ids = [r['id'] for r in sorted(rows, key=lambda r: datetime.fromisoformat(r['time']))]
        self.assertEqual(' → '.join(ids), self.choice(2, 13))

    def test_actual_casework_and_sql_mutations(self):
        # Learner code runs only against supplied synthetic fixtures and temp copies.
        with tempfile.TemporaryDirectory(prefix='bifrost-exam-case-') as directory:
            directory = Path(directory)
            def save(name, value):
                path = directory / name
                path.write_text(json.dumps(value), encoding='utf-8')
                return path
            host = self.output(self.casework.host)
            self.assertIn('C01 viewer->helper remote=203.0.113.44:443', host)
            self.assertIn('C03 pid=999 process=UNKNOWN', host)
            self.assertEqual(self.choice(3, 10), 'viewer → helper → 203.0.113.44:443')
            snapshot = json.loads((LAB / 'snapshot.json').read_text())
            snapshot['connections'][0]['pid'] = 999
            self.assertIn('C01 pid=999 process=UNKNOWN', self.output(self.casework.host, save('snapshot.json', snapshot)))
            self.assertIn('records=3 mode=plan-only', self.output(self.casework.plan))
            self.assertIn('total=3 displayed=2 synthetic=True', self.output(self.casework.browser))
            self.assertEqual(self.choice(3, 18), '표시 2행 / 전체 3행')
            sql = (LAB / 'history.sql').read_text()
            with contextlib.closing(sqlite3.connect(':memory:')) as db:
                db.executescript(sql)
                self.assertEqual(db.execute("SELECT id FROM visits WHERE transition != 'auto' ORDER BY time,id").fetchall(), [('B01',), ('B02',)])
            path = directory / 'history.sql'
            path.write_text(sql.replace("'auto'", "'link'"))
            self.assertIn('total=3 displayed=3 synthetic=True', self.output(self.casework.browser, path))
            self.assertEqual(self.choice(3, 19), '표시 3행 / 전체 3행')
            carving = self.output(self.casework.carve)
            self.assertEqual(carving, 'offset=2 declared=3 available=3 COMPLETE\noffset=10 declared=5 available=2 INCOMPLETE')
            raw = bytes.fromhex((LAB / 'fragments.hex').read_text())
            self.assertEqual(int.from_bytes(raw[4:6], 'little'), 3)
            self.assertEqual(self.choice(4, 2), '3바이트')
            self.assertEqual((raw + bytes.fromhex('5a3132'))[14:], b'XYZ12')
            path = directory / 'fragments.hex'; path.write_text((raw + bytes.fromhex('5a3132')).hex())
            self.assertIn('offset=10 declared=5 available=5 COMPLETE', self.output(self.casework.carve, path))
            self.assertTrue(self.choice(4, 4).startswith('XYZ12,'))
            self.assertIn('linked=4 excluded=1', self.output(self.casework.correlate))
            with (LAB / 'crosslog.csv').open(newline='') as file:
                rows = list(csv.DictReader(file))
            target = next(r for r in rows if r['id'] == 'W02')
            target.update(host='workstation-7', session='S10')
            path = directory / 'crosslog.csv'
            with path.open('w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
            output = self.output(self.casework.correlate, path)
            self.assertIn('linked=5 excluded=0', output)
            self.assertIn('W02 2026-10-01T00:00:10+00:00', output)
            self.assertEqual(self.choice(4, 18), '5건, 00:00:10')
            rows[0]['time'] = '2026-10-01T09:00:00'
            with path.open('w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=rows[0].keys()); writer.writeheader(); writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, 'timezone required'):
                self.output(self.casework.correlate, path)
            response = json.loads((LAB / 'response.json').read_text())
            self.assertIn('isolate-network READY-FOR-REVIEW', self.output(self.casework.respond))
            response['actions'][0]['authorized'] = False
            output = self.output(self.casework.respond, save('response.json', response))
            self.assertIn('isolate-network HOLD', output)
            self.assertIn('execution=NONE', output)
            self.assertEqual(self.choice(4, 23), 'HOLD')

    def test_independent_png_structure_crc_and_extract(self):
        fixtures = {name: bytes.fromhex(value) for name, value in json.loads((LAB / 'signature-fixtures.json').read_text()).items()}
        png = fixtures['image.png']
        self.assertEqual(png[:8].hex(' '), self.choice(4, 8))
        pos, chunks = 8, []
        while pos < len(png):
            size = struct.unpack('>I', png[pos:pos+4])[0]
            kind = png[pos+4:pos+8]
            data = png[pos+8:pos+8+size]
            crc = struct.unpack('>I', png[pos+8+size:pos+12+size])[0]
            self.assertEqual(zlib.crc32(kind + data) & 0xffffffff, crc)
            chunks.append(kind)
            if kind == b'IHDR':
                self.assertEqual(size, 13)
                self.assertEqual(size + 12, int(self.choice(4, 10).removesuffix('바이트')))
            pos += 12 + size
        self.assertEqual(chunks, [b'IHDR', b'IDAT', b'IEND'])
        self.assertEqual(pos, len(png))
        self.assertEqual(fixtures['renamed.txt'], png)
        mixed = fixtures['mixed.bin']; start = mixed.find(png[:8])
        self.assertEqual(start, 17)
        end, _ = self.signature.png_end(mixed, start)
        self.assertEqual(mixed[start:end], png)
        self.assertEqual(hashlib.sha256(mixed[start:end]).digest(), hashlib.sha256(png).digest())
        bad = bytearray(png); bad[29] ^= 1  # IHDR CRC only, keep signature/data intact.
        with self.assertRaisesRegex(ValueError, 'CRC mismatch'):
            self.signature.png_end(bytes(bad))
        self.assertEqual(self.choice(4, 5), '아홉 번째 바이트')
        self.assertEqual(self.choice(4, 6), '4바이트')

    def test_actual_os_records_and_mutations(self):
        with tempfile.TemporaryDirectory(prefix='bifrost-exam-os-') as directory:
            directory = Path(directory)
            xml = LAB / 'events-synthetic.xml'
            baseline = self.output(self.artifacts.windows, xml)
            self.assertIn('record=101 event=4625', baseline)
            self.assertIn('record=102 event=4624 utc=2026-10-02T00:00:10+00:00 user=alice type=3', baseline)
            tree = ET.parse(xml); ns = self.artifacts.NS
            for event in tree.getroot().findall('e:Event', ns):
                data = event.find('e:EventData', ns); data[:] = list(reversed(list(data)))
            path = directory / 'reordered.xml'; tree.write(path)
            self.assertEqual(self.output(self.artifacts.windows, path), baseline)
            ids = tree.getroot().findall('e:Event/e:System/e:EventRecordID', ns)
            ids[1].text = ids[0].text; tree.write(path)
            with self.assertRaisesRegex(ValueError, 'duplicate record ID'):
                self.output(self.artifacts.windows, path)
            linux = LAB / 'linux-auth.jsonl'
            self.assertIn('L13 user=alice result=allow linked-login=True', self.output(self.artifacts.linux, linux))
            self.assertIn('L14 user=bob result=deny linked-login=False', self.output(self.artifacts.linux, linux))
            rows = [json.loads(line) for line in linux.read_text().splitlines()]
            next(r for r in rows if r['id'] == 'L13')['session'] = 'S99'
            path = directory / 'linux.jsonl'; path.write_text('\n'.join(json.dumps(r) for r in rows))
            self.assertIn('L13 user=alice result=allow linked-login=False', self.output(self.artifacts.linux, path))
            self.assertEqual(self.choice(5, 14), 'linked-login=False가 되고 allow 자체는 유지된다.')
            records = json.loads((LAB / 'fs-records.json').read_text())
            self.assertIn('inode=42 observed-names=2 declared-links=2', self.output(self.artifacts.filesystem, LAB / 'fs-records.json'))
            records['records'] = [r for r in records['records'] if r['record'] != 'R2']
            path = directory / 'fs.json'; path.write_text(json.dumps(records))
            self.assertIn('inode=42 observed-names=1 declared-links=2', self.output(self.artifacts.filesystem, path))
            self.assertEqual(self.choice(5, 19), '이름 2개와 파일 객체 1개')

    def test_memory_intervals_and_coverage_boundaries(self):
        with tempfile.TemporaryDirectory(prefix='bifrost-exam-range-') as directory:
            directory = Path(directory)
            sample = json.loads((LAB / 'memory-model.json').read_text())
            m2 = next(r for p in sample['processes'] for r in p['ranges'] if r['id'] == 'M2')
            self.assertEqual(self.choice(6, 2), f"[{m2['start']},{m2['start'] + m2['size']})")
            self.assertNotIn(int(self.choice(6, 3)), range(m2['start'], m2['start'] + m2['size']))
            self.assertIn('review=1', self.output(self.artifacts.memory, LAB / 'memory-model.json'))
            m2['permission'] = 'rx'
            path = directory / 'memory.json'; path.write_text(json.dumps(sample))
            self.assertEqual(self.output(self.artifacts.memory, path), 'review=0 verdict=NOT-A-MALWARE-VERDICT')
            self.assertEqual(self.choice(6, 6), '0개')
            m2['size'] = 0; path.write_text(json.dumps(sample))
            with self.assertRaisesRegex(ValueError, 'positive size'):
                self.output(self.artifacts.memory, path)
            data = json.loads((LAB / 'coverage.json').read_text())
            for question, e in zip([15, 16], data['events']):
                center = e['recorded'] - e['clock_ahead']
                expected = (center - e['uncertainty'], center + e['uncertainty'])
                self.assertEqual(self.artifacts.interval(e), expected)
                self.assertEqual(self.choice(6, question), f'[{expected[0]},{expected[1]}]')
            for lo_a, hi_a, lo_b, hi_b, number in [(90,94,93,99,17),(90,94,94,99,18),(90,92,93,99,19),(95,100,80,90,25)]:
                a = dict(recorded=(lo_a+hi_a), clock_ahead=0, uncertainty=(hi_a-lo_a))
                b = dict(recorded=(lo_b+hi_b), clock_ahead=0, uncertainty=(hi_b-lo_b))
                # Double every bound so odd centers can remain integer in this model.
                fixture = dict(events=[dict(id='A',**a),dict(id='B',**b)],coverage=[])
                path = directory / 'intervals.json'; path.write_text(json.dumps(fixture))
                self.assertIn('relation=' + self.choice(6, number), self.output(self.artifacts.coverage, path))
            path = directory / 'coverage.json'; path.write_text(json.dumps(data))
            baseline = self.output(self.artifacts.coverage, path)
            self.assertIn('relation=ORDER-UNCERTAIN', baseline)
            data['coverage'][1]['enabled'] = True; path.write_text(json.dumps(data))
            self.assertEqual(self.output(self.artifacts.coverage, path), baseline.replace('process logging-enabled=False','process logging-enabled=True'))
            for e in data['events']: e['uncertainty'] = 0
            path.write_text(json.dumps(data))
            output = self.output(self.artifacts.coverage, path)
            self.assertIn('E31 corrected=[92,92]\nE32 corrected=[96,96]\nrelation=A-BEFORE-B', output)
            self.assertEqual(self.choice(6, 20), '[92,92], [96,96], A-BEFORE-B')


if __name__ == '__main__':
    unittest.main(verbosity=2)
