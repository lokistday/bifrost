"""Execute authored code-output questions independently from the browser grader."""
import json
import importlib.util
import subprocess
import sys
import unittest
from pwn_exam_answers_test import SystemExamTest
from forensic_exam_answers_test import ForensicExamTest
from exam_review_test import ExamReviewTest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExamAnswersTest(unittest.TestCase):
    def test_answers_against_actual_workflow_lab(self):
        spec = importlib.util.spec_from_file_location('exam_workflow', ROOT / 'labs/foundation/workflow.py')
        workflow = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(workflow)
        # Module 05 answers must match the same implementation used by learners.
        original = {'tags': ['base']}
        duplicate = workflow.tagged_copy(original, 'new')
        self.assertEqual(original, {'tags': ['base']})
        self.assertEqual(duplicate['tags'], ['base', 'new'])
        with tempfile.TemporaryDirectory(prefix='bifrost-exam-audit-') as folder:
            target = Path(folder) / 'report.json'
            target.write_text('{"version":1}', encoding='utf-8')
            with self.assertRaises(RuntimeError):
                workflow.atomic_json(target, {'version': 2}, fail_before_replace=True)
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'version': 1})
            self.assertEqual(list(Path(folder).glob('.pending-*')), [])
            workflow.atomic_json(target, {'version': 2})
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'version': 2})
        self.assertEqual(workflow.resolve_timeout({'timeout': 10}, {'BIFROST_TIMEOUT': '20'}, 30), (30, 'cli'))
        with self.assertRaises(ValueError):
            workflow.resolve_timeout(environ={'BIFROST_TIMEOUT': ''})
        with self.assertRaises(ValueError):
            workflow.resolve_timeout({'timeout': 'bad'}, cli=30)
        self.assertEqual(workflow.timeout_value('20'), 20)
        args = ['hello world', 'x;echo NOT_A_COMMAND']
        child = workflow.run_worker(args)
        self.assertEqual(child.returncode, 0)
        self.assertEqual(json.loads(child.stdout.removeprefix('argv=')), args)
        self.assertEqual(workflow.run_worker(['--fail']).returncode, 3)
        with self.assertRaises(subprocess.TimeoutExpired):
            workflow.run_worker(['--sleep'], timeout=.1)
        payload = dict(event='exam.audit', request_id='one\ntwo', result='ok', status=200,
                       password='fixture-only', authorization='fixture-only')
        encoded = workflow.log_record(payload)
        self.assertEqual(set(json.loads(encoded)), {'event', 'request_id', 'result', 'status'})
        self.assertNotIn('fixture-only', encoded)
        self.assertNotIn('\n', encoded)
        with self.assertRaises(ValueError):
            workflow.log_record({**payload, 'status': True})

    def test_executable_answers(self):
        cases = json.loads((ROOT / 'tests/exam-reference-cases.json').read_text(encoding='utf-8'))
        self.assertEqual(len(cases), 27)
        for case in cases:
            exam = json.loads((ROOT / f'content/exams/{case["exam"]}.json').read_text(encoding='utf-8'))
            question = next(q for q in exam['questions'] if q['id'] == case['question'])
            expected = question['options'][question['answer']]
            with self.subTest(exam=exam['id'], question=question['id']):
                result = subprocess.run([sys.executable, '-I', '-X', 'utf8', '-c', question['code']],
                                        capture_output=True, text=True, encoding='utf-8', timeout=3)
                if case['kind'] == 'stdout':
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), expected)
                else:
                    self.assertNotEqual(result.returncode, 0)
                    error_type = result.stderr.strip().splitlines()[-1].split(':', 1)[0]
                    self.assertEqual(error_type, expected)

    def test_existing_exam_code_answer(self):
        exam = json.loads((ROOT / 'content/exams/foundation-01.json').read_text(encoding='utf-8'))
        question = next(q for q in exam['questions'] if q['id'] == 'env-08')
        result = subprocess.run([sys.executable, '-I', '-c', question['code']],
                                capture_output=True, text=True, timeout=3)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(' / '.join(result.stdout.strip().splitlines()), question['options'][question['answer']])

    def test_coverage_and_answers(self):
        course = json.loads((ROOT / 'content/courses/foundation.json').read_text(encoding='utf-8'))
        questions = []
        for i, module in enumerate(course['modules'], 1):
            exam = json.loads((ROOT / f'content/exams/foundation-0{i}.json').read_text(encoding='utf-8'))
            self.assertEqual(exam['module'], i)
            self.assertEqual(len(exam['questions']), 25)
            self.assertEqual({q['lesson'] for q in exam['questions']}, {l['id'] for l in module['lessons']})
            for q in exam['questions']:
                self.assertEqual(len(set(q['options'])), 4)
                self.assertIs(type(q['answer']), int)
                self.assertIn(q['answer'], range(4))
                self.assertTrue(q['explanation'].strip())
                questions.append(q)
        self.assertEqual(len(questions), 125)
        self.assertEqual(len({q['id'] for q in questions}), 125)
        self.assertEqual(len({(q['prompt'], q.get('code', '')) for q in questions}), 125)


if __name__ == '__main__':
    unittest.main(verbosity=2)
