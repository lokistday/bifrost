"""Original BF toy format: magic[2], little-endian count[2], count bytes.

This is not an executable format or a secure network protocol.
"""
import argparse
import struct


def parse(data):
    if len(data) < 4 or data[:2] != b"BF":
        raise ValueError("header")
    count, = struct.unpack_from("<H", data, 2)
    if count > 64 or len(data) != 4 + count:
        raise ValueError("length")
    return data[4:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hex", nargs="?", default="42460300414243")
    args = parser.parse_args()
    try:
        data = bytes.fromhex(args.hex)
        body = parse(data)
    except ValueError as error:
        parser.exit(2, f"INVALID: {error}\n")
    print(f"little={int.from_bytes(data[2:4], 'little')} big={int.from_bytes(data[2:4], 'big')}")
    print(f"payload={body.decode('ascii', errors='backslashreplace')}")


if __name__ == "__main__":
    main()
