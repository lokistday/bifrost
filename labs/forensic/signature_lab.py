"""Bounded, offline PNG structure exercise. Not a general image validator."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

MAGIC = bytes.fromhex('89504e470d0a1a0a')
LIMIT = 1024 * 1024

def read(path):
    with Path(path).open('rb') as f:
        data = f.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('input exceeds 1 MiB')
    return data

def png_end(data, start=0):
    if data[start:start+8] != MAGIC:
        raise ValueError('PNG signature missing')
    pos = start + 8
    seen = []
    image_data = bytearray()
    dimensions = None
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError('truncated chunk header/CRC')
        length = int.from_bytes(data[pos:pos+4], 'big')
        kind = data[pos+4:pos+8]
        end = pos + 12 + length
        if end > len(data):
            raise ValueError('truncated chunk body')
        payload = data[pos+8:pos+8+length]
        crc = int.from_bytes(data[pos+8+length:end], 'big')
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError('chunk CRC mismatch')
        if not seen and kind != b'IHDR':
            raise ValueError('IHDR must be first')
        if kind == b'IHDR':
            if seen or length != 13:
                raise ValueError('invalid/repeated IHDR')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            if not (1 <= width <= 64 and 1 <= height <= 64):
                raise ValueError('dimensions outside teaching contract')
            if (depth, color, compression, filtering, interlace) != (8, 2, 0, 0, 0):
                raise ValueError('unsupported: only small RGB8 non-interlaced PNG')
            dimensions = (width, height)
        elif kind == b'IDAT':
            if b'IDAT' in seen and seen[-1] != b'IDAT':
                raise ValueError('nonconsecutive IDAT')
            image_data.extend(payload)
        elif kind == b'IEND':
            if length or b'IDAT' not in seen:
                raise ValueError('invalid IEND/missing IDAT')
            width, height = dimensions
            expected = height * (1 + width * 3)
            decoder = zlib.decompressobj()
            raw = decoder.decompress(bytes(image_data), expected + 1)
            if len(raw) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
                raise ValueError('invalid or oversized pixel stream')
            if any(raw[row * (1 + width * 3)] > 4 for row in range(height)):
                raise ValueError('invalid PNG row filter')
            return end, seen + [kind]
        elif kind not in (b'PLTE',) and not (kind[0] & 32):
            raise ValueError('unsupported critical chunk')
        seen.append(kind)
        pos = end
    raise ValueError('IEND missing')

def inspect(path):
    data = read(path)
    print(f'file={Path(path).name} bytes={len(data)} sha256={hashlib.sha256(data).hexdigest()}')
    for pos in range(0, min(64, len(data)), 16):
        row = data[pos:pos+16]
        print(f'{pos:08x}  {row.hex(" "):<47}  '+''.join(chr(b) if 32 <= b < 127 else '.' for b in row))
    if data.startswith(MAGIC):
        try:
            end, chunks = png_end(data)
            print('PNG_CONTRACT_VALID chunks='+','.join(c.decode('ascii') for c in chunks)+f' end={end} trailing={len(data)-end}')
        except ValueError as e:
            print('PNG_UNVERIFIED: '+str(e))
    elif data.startswith(b'\xff\xd8\xff'):
        print('JPEG_CANDIDATE: full decoding not performed')
    elif data.startswith(b'PK\x03\x04'):
        print('ZIP_CANDIDATE: archive structure/content not verified')
    else:
        print('UNKNOWN: no supported prefix; not proof of no evidence')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    setup = sub.add_parser('setup'); setup.add_argument('directory')
    view = sub.add_parser('inspect'); view.add_argument('file')
    carve = sub.add_parser('carve'); carve.add_argument('file'); carve.add_argument('output')
    args = parser.parse_args()
    try:
        if args.action == 'setup':
            fixtures = json.loads(Path(__file__).with_name('signature-fixtures.json').read_text())
            target = Path(args.directory); target.mkdir(exist_ok=False)
            for name, encoded in fixtures.items():
                (target/name).write_bytes(bytes.fromhex(encoded))
            print(f'created={len(fixtures)} files; originals in signature-fixtures.json')
        elif args.action == 'inspect':
            inspect(args.file)
        else:
            data = read(args.file)
            start = data.find(MAGIC)
            if start < 0:
                raise ValueError('no PNG candidate')
            end, _ = png_end(data, start)
            with Path(args.output).open('xb') as out:
                out.write(data[start:end])
            print(f'offset={start} end={end} extracted={end-start}; filename/history not recovered')
    except (OSError, ValueError, zlib.error) as e:
        parser.exit(2, f'ERROR: {e}\n')

if __name__ == '__main__':
    main()
