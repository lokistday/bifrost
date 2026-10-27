"""Executable regression cases for the new reverse/DFIR/Misc exercises.

Runs generated labs when present; authored originals are a fallback before build.
All edits occur in temporary directories, never the shipped fixtures.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def folder(track):
    generated = ROOT / "labs" / track
    marker = {"rev": "binary_lab.py", "forensic": "casework.py", "misc": "toolbox.py"}[track]
    return generated if (generated / marker).exists() else ROOT / "scripts/lab_sources" / track


def load(track, filename):
    spec = importlib.util.spec_from_file_location("bifrost_test_" + filename.removesuffix(".py"), folder(track) / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(track, script, *args):
    return subprocess.run([sys.executable, str(folder(track) / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", timeout=20)


class ReverseExpansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.binary = load("rev", "binary_lab.py")
        cls.flow = load("rev", "dataflow.py")

    def test_format_empty_and_regular(self):
        self.assertEqual(self.binary.parse(b"BF\x00\x00"), b"")
        self.assertEqual(self.binary.parse(b"BF\x03\x00ABC"), b"ABC")

    def test_format_does_not_silently_slice_short_or_trailing_data(self):
        for data in (b"", b"BF", b"ZZ\x00\x00", b"BF\x03\x00AB", b"BF\x03\x00ABC!", b"BF\x41\x00" + b"A" * 65):
            with self.subTest(data=data[:10]):
                with self.assertRaises(ValueError):
                    self.binary.parse(data)

    def test_endian_output_is_not_native(self):
        result = run("rev", "binary_lab.py")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), ["little=3 big=768", "payload=ABC"])

    def test_bad_hex_has_actionable_nonzero_status(self):
        result = run("rev", "binary_lab.py", "not hex")
        self.assertEqual(result.returncode, 2)
        self.assertIn("INVALID", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_transform_has_position_dependency(self):
        self.assertEqual(self.flow.encode(b"AAA"), b"abc")
        self.assertEqual(self.flow.encode(b"BIF").hex(), "626a68")

    def test_transform_roundtrips_boundaries(self):
        for data in (b"", b"A?", bytes(range(16)), b"\x7f" * 16):
            self.assertEqual(self.flow.decode(self.flow.encode(data)), data)

    def test_wrong_inverse_can_pass_then_fail(self):
        wrong = lambda data: bytes((value ^ 32) - i for i, value in enumerate(data))
        self.assertEqual(wrong(self.flow.encode(b"AAA")), b"AAA")
        with self.assertRaises(ValueError):
            wrong(self.flow.encode(b"A?"))

    def test_transform_rejects_unsupported_input_range(self):
        for text in ("한글", "A" * 17):
            self.assertEqual(run("rev", "dataflow.py", text).returncode, 2)

    def test_reference_candidate_counterexample(self):
        result = run("rev", "differential.py")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.splitlines(), [
            "trailing reference=REJECT candidate=ACCEPT:414243", "cases=5 mismatches=1"])

    @unittest.skipUnless(shutil.which("gcc"), "GCC C exercises are checked on Linux/WSL")
    def test_benign_c_programs_and_integer_rejection(self):
        with tempfile.TemporaryDirectory(prefix="bifrost-reverse-") as directory:
            temp = Path(directory)
            for source in ("calling", "flow"):
                output = temp / (source + (".exe" if sys.platform == "win32" else ""))
                compile_result = subprocess.run(["gcc", "-g", "-O0", "-Wall", "-Wextra", "-Werror",
                    str(folder("rev") / (source + ".c")), "-o", str(output)], capture_output=True, text=True)
                self.assertEqual(compile_result.returncode, 0, compile_result.stderr)
            self.assertEqual(subprocess.check_output([str(temp / "calling")], text=True).strip(), "result=20")
            for args, expected in [(["4", "-2", "6", "0", "99"], "sum=10"),
                                   (["4", "-2", "6", "99"], "sum=109"), (["0", "4"], "sum=0"),
                                   (["-1", "-2", "-3"], "sum=0")]:
                self.assertEqual(subprocess.check_output([str(temp / "flow"), *args], text=True).strip(), expected)
            for args in ([], ["101"], ["1x"], ["999999999999999999999999999999"], ["1"] * 9):
                self.assertEqual(subprocess.run([str(temp / "flow"), *args], capture_output=True).returncode, 2)


class ForensicExpansion(unittest.TestCase):
    def fixture(self, name):
        return json.loads((folder("forensic") / name).read_text(encoding="utf-8"))

    def source_run(self, mode, data):
        with tempfile.TemporaryDirectory(prefix="bifrost-forensic-") as directory:
            source = Path(directory) / "sample.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            return run("forensic", "casework.py", mode, "--source", source)

    def test_plan_outputs_only_an_authored_plan(self):
        result = run("forensic", "casework.py", "plan")
        self.assertEqual(result.returncode, 0)
        self.assertIn("E01 memory volatile=True", result.stdout)
        self.assertIn("records=3 mode=plan-only", result.stdout)

    def test_plan_count_changes_with_added_evidence(self):
        sample = self.fixture("case.json")
        sample["items"].append({"id":"E09", "kind":"app-log", "volatile":False, "purpose":"app events", "order":4})
        self.assertIn("records=4", self.source_run("plan", sample).stdout)

    def test_plan_order_is_input_not_a_safety_decision(self):
        sample = self.fixture("case.json")
        sample["items"][0]["order"], sample["items"][2]["order"] = 3, 1
        self.assertTrue(self.source_run("plan", sample).stdout.startswith("E03 disk-copy"))

    def test_plan_rejects_duplicate_or_bad_type(self):
        for field, value in [("order", 2), ("order", True), ("volatile", "false"), ("id", "E02")]:
            sample = self.fixture("case.json")
            sample["items"][0][field] = value
            self.assertEqual(self.source_run("plan", sample).returncode, 2)

    def test_host_join_keeps_unknown(self):
        result = run("forensic", "casework.py", "host")
        self.assertEqual(result.returncode, 0)
        self.assertIn("viewer->helper", result.stdout)
        self.assertIn("C03 pid=999 process=UNKNOWN", result.stdout)

    def test_join_does_not_reuse_previous_name_for_missing_pid(self):
        sample = self.fixture("snapshot.json")
        sample["connections"][0]["pid"] = 999
        result = self.source_run("host", sample)
        self.assertTrue(result.stdout.startswith("C01 pid=999 process=UNKNOWN"))
        self.assertNotIn("viewer->helper", result.stdout)

    def test_browser_counts_filter_results(self):
        result = run("forensic", "casework.py", "browser")
        self.assertIn("total=3 displayed=2 synthetic=True", result.stdout)
        sql = (folder("forensic") / "history.sql").read_text(encoding="utf-8").replace("'auto'", "'link'")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "history.sql"
            source.write_text(sql, encoding="utf-8")
            result = run("forensic", "casework.py", "browser", "--source", source)
            self.assertIn("total=3 displayed=3", result.stdout)

    def test_carve_distinguishes_complete_and_truncated(self):
        result = run("forensic", "casework.py", "carve")
        self.assertEqual(result.stdout.splitlines(), ["offset=2 declared=3 available=3 COMPLETE",
            "offset=10 declared=5 available=2 INCOMPLETE"])

    def test_carve_candidate_completion_and_no_candidate(self):
        original = (folder("forensic") / "fragments.hex").read_text(encoding="ascii").strip()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "fragments.hex"
            source.write_text(original + "5a3132", encoding="ascii")
            self.assertIn("offset=10 declared=5 available=5 COMPLETE",
                run("forensic", "casework.py", "carve", "--source", source).stdout)
            source.write_text("00010203", encoding="ascii")
            self.assertEqual(run("forensic", "casework.py", "carve", "--source", source).stdout, "")

    def test_cross_log_uses_two_keys_and_utc(self):
        result = run("forensic", "casework.py", "correlate")
        self.assertTrue(result.stdout.startswith("A01 2026-10-01T00:00:00+00:00 login"))
        self.assertIn("linked=4 excluded=1", result.stdout)
        self.assertNotIn("W02", result.stdout)

    def test_cross_log_one_key_not_enough(self):
        text = (folder("forensic") / "crosslog.csv").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "crosslog.csv"
            source.write_text(text.replace("workstation-8,S11", "workstation-8,S10"), encoding="utf-8")
            self.assertIn("linked=4 excluded=1", run("forensic", "casework.py", "correlate", "--source", source).stdout)
            source.write_text(text.replace("workstation-8,S11", "workstation-7,S10"), encoding="utf-8")
            result = run("forensic", "casework.py", "correlate", "--source", source)
            self.assertIn("linked=5 excluded=0", result.stdout)

    def test_missing_timezone_not_silently_utc(self):
        text = (folder("forensic") / "crosslog.csv").read_text(encoding="utf-8").replace("09:00:00+09:00", "09:00:00")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "crosslog.csv"
            source.write_text(text, encoding="utf-8")
            result = run("forensic", "casework.py", "correlate", "--source", source)
            self.assertEqual(result.returncode, 2)
            self.assertIn("timezone required", result.stderr)

    def test_response_checklist_never_executes(self):
        result = run("forensic", "casework.py", "respond")
        self.assertIn("isolate-network READY-FOR-REVIEW", result.stdout)
        self.assertIn("power-off HOLD", result.stdout)
        self.assertIn("execution=NONE", result.stdout)

    def test_response_missing_approval_or_string_true_does_not_pass(self):
        for value in (False, "true", 1):
            sample = self.fixture("response.json")
            sample["actions"][0]["authorized"] = value
            self.assertIn("isolate-network HOLD", self.source_run("respond", sample).stdout)


class MiscExpansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.toolbox = load("misc", "toolbox.py")

    def test_regex_rejects_partial_match(self):
        rows, rejected = self.toolbox.parse_lines("noise id=L01 user=alice status=ok extra")
        self.assertEqual((rows, rejected), ([], [1]))

    def test_duplicate_id_does_not_double_count(self):
        rows, rejected = self.toolbox.parse_lines("id=L01 user=alice status=ok\nid=L01 user=alice status=ok")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rejected, [2])

    def test_original_parse_output(self):
        self.assertEqual(run("misc", "toolbox.py", "parse").stdout.splitlines(),
            ["denied=L02,L04", "accepted=3 rejected-lines=3"])

    def test_archive_member_names(self):
        for name in ("../outside.txt", "/tmp/a", "C:\\temp\\a", "notes/../a", "\\\\server\\share", ""):
            self.assertFalse(self.toolbox.safe_member(name), name)
        self.assertTrue(self.toolbox.safe_member("notes/a.txt"))
        self.assertTrue(self.toolbox.safe_member("CON"), "Documented lexical checker limitation")

    def test_archive_only_inspects_fixed_fixture(self):
        result = run("misc", "toolbox.py", "archive")
        self.assertIn("notes.txt size=9 CANDIDATE", result.stdout)
        self.assertIn("../outside.txt size=13 REJECT", result.stdout)
        self.assertIn("extracted=0", result.stdout)

    def test_bfs_has_shortest_edge_count_and_cycle_termination(self):
        graph = json.loads((folder("misc") / "graph.json").read_text(encoding="utf-8"))["edges"]
        self.assertEqual(self.toolbox.shortest_path(graph, "start", "report"), ["start", "inspect", "report"])
        graph["inspect"] = []
        self.assertEqual(self.toolbox.shortest_path(graph, "start", "report"), ["start", "decode", "parse", "report"])
        graph["parse"] = []
        self.assertIsNone(self.toolbox.shortest_path(graph, "start", "report"))

    def test_bfs_start_equal_goal(self):
        self.assertEqual(self.toolbox.shortest_path({}, "x", "x"), ["x"])

    def test_constraints_unique_underconstrained_and_conflicting(self):
        sample = json.loads((folder("misc") / "clues.json").read_text(encoding="utf-8"))
        self.assertEqual(self.toolbox.solve_clues(sample), [{"alice":2, "bob":3, "carol":1}])
        opened = {**sample, "not_at":[]}
        self.assertEqual(len(self.toolbox.solve_clues(opened)), 3)
        conflict = {**sample, "before":sample["before"] + [["bob", "alice"]]}
        self.assertEqual(self.toolbox.solve_clues(conflict), [])

    def test_canonical_ignores_only_documented_order(self):
        sample = json.loads((folder("misc") / "repro.json").read_text(encoding="utf-8"))
        encoded = self.toolbox.canonical(sample)
        self.assertEqual(encoded, self.toolbox.canonical({**sample, "events":list(reversed(sample["events"]))}))
        changed = json.loads(json.dumps(sample))
        changed["events"][0]["status"] = "ok"
        self.assertNotEqual(encoded, self.toolbox.canonical(changed))

    def test_canonical_rejects_duplicate_ids_or_bad_status(self):
        for rows in ([{"id":"x", "status":"ok"}, {"id":"x", "status":"ok"}], [{"id":"x", "status":"maybe"}]):
            with self.assertRaises(ValueError):
                self.toolbox.canonical({"schema":1, "events":rows})

    def test_canonical_rejects_silent_metadata_loss(self):
        for sample in ([], {"schema":True, "events":[]}, {"schema":1,"events":[]},
                       {"schema":1,"events":["not a row"]},
                       {"schema":1,"events":[{"id":"x","status":"ok"}],"important":"metadata"}):
            with self.assertRaises(ValueError):
                self.toolbox.canonical(sample)

    def test_verify_digest_matches_golden(self):
        result = run("misc", "toolbox.py", "verify")
        self.assertIn("order-independent=True value-sensitive=True", result.stdout)
        self.assertIn("sha256=b9d3a37611682440379f60a8ba04705e66a71a7b5f5e0f6bd8975c5b3b2a191c", result.stdout)


if __name__ == "__main__":
    unittest.main()
