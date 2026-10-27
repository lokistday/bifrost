"""Offline data-handling exercises. Python 3.10+, standard library only."""
import argparse
import json
from pathlib import Path
import sys


def parse_minutes(value):
    if type(value) is not int or not 0 <= value <= 1440:
        raise ValueError("minutes must be an integer from 0 to 1440")
    return value


def validate_record(record):
    if not isinstance(record, dict) or set(record) != {"learner", "minutes"}:
        raise ValueError("record needs exactly learner and minutes")
    if not isinstance(record["learner"], str) or not record["learner"].strip():
        raise ValueError("learner must be nonempty text")
    return {"learner": record["learner"], "minutes": parse_minutes(record["minutes"])}


def load_record(path):
    with Path(path).open(encoding="utf-8") as handle:
        return validate_record(json.load(handle))


def summary(record, minimum):
    item = validate_record(record)
    parse_minutes(minimum)
    return f"learner={item['learner']} minutes={item['minutes']} selected={item['minutes'] >= minimum}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest="mode", required=True)
    sub.add_parser("text", help="Compare code-point and UTF-8 byte lengths")
    sub.add_parser("errors", help="Classify expected input errors")
    for mode in ("json", "summary"):
        child = sub.add_parser(mode)
        child.add_argument("path", nargs="?", default=str(Path(__file__).with_name("record.json")))
        if mode == "summary":
            child.add_argument("--minimum", type=int, default=20)
    args = parser.parse_args(argv)
    try:
        if args.mode == "text":
            value = "A\uac00"
            raw = value.encode("utf-8")
            print(f"codepoints={len(value)} bytes={len(raw)} hex={raw.hex()}")
            print(f"roundtrip={raw.decode('utf-8') == value}")
            try:
                raw.decode("ascii")
            except UnicodeDecodeError:
                print("wrong_encoding=UnicodeDecodeError")
        elif args.mode == "errors":
            for label, value in (("ok", 30), ("text", "30"), ("negative", -1), ("boolean", True)):
                try:
                    print(f"{label}={parse_minutes(value)}")
                except ValueError:
                    print(f"{label}=INVALID")
        else:
            record = load_record(args.path)
            if args.mode == "json":
                print(f"learner={record['learner']} minutes={record['minutes']}")
                print(f"canonical={json.dumps(record, sort_keys=True, separators=(',', ':'))}")
            else:
                print(summary(record, args.minimum))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"INVALID: {type(error).__name__}: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
