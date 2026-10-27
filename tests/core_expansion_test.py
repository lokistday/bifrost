"""Behavioral tests for the Foundation/Web/Pwn curriculum expansion.

Uses generated downloadable labs in normal CI. BIFROST_CORE_LABS may point to
scripts/lab_sources while an author tests sources before the shared build.
C tests run on Linux/WSL when gcc is available; Windows does not install tools.
"""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]
LABS = Path(os.environ.get("BIFROST_CORE_LABS", str(ROOT / "labs")))
CHILD_ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def load_source(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


def run_python(track, *args, cwd=None):
    return subprocess.run([sys.executable, *args], cwd=cwd or LABS / track,
                          env=CHILD_ENV, text=True, encoding="utf-8", capture_output=True)


class FoundationExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_source("foundation_data_tools", LABS / "foundation/data_tools.py")

    def test_text_preserves_bytes_and_reports_wrong_encoding(self):
        result = run_python("foundation", "data_tools.py", "text")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "codepoints=2 bytes=4 hex=41eab080", "roundtrip=True", "wrong_encoding=UnicodeDecodeError"])

    def test_json_success_and_wrong_type_are_distinct(self):
        good = run_python("foundation", "data_tools.py", "json", "record.json")
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(good.stdout.splitlines(), ["learner=Loki minutes=30",
                         'canonical={"learner":"Loki","minutes":30}'])
        bad = run_python("foundation", "data_tools.py", "json", "record-invalid.json")
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")
        self.assertIn("INVALID: ValueError", bad.stderr)

    def test_record_contract_rejects_missing_extra_bool_and_bad_range(self):
        base = {"learner": "Loki", "minutes": 30}
        for minutes in (-1, 1441, "30", 30.0, True, None):
            with self.subTest(minutes=minutes):
                with self.assertRaises(ValueError):
                    self.data.validate_record({**base, "minutes": minutes})
        for value in ([], {}, {**base, "admin": True}, {**base, "learner": " "}):
            with self.subTest(record=value):
                with self.assertRaises(ValueError):
                    self.data.validate_record(value)
        for minutes in (0, 1440):
            self.assertEqual(self.data.validate_record({**base, "minutes": minutes})["minutes"], minutes)

    def test_cli_boundary_and_error_status(self):
        for minimum, selected in ((0, True), (30, True), (31, False), (1440, False)):
            result = run_python("foundation", "data_tools.py", "summary", "record.json", "--minimum", str(minimum))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), f"learner=Loki minutes=30 selected={selected}")
        for minimum in ("-1", "1441", "abc"):
            result = run_python("foundation", "data_tools.py", "summary", "record.json", "--minimum", minimum)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertTrue(result.stderr)
        missing = run_python("foundation", "data_tools.py", "json", "nonexistent-record.json")
        self.assertEqual(missing.returncode, 2)
        self.assertIn("FileNotFoundError", missing.stderr)

    def test_json_syntax_errors_are_not_successful_records(self):
        with tempfile.TemporaryDirectory(prefix="bifrost-json-") as folder:
            file = Path(folder) / "bad.json"
            file.write_text('{"learner":"Loki",}', encoding="utf-8")
            result = run_python("foundation", "data_tools.py", "json", str(file))
            self.assertEqual(result.returncode, 2)
            self.assertIn("JSONDecodeError", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_learner_tests_detect_the_documented_boundary_mutation(self):
        with tempfile.TemporaryDirectory(prefix="bifrost-boundary-") as folder:
            target = Path(folder)
            for file in ("data_tools.py", "test_data_tools.py"):
                shutil.copyfile(LABS / "foundation" / file, target / file)
            normal = run_python("foundation", "-m", "unittest", "-v", "test_data_tools", cwd=target)
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertIn("Ran 4 tests", normal.stderr)
            file = target / "data_tools.py"
            content = file.read_text(encoding="utf-8")
            self.assertEqual(content.count(" >= minimum"), 1)
            file.write_text(content.replace(" >= minimum", " > minimum"), encoding="utf-8")
            broken = run_python("foundation", "-m", "unittest", "-v", "test_data_tools", cwd=target)
            self.assertNotEqual(broken.returncode, 0)
            self.assertIn("test_selection_boundary", broken.stderr)
            self.assertIn("FAILED", broken.stderr)


class WebExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_source("web_controls_model", LABS / "web/web_controls.py")

    def test_csrf_checks_independent_conditions(self):
        m = self.model
        self.assertTrue(m.allow_change("POST", "alice", m.TOKEN, m.SITE))
        for values in (("GET", "alice", m.TOKEN, m.SITE),
                       ("POST", None, m.TOKEN, m.SITE),
                       ("POST", "alice", "", m.SITE),
                       ("POST", "alice", None, m.SITE),
                       ("POST", "alice", "\uac00", m.SITE),
                       ("POST", "alice", m.TOKEN, "https://other.example.invalid")):
            with self.subTest(values=values):
                self.assertFalse(m.allow_change(*values))

    def test_cors_does_not_reflect_untrusted_origins(self):
        m = self.model
        headers = m.cors_headers(m.SITE)
        self.assertEqual(headers["Access-Control-Allow-Origin"], m.SITE)
        self.assertEqual(headers["Access-Control-Allow-Credentials"], "true")
        self.assertEqual(headers["Vary"], "Origin")
        for origin in ("null", "*", m.SITE + ".attacker.invalid", "http://learn.example.invalid",
                       "https://learn.example.invalid:8443", None):
            self.assertEqual(m.cors_headers(origin), {})

    def test_csp_checklist_separates_report_only_and_missing_rules(self):
        m = self.model
        policy = "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        self.assertEqual(m.review_csp("Content-Security-Policy", policy), "CHECKLIST_PASS")
        self.assertEqual(m.review_csp("Content-Security-Policy-Report-Only", policy), "REPORT_ONLY")
        self.assertEqual(m.review_csp("Content-Security-Policy", policy.replace("; base-uri 'none'", "")), "REVIEW")
        self.assertEqual(m.review_csp("Content-Security-Policy", policy.replace("script-src 'self'", "script-src 'self' 'unsafe-inline'")), "REVIEW")

    def test_file_contract_and_resolved_symlink_boundary(self):
        m = self.model
        with tempfile.TemporaryDirectory(prefix="bifrost-file-boundary-") as folder:
            root = Path(folder) / "root"
            root.mkdir()
            self.assertEqual(m.choose_file(root, "note_1.txt"), root.resolve() / "note_1.txt")
            for name in ("../private.txt", "nested/note.txt", "note..txt", "/tmp/note.txt",
                         "note.txt.exe", "note.TXT", "%2e%2e.txt", "C:\\private.txt", None):
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        m.choose_file(root, name)
            outside = Path(folder) / "outside.txt"
            outside.write_text("not an application file", encoding="utf-8")
            link = root / "link.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                # Windows may not grant symlink creation; the filename checks above still ran.
                return
            with self.assertRaises(ValueError):
                m.choose_file(root, "link.txt")

    def test_ssrf_syntax_contract_and_no_hidden_requests(self):
        m = self.model
        self.assertTrue(m.allowed_fetch("https://assets.example.invalid/guide.txt"))
        self.assertTrue(m.allowed_fetch("https://assets.example.invalid:443/diagram.png"))
        for url in ("http://127.0.0.1/", "https://assets.example.invalid@other.invalid/guide.txt",
                    "https://assets.example.invalid.attacker.invalid/guide.txt",
                    "https://assets.example.invalid:8443/guide.txt", "https://assets.example.invalid/private.txt",
                    "https://assets.example.invalid/guide.txt?next=http://127.0.0.1",
                    "https://assets.example.invalid/guide.txt#fragment", " https://assets.example.invalid/guide.txt",
                    "https://assets.example.invalid:\uac00/guide.txt", None):
            with self.subTest(url=url):
                self.assertFalse(m.allowed_fetch(url))
        result = run_python("web", "web_controls.py", "ssrf")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines()[-1], "network_requests=0")

    def test_model_commands_match_lesson_outputs(self):
        expected = {
            "csrf": ["valid=ALLOW", "no-token=DENY", "foreign=DENY", "get-change=DENY"],
            "cors": ["allowed=EXPOSE", "foreign=NO_CORS_HEADERS", "suffix=NO_CORS_HEADERS",
                     "null=NO_CORS_HEADERS", "authorization=SEPARATE_CHECK"],
            "csp": ["enforced=CHECKLIST_PASS", "report-only=REPORT_ONLY", "inline=REVIEW",
                    "browser_enforcement=NOT_TESTED"],
            "files": ["note.txt=ALLOW_NAME", "../private.txt=DENY", "nested/note.txt=DENY",
                      "note.txt.exe=DENY", "%2e%2e.txt=DENY"],
        }
        for mode, lines in expected.items():
            with self.subTest(mode=mode):
                result = run_python("web", "web_controls.py", mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.splitlines(), lines)


