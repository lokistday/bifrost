"""Offline original artifacts. No EVTX/filesystem/memory acquisition or parsing.

XML and JSON inputs are small trusted authored fixtures, not arbitrary hostile data.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
NS = {"e": "http://schemas.microsoft.com/win/2004/08/events/event"}


def utc(text):
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("timezone required")
    return value.astimezone(timezone.utc).isoformat()


def windows(source):
    root = ET.parse(source).getroot()
    events = root.findall("e:Event", NS)
    if not events:
        raise ValueError("no supported namespaced Event records")
    seen = set()
    # This fixed fixture is one computer/channel/export. IDs are not global.
    for event in events:
        record = event.findtext("e:System/e:EventRecordID", namespaces=NS)
        if not record or record in seen:
            raise ValueError("missing/duplicate record ID")
        seen.add(record)
        fields = {}
        for item in event.findall("e:EventData/e:Data", NS):
            name = item.get("Name")
            if not name or name in fields:
                raise ValueError("missing/duplicate Data Name")
            fields[name] = item.text or ""
        stamp = event.find("e:System/e:TimeCreated", NS)
        if stamp is None:
            raise ValueError("missing TimeCreated")
        event_id = event.findtext("e:System/e:EventID", namespaces=NS)
        print(f"record={record} event={event_id} utc={utc(stamp.get('SystemTime', ''))} user={fields.get('TargetUserName', 'UNKNOWN')} type={fields.get('LogonType', 'UNKNOWN')}")
    print(f"records={len(seen)} format=synthetic-xml")


def linux(source):
    rows = [json.loads(line) for line in Path(source).read_text(encoding="utf-8").splitlines() if line.strip()]
    sessions = set()
    for row in sorted(rows, key=lambda row: (utc(row["time"]), row["id"])):
        utc(row["time"])
        key = (row["host"], row["user"], row["session"])
        if row["event"] == "auth-success" and row["result"] == "allow":
            sessions.add(key)
        if row["service"] == "sudo":
            print(f"{row['id']} user={row['user']} result={row['result']} linked-login={key in sessions} command={row['command']}")
    print("execution-outcome=NOT-PROVIDED")


def filesystem(source):
    rows = json.loads(Path(source).read_text(encoding="utf-8"))["records"]
    grouped = {}
    for row in rows:
        grouped.setdefault(row["inode"], []).append(row["path"])
    for inode, paths in sorted(grouped.items()):
        links = sorted({row["links"] for row in rows if row["inode"] == inode})
        print(f"inode={inode} observed-names={len(paths)} declared-links={','.join(map(str, links))} paths={','.join(paths)}")
    missing = sum(row["birth"] is None for row in rows)
    print(f"birth-unknown={missing} ctime-is-creation=False")


def memory(source):
    sample = json.loads(Path(source).read_text(encoding="utf-8"))
    reviewed = 0
    for process in sample["processes"]:
        for area in process["ranges"]:
            if type(area["start"]) is not int or type(area["size"]) is not int or area["start"] < 0 or area["size"] <= 0:
                raise ValueError("range must have nonnegative start and positive size")
            if not isinstance(area["permission"], str) or set(area["permission"]) - set("rwx"):
                raise ValueError("invalid permission")
            if "w" in area["permission"] and "x" in area["permission"] and area["backing"] == "private":
                reviewed += 1
                print(f"{area['id']} pid={process['pid']} private-WX=REVIEW range=[{area['start']},{area['start'] + area['size']})")
    print(f"review={reviewed} verdict=NOT-A-MALWARE-VERDICT")


def interval(event):
    for name in ("recorded", "clock_ahead", "uncertainty"):
        if type(event[name]) is not int:
            raise ValueError("integer clock model required")
    if event["uncertainty"] < 0:
        raise ValueError("uncertainty cannot be negative")
    center = event["recorded"] - event["clock_ahead"]
    return center - event["uncertainty"], center + event["uncertainty"]


def coverage(source):
    sample = json.loads(Path(source).read_text(encoding="utf-8"))
    intervals = []
    for event in sample["events"]:
        lo, hi = interval(event)
        intervals.append((lo, hi))
        print(f"{event['id']} corrected=[{lo},{hi}]")
    if len(intervals) == 2:
        a, b = intervals
        relation = "A-BEFORE-B" if a[1] < b[0] else "B-BEFORE-A" if b[1] < a[0] else "ORDER-UNCERTAIN"
        print(f"relation={relation}")
    for item in sample["coverage"]:
        if type(item["enabled"]) is not bool or type(item["start"]) is not int or type(item["end"]) is not int or item["start"] > item["end"]:
            raise ValueError("invalid coverage window")
        print(f"source={item['source']} logging-enabled={item['enabled']} window=[{item['start']},{item['end']}]")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["windows", "linux", "filesystem", "memory", "coverage"])
    parser.add_argument("--source")
    args = parser.parse_args()
    defaults = {"windows":"events-synthetic.xml", "linux":"linux-auth.jsonl", "filesystem":"fs-records.json",
                "memory":"memory-model.json", "coverage":"coverage.json"}
    try:
        globals()[args.mode](Path(args.source) if args.source else HERE / defaults[args.mode])
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
        parser.exit(2, f"INVALID: {error}\n")


if __name__ == "__main__":
    main()
