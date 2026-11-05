"""Audit all 150 System Security questions against authored lessons and real C labs.

Evidence checks do not prove semantic correctness. The recorded editorial review
is complemented by compiling the exact learner labs and safe task variants here.
"""
import collections
import json
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SystemExamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course = json.loads((ROOT / 'content/courses/pwn.json').read_text(encoding='utf-8'))
        cls.banks = [json.loads((ROOT / f'content/exams/pwn-{n:02}.json').read_text(encoding='utf-8')) for n in range(1, 7)]
        cls.questions = {q['id']: q for bank in cls.banks for q in bank['questions']}

    def answer(self, module, number):
        q = self.questions[f'pwn-m{module:02}-q{number:02}']
        return q['options'][q['answer']]

    def test_scope_evidence_and_unambiguous_structure(self):
        evidence = json.loads((ROOT / 'developer-notes/pwn-exam-evidence-2026-11-05.json').read_text(encoding='utf-8'))
        self.assertEqual(len(self.questions), 150)
        self.assertEqual(set(evidence), set(self.questions))
        prompts = set()
        for n, bank in enumerate(self.banks, 1):
            module = self.course['modules'][n - 1]
            lessons = {l['id']: l for l in module['lessons']}
            self.assertEqual((bank['course'], bank['module'], bank['version']), ('pwn', n, 1))
            self.assertEqual(len(bank['questions']), 25)
            counts = collections.Counter(q['lesson'] for q in bank['questions'])
            self.assertEqual(set(counts), set(lessons))
            self.assertGreaterEqual(min(counts.values()), 8 if len(lessons) == 3 else 12)
            balance = collections.Counter(q['answer'] for q in bank['questions'])
            self.assertEqual(sorted(balance.values()), [6, 6, 6, 7])
            for q in bank['questions']:
                with self.subTest(question=q['id']):
                    self.assertNotIn(q['prompt'], prompts)
                    prompts.add(q['prompt'])
                    self.assertEqual(len(q['options']), 4)
                    self.assertEqual(len(set(o.strip() for o in q['options'])), 4)
                    self.assertIs(type(q['answer']), int)
                    self.assertIn(q['answer'], range(4))
                    self.assertGreater(len(q['explanation']), 30)
                    record = evidence[q['id']]
                    self.assertEqual(record['lesson'], q['lesson'])
                    source = lessons[q['lesson']]
                    for component in record['section'].split('.'):
                        source = source[component]
                    self.assertIn(record['quote'], source, 'Evidence must be an exact authored lesson paragraph')

    def test_exam_edit_does_not_invalidate_shared_assets(self):
        spec = importlib.util.spec_from_file_location('exam_cache_metadata', ROOT / 'scripts/build_metadata.py')
        metadata = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(metadata)
        real_read = Path.read_bytes
        def fingerprint(changed=None):
            def read(file):
                value = real_read(file)
                return value + b'\n/* audit mutation */' if file == changed else value
            with patch.object(Path, 'read_bytes', read), patch.object(Path, 'write_text'):
                return metadata.build({})['contentVersion']
        baseline = fingerprint()
        self.assertEqual(fingerprint(ROOT / 'content/exams/pwn-01.json'), baseline)
        self.assertNotEqual(fingerprint(ROOT / 'css/main.css'), baseline)

    @unittest.skipUnless(shutil.which('gcc'), 'Executable C answer audit requires GCC (run under Linux/WSL)')
    def test_real_lab_outputs_and_task_variants(self):
        with tempfile.TemporaryDirectory(prefix='bifrost-pwn-exam-') as folder:
            folder = Path(folder)
            def run(name, args=(), replace=None, driver=None, status=0):
                source = (ROOT / f'labs/pwn/{name}.c').read_text(encoding='utf-8')
                for before, after in (replace or {}).items():
                    self.assertIn(before, source)
                    source = source.replace(before, after)
                if driver:
                    source = '#define main learner_example_main\n' + source + '\n#undef main\n' + driver
                file = folder / f'{name}.c'
                exe = folder / name
                file.write_text(source, encoding='utf-8')
                subprocess.run(['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-Wformat=2', '-O0',
                                str(file), '-o', str(exe)], check=True, capture_output=True, text=True, timeout=15)
                result = subprocess.run([str(exe), *args], capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, status, result.stderr)
                return result.stdout.strip()

            # Build/memory/bounds: never execute the undefined original bounds read.
            self.assertEqual(run('memory', replace={'local = 7': 'local = 8'}), 'local=8 heap=9\n10 20 30')
            self.assertEqual(self.answer(1, 8), 'local=8이 되고 heap=9 및 배열 값은 유지된다.')
            self.assertEqual(run('bounds', replace={'i <= 3': 'i < 3'}), '10\n20\n30')
            self.assertEqual(self.answer(1, 23), '10 / 20 / 30 세 값')
            self.assertEqual(run('memory'), 'local=7 heap=9\n10 20 30')
            self.assertEqual(self.answer(2, 8), '9')

            # Fixed decimal syntax and inclusive upper bound.
            for arg, output in [('0003', 'count=3'), ('0', 'count=0'), ('1024', 'count=1024')]:
                self.assertEqual(run('parse_count', [arg]), output)
            for arg in ['1025', '-1', '+3', ' 3', '3x', '', '9' * 100]:
                self.assertEqual(run('parse_count', [arg], status=2), 'INVALID_COUNT')
            self.assertEqual(self.answer(3, 1), '0003')
            self.assertEqual(self.answer(3, 2), '1024는 허용, 1025는 거부')
            self.assertEqual(self.answer(3, 6), '십진수 3')
            self.assertEqual(run('allocation_size', replace={'allocation_size(3, 4, 8': 'allocation_size(5, 4, 8'}),
                             'small=OK bytes=28\nhuge=REJECT\nempty=OK bytes=8\nzero-element=REJECT')
            self.assertEqual(self.answer(3, 13), '28')
            self.assertEqual(run('format_data'), 'literal=%s%n\nrequired=6 capacity=8 truncated=no\nstored=[%s%n]')
            self.assertEqual(self.answer(3, 19), '%s%n을 데이터 문자열로 출력한다.')
            self.assertEqual(run('format_data', ['ABCDEF']), 'literal=ABCDEF\nrequired=8 capacity=8 truncated=yes\nstored=[ABCDEF')
            self.assertEqual(self.answer(3, 23), 'needed=8, 잘림 yes')
            self.assertIn('required=9 capacity=10 truncated=no\nstored=[Bifrost]',
                          run('format_data', ['Bifrost'], replace={'message[8]': 'message[10]'}))
            self.assertEqual(self.answer(3, 24), '10바이트')

            # Execute the actual static parser with new boundary inputs.
            parser = run('packet_parse', driver='''
int main(void) {
    unsigned char big[260] = {1,2};
    unsigned char mismatch[] = {0,2,'B','I','F'};
    unsigned char empty[] = {0,0};
    size_t n = 99;
    int ok = payload_length(big, sizeof big, &n);
    printf("big=%d length=%zu\\n", ok, n);
    printf("mismatch=%d\\n", payload_length(mismatch, sizeof mismatch, &n));
    ok = payload_length(empty, sizeof empty, &n);
    printf("empty=%d length=%zu\\n", ok, n);
    return 0;
}''')
            self.assertEqual(parser, 'big=1 length=258\nmismatch=0\nempty=1 length=0')
            self.assertEqual(self.answer(4, 15), '258')
            self.assertEqual(self.answer(4, 17), '거부한다. 선언 2와 실제 본문 3이 다르다.')
            self.assertEqual(self.answer(4, 18), '허용하고 payload 길이 0')
            self.assertIn('normal=OK length=3', run('packet_parse'))
            self.assertEqual(self.answer(4, 25), 'OK, length=3')

            wire = run('struct_wire', replace={'UINT32_C(0x01020304)': 'UINT32_C(0x0A0B0C0D)'})
            self.assertEqual(wire, 'wire_bytes=7 hex=010a0b0c0d0506\nroundtrip=True\nshort=REJECT')
            self.assertEqual(self.answer(5, 5), '7바이트')
            self.assertEqual(self.answer(5, 8), '010a0b0c0d0506')
            nul = run('embedded_nul')
            self.assertIn('string_length=2', nul)
            self.assertIn('4142004344', nul)
            self.assertEqual(self.answer(5, 14), '2')
            self.assertEqual(self.answer(5, 15), '4142004344')
            endnul = run('embedded_nul', replace={"'A', 'B', 0, 'C', 'D'": "'A', 'B', 'C', 'D', 0"})
            self.assertIn('buffer_bytes=5 string_length=4', endnul)
            self.assertIn('4142434400', endnul)
            self.assertEqual(self.answer(5, 20), '버퍼 5바이트, strlen 4')
            self.assertEqual(self.answer(5, 25), '4142434400')

            fd = run('fd_lifetime')
            self.assertIn('first=AB', fd)
            self.assertIn('via_dup=CD', fd)
            self.assertIn('after_close=EF', fd)
            self.assertEqual(self.answer(6, 3), 'CD')
            self.assertIn('first=12\nvia_dup=34\nafter_close=56', run('fd_lifetime', replace={'ABCDEF': '123456'}))
            self.assertEqual(self.answer(6, 6), '12 → 34 → 56')
            run('fd_lifetime', replace={'dup(fd)': 'fd'}, status=2)
            stream = run('stream_chunks', replace={'0, 2, 0': '0, 1, 0'})
            self.assertEqual(stream, 'complete=OK payload=BIFRO reads=7\ntruncated=REJECT reads=6\nwritten=7 calls=7\nstalled=REJECT')
            self.assertEqual(self.answer(6, 15), '7회')
            self.assertEqual(self.answer(6, 16), '6회: 헤더 2 + 본문 3 + EOF 확인 1')
            self.assertEqual(run('open_boundary'), 'regular=ACCEPT\nsecond_create=EXISTS\nsymlink=REJECT\nopened_object=STILL_REGULAR')
            self.assertEqual(self.answer(6, 24), 'second_create=EXISTS')
            run('open_boundary', replace={' | O_NOFOLLOW': ''}, status=2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
