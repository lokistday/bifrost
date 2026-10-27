"""Small deterministic, offline data-analysis tools for original fixtures.

Archive exercise examines only an in-memory, fixed educational archive.
No file is extracted, and no network service is contacted.
"""
import argparse
from collections import deque
import hashlib
import io
import itertools
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

HERE = Path(__file__).resolve().parent
LINE = re.compile(r"id=(?P<id>L[0-9]{2}) user=(?P<user>[a-z]+) status=(?P<status>ok|denied)", re.ASCII)


def parse_lines(text):
    accepted, rejected = [], []
    seen = set()
    for number, line in enumerate(text.splitlines(), 1):
        match = LINE.fullmatch(line)
        if match is None or match["id"] in seen:
            rejected.append(number)
        else:
            seen.add(match["id"])
            accepted.append(match.groupdict())
    return accepted, rejected


def parse(source=None):
    rows, rejected = parse_lines((Path(source) if source else HERE / "events.txt").read_text(encoding="utf-8"))
    print("denied=" + ",".join(row["id"] for row in rows if row["status"] == "denied"))
    print(f"accepted={len(rows)} rejected-lines={','.join(map(str, rejected)) or 'none'}")


def safe_member(name):
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and ":" not in normalized


def archive(source=None):
    # Intentionally suspicious MEMBER NAME only; never extracted to disk.
    memory = io.BytesIO()
    with zipfile.ZipFile(memory, "w", zipfile.ZIP_STORED) as bundle:
        bundle.writestr("notes.txt", "training\n")
        bundle.writestr("../outside.txt", "example only\n")
    with zipfile.ZipFile(memory) as bundle:
        for item in bundle.infolist():
            print(f"{item.filename} size={item.file_size} {'CANDIDATE' if safe_member(item.filename) else 'REJECT'}")
    print("extracted=0")


def shortest_path(edges, start, goal):
    todo = deque([(start, [start])])
    visited = {start}
    while todo:
        node, path = todo.popleft()
        if node == goal:
            return path
        for neighbor in sorted(edges.get(node, [])):
            if neighbor not in visited:
                visited.add(neighbor)
                todo.append((neighbor, path + [neighbor]))
    return None


def graph(source=None):
    sample = json.loads((Path(source) if source else HERE / "graph.json").read_text(encoding="utf-8"))
    path = shortest_path(sample["edges"], sample["start"], sample["goal"])
    print("path=" + ("->".join(path) if path else "UNREACHABLE"))
    print(f"edges={len(path) - 1 if path else 'none'}")


def solve_clues(sample):
    solutions = []
    for order in itertools.permutations(sample["positions"]):
        placement = dict(zip(sample["people"], order))
        if all(placement[a] < placement[b] for a, b in sample["before"]) and all(
                placement[person] != position for person, position in sample["not_at"]):
            solutions.append(placement)
    return solutions


def constraints(source=None):
    sample = json.loads((Path(source) if source else HERE / "clues.json").read_text(encoding="utf-8"))
    solutions = solve_clues(sample)
    for solution in solutions:
        print(" ".join(f"{person}={solution[person]}" for person in sample["people"]))
    print(f"solutions={len(solutions)}")


def canonical(sample):
    if (not isinstance(sample, dict) or set(sample) != {"schema", "events"}
            or type(sample.get("schema")) is not int or sample["schema"] != 1
            or not isinstance(sample.get("events"), list) or not sample["events"]):
        raise ValueError("schema")
    rows = sample["events"]
    if any(not isinstance(row, dict) or set(row) != {"id", "status"}
           or not isinstance(row["id"], str) or not row["id"].strip()
           or not isinstance(row["status"], str) or row["status"] not in {"ok", "denied"} for row in rows):
        raise ValueError("row")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("duplicate ID")
    result = {"schema": 1, "events": sorted(rows, key=lambda row: row["id"])}
    return json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def verify(source=None):
    sample = json.loads((Path(source) if source else HERE / "repro.json").read_text(encoding="utf-8"))
    data = canonical(sample)
    permuted = dict(sample, events=list(reversed(sample["events"])))
    changed = json.loads(json.dumps(sample))
    changed["events"][0]["status"] = "ok" if changed["events"][0]["status"] == "denied" else "denied"
    print("canonical=" + data.decode("ascii"))
    print(f"order-independent={canonical(permuted) == data} value-sensitive={canonical(changed) != data}")
    print("sha256=" + hashlib.sha256(data).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["parse", "archive", "graph", "constraints", "verify"])
    parser.add_argument("--source")
    args = parser.parse_args()
    try:
        globals()[args.mode](args.source)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"INVALID: {error}\n")


if __name__ == "__main__":
    main()
