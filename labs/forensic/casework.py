"""Synthetic offline case exercises; does not acquire memory, read browser
profiles, connect to any host, or make incident-response changes.
"""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3

HERE = Path(__file__).resolve().parent


def load(name, source=None):
    return json.loads((Path(source) if source else HERE / name).read_text(encoding="utf-8"))


def plan(source=None):
    case = load("case.json", source)
    if not isinstance(case, dict) or not isinstance(case.get("items"), list):
        raise ValueError("items must be a list")
    ids, orders = set(), set()
    for item in case["items"]:
        if not isinstance(item, dict) or not all(isinstance(item.get(key), str) and item[key].strip()
                                                  for key in ("id", "kind", "purpose")):
            raise ValueError("item fields")
        if type(item.get("volatile")) is not bool or type(item.get("order")) is not int or item["order"] < 1:
            raise ValueError("item volatility/order")
        if item["id"] in ids or item["order"] in orders:
            raise ValueError("duplicate ID/order")
        ids.add(item["id"])
        orders.add(item["order"])
    for item in sorted(case["items"], key=lambda x: x["order"]):
        print(f"{item['id']} {item['kind']} volatile={item['volatile']}")
    print(f"records={len(case['items'])} mode=plan-only")


def host(source=None):
    sample = load("snapshot.json", source)
    by_pid = {p["pid"]: p for p in sample["processes"]}
    for conn in sample["connections"]:
        process = by_pid.get(conn["pid"])
        if process is None:
            print(f"{conn['id']} pid={conn['pid']} process=UNKNOWN")
            continue
        parent = by_pid.get(process["ppid"], {})
        print(f"{conn['id']} {parent.get('name', 'UNKNOWN')}->{process['name']} remote={conn['remote']}")


def browser(source=None):
    # A synthetic database is constructed only in memory. Never open user profiles.
    with sqlite3.connect(":memory:") as db:
        db.executescript((Path(source) if source else HERE / "history.sql").read_text(encoding="utf-8"))
        selected = db.execute("SELECT id,time,transition FROM visits WHERE transition != ? ORDER BY time,id", ("auto",)).fetchall()
        for row in selected:
            print(" ".join(row))
        count = db.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
        print(f"total={count} displayed={len(selected)} synthetic=True")


def carve(source=None):
    data = bytes.fromhex((Path(source) if source else HERE / "fragments.hex").read_text(encoding="ascii"))
    start = 0
    while True:
        offset = data.find(b"BF", start)
        if offset == -1:
            break
        if offset + 4 > len(data):
            print(f"offset={offset} INCOMPLETE header")
        else:
            length = int.from_bytes(data[offset + 2:offset + 4], "little")
            payload = data[offset + 4:offset + 4 + length]
            state = "COMPLETE" if len(payload) == length else "INCOMPLETE"
            print(f"offset={offset} declared={length} available={len(payload)} {state}")
        start = offset + 2


def correlate(source=None):
    with (Path(source) if source else HERE / "crosslog.csv").open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        stamp = datetime.fromisoformat(row["time"])
        if stamp.tzinfo is None:
            raise ValueError("timezone required")
        row["utc"] = stamp.astimezone(timezone.utc)
    chosen = [row for row in rows if row["host"] == "workstation-7" and row["session"] == "S10"]
    for row in sorted(chosen, key=lambda row: (row["utc"], row["id"])):
        print(f"{row['id']} {row['utc'].isoformat()} {row['event']}")
    print(f"linked={len(chosen)} excluded={len(rows) - len(chosen)}")


def respond(source=None):
    case = load("response.json", source)
    confirmed = sorted({o["host"] for o in case["observations"] if o["confirmed"] is True})
    print("confirmed-hosts=" + ",".join(confirmed))
    for action in case["actions"]:
        # Planning checklist, not an automated real-world response decision.
        ready = all(action[key] is True for key in ("authorized", "impact_reviewed", "evidence_preserved"))
        print(f"{action['name']} {'READY-FOR-REVIEW' if ready else 'HOLD'}")
    print("execution=NONE recovery-validation=REQUIRED")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["plan", "host", "browser", "carve", "correlate", "respond"])
    parser.add_argument("--source")
    args = parser.parse_args()
    try:
        globals()[args.mode](args.source)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
        parser.exit(2, f"INVALID: {error}\n")


if __name__ == "__main__":
    main()
