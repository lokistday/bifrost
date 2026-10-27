"""Offline exercises: ownership, atomic output, config, subprocess and log boundaries."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


def tagged_copy(record, tag):
    result = copy.deepcopy(record)
    result["tags"].append(tag)
    return result


def atomic_json(target, value, fail_before_replace=False):
    """Replace one file in a controlled directory; not a durable database transaction."""
    target = Path(target)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=target.parent, prefix=".pending-", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        if fail_before_replace:
            raise RuntimeError("simulated failure before replace")
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def timeout_value(value):
    if isinstance(value, str):
        if not re.fullmatch(r"[0-9]+", value):
            raise ValueError("timeout requires decimal digits")
        value = int(value)
    if type(value) is not int or not 1 <= value <= 60:
        raise ValueError("timeout must be an integer from 1 to 60")
    return value


def resolve_timeout(file_config=None, environ=None, cli=None):
    value, source = 5, "default"
    if file_config is not None:
        if not isinstance(file_config, dict) or set(file_config) - {"timeout"}:
            raise ValueError("only timeout is allowed in file configuration")
        if "timeout" in file_config:
            value, source = timeout_value(file_config["timeout"]), "file"
    if environ is not None and "BIFROST_TIMEOUT" in environ:
        value, source = timeout_value(environ["BIFROST_TIMEOUT"]), "environment"
    if cli is not None:
        value, source = timeout_value(cli), "cli"
    return value, source


def run_worker(values, timeout=3):
    return subprocess.run([sys.executable, str(Path(__file__).with_name("argv_worker.py")), *values],
                          shell=False, capture_output=True, text=True, encoding="utf-8", timeout=timeout)


def log_record(payload):
    """Allow fields and JSON-escape them. This is not a generic secret detector."""
    if not isinstance(payload, dict):
        raise ValueError("event must be an object")
    event = payload.get("event")
    if not isinstance(event, str) or not re.fullmatch(r"[a-z][a-z0-9._-]{0,63}", event):
        raise ValueError("invalid event name")
    request_id = payload.get("request_id")
    if not isinstance(request_id, str) or not 1 <= len(request_id) <= 64:
        raise ValueError("invalid request identifier")
    result = payload.get("result")
    if result not in ("ok", "denied", "error"):
        raise ValueError("invalid result")
    status = payload.get("status")
    if type(status) is not int or not 100 <= status <= 599:
        raise ValueError("invalid HTTP status")
    selected = {key: payload[key] for key in ("event", "request_id", "result", "status")}
    return json.dumps(selected, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("copy", "atomic", "config", "process", "logging"))
    args = parser.parse_args(argv)
    if args.mode == "copy":
        original = {"learner": "Loki", "tags": ["start"]}
        alias = original
        shallow = dict(original)
        separate = tagged_copy(original, "safe")
        shallow["tags"].append("review")
        print(f"alias_same={alias is original}")
        print(f"shallow_nested_same={shallow['tags'] is original['tags']}")
        print("original_tags=" + ",".join(original["tags"]))
        print("separate_tags=" + ",".join(separate["tags"]))
    elif args.mode == "atomic":
        with tempfile.TemporaryDirectory(prefix="bifrost-atomic-") as folder:
            target = Path(folder) / "report.json"
            target.write_text('{"version":1}\n', encoding="utf-8")
            try:
                atomic_json(target, {"version": 2}, fail_before_replace=True)
            except RuntimeError:
                print("after_failure=" + target.read_text(encoding="utf-8").strip())
            atomic_json(target, {"version": 2})
            print("after_success=" + target.read_text(encoding="utf-8").strip())
            print("pending_files=" + str(len(list(Path(folder).glob(".pending-*")))))
    elif args.mode == "config":
        # Explicit mappings keep the demonstration independent of the host environment.
        cases = [("default", None, None, None), ("file", {"timeout": 10}, None, None),
                 ("environment", {"timeout": 10}, {"BIFROST_TIMEOUT": "20"}, None),
                 ("cli", {"timeout": 10}, {"BIFROST_TIMEOUT": "20"}, 30)]
        for label, file_config, env, cli in cases:
            value, source = resolve_timeout(file_config, env, cli)
            print(f"{label}={value} source={source}")
        try:
            resolve_timeout(environ={"BIFROST_TIMEOUT": ""})
        except ValueError:
            print("empty_environment=INVALID")
    elif args.mode == "process":
        result = run_worker(["two words", "x;echo NOT_A_COMMAND"])
        print(result.stdout.strip())
        print("exit=" + str(result.returncode))
        failed = run_worker(["--fail"])
        print("child_failure=" + str(failed.returncode))
        try:
            run_worker(["--sleep"], timeout=0.05)
        except subprocess.TimeoutExpired:
            print("timeout=EXPIRED")
    else:
        payload = {"event": "profile.update", "request_id": "REQ-001", "result": "denied", "status": 403,
                   "password": "PUBLIC-DEMO-PASSWORD", "authorization": "Bearer PUBLIC-DEMO-TOKEN"}
        line = log_record(payload)
        print(line)
        print("secret_values_present=" + str("PUBLIC-DEMO" in line))
        print("physical_lines=" + str(len(line.splitlines())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
