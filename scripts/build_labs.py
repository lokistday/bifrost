"""Rebuild original, offline teaching fixtures and deterministic downloadable bundles."""
from pathlib import Path
import hashlib
import json
import socket
import struct
import zipfile
import shutil
import tempfile
import atexit

PROJECT = Path(__file__).resolve().parents[1]
PUBLISH = PROJECT / 'labs'
assert PUBLISH.resolve() == PROJECT / 'labs' and not PUBLISH.is_symlink(), 'Unexpected labs output directory'
_staging = tempfile.TemporaryDirectory(prefix='bifrost-labs-')
atexit.register(_staging.cleanup)
ROOT = Path(_staging.name)
(ROOT / 'network').mkdir()
SOURCES = Path(__file__).resolve().parent / 'lab_sources'
assert SOURCES.resolve() == PROJECT / 'scripts/lab_sources', 'Unexpected source directory'
FIXTURES = Path(__file__).resolve().parents[1] / 'content' / 'lab-fixtures'

def write(track, name, content):
    folder = ROOT / track
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(content.strip() + '\n', encoding='utf-8', newline='\n')






# A real, tiny Ethernet/IPv4 PCAP, generated without third-party libraries.
def checksum(data):
    if len(data) % 2: data += b'\0'
    total = sum(struct.unpack('!' + 'H' * (len(data) // 2), data))
    while total >> 16: total = (total & 65535) + (total >> 16)
    return (~total) & 65535

def packet(src, dst, proto, payload):
    ip = struct.pack('!BBHHHBBH4s4s', 0x45, 0, 20 + len(payload), 1, 0, 64, proto, 0, socket.inet_aton(src), socket.inet_aton(dst))
    ip = ip[:10] + struct.pack('!H', checksum(ip)) + ip[12:]
    ethernet = '0200000000010200000000020800' if src == '192.0.2.20' else '0200000000020200000000010800'
    return bytes.fromhex(ethernet) + ip + payload

def tcp(src, dst, sport, dport, seq, ack, flags, data=b''):
    header = struct.pack('!HHIIBBHHH', sport, dport, seq, ack, 5 << 4, flags, 65535, 0, 0)
    pseudo = socket.inet_aton(src) + socket.inet_aton(dst) + struct.pack('!BBH', 0, 6, len(header) + len(data))
    header = header[:16] + struct.pack('!H', checksum(pseudo + header + data)) + header[18:]
    return packet(src, dst, 6, header + data)

client, server = '192.0.2.10', '192.0.2.20'
question = b'\x07bifrost\x04test\x00' + struct.pack('!HH', 1, 1)
query = struct.pack('!HHHHHH', 0x1234, 0x0100, 1, 0, 0, 0) + question
answer = struct.pack('!HHHHHH', 0x1234, 0x8180, 1, 1, 0, 0) + question + b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 60, 4) + socket.inet_aton(server)
udp = lambda a, b, data: struct.pack('!HHHH', a, b, 8 + len(data), 0) + data
request = b'GET /lesson HTTP/1.1\r\nHost: bifrost.test\r\n\r\n'
response = b'HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\nBifrost\n'
frames = [packet(client, server, 17, udp(53000, 53, query)), packet(server, client, 17, udp(53, 53000, answer)),
          tcp(client, server, 50000, 80, 100, 0, 2), tcp(server, client, 80, 50000, 200, 101, 18),
          tcp(client, server, 50000, 80, 101, 201, 16), tcp(client, server, 50000, 80, 101, 201, 24, request),
          tcp(server, client, 80, 50000, 201, 101 + len(request), 24, response),
          tcp(client, server, 50000, 80, 101 + len(request), 201 + len(response), 16)]
pcap = struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
for i, frame in enumerate(frames):
    pcap += struct.pack('<IIII', 1792454400 + i, 0, len(frame), len(frame)) + frame
(ROOT / 'network' / 'traffic.pcap').write_bytes(pcap)

# The frozen TLS bytes came from an actual local OpenSSL MemoryBIO exchange.
# Only Ethernet/IP/TCP headers, sequencing and timestamps are constructed here.
# Keeping the transcript as source makes ordinary builds byte-for-byte stable.
tls_fixture = json.loads((FIXTURES / 'tls13.json').read_text(encoding='utf-8'))
tls_frames = [tcp(client, server, 50001, 443, 1000, 0, 2),
              tcp(server, client, 443, 50001, 9000, 1001, 18),
              tcp(client, server, 50001, 443, 1001, 9001, 16)]
client_seq, server_seq = 1001, 9001
for chunk in tls_fixture['chunks']:
    payload = bytes.fromhex(chunk['hex'])
    for offset in range(0, len(payload), 1200):
        data = payload[offset:offset + 1200]
        if chunk['direction'] == 'client_to_server':
            tls_frames.append(tcp(client, server, 50001, 443, client_seq, server_seq, 24, data))
            client_seq += len(data)
        else:
            tls_frames.append(tcp(server, client, 443, 50001, server_seq, client_seq, 24, data))
            server_seq += len(data)
tls_frames.extend([tcp(client, server, 50001, 443, client_seq, server_seq, 17),
                   tcp(server, client, 443, 50001, server_seq, client_seq + 1, 17),
                   tcp(client, server, 50001, 443, client_seq + 1, server_seq + 1, 16)])
tls_pcap = struct.pack('<IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
for i, frame in enumerate(tls_frames):
    tls_pcap += struct.pack('<IIII', 1792454500 + i, 0, len(frame), len(frame)) + frame
(ROOT / 'network' / 'tls13.pcap').write_bytes(tls_pcap)
write('network', 'tls13.keys', tls_fixture['keylog'])
write('network', 'tls13-provenance.json', json.dumps({key: value for key, value in tls_fixture.items()
      if key not in ('chunks', 'keylog')}, ensure_ascii=False, indent=2))




# Readable authored sources for the expanded labs. Keep these outside generated
# labs/: rebuilding copies the originals before calculating checksums and ZIPs.
source_manifest = json.loads((PROJECT / 'content/lab-sources.json').read_text(encoding='utf-8'))
for track, names in source_manifest.items():
    assert track in {c['id'] for c in json.loads((PROJECT / 'content/site.json').read_text(encoding='utf-8'))['courses']}
    for name in names:
        assert Path(name).name == name and '/' not in name and '\\' not in name and name not in ('.', '..')
        source = SOURCES / track / name
        assert (SOURCES / track).resolve() == SOURCES / track, f'Unexpected course source directory: {track}'
        assert source.is_file() and not source.is_symlink(), f'Not an authored regular file: {source}'
        assert source.resolve().parent == (SOURCES / track).resolve(), f'Source escapes track: {source}'
        write(track, name, source.read_text(encoding='utf-8'))

for track in source_manifest:
    for name in ('lab_input.py', 'project.py'):
        write(track, name, (PROJECT / 'scripts/lab_common' / name).read_text(encoding='utf-8'))
    if track in ('cloud', 'network', 'crypto'):
        write(track, 'model_contracts.py', (PROJECT / 'scripts/lab_common/model_contracts.py').read_text(encoding='utf-8'))

for folder in sorted(ROOT.iterdir()):
    if not folder.is_dir(): continue
    write(folder.name, 'README.md', f'''# Bifrost · {folder.name}
이 묶음은 Bifrost가 직접 만든 교육용 자료입니다. 실제 개인정보·접속 키·운영 로그가 아닙니다.

ZIP을 먼저 풀고 파일을 확인하세요. Python 예제의 기본 환경은 Python 3.10 이상입니다.
기본 예제는 표준 라이브러리만 사용하며, crypto의 실제 AEAD·서명·봉투 암호 예제는 선택 패키지가 필요합니다.
선택 패키지 설치와 실행 범위는 crypto의 requirements.txt 및 차시별 가이드를 확인하세요.
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3 명령으로 실행합니다.
C 예제는 Ubuntu/WSL의 gcc, gdb, binutils를 기준으로 합니다. 바이너리를 제공하지 않고 소스를 제공합니다.
명령은 각 차시를 따라 실행하세요. 스크립트가 외부 서비스에 접속하거나 클라우드 자원을 만들지는 않습니다.

각 폴더의 모든 파일을 함께 유지하세요. 수정할 때 원본은 보관하고 작업용 사본을 만드세요.
network의 traffic.pcap은 합성 DNS 2개와 TCP/HTTP 6개, 총 8프레임입니다.
별도 tls13.pcap은 메모리 안에서 실제 TLS 1.3 교환을 생성하고 합성 네트워크 헤더를 붙인 표본입니다.
network 정책·cloud 구성은 단순화한 교육 모델입니다. 실제 장비나 공급자에 그대로 적용할 형식이 아닙니다.
crypto의 고전 암호와 XOR 예제는 원리 관찰용이며 실제 보안에 사용하지 않습니다.
자세한 준비·예상 결과·한계·풀이가 제공된 묶음은 LAB-GUIDE.md를 먼저 읽으세요.
후속 응용 차시는 ROUND2-GUIDE.md를, network·cloud·crypto의 앞선 확장은 ADVANCED-GUIDE.md를 함께 확인하세요.
분야를 마치면 project-brief.md의 종합 프로젝트를 진행하세요. A/B 표본·결과 검사·보고서 루브릭이 있습니다.
''')
    hashes = '\n'.join(f'{hashlib.sha256(file.read_bytes()).hexdigest()}  {file.name}'
                       for file in sorted(folder.iterdir(), key=lambda path: path.name)
                       if file.is_file() and file.name != 'SHA256SUMS.txt')
    write(folder.name, 'SHA256SUMS.txt', hashes)
    # Store these small bundles without zlib-version differences. Set metadata
    # explicitly because ZipInfo otherwise differs between Windows and Linux.
    with zipfile.ZipFile(ROOT / f'{folder.name}.zip', 'w', zipfile.ZIP_STORED) as archive:
        for file in sorted(folder.iterdir(), key=lambda path: path.name):
            if not file.is_file():
                continue
            info = zipfile.ZipInfo(f'{folder.name}/{file.name}', (2026, 10, 21, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, file.read_bytes())

print('Rebuilt 9 offline lab bundles.')

# Only files produced in this fresh staging directory can enter the publication
# manifest. Local learner scratch files are preserved but never published.
manifest = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file())
PUBLISH.mkdir(exist_ok=True)
for name in manifest:
    target = PUBLISH / name
    assert not target.is_symlink() and not target.parent.is_symlink(), f'Refuse symlink output: {target}'
    assert target.resolve().is_relative_to(PUBLISH.resolve()), f'Output escapes labs: {target}'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
(PUBLISH / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
