"""Round-two reverse/artifact/media lessons: real execution and input mutations."""
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]


def folder(track):
    marker = {"rev":"integer_views.py", "forensic":"artifacts_round2.py", "misc":"media_tools.py"}[track]
    result = ROOT / "labs" / track
    return result if (result / marker).is_file() else ROOT / "scripts/lab_sources" / track


def module(track, name):
    spec = importlib.util.spec_from_file_location("bf_round2_" + name, folder(track) / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(track, script, *args):
    return subprocess.run([sys.executable, str(folder(track) / script), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8", timeout=20)


class ReverseRoundTwo(unittest.TestCase):
    def test_integer_views_and_sign_boundary(self):
        view = module("rev", "integer_views")
        self.assertEqual(view.inspect(bytes.fromhex("feff"), 0xa5), (65534, -2, 5, 1, 2))
        self.assertEqual(view.inspect(bytes.fromhex("ff7f"), 0x85), (32767, 32767, 5, 1, 0))
        self.assertEqual(view.inspect(bytes.fromhex("0080"), 0x05), (32768, -32768, 5, 0, 0))

    def test_integer_contract(self):
        for args in [("ff",), ("feff", "--flags", "256"), ("feff", "--flags", "-1"), ("zzzz",)]:
            result = run("rev", "integer_views.py", *args)
            self.assertEqual(result.returncode, 2)
            self.assertIn("INVALID", result.stderr)

    def test_integer_extension_output(self):
        result = run("rev", "integer_views.py")
        self.assertIn("zero32=0000fffe sign32=fffffffe", result.stdout)
        self.assertIn("version=5 urgent=1 reserved=2", result.stdout)

    def test_state_allowed_and_zero_data(self):
        trace = module("rev", "state_machine").trace
        self.assertEqual(trace(["HELLO", "DATA", "DATA", "END"])[1], 2)
        self.assertEqual(trace(["HELLO", "END"])[1], 0)

    def test_state_wrong_start_incomplete_and_after_end(self):
        trace = module("rev", "state_machine").trace
        for tokens, expected in [(["DATA","END"], "state=CLOSED"),
                                 (["HELLO","DATA"], "incomplete final=READY"),
                                 (["HELLO","END","DATA"], "state=DONE"),
                                 (["HELLO","HELLO","END"], "state=READY")]:
            with self.assertRaisesRegex(ValueError, expected):
                trace(tokens)

    @unittest.skipUnless(shutil.which("gcc") and sys.platform == "linux", "ELF/shared-library check requires Linux/WSL GCC")
    def test_real_elf_layout_relocation_shared_library_and_switch(self):
        with tempfile.TemporaryDirectory(prefix="bf-elf-r2-") as directory:
            temp = Path(directory)
            def command(*args):
                result = subprocess.run(list(args), cwd=temp, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout
            for name in ("layout.c", "linkmain.c", "linkpart.c", "switches.c"):
                shutil.copyfile(folder("rev") / name, temp / name)
            command("gcc", "-g", "-O0", "-Wall", "-Wextra", "-Werror", "layout.c", "-o", "layout")
            self.assertEqual(command(str(temp / "layout")).strip(), "BF-LAYOUT init=7 zero=0")
            if shutil.which("readelf"):
                sections = command("readelf", "-SW", "layout")
                self.assertRegex(sections, r"\.bss\s+NOBITS")
                self.assertIn("LOAD", command("readelf", "-lW", "layout"))
            command("gcc", "-g", "-O0", "-c", "linkmain.c", "-o", "linkmain.o")
            command("gcc", "-g", "-O0", "-fPIC", "-shared", "linkpart.c", "-o", "libbfmath.so")
            command("gcc", "linkmain.o", "-L.", "-lbfmath", "-Wl,-rpath,$ORIGIN", "-o", "linkdemo")
            self.assertEqual(command(str(temp / "linkdemo")).strip(), "adjusted=12")
            if shutil.which("readelf"):
                self.assertIn("adjust", command("readelf", "-rW", "linkmain.o"))
                self.assertIn("libbfmath.so", command("readelf", "-dW", "linkdemo"))
            (temp / "linkpart.c").write_text((temp / "linkpart.c").read_text().replace("+ 7", "+ 9"))
            command("gcc", "-g", "-O0", "-fPIC", "-shared", "linkpart.c", "-o", "libbfmath.so")
            self.assertEqual(command(str(temp / "linkdemo")).strip(), "adjusted=14")
            outputs = []
            for opt in ("-O0", "-O2"):
                command("gcc", "-g", opt, "-Wall", "-Wextra", "-Werror", "switches.c", "-o", "switch")
                outputs.append(command(str(temp / "switch")).strip())
            self.assertEqual(outputs, ["-1:-1 0:11 1:17 2:23 3:31 4:47 5:59 6:-1"] * 2)


class ArtifactRoundTwo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.art = module("forensic", "artifacts_round2")

    def source(self, mode, text):
        with tempfile.TemporaryDirectory(prefix="bf-artifact-r2-") as directory:
            path = Path(directory) / "source.txt"
            path.write_text(text, encoding="utf-8")
            return run("forensic", "artifacts_round2.py", mode, "--source", path)

    def fixture(self, name):
        return (folder("forensic") / name).read_text(encoding="utf-8")

    def test_windows_named_fields_and_utc(self):
        result = run("forensic", "artifacts_round2.py", "windows")
        self.assertEqual(result.returncode, 0)
        self.assertIn("record=102 event=4624 utc=2026-10-02T00:00:10+00:00 user=alice type=3", result.stdout)
        self.assertIn("records=2 format=synthetic-xml", result.stdout)

    def test_windows_duplicate_record_in_single_export_rejected(self):
        text = self.fixture("events-synthetic.xml").replace("<EventRecordID>102", "<EventRecordID>101")
        result = self.source("windows", text)
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing/duplicate record ID", result.stderr)

    def test_windows_missing_namespace_not_silently_empty(self):
        text = self.fixture("events-synthetic.xml").replace(' xmlns="http://schemas.microsoft.com/win/2004/08/events/event"', "")
        self.assertEqual(self.source("windows", text).returncode, 2)

    def test_windows_duplicate_data_name_rejected(self):
        text = self.fixture("events-synthetic.xml").replace('Name="LogonType"', 'Name="TargetUserName"')
        self.assertIn("duplicate Data Name", self.source("windows", text).stderr)

    def test_linux_joins_but_does_not_claim_execution(self):
        result = run("forensic", "artifacts_round2.py", "linux")
        self.assertIn("L13 user=alice result=allow linked-login=True", result.stdout)
        self.assertIn("L14 user=bob result=deny linked-login=False", result.stdout)
        self.assertIn("execution-outcome=NOT-PROVIDED", result.stdout)

    def test_linux_session_mismatch_and_input_order(self):
        text = self.fixture("linux-auth.jsonl")
        reversed_text = "\n".join(reversed(text.splitlines()))
        baseline = run("forensic", "artifacts_round2.py", "linux").stdout
        self.assertEqual(self.source("linux", reversed_text).stdout, baseline)
        rows = [json.loads(line) for line in text.splitlines()]
        rows[2]["session"] = "S99"
        self.assertIn("L13 user=alice result=allow linked-login=False",
            self.source("linux", "\n".join(map(json.dumps, rows))).stdout)

    def test_inode_partial_observation_does_not_change_declared_links(self):
        sample = json.loads(self.fixture("fs-records.json"))
        self.assertIn("inode=42 observed-names=2 declared-links=2", run("forensic", "artifacts_round2.py", "filesystem").stdout)
        sample["records"].pop(1)
        result = self.source("filesystem", json.dumps(sample))
        self.assertIn("inode=42 observed-names=1 declared-links=2", result.stdout)
        self.assertIn("birth-unknown=1 ctime-is-creation=False", result.stdout)

    def test_memory_rule_is_not_a_verdict(self):
        result = run("forensic", "artifacts_round2.py", "memory")
        self.assertIn("range=[8192,12288)", result.stdout)
        self.assertIn("review=1 verdict=NOT-A-MALWARE-VERDICT", result.stdout)
        sample = json.loads(self.fixture("memory-model.json"))
        sample["processes"][0]["ranges"][1]["permission"] = "rx"
        self.assertIn("review=0 verdict=NOT-A-MALWARE-VERDICT", self.source("memory", json.dumps(sample)).stdout)

    def test_memory_invalid_range(self):
        for size in (0, -1, True):
            sample = json.loads(self.fixture("memory-model.json"))
            sample["processes"][0]["ranges"][1]["size"] = size
            self.assertEqual(self.source("memory", json.dumps(sample)).returncode, 2)

    def test_clock_intervals_overlap_or_touch_are_uncertain(self):
        result = run("forensic", "artifacts_round2.py", "coverage")
        self.assertIn("E31 corrected=[90,94]", result.stdout)
        self.assertIn("relation=ORDER-UNCERTAIN", result.stdout)
        sample = json.loads(self.fixture("coverage.json"))
        sample["events"][1].update(recorded=97, uncertainty=3)
        self.assertIn("relation=ORDER-UNCERTAIN", self.source("coverage", json.dumps(sample)).stdout)

    def test_clock_zero_uncertainty_assumption_changes_relation(self):
        sample = json.loads(self.fixture("coverage.json"))
        for event in sample["events"]:
            event["uncertainty"] = 0
        result = self.source("coverage", json.dumps(sample))
        self.assertIn("relation=A-BEFORE-B", result.stdout)
        self.assertIn("source=process logging-enabled=False", result.stdout)

    def test_bad_clock_model_and_naive_time_rejected(self):
        with self.assertRaises(ValueError):
            self.art.utc("2026-10-02T00:00:00")
        with self.assertRaises(ValueError):
            self.art.interval({"recorded":100,"clock_ahead":0,"uncertainty":-1})


class MediaRoundTwo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media = module("misc", "media_tools")

    def test_magic_is_only_a_candidate(self):
        self.assertEqual(self.media.kind(b"\x1f\x8b"), "GZIP-CANDIDATE")
        self.assertEqual(self.media.kind(b"PK\x03\x04"), "ZIP-CANDIDATE")
        self.assertEqual(self.media.kind(b""), "UNKNOWN")
        self.assertIn("structure-validated=False", run("misc", "media_tools.py", "identify").stdout)

    def test_ppm_channels_and_mutation(self):
        text = (folder("misc") / "sample-p3.ppm").read_text(encoding="ascii")
        width, height, maximum, pixels = self.media.read_ppm(text)
        self.assertEqual((width,height,maximum,len(pixels)), (2,2,255,4))
        self.assertEqual(pixels[0], (255,0,0))
        self.assertEqual([sum(p[i] for p in pixels) for i in range(3)], [510,510,510])
        changed = text.replace("255 0 0", "0 0 0")
        pixels = self.media.read_ppm(changed)[3]
        self.assertEqual([sum(p[i] for p in pixels) for i in range(3)], [255,510,510])

    def test_ppm_count_range_and_dimension_bounds(self):
        for text in ("P3 1 1 255 0 0", "P3 1 1 255 256 0 0", "P3 65 1 255 0 0 0", "P6 1 1 255 0 0 0"):
            with self.assertRaises(ValueError):
                self.media.read_ppm(text)

    def test_frequency_ignores_order_and_is_not_randomness(self):
        self.assertEqual(self.media.entropy(b"A" * 256), 0)
        self.assertEqual(self.media.entropy(b"ABAB"), self.media.entropy(b"AABB"))
        self.assertEqual(self.media.entropy(bytes(range(256))), 8)
        self.assertEqual(self.media.entropy(bytes(reversed(range(256)))), 8)
        self.assertIn("classification=NOT-DETERMINED", run("misc", "media_tools.py", "frequency").stdout)

    def test_decompression_exact_budget_and_one_over(self):
        data = zlib.compress(b"A" * 32)
        self.assertEqual(self.media.bounded_decompress(data, 32), b"A" * 32)
        for limit in (0,31):
            with self.assertRaisesRegex(ValueError, "output budget"):
                self.media.bounded_decompress(data, limit)

    def test_decompression_input_truncated_trailing_and_concatenated(self):
        data = zlib.compress(b"A" * 32)
        for payload, expected in [(data[:-1], "truncated"), (data+b"!", "trailing"), (data+data, "trailing")]:
            with self.assertRaisesRegex(ValueError, expected):
                self.media.bounded_decompress(payload)
        with self.assertRaisesRegex(ValueError, "input budget"):
            self.media.bounded_decompress(data, input_limit=1)

    def test_batch_resume_input_change_and_cache_tampering(self):
        sample = json.loads((folder("misc") / "batch-jobs.json").read_text())
        empty = {"schema":1,"transform":self.media.TRANSFORM_VERSION,"done":{}}
        rows, state = self.media.batch_process(sample, empty)
        self.assertEqual([r[1] for r in rows], ["RUN"] * 3)
        self.assertEqual([r[1] for r in self.media.batch_process(sample,state)[0]], ["SKIP"] * 3)
        sample["jobs"][1]["text"] = "Changed"
        rows, state = self.media.batch_process(sample,state)
        self.assertEqual([r[1] for r in rows], ["SKIP","RUN","SKIP"])
        state["done"]["J01"]["result"] = "tampered"
        self.assertEqual(self.media.batch_process(sample,state)[0][0][1], "RUN")

    def test_batch_invalid_duplicate_version_and_schema(self):
        sample = {"schema":1,"jobs":[{"id":"x","text":"one"},{"id":"x","text":"two"}]}
        empty = {"schema":1,"transform":self.media.TRANSFORM_VERSION,"done":{}}
        with self.assertRaisesRegex(ValueError, "duplicate job"):
            self.media.batch_process(sample,empty)
        sample = {"schema":1,"jobs":[{"id":"x","text":"one"}]}
        with self.assertRaisesRegex(ValueError, "checkpoint schema/version"):
            self.media.batch_process(sample,{**empty,"transform":"old"})
        with self.assertRaisesRegex(ValueError, "job schema"):
            self.media.batch_process({**sample,"schema":True},empty)

    def test_batch_checkpoint_file_roundtrip(self):
        with tempfile.TemporaryDirectory(prefix="bf-batch-r2-") as directory:
            checkpoint = Path(directory) / "state.json"
            first = run("misc", "media_tools.py", "batch", "--checkpoint", checkpoint)
            second = run("misc", "media_tools.py", "batch", "--checkpoint", checkpoint)
            self.assertEqual(first.returncode, 0)
            self.assertEqual(second.returncode, 0)
            self.assertIn("J01 RUN BIFROST", first.stdout)
            self.assertIn("J01 SKIP BIFROST", second.stdout)
            self.assertFalse(Path(str(checkpoint) + ".tmp").exists())


if __name__ == "__main__":
    unittest.main()
