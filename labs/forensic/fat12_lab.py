"""Small real FAT12 volume exercise; no mounting, acquisition or general recovery."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct

SECTOR = 512
TOTAL = 2880
IMAGE_SIZE = SECTOR * TOTAL
MAX_IMAGE = 2 * 1024 * 1024
GEOMETRY = (512, 1, 1, 2, 224, 2880, 9)
README = (b"BIFROST FAT12 evidence: follow cluster links, not physical order.\n" * 20)[:1100]
EVIDENCE = b"Educational sample only. No personal data.\n"
DELETED = b"Residual bytes in a free cluster are not a complete recovered file.\n"


def set_fat(table, cluster, value):
    offset = cluster + cluster // 2
    pair = int.from_bytes(table[offset:offset + 2], 'little')
    if cluster & 1:
        pair = (pair & 0x000f) | (value << 4)
    else:
        pair = (pair & 0xf000) | value
    table[offset:offset + 2] = pair.to_bytes(2, 'little')


def fat_entry(table, cluster):
    offset = cluster + cluster // 2
    if offset + 2 > len(table):
        raise ValueError('FAT entry outside table')
    pair = int.from_bytes(table[offset:offset + 2], 'little')
    return (pair >> 4 if cluster & 1 else pair) & 0xfff


def directory_entry(name, cluster, size, deleted=False):
    entry = bytearray(32)
    entry[:11] = name
    entry[11] = 0x20
    # FAT local calendar fields: fixed educational value, no timezone assertion.
    date = ((2026 - 1980) << 9) | (11 << 5) | 9
    struct.pack_into('<HH', entry, 22, (12 << 11), date)
    struct.pack_into('<HI', entry, 26, cluster, size)
    if deleted:
        entry[0] = 0xe5
    return entry


def make_image():
    image = bytearray(IMAGE_SIZE)
    image[:3] = b'\xeb\x3c\x90'
    image[3:11] = b'BIFROST '
    struct.pack_into('<HBHBHHBHHHII', image, 11,
                     512, 1, 1, 2, 224, 2880, 0xf0, 9, 18, 2, 0, 0)
    image[38] = 0x29
    struct.pack_into('<I', image, 39, 0xb1f02026)
    image[43:54] = b'BIFROSTLAB '
    image[54:62] = b'FAT12   '
    # Valid volume structures, no executable boot loader is supplied.
    image[510:512] = b'\x55\xaa'
    fat = bytearray(9 * SECTOR)
    fat[:3] = b'\xf0\xff\xff'
    for cluster, value in [(2, 5), (5, 3), (3, 0xfff), (4, 0xfff)]:
        set_fat(fat, cluster, value)
    image[SECTOR:10 * SECTOR] = fat
    image[10 * SECTOR:19 * SECTOR] = fat
    root = 19 * SECTOR
    entries = [directory_entry(b'README  TXT', 2, len(README)),
               directory_entry(b'EVIDENCETXT', 4, len(EVIDENCE)),
               directory_entry(b'EMPTY   TXT', 0, 0),
               directory_entry(b'OLDNOTE TXT', 6, len(DELETED), True)]
    for i, entry in enumerate(entries):
        image[root + i * 32:root + (i + 1) * 32] = entry
    for i, cluster in enumerate([2, 5, 3]):
        start = (33 + cluster - 2) * SECTOR
        part = README[i * SECTOR:(i + 1) * SECTOR]
        image[start:start + len(part)] = part
    for cluster, data in [(4, EVIDENCE), (6, DELETED)]:
        start = (33 + cluster - 2) * SECTOR
        image[start:start + len(data)] = data
    # Slack belongs to allocated space but is outside README's logical length.
    slack = (33 + 3 - 2) * SECTOR + len(README) - 2 * SECTOR
    image[slack:slack + 17] = b'OUTSIDE_FILE_SIZE'
    return bytes(image)


def setup(folder):
    # Existing learner folders and files are never replaced.
    folder.mkdir(parents=True, exist_ok=False)
    normal = make_image()
    files = {'volume.img': normal}
    loop = bytearray(normal)
    early = bytearray(normal)
    for start in [SECTOR, 10 * SECTOR]:
        fat = bytearray(loop[start:start + 9 * SECTOR])
        set_fat(fat, 5, 2)
        loop[start:start + len(fat)] = fat
        fat = bytearray(early[start:start + 9 * SECTOR])
        set_fat(fat, 2, 0xfff)
        early[start:start + len(fat)] = fat
    mismatch = bytearray(normal)
    mismatch[SECTOR + 4] ^= 1
    files.update({'loop.img': bytes(loop), 'early-end.img': bytes(early),
                  'fat-mismatch.img': bytes(mismatch), 'truncated.img': normal[:10000]})
    for name, data in files.items():
        with (folder / name).open('xb') as stream:
            stream.write(data)
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    with (folder / 'sample-hashes.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(hashes, stream, indent=2)
        stream.write('\n')
    print('Created five real-format FAT12 volume samples and sample-hashes.json')


def read_image(path):
    with path.open('rb') as stream:
        image = stream.read(MAX_IMAGE + 1)
    if len(image) > MAX_IMAGE:
        raise ValueError('image exceeds 2 MiB exercise limit')
    if len(image) < SECTOR or image[510:512] != b'\x55\xaa':
        raise ValueError('missing volume boot signature')
    bps = struct.unpack_from('<H', image, 11)[0]
    spc = image[13]
    reserved = struct.unpack_from('<H', image, 14)[0]
    fats = image[16]
    roots, total = struct.unpack_from('<HH', image, 17)
    spf = struct.unpack_from('<H', image, 22)[0]
    if (bps, spc, reserved, fats, roots, total, spf) != GEOMETRY:
        raise ValueError('unsupported BPB geometry; this exercise supports one FAT12 profile')
    if len(image) != total * bps:
        raise ValueError('image length does not match BPB total sectors')
    root_sectors = (roots * 32 + bps - 1) // bps
    root_start = reserved + fats * spf
    data_start = root_start + root_sectors
    clusters = (total - data_start) // spc
    if not 1 <= clusters < 4085:
        raise ValueError('cluster count is outside FAT12 range')
    table = image[reserved * bps:(reserved + spf) * bps]
    mirror = image[(reserved + spf) * bps:(reserved + 2 * spf) * bps]
    if table != mirror:
        raise ValueError('FAT copies differ; do not choose a winner automatically')
    if table[:3] != b'\xf0\xff\xff':
        raise ValueError('unsupported FAT reserved entries')
    entries = []
    seen_names = set()
    for index in range(roots):
        offset = root_start * bps + index * 32
        entry = image[offset:offset + 32]
        if entry[0] == 0:
            break
        if entry[11] == 0x08:
            continue
        if entry[11] != 0x20:
            raise ValueError('unsupported root entry: only archive files are in this exercise')
        deleted = entry[0] == 0xe5
        raw_name = (b'?' + entry[1:11]) if deleted else entry[:11]
        try:
            base = raw_name[:8].decode('ascii').rstrip()
            extension = raw_name[8:11].decode('ascii').rstrip()
        except UnicodeDecodeError as exc:
            raise ValueError('unsupported non-ASCII short name') from exc
        name = base + ('.' + extension if extension else '')
        if not base or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_?.' for c in name):
            raise ValueError('unsupported short name')
        if not deleted and name in seen_names:
            raise ValueError('duplicate live short name')
        seen_names.add(name)
        start = struct.unpack_from('<H', entry, 26)[0]
        size = struct.unpack_from('<I', entry, 28)[0]
        if size > 128 * 1024:
            raise ValueError('file exceeds 128 KiB exercise limit')
        entries.append(dict(name=name, deleted=deleted, first_cluster=start, size=size,
                            entry_offset=offset, raw_write_time=entry[22:26].hex()))
    return image, table, dict(bytes_per_sector=bps, sectors_per_cluster=spc,
                             root_sector=root_start, data_sector=data_start,
                             cluster_count=clusters), entries


def chain_for(entry, table, geometry):
    if entry['size'] == 0:
        if entry['first_cluster'] != 0:
            raise ValueError('unsupported empty file with nonzero cluster')
        return []
    needed = math.ceil(entry['size'] / (geometry['bytes_per_sector'] * geometry['sectors_per_cluster']))
    cluster = entry['first_cluster']
    chain = []
    visited = set()
    while True:
        if cluster in visited:
            raise ValueError('cycle in allocated cluster chain')
        if not 2 <= cluster <= geometry['cluster_count'] + 1:
            raise ValueError('invalid/free/reserved cluster in allocated chain')
        visited.add(cluster)
        chain.append(cluster)
        if len(chain) > needed:
            raise ValueError('allocated chain is longer than declared file size needs')
        following = fat_entry(table, cluster)
        if following >= 0xff8:
            break
        if following == 0 or 0xff0 <= following <= 0xff7:
            raise ValueError('free/reserved/bad marker in allocated chain')
        cluster = following
    if len(chain) != needed:
        raise ValueError('allocated chain ends before declared file size')
    return chain


def analyse(path):
    image, table, geometry, entries = read_image(path)
    occupied = set()
    for entry in entries:
        if entry['deleted']:
            # Deleted entries are hints only; freed allocation links are not a recovery map.
            entry['chain'] = None
            entry['status'] = 'DELETED_ENTRY_HINT_ONLY'
            continue
        chain = chain_for(entry, table, geometry)
        if occupied.intersection(chain):
            raise ValueError('live files share clusters: cross-link')
        occupied.update(chain)
        entry['chain'] = chain
        entry['status'] = 'ALLOCATED_CHAIN_READABLE_IN_PROFILE'
    report = dict(profile='FAT12_1440KiB_ROOT_SHORT_NAMES',
                  image_sha256=hashlib.sha256(image).hexdigest(), geometry=geometry, entries=entries)
    return image, report


def extract(path, name, output):
    image, report = analyse(path)
    entry = next((e for e in report['entries'] if not e['deleted'] and e['name'] == name), None)
    if entry is None:
        raise ValueError('allocated short name not found; deleted recovery is not supported')
    geometry = report['geometry']
    unit = geometry['bytes_per_sector'] * geometry['sectors_per_cluster']
    parts = []
    for cluster in entry['chain']:
        start = geometry['data_sector'] * geometry['bytes_per_sector'] + (cluster - 2) * unit
        parts.append(image[start:start + unit])
    content = b''.join(parts)[:entry['size']]
    # Never replace an image, an existing extracted file or learner notes.
    with output.open('xb') as stream:
        stream.write(content)
    print(json.dumps(dict(name=name, size=len(content), chain=entry['chain'],
                          sha256=hashlib.sha256(content).hexdigest()), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    setup_parser = sub.add_parser('setup')
    setup_parser.add_argument('folder', type=Path)
    inspect_parser = sub.add_parser('inspect')
    inspect_parser.add_argument('image', type=Path)
    extract_parser = sub.add_parser('extract')
    extract_parser.add_argument('image', type=Path)
    extract_parser.add_argument('name')
    extract_parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'setup':
            setup(args.folder)
        elif args.command == 'inspect':
            print(json.dumps(analyse(args.image)[1], indent=2))
        else:
            extract(args.image, args.name, args.output)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'UNVERIFIED: {exc}\n')


if __name__ == '__main__':
    main()