@unittest.skipUnless(shutil.which("gcc"), "C exercises require Linux/WSL with gcc")
class PwnExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix="bifrost-pwn-expansion-")
        cls.build = Path(cls.folder.name)
        for name in ("parse_count", "allocation_size", "format_data", "ownership", "packet_parse"):
            result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wformat=2", "-O0",
                                     str(LABS / "pwn" / f"{name}.c"), "-o", str(cls.build / name)],
                                    capture_output=True, text=True)
            if result.returncode:
                raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def run_c(self, name, *args):
        return subprocess.run([str(self.build / name), *args], capture_output=True, text=True)

    def test_numeric_input_boundaries(self):
        for value, count in (("0", 0), ("1", 1), ("1024", 1024), ("0003", 3)):
            result = self.run_c("parse_count", value)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, f"count={count}\n")
        for value in ("", "-1", "+1", "1025", "30x", " 30", "999999999999999999999999999999999999"):
            result = self.run_c("parse_count", value)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "INVALID_COUNT\n")

    def test_allocation_preconditions(self):
        result = self.run_c("allocation_size")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), ["small=OK bytes=20", "huge=REJECT",
                         "empty=OK bytes=8", "zero-element=REJECT"])

    def test_format_data_and_nul_boundary(self):
        default = self.run_c("format_data")
        self.assertEqual(default.stdout.splitlines(), ["literal=%s%n", "required=6 capacity=8 truncated=no", "stored=[%s%n]"])
        for text, needed, truncated, stored in (("12345", 7, "no", "[12345]"),
                                               ("123456", 8, "yes", "[123456"),
                                               ("Bifrost", 9, "yes", "[Bifros")):
            result = self.run_c("format_data", text)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.splitlines(), [f"literal={text}",
                             f"required={needed} capacity=8 truncated={truncated}", f"stored={stored}"])

    def test_ownership_normal_path(self):
        result = self.run_c("ownership")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), ["borrowed=Bifrost", "owner_is_null=yes"])

    def test_parser_rejects_truncation_and_extra_data(self):
        result = self.run_c("packet_parse")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), ["normal=OK length=3", "short-header=REJECT",
                         "short-body=REJECT", "extra-byte=REJECT"])

    def compile_variant(self, name, content):
        source = self.build / f"{name}.c"
        source.write_text(content, encoding="utf-8")
        result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wformat=2",
                                 str(source), "-o", str(self.build / name)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.run_c(name)

    def test_documented_c_change_tasks(self):
        allocation = (LABS / "pwn/allocation_size.c").read_text(encoding="utf-8")
        changed = self.compile_variant("five_items", allocation.replace("allocation_size(3, 4, 8,", "allocation_size(5, 4, 8,"))
        self.assertEqual(changed.stdout.splitlines()[0], "small=OK bytes=28")

        formatting = (LABS / "pwn/format_data.c").read_text(encoding="utf-8")
        self.compile_variant("larger_format_buffer", formatting.replace("char message[8]", "char message[10]"))
        result = self.run_c("larger_format_buffer", "Bifrost")
        self.assertEqual(result.stdout.splitlines(), ["literal=Bifrost", "required=9 capacity=10 truncated=no", "stored=[Bifrost]"])

        parser = (LABS / "pwn/packet_parse.c").read_text(encoding="utf-8")
        invalid = self.compile_variant("wrong_declared_length", parser.replace("normal[] = {0, 3,", "normal[] = {0, 2,"))
        self.assertEqual(invalid.stdout.splitlines()[0], "normal=REJECT")
        empty = self.compile_variant("empty_payload", parser.replace("normal[] = {0, 3, 'B', 'I', 'F'}", "normal[] = {0, 0}"))
        self.assertEqual(empty.stdout.splitlines()[0], "normal=OK length=0")

    def test_length_guard_mutation_is_observable(self):
        parser = (LABS / "pwn/packet_parse.c").read_text(encoding="utf-8")
        self.assertEqual(parser.count("if (length != size - 2)"), 1)
        changed = self.compile_variant("broken_length_guard", parser.replace("if (length != size - 2)", "if (length < size - 2)"))
        # A weakened guard must be detected by the fixture expectation: it now
        # accepts a body shorter than the declared length.
        self.assertIn("short-body=OK", changed.stdout.splitlines())
        self.assertNotIn("short-body=REJECT", changed.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
