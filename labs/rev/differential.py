"""Compare an intentionally incomplete candidate with the toy BF reference.

Only small fixed local byte strings are processed; no fuzzing targets or network.
"""
from binary_lab import parse


def candidate(data):
    if len(data) < 4 or data[:2] != b"BF":
        raise ValueError("header")
    count = int.from_bytes(data[2:4], "little")
    if count > 64 or len(data) < 4 + count:  # BUG: trailing bytes accepted
        raise ValueError("length")
    return data[4:4 + count]


def outcome(fn, data):
    try:
        return "ACCEPT:" + fn(data).hex()
    except ValueError:
        return "REJECT"


def main():
    cases = {"valid": b"BF\x03\x00ABC", "short": b"BF\x03\x00AB",
             "trailing": b"BF\x03\x00ABC!", "empty": b"BF\x00\x00", "magic": b"ZZ\x00\x00"}
    mismatches = 0
    for label, data in cases.items():
        a, b = outcome(parse, data), outcome(candidate, data)
        if a != b:
            mismatches += 1
            print(f"{label} reference={a} candidate={b}")
    print(f"cases={len(cases)} mismatches={mismatches}")


if __name__ == "__main__":
    main()
