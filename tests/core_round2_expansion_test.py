"""Behavioral and mutation tests for the second Foundation/Web/Pwn expansion."""
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
LABS = Path(os.environ.get("BIFROST_CORE_ROUND2_LABS", str(ROOT / "labs")))
CHILD_ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def load_source(name, file, source=None):
    module = types.ModuleType(name)
    module.__file__ = str(file)
    sys.modules[name] = module  # dataclass resolves its defining module here.
    exec(compile(source if source is not None else file.read_text(encoding="utf-8"), str(file), "exec"), module.__dict__)
    return module


def run_python(track, *args, cwd=None):
    return subprocess.run([sys.executable, *args], cwd=cwd or LABS / track,
                          env=CHILD_ENV, text=True, encoding="utf-8", capture_output=True)


class FoundationRound2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = LABS / "foundation/workflow.py"
        cls.model = load_source("bifrost_workflow_round2", cls.file)

    def test_deep_copy_preserves_two_nested_containers(self):
        original = {"tags": ["start"], "nested": {"counts": [1]}}
        changed = self.model.tagged_copy(original, "done")
        changed["nested"]["counts"].append(2)
        self.assertEqual(original, {"tags": ["start"], "nested": {"counts": [1]}})
        self.assertEqual(changed, {"tags": ["start", "done"], "nested": {"counts": [1, 2]}})
        self.assertIsNot(original["tags"], changed["tags"])

    def test_shallow_copy_mutation_is_detectable(self):
        source = self.file.read_text(encoding="utf-8")
        self.assertEqual(source.count("result = copy.deepcopy(record)"), 1)
        broken = load_source("bifrost_workflow_shallow_mutant", self.file,
                             source.replace("result = copy.deepcopy(record)", "result = dict(record)"))
        original = {"tags": ["start"]}
        broken.tagged_copy(original, "done")
        self.assertNotEqual(original["tags"], ["start"])

    def test_atomic_success_failure_and_partial_serialization_cleanup(self):
        with tempfile.TemporaryDirectory(prefix="bifrost-atomic2-") as folder:
            file = Path(folder) / "report.json"
            file.write_text('{"version":1}\n', encoding="utf-8")
            with self.assertRaises(RuntimeError):
                self.model.atomic_json(file, {"version": 2}, fail_before_replace=True)
            self.assertEqual(json.loads(file.read_text(encoding="utf-8")), {"version": 1})
            self.assertEqual(list(Path(folder).glob(".pending-*")), [])
            with self.assertRaises(TypeError):
                self.model.atomic_json(file, {"unserializable": object()})
            self.assertEqual(json.loads(file.read_text(encoding="utf-8")), {"version": 1})
            self.assertEqual(list(Path(folder).glob(".pending-*")), [])
            self.model.atomic_json(file, {"version": 3, "status": "complete"})
            self.assertEqual(json.loads(file.read_text(encoding="utf-8")), {"version": 3, "status": "complete"})
            self.assertEqual(list(Path(folder).glob(".pending-*")), [])

    def test_atomic_cleanup_mutation_leaves_detectable_fixture(self):
        source = self.file.read_text(encoding="utf-8")
        broken = load_source("bifrost_workflow_cleanup_mutant", self.file,
                             source.replace("temporary.unlink(missing_ok=True)", "pass  # removed cleanup"))
        with tempfile.TemporaryDirectory(prefix="bifrost-pending2-") as folder:
            file = Path(folder) / "report.json"
            file.write_text('{"version":1}', encoding="utf-8")
            with self.assertRaises(RuntimeError):
                broken.atomic_json(file, {"version": 2}, fail_before_replace=True)
            self.assertEqual(len(list(Path(folder).glob(".pending-*"))), 1)

    def test_configuration_precedence_and_strict_layers(self):
        m = self.model
        self.assertEqual(m.resolve_timeout(), (5, "default"))
        self.assertEqual(m.resolve_timeout({"timeout": 10}), (10, "file"))
        self.assertEqual(m.resolve_timeout({"timeout": 10}, {"BIFROST_TIMEOUT": "20"}), (20, "environment"))
        self.assertEqual(m.resolve_timeout({"timeout": 10}, {"BIFROST_TIMEOUT": "20"}, 30), (30, "cli"))
        self.assertEqual(m.resolve_timeout(environ={}), (5, "default"))
        for value in (1, 60):
            self.assertEqual(m.resolve_timeout(cli=value), (value, "cli"))
        for value in (0, 61, True, "", "-1", "1x", " 20", None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    m.timeout_value(value)
        with self.assertRaises(ValueError):
            m.resolve_timeout({"timeout": -1}, None, 30)
        with self.assertRaises(ValueError):
            m.resolve_timeout(environ={"BIFROST_TIMEOUT": ""})

    def test_argv_data_failure_and_timeout(self):
        m = self.model
        result = m.run_worker(["a b", "x|y", "$(demo)"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'argv=["a b","x|y","$(demo)"]')
        failure = m.run_worker(["--fail"])
        self.assertEqual(failure.returncode, 3)
        self.assertEqual(failure.stdout, "")
        self.assertEqual(failure.stderr.strip(), "fixture failure")
        with self.assertRaises(subprocess.TimeoutExpired):
            m.run_worker(["--sleep"], timeout=0.05)

    def test_logging_allowlist_escaping_and_schema(self):
        m = self.model
        payload = {"event": "profile.update", "request_id": "R1\nFORGED", "result": "denied", "status": 403,
                   "password": "PUBLIC-SECRET", "authorization": "Bearer PUBLIC", "body": {"note": "private"}}
        line = m.log_record(payload)
        self.assertEqual(len(line.splitlines()), 1)
        parsed = json.loads(line)
        self.assertEqual(set(parsed), {"event", "request_id", "result", "status"})
        self.assertEqual(parsed["request_id"], payload["request_id"])
        self.assertNotIn("PUBLIC", line)
        for update in ({"status": True}, {"status": 600}, {"event": "bad\nevent"},
                       {"result": "unknown"}, {"request_id": "x" * 65}):
            with self.subTest(update=update):
                with self.assertRaises(ValueError):
                    m.log_record({**payload, **update})
        # Field selection is intentionally not a generic value-secret detector.
        self.assertIn("PUBLIC-SECRET", m.log_record({**payload, "request_id": "PUBLIC-SECRET"}))

    def test_workflow_documented_modes(self):
        expected = {
            "copy": ["alias_same=True", "shallow_nested_same=True", "original_tags=start,review", "separate_tags=start,safe"],
            "atomic": ['after_failure={"version":1}', 'after_success={"version":2}', "pending_files=0"],
            "config": ["default=5 source=default", "file=10 source=file", "environment=20 source=environment",
                       "cli=30 source=cli", "empty_environment=INVALID"],
            "process": ['argv=["two words","x;echo NOT_A_COMMAND"]', "exit=0", "child_failure=3", "timeout=EXPIRED"],
            "logging": ['{"event":"profile.update","request_id":"REQ-001","result":"denied","status":403}',
                        "secret_values_present=False", "physical_lines=1"],
        }
        for mode, lines in expected.items():
            with self.subTest(mode=mode):
                result = run_python("foundation", "workflow.py", mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.splitlines(), lines)


class WebRound2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file = LABS / "web/web_state.py"
        cls.model = load_source("bifrost_web_state_round2", cls.file)

    def test_profile_contract_preserves_server_fields_and_original(self):
        m = self.model
        profile = {"owner": "alice", "role": "learner", "display_name": "Loki", "theme": "dark"}
        changed = m.update_profile(profile, {"display_name": "A" * 40, "theme": "light"}, "alice")
        self.assertEqual(changed["role"], "learner")
        self.assertEqual(changed["theme"], "light")
        self.assertEqual(profile, {"owner": "alice", "role": "learner", "display_name": "Loki", "theme": "dark"})
        for payload in ({}, {"role": "admin"}, {"display_name": "Freya", "role": "admin"},
                        {"display_name": "A" * 41}, {"display_name": " "},
                        {"display_name": True}, {"theme": "neon"}):
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    m.update_profile(profile, payload, "alice")
                self.assertEqual(profile["display_name"], "Loki")
                self.assertEqual(profile["role"], "learner")
        with self.assertRaises(PermissionError):
            m.update_profile(profile, {"theme": "light"}, "bob")

    def test_session_rotation_logout_collision_and_expiry(self):
        m = self.model
        session = m.SessionModel()
        with self.assertRaises(ValueError):
            session.rotate_after_verified_login("S-OLD", "S-OLD", "alice", 90)
        self.assertIn("S-OLD", session.sessions)
        session.rotate_after_verified_login("S-OLD", "S-NEW", "alice", 90)
        self.assertNotIn("S-OLD", session.sessions)
        self.assertEqual(session.user_for("S-NEW", 139), "alice")
        self.assertIsNone(session.user_for("S-NEW", 140))
        session.logout("S-NEW")
        self.assertIsNone(session.user_for("S-NEW", 91))
        self.assertNotIn("S-NEW", session.sessions)
        expired = m.SessionModel()
        with self.assertRaises(ValueError):
            expired.rotate_after_verified_login("S-OLD", "S-NEW", "alice", 100)

    def test_reset_scope_mismatch_does_not_consume(self):
        m = self.model
        for token, user, purpose, now in (("wrong", "alice", "reset-password", 90),
                                          ("PUBLIC-RESET-TOKEN", "bob", "reset-password", 90),
                                          ("PUBLIC-RESET-TOKEN", "alice", "email-change", 90),
                                          ("PUBLIC-RESET-TOKEN", "alice", "reset-password", 100),
                                          ("\uac00", "alice", "reset-password", 90)):
            ticket = m.fixture_ticket()
            self.assertFalse(m.consume_ticket(ticket, token, user, purpose, now))
            self.assertFalse(ticket.used)
        ticket = m.fixture_ticket(expires=120)
        self.assertTrue(m.consume_ticket(ticket, "PUBLIC-RESET-TOKEN", "alice", "reset-password", 119))
        self.assertFalse(m.consume_ticket(ticket, "PUBLIC-RESET-TOKEN", "alice", "reset-password", 119))
        self.assertFalse(m.consume_ticket(m.fixture_ticket(120), "PUBLIC-RESET-TOKEN", "alice", "reset-password", 120))

    def test_reset_replay_guard_mutation_changes_contract(self):
        source = self.file.read_text(encoding="utf-8")
        broken = load_source("bifrost_reset_replay_mutant", self.file, source.replace("if ticket.used or now >=", "if now >="))
        ticket = broken.fixture_ticket()
        self.assertTrue(broken.consume_ticket(ticket, "PUBLIC-RESET-TOKEN", "alice", "reset-password", 90))
        self.assertTrue(broken.consume_ticket(ticket, "PUBLIC-RESET-TOKEN", "alice", "reset-password", 91))

    def test_cache_policy_classification_and_known_public_exposure(self):
        m = self.model
        for header, expected in (("no-store", "NO_STORE"), ("private, max-age=60", "PRIVATE_ONLY"),
                                 ("no-cache", "STORE_REVALIDATE"), ("public, max-age=60", "SHARED_FRESH"),
                                 ("max-age=60", "REVIEW")):
            self.assertEqual(m.cache_rule(header), expected)
        cache = {}
        self.assertEqual(m.cached_profile(cache, "alice", "public, max-age=60"), "profile:alice")
        self.assertEqual(m.cached_profile(cache, "bob", "public, max-age=60"), "profile:alice")
        # A protected response in this model bypasses storage, but does not purge old copies.
        self.assertEqual(m.cached_profile(cache, "bob", "no-store"), "profile:bob")
        self.assertEqual(cache["/profile"], "profile:alice")
        fresh = {}
        self.assertEqual(m.cached_profile(fresh, "alice", "no-store"), "profile:alice")
        self.assertEqual(m.cached_profile(fresh, "bob", "no-store"), "profile:bob")
        self.assertEqual(fresh, {})

    def test_idempotency_conflict_and_per_user_scope(self):
        m = self.model
        shop = m.Checkout()
        try:
            self.assertEqual(shop.reserve("alice", "REQ-1", 2), "RESERVED")
            self.assertEqual(shop.reserve("alice", "REQ-1", 2), "REPLAY")
            self.assertEqual(shop.reserve("alice", "REQ-1", 2), "REPLAY")
            self.assertEqual(shop.stock(), 1)
            self.assertEqual(shop.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 1)
            self.assertEqual(shop.reserve("alice", "REQ-1", 1), "CONFLICT")
            self.assertEqual(shop.reserve("bob", "REQ-1", 2), "OUT_OF_STOCK")
            self.assertEqual(shop.reserve("bob", "REQ-1", 1), "RESERVED")
            self.assertEqual(shop.stock(), 0)
            self.assertEqual(shop.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 2)
        finally:
            shop.close()

    def test_checkout_rollback_and_validation_leave_state_unchanged(self):
        m = self.model
        shop = m.Checkout()
        try:
            for quantity in (0, -1, 11, True, "1"):
                with self.assertRaises(ValueError):
                    shop.reserve("alice", "REQ-1", quantity)
            with self.assertRaises(RuntimeError):
                shop.reserve("alice", "REQ-X", 1, fail_after_update=True)
            self.assertEqual(shop.stock(), 3)
            self.assertEqual(shop.db.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)
            self.assertFalse(shop.db.in_transaction)
        finally:
            shop.close()

    def test_rollback_mutation_breaks_inventory_invariant(self):
        source = self.file.read_text(encoding="utf-8")
        needle = 'if self.db.in_transaction:\n                self.db.execute("ROLLBACK")'
        self.assertEqual(source.count(needle), 1)
        broken = load_source("bifrost_rollback_mutant", self.file,
                             source.replace(needle, 'if self.db.in_transaction:\n                pass'))
        shop = broken.Checkout()
        try:
            with self.assertRaises(RuntimeError):
                shop.reserve("alice", "REQ-X", 1, fail_after_update=True)
            self.assertEqual(shop.stock(), 2)
            self.assertTrue(shop.db.in_transaction)
        finally:
            shop.close()

    def test_web_documented_modes(self):
        expected = {
            "contract": ["normal_name=Freya", "role_assignment=REJECT", "original_role=learner", "original_name=Loki"],
            "sessions": ["old_after_rotate=None", "new_after_rotate=alice", "at_expiry=None", "after_logout=None"],
            "reset": ["valid=ACCEPT", "replay=REJECT", "wrong_user=REJECT", "expired=REJECT", "wrong_purpose=REJECT"],
            "cache": ["public_alice=profile:alice", "public_bob=profile:alice", "no_store_bob=profile:bob",
                      "no_cache=STORE_REVALIDATE", "private=PRIVATE_ONLY"],
            "checkout": ["first=RESERVED stock=1", "repeat=REPLAY stock=1", "changed=CONFLICT stock=1",
                         "other=OUT_OF_STOCK stock=1", "rollback_stock=1"],
        }
        for mode, lines in expected.items():
            with self.subTest(mode=mode):
                result = run_python("web", "web_state.py", mode)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.splitlines(), lines)


@unittest.skipUnless(shutil.which("gcc"), "C round2 exercises need Linux/WSL with GCC")
class PwnRound2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory(prefix="bifrost-pwn-round2-")
        cls.build = Path(cls.folder.name)
        for name in ("struct_wire", "embedded_nul", "fd_lifetime", "stream_chunks", "open_boundary"):
            result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wformat=2", "-O0",
                                     str(LABS / "pwn" / f"{name}.c"), "-o", str(cls.build / name)],
                                    text=True, capture_output=True)
            if result.returncode:
                raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def run_c(self, name, *args):
        return subprocess.run([str(self.build / name), *args], text=True, capture_output=True)

    def variant(self, name, source):
        file = self.build / f"{name}.c"
        file.write_text(source, encoding="utf-8")
        result = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wformat=2",
                                 str(file), "-o", str(self.build / name)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.run_c(name)

    def test_struct_fixed_wire_and_independent_expected_bytes(self):
        result = self.run_c("struct_wire")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["wire_bytes=7 hex=01010203040506", "roundtrip=True", "short=REJECT"])
        layout = self.run_c("struct_wire", "--layout")
        self.assertEqual(layout.returncode, 0)
        self.assertIn("type_offset=0", layout.stdout)
        source = (LABS / "pwn/struct_wire.c").read_text(encoding="utf-8")
        changed = self.variant("different_code", source.replace("0x01020304", "0x0A0B0C0D"))
        self.assertEqual(changed.stdout.splitlines()[0], "wire_bytes=7 hex=010a0b0c0d0506")
        wrong_order = self.variant("wrong_decode", source.replace("((uint32_t)data[1] << 24)", "((uint32_t)data[4] << 24)"))
        self.assertIn("roundtrip=False", wrong_order.stdout.splitlines())

    def test_nul_position_and_explicit_field_length(self):
        result = self.run_c("embedded_nul")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["buffer_bytes=5 string_length=2", "hex=4142004344",
                         "text_contract=REJECT_NUL", "plain_text=ACCEPT"])
        source = (LABS / "pwn/embedded_nul.c").read_text(encoding="utf-8")
        changed = self.variant("nul_at_end", source.replace("data[] = {'A', 'B', 0, 'C', 'D'}", "data[] = {'A', 'B', 'C', 'D', 0}"))
        self.assertEqual(changed.stdout.splitlines(), ["buffer_bytes=5 string_length=4", "hex=4142434400",
                         "text_contract=REJECT_NUL", "plain_text=ACCEPT"])

    def test_dup_shared_offset_and_integer_alias_mutation(self):
        result = self.run_c("fd_lifetime")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["first=AB", "via_dup=CD", "after_close=EF", "last_read=EOF"])
        source = (LABS / "pwn/fd_lifetime.c").read_text(encoding="utf-8")
        changed = self.variant("digits_fd", source.replace('"ABCDEF"', '"123456"'))
        self.assertEqual(changed.stdout.splitlines(), ["first=12", "via_dup=34", "after_close=56", "last_read=EOF"])
        alias = self.variant("integer_alias", source.replace("duplicate = dup(fd);", "duplicate = fd;"))
        self.assertEqual(alias.returncode, 2)
        self.assertNotIn("after_close=EF", alias.stdout)

    def test_partial_io_chunk_tasks_and_premature_rejection_mutation(self):
        result = self.run_c("stream_chunks")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["complete=OK payload=BIFRO reads=4", "truncated=REJECT reads=4",
                         "written=7 calls=4", "stalled=REJECT"])
        source = (LABS / "pwn/stream_chunks.c").read_text(encoding="utf-8")
        changed = source.replace("full = {input, sizeof input, 0, 2, 0}", "full = {input, sizeof input, 0, 1, 0}")
        changed = changed.replace("short_body = {input, 5, 0, 2, 0}", "short_body = {input, 5, 0, 1, 0}")
        changed = changed.replace("writer = {{0}, 0, 2, 0, 0}", "writer = {{0}, 0, 1, 0, 0}")
        small = self.variant("one_byte_chunks", changed)
        self.assertEqual(small.stdout.splitlines(), ["complete=OK payload=BIFRO reads=7", "truncated=REJECT reads=6",
                         "written=7 calls=7", "stalled=REJECT"])
        # This safe mutant rejects a short read instead of accumulating it;
        # it never prints or copies uninitialized payload bytes.
        wrong = self.variant("reject_partial", source.replace("if (count == 0) return 0;",
                               "if (count == 0 || count < wanted - used) return 0;", 1))
        self.assertIn("complete=REJECT payload=-", wrong.stdout)

    def test_open_policies_and_nofollow_mutation(self):
        result = self.run_c("open_boundary")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["regular=ACCEPT", "second_create=EXISTS", "symlink=REJECT",
                         "opened_object=STILL_REGULAR"])
        source = (LABS / "pwn/open_boundary.c").read_text(encoding="utf-8")
        wrong = self.variant("follow_link", source.replace("O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK",
                                                              "O_RDONLY | O_CLOEXEC | O_NONBLOCK"))
        self.assertEqual(wrong.returncode, 2)
        self.assertNotIn("symlink=REJECT", wrong.stdout)


if __name__ == "__main__":
    unittest.main()
