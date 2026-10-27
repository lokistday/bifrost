"""Trace an invertible toy byte transform; this is not encryption."""
import argparse


def encode(data):
    return bytes((value ^ 0x20) + index for index, value in enumerate(data))


def decode(data):
    return bytes((value - index) ^ 0x20 for index, value in enumerate(data))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", default="BIF")
    args = parser.parse_args()
    if not args.text.isascii() or len(args.text) > 16:
        parser.exit(2, "INVALID: ASCII text of at most 16 bytes required\n")
    source = args.text.encode("ascii")
    result = encode(source)
    for i, (a, b) in enumerate(zip(source, result)):
        print(f"i={i} source={a} xor={a ^ 0x20} stored={b}")
    print(f"hex={result.hex()} roundtrip={decode(result) == source}")


if __name__ == "__main__":
    main()
