"""One fixed-width value interpreted with explicit signedness; no native C UB."""
import argparse
import struct


def inspect(data, flags):
    if len(data) != 2 or type(flags) is not int or not 0 <= flags <= 255:
        raise ValueError("exactly two bytes and flags 0..255 required")
    unsigned, = struct.unpack("<H", data)
    signed, = struct.unpack("<h", data)
    return unsigned, signed, flags & 15, (flags >> 7) & 1, (flags >> 4) & 7


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hex", nargs="?", default="feff")
    parser.add_argument("--flags", type=lambda text: int(text, 0), default=0xa5)
    args = parser.parse_args()
    try:
        unsigned, signed, version, urgent, reserved = inspect(bytes.fromhex(args.hex), args.flags)
    except ValueError as error:
        parser.exit(2, f"INVALID: {error}\n")
    print(f"u16={unsigned} s16={signed}")
    print(f"zero32={unsigned:08x} sign32={signed & 0xffffffff:08x}")
    print(f"version={version} urgent={urgent} reserved={reserved}")


if __name__ == "__main__":
    main()
