"""Review regressions across the 17 authored banks; run standalone or in answer CI."""
import json
import itertools
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExamReviewTest(unittest.TestCase):
    def test_independent_answer_arrangements(self):
        sequences = []
        for file in sorted((ROOT / 'content/exams').glob('*.json')):
            bank = json.loads(file.read_text(encoding='utf-8'))
            sequence = [q['answer'] for q in bank['questions']]
            self.assertEqual(bank['version'], 2)
            for _, run in itertools.groupby(sequence):
                self.assertLessEqual(len(list(run)), 3, bank['id'])
            for period in range(2, 6):
                for start in range(25 - 3 * period + 1):
                    self.assertNotEqual(sequence[start:start+3*period], sequence[start:start+period]*3,
                                        f'{bank["id"]}: long periodic answer block')
            sequences.append((bank['id'], sequence))
        self.assertEqual(len(sequences), 17)
        for (name, a), (other, b) in itertools.combinations(sequences, 2):
            for shift in range(25):
                rotated = b[shift:] + b[:shift]
                self.assertLessEqual(sum(x == y for x, y in zip(a, rotated)), 14, (name, other, shift))
            for shift in range(-9, 10):
                left, right = (a[shift:], b[:25-shift]) if shift >= 0 else (a[:25+shift], b[-shift:])
                self.assertLessEqual(sum(x == y for x, y in zip(left, right)), int(len(left) * .7),
                                     (name, other, shift))

    def test_migration_against_independent_v1_option_fixture(self):
        previous = json.loads((ROOT / 'tests/exam-v1-options.json').read_text(encoding='utf-8'))
        corrections = json.loads((ROOT / 'developer-notes/exam-recheck-changes-2026-11-06.json').read_text(encoding='utf-8'))
        corrected_options = {r['question']: r['after']['options'] for r in corrections if 'options' in r['after']}
        distractors = json.loads((ROOT / 'developer-notes/exam-distractor-revisions-2026-11-06.json').read_text(encoding='utf-8'))
        revised_distractors = {(r['question'], r['old_option_index']): r['after'] for r in distractors}
        for file in sorted((ROOT / 'content/exams').glob('*.json')):
            bank = json.loads(file.read_text(encoding='utf-8'))
            self.assertEqual(bank['previousVersion'], 1)
            self.assertEqual(set(bank['previousAnswerMap']), set(previous[bank['id']]))
            for q in bank['questions']:
                old = previous[bank['id']][q['id']]
                mapping = bank['previousAnswerMap'][q['id']]
                self.assertEqual(sorted(mapping), [0, 1, 2, 3])
                self.assertEqual(mapping[old['answer']], q['answer'], q['id'])
                expected = corrected_options.get(q['id'], old['options'])
                for old_index, new_index in enumerate(mapping):
                    text = revised_distractors.get((q['id'], old_index), expected[old_index])
                    self.assertEqual(q['options'][new_index], text, q['id'])

    def test_all_425_questions_have_visible_distinct_options_and_module_scope(self):
        seen = set()
        counts = {}
        for course, modules in [('foundation', 5), ('pwn', 6), ('forensic', 6)]:
            authored = json.loads((ROOT / f'content/courses/{course}.json').read_text(encoding='utf-8'))
            total = 0
            for number in range(1, modules + 1):
                bank = json.loads((ROOT / f'content/exams/{course}-{number:02}.json').read_text(encoding='utf-8'))
                self.assertEqual(len(bank['questions']), 25)
                allowed = {l['id'] for l in authored['modules'][number - 1]['lessons']}
                self.assertEqual({q['lesson'] for q in bank['questions']}, allowed)
                for q in bank['questions']:
                    with self.subTest(question=q['id']):
                        self.assertNotIn(q['id'], seen)
                        seen.add(q['id'])
                        self.assertIn(q['lesson'], allowed)
                        self.assertIs(type(q['answer']), int)
                        self.assertIn(q['answer'], range(4))
                        visible = [re.sub(r'\s+', ' ', option).strip() for option in q['options']]
                        self.assertEqual(len(visible), 4)
                        self.assertEqual(len(set(visible)), 4, 'HTML whitespace collapsing must not make choices identical')
                        for original, rendered in zip(q['options'], visible):
                            self.assertEqual(original, rendered,
                                'Whitespace-sensitive inputs need quotes or a visible explanation, not invisible edge spaces')
                    total += 1
            counts[course] = total
        self.assertEqual(counts, dict(foundation=125, pwn=150, forensic=150))
        self.assertEqual(len(seen), 425)

    def test_printable_ascii_is_valid_utf8_but_not_every_utf8_string_is_ascii(self):
        raw = bytes(range(32, 127))
        self.assertEqual(raw.decode('ascii'), raw.decode('utf-8'))
        non_ascii_utf8 = '가'.encode('utf-8')
        self.assertEqual(non_ascii_utf8.decode('utf-8'), '가')
        with self.assertRaises(UnicodeDecodeError):
            non_ascii_utf8.decode('ascii')

    @unittest.skipUnless(shutil.which('gcc'), 'GCC reference checks run in Linux/WSL')
    def test_zero_conversion_and_equal_length_counterexamples(self):
        code = r'''
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    const char *inputs[] = {"x", "3x", "30"};
    for (size_t i=0; i<3; ++i) {
        char *end;
        (void)strtoumax(inputs[i], &end, 10);
        printf("%s: digits=%d entire=%d\n", inputs[i], end != inputs[i], *end == '\0');
    }
    char data[8] = "ABC";
    size_t filled = 3;
    printf("capacity=%zu filled=%zu string=%zu\n", sizeof data, filled, strlen(data));
    return 0;
}
'''
        with tempfile.TemporaryDirectory(prefix='bifrost-exam-review-') as directory:
            source = Path(directory) / 'reference.c'
            exe = Path(directory) / 'reference'
            source.write_text(code, encoding='utf-8')
            subprocess.run(['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(exe)],
                           check=True, capture_output=True, timeout=15)
            result = subprocess.run([str(exe)], check=True, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.stdout, 'x: digits=0 entire=0\n3x: digits=1 entire=0\n30: digits=1 entire=1\ncapacity=8 filled=3 string=3\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
