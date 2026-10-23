"""Rebuild original, offline teaching fixtures and deterministic downloadable bundles."""
from pathlib import Path
import csv
import hashlib
import io
import json
import socket
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1] / 'labs'
SOURCES = Path(__file__).resolve().parent / 'lab_sources'
FIXTURES = Path(__file__).resolve().parents[1] / 'content' / 'lab-fixtures'

def write(track, name, content):
    folder = ROOT / track
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(content.strip() + '\n', encoding='utf-8', newline='\n')

write('foundation', 'hello.py', '''name = "Bifrost"
minutes = 15
print(f"Hello, {name}")
print(f"Study: {minutes * 2} minutes")''')
write('foundation', 'events.csv', '''user,status
alice,ok
bob,denied
alice,ok
carol,denied''')
write('foundation', 'summarize.py', '''from pathlib import Path
import csv

path = Path(__file__).with_name("events.csv")
with path.open(encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))
denied = [row for row in rows if row["status"] == "denied"]
print(f"events={len(rows)} denied={len(denied)}")
for row in denied:
    print(row["user"])''')
write('foundation', 'addresses.c', '''#include <stdio.h>
int main(void) {
    int value = 7;
    int *pointer = &value;
    printf("value=%d dereferenced=%d\\n", value, *pointer);
    printf("address=%p\\n", (void *)pointer);
    *pointer = 9;
    printf("after=%d\\n", value);
    return 0;
}''')
write('foundation', 'notes.txt', 'Bifrost\nLinux practice\nKeep evidence')

write('web', 'demo.py', '''"""Offline models, not a server or a production authentication system."""
import html
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
db.executemany("INSERT INTO users VALUES (?, ?)", [(1, "alice"), (2, "bob")])
payload = "' OR 1=1 --"
unsafe = db.execute("SELECT name FROM users WHERE name = '" + payload + "'").fetchall()
safe = db.execute("SELECT name FROM users WHERE name = ?", (payload,)).fetchall()
print(f"unsafe_rows={len(unsafe)} safe_rows={len(safe)}")
print("alice_rows=" + str(len(db.execute("SELECT name FROM users WHERE name = ?", ("alice",)).fetchall())))
print(html.escape('<b>hello</b>'))
def can_read(user, owner):
    return (isinstance(user, str) and bool(user.strip())
            and isinstance(owner, str) and bool(owner.strip())
            and user == owner)
print(f"own={can_read('alice', 'alice')} other={can_read('alice', 'bob')}")
assert len(unsafe) == 2 and len(safe) == 0
assert can_read("alice", "alice") and not can_read("alice", "bob")
print("regression=PASS")''')
write('web', 'browser.html', '''<!doctype html><html lang="ko"><meta charset="utf-8">
<title>Bifrost DOM 실습</title><h1>텍스트와 HTML</h1>
<p>왼쪽은 텍스트 노드, 오른쪽은 코드에 고정된 HTML입니다.</p>
<p id="text"></p><p id="markup"></p>
<script>
const sample = '<b>Bifrost</b>';
document.querySelector('#text').textContent = sample;
// Only a fixed, authored literal is used here. Do not insert untrusted data this way.
document.querySelector('#markup').innerHTML = sample;
</script></html>''')
write('web', 'requests.txt', '''GET /notes/1 HTTP/1.1
Host: localhost
Cookie: session=DEMO_ONLY

HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Set-Cookie: session=DEMO_ONLY; HttpOnly; SameSite=Lax

This is Alice's note.

# Separate example: Alice requests Bob's note -> 403 Forbidden.
# DEMO_ONLY is a fictional identifier, not a working credential.
# In HTTPS production, a session cookie should also use Secure.''')
write('web', 'permissions.csv', '''actor,resource,action,expected
alice,alice-note,read,allow
alice,bob-note,read,deny
anonymous,alice-note,read,deny
bob,bob-note,read,allow''')

write('pwn', 'memory.c', '''#include <stdio.h>
#include <stdlib.h>
int main(void) {
    int local = 7;
    int values[3] = {10, 20, 30};
    int *heap = malloc(sizeof *heap);
    if (!heap) return 1;
    *heap = 9;
    printf("local=%d heap=%d\\n", local, *heap);
    for (size_t i = 0; i < sizeof values / sizeof values[0]; ++i)
        printf("%d%s", values[i], i == 2 ? "\\n" : " ");
    free(heap);
    heap = NULL;
    return 0;
}''')
write('pwn', 'bounds.c', '''/* Deliberate LOCAL teaching error. Compile with AddressSanitizer first. */
#include <stdio.h>
int main(void) {
    int values[3] = {10, 20, 30};
    for (int i = 0; i <= 3; ++i) printf("%d\\n", values[i]);
    return 0;
}''')
write('rev', 'check.c', '''#include <stdio.h>
#include <string.h>
int check(const char *text) {
    return strlen(text) == 7 && strcmp(text, "BIFROST") == 0;
}
int main(int argc, char **argv) {
    if (argc != 2) { puts("usage: check WORD"); return 2; }
    puts(check(argv[1]) ? "match" : "no match");
    return 0;
}''')
write('rev', 'analysis.md', '''# 분석 기록
- 환경 / CPU / 컴파일 명령:
- 가설:
- 정적 근거 (함수·문자열·분기):
- 동적 근거 (입력·중단점·출력):
- 반례:
- 결론과 한계:''')

write('forensic', 'auth.csv', '''id,time,host,user,event,source
E01,2026-10-20T09:00:00+09:00,app,alice,login_ok,192.0.2.10
E02,2026-10-20T00:01:00+00:00,app,bob,login_denied,198.51.100.8
E03,2026-10-20T00:01:10+00:00,app,bob,login_denied,198.51.100.8
E04,2026-10-20T00:01:20+00:00,app,bob,login_denied,198.51.100.8
E05,2026-10-20T09:02:00+09:00,app,bob,login_ok,198.51.100.8
E06,2026-10-20T00:03:00+00:00,app,bob,file_read,198.51.100.8''')
write('forensic', 'evidence.txt', 'Bifrost training evidence\ncase=BF-001\nowner=alice')
write('forensic', 'timeline.py', '''from pathlib import Path
from datetime import datetime, timezone
import csv
with Path(__file__).with_name("auth.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
for row in sorted(rows, key=lambda r: datetime.fromisoformat(r["time"])):
    time = datetime.fromisoformat(row["time"]).astimezone(timezone.utc)
    print(time.isoformat(), row["id"], row["event"])''')

write('network', 'flows.csv', '''id,time,src,dst,port,action,service
N01,2026-10-20T00:00:00Z,192.0.2.10,10.10.10.20,443,ALLOW,web
N02,2026-10-20T00:00:01Z,10.10.10.20,10.10.20.30,5432,ALLOW,database
N03,2026-10-20T00:01:00Z,198.51.100.8,10.10.20.30,5432,DENY,database
N04,2026-10-20T00:01:10Z,198.51.100.8,10.10.10.20,22,DENY,ssh
N05,2026-10-20T00:01:20Z,198.51.100.8,10.10.10.20,22,DENY,ssh
N06,2026-10-20T00:01:30Z,10.10.10.20,203.0.113.9,443,ALLOW,egress''')
write('network', 'policy.json', json.dumps({'description': 'Simplified first-match educational policy; default deny. Not an actual firewall config.', 'rules': [
    {'src': '0.0.0.0/0', 'dst': '10.10.10.20/32', 'port': 443, 'action': 'ALLOW'},
    {'src': '10.10.10.20/32', 'dst': '10.10.20.30/32', 'port': 5432, 'action': 'ALLOW'}]}, indent=2))
write('network', 'evaluate.py', '''from pathlib import Path
import csv
import ipaddress
import json
root = Path(__file__).parent
rules = json.loads((root / "policy.json").read_text())["rules"]
with (root / "flows.csv").open(newline="", encoding="utf-8") as f:
    for flow in csv.DictReader(f):
        action = "DENY"
        for rule in rules:
            if (ipaddress.ip_address(flow["src"]) in ipaddress.ip_network(rule["src"])
                and ipaddress.ip_address(flow["dst"]) in ipaddress.ip_network(rule["dst"])
                and int(flow["port"]) == rule["port"]):
                action = rule["action"]
                break
        print(flow["id"], action, "MATCH" if action == flow["action"] else "MISMATCH")''')
write('network', 'detect.py', '''from pathlib import Path
from collections import Counter
import csv
with Path(__file__).with_name("flows.csv").open(newline="", encoding="utf-8") as f:
    counts = Counter(row["src"] for row in csv.DictReader(f) if row["action"] == "DENY")
for source, count in sorted(counts.items()):
    if count >= 3:
        print(f"REVIEW {source} denied={count}")
# Whole-file teaching counter. No time window, identity or intent inference.''')
write('network', 'design.md', '''# BF-001 통합 네트워크 검토
- 진입점: Internet -> web 10.10.10.20:443
- 데이터: web -> database 10.10.20.30:5432
- 관리: 별도 관리 구간과 신원 검증 필요
- 누락된 관측: DNS, TLS 인증서, 사용자 신원, 허용 egress의 목적

| 흐름 | 허용/거부 | 근거 | 검증 방법 | 롤백 |
| --- | --- | --- | --- | --- |
| Internet -> DB | | | | |
| web -> DB | | | | |
| web -> 외부 | | | | |

증거 ID / 대안 가설 / 탐지의 오탐 / 변경 영향 / 재검증 결과를 기록하세요.''')

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

write('crypto', 'lab.py', '''import base64
import hashlib
import hmac
import sys
mode = sys.argv[1] if len(sys.argv) > 1 else "representation"
data = b"Bifrost"
if mode == "representation":
    print(data.hex())
    print(base64.b64encode(data).decode())
    print(base64.b64decode("Qmlmcm9zdA==").decode())
elif mode == "modular":
    print(17 % 5, pow(3, -1, 26))
elif mode == "classical":
    text = "BIFROST"
    cipher = "".join(chr((ord(c) - 65 + 3) % 26 + 65) for c in text)
    print(cipher)
    print("".join(chr((ord(c) - 65 - 3) % 26 + 65) for c in cipher))
elif mode == "hash":
    a, b = hashlib.sha256(data).digest(), hashlib.sha256(data + b"!").digest()
    print("same=", a == b)
    print("hex_length=", len(a.hex()))
elif mode == "mac":
    key = b"DEMO-KEY-NOT-FOR-PRODUCTION"
    tag = hmac.digest(key, data, "sha256")
    print("original=", hmac.compare_digest(tag, hmac.digest(key, data, "sha256")))
    print("changed=", hmac.compare_digest(tag, hmac.digest(key, data + b"!", "sha256")))
elif mode == "nonce":
    # Toy XOR demonstration of stream reuse, NOT a cipher to deploy.
    a, b, stream = b"YES", b"NO!", bytes([31, 22, 9])
    xor = lambda x, y: bytes(i ^ j for i, j in zip(x, y))
    print(xor(xor(a, stream), xor(b, stream)) == xor(a, b))
elif mode == "password":
    # Fixed teaching salts; real systems need a fresh random salt per password.
    derive = lambda salt: hashlib.scrypt(b"demo-password", salt=salt, n=16384, r=8, p=1, dklen=32)
    print("same_salt=", derive(b"teaching-salt-A") == derive(b"teaching-salt-A"))
    print("other_salt=", derive(b"teaching-salt-A") == derive(b"teaching-salt-B"))
else:
    raise SystemExit("mode: representation modular classical hash mac nonce password")''')
write('crypto', 'protocol.md', '''# Bifrost: 키 역할 설계 (실제 암호문이나 키가 아닙니다)
- Alice의 서명 개인키: Alice만 보유
- Alice의 검증 공개키: Bob이 신뢰할 수 있는 경로로 확보
- Bob의 복호 개인키: Bob만 보유
- Bob의 암호화 공개키: Alice가 신뢰할 수 있는 경로로 확보
- 질문: Bob에게 보낼 내용을 암호화할 때 누구의 공개키를 사용할까?
- 질문: Alice의 서명을 검증할 때 누구의 공개키를 사용할까?
- 질문: 키가 바뀌면 기존 기록의 검증·복호화는 어떻게 보장할까?''')

write('misc', 'puzzle.txt', 'label=training\npayload=UW1sbWNtOXpkQT09\nnoise=ignore-me')
write('misc', 'solve.py', '''from pathlib import Path
import base64
import sys
path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("puzzle.txt")
fields = dict(line.split("=", 1) for line in path.read_text(encoding="utf-8").splitlines() if "=" in line)
value = fields["payload"].encode("ascii")
for step in range(2):
    value = base64.b64decode(value, validate=True)
    print(f"step={step + 1}: {value.decode('ascii')}")''')
write('misc', 'writeup.md', '''# 문제 해결 기록
## 입력과 목표
## 단서와 가설 (사실 / 추측 구분)
## 실패한 접근
## 재현 명령과 중간 출력
## 최종 결과의 검증
## 다른 입력에서의 한계''')

write('cloud', 'config.json', json.dumps({'workload': 'training-notes', 'provider': 'fictional', 'storage': {'name': 'training-notes', 'public': True, 'encrypted': False}, 'identity': {'action': '*', 'resource': '*', 'long_lived_key': True}, 'network': {'database_public': True, 'admin_source': '0.0.0.0/0'}, 'audit': {'enabled': False, 'retention_days': 0}}, indent=2))
write('cloud', 'config-reviewed.json', json.dumps({'workload': 'training-notes', 'provider': 'fictional',
    'storage': {'name': 'training-notes', 'public': False, 'encrypted': True},
    'identity': {'action': 'ReadObject', 'resource': 'training-notes', 'long_lived_key': False},
    'network': {'database_public': False, 'admin_source': '192.0.2.0/24'},
    'audit': {'enabled': True, 'retention_days': 30}}, indent=2))
write('cloud', 'audit.csv', '''id,time,actor,action,resource,result
C01,2026-10-20T00:00:00Z,reader,ReadObject,training-notes,Allow
C02,2026-10-20T00:01:00Z,reader,ChangePolicy,training-notes,Deny
C03,2026-10-20T00:02:00Z,deploy-role,ChangePolicy,training-notes,Allow
C04,2026-10-20T00:03:00Z,anonymous,ReadObject,training-notes,Allow''')
write('cloud', 'responsibility.csv', '''control,IaaS_customer,SaaS_customer
physical_datacenter,no,no
guest_os_patch,yes,usually_no
data_classification,yes,yes
identity_access,yes,yes
application_config,yes,service_dependent''')

# Readable authored sources for the expanded labs. Keep these outside generated
# labs/: rebuilding copies the originals before calculating checksums and ZIPs.
for folder in sorted(SOURCES.iterdir()):
    if folder.is_dir():
        for source in sorted(folder.iterdir()):
            if source.is_file():
                write(folder.name, source.name, source.read_text(encoding='utf-8'))

for folder in sorted(ROOT.iterdir()):
    if not folder.is_dir(): continue
    write(folder.name, 'README.md', f'''# Bifrost · {folder.name}
이 묶음은 Bifrost가 직접 만든 교육용 자료입니다. 실제 개인정보·접속 키·운영 로그가 아닙니다.

ZIP을 먼저 풀고 파일을 확인하세요. Python 예제의 기본 환경은 Python 3.10 이상입니다.
기본 예제는 표준 라이브러리만 사용하며, crypto의 aead.py·signature.py만 선택 패키지가 필요합니다.
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3 명령으로 실행합니다.
C 예제는 Ubuntu/WSL의 gcc, gdb, binutils를 기준으로 합니다. 바이너리를 제공하지 않고 소스를 제공합니다.
명령은 각 차시를 따라 실행하세요. 스크립트가 외부 서비스에 접속하거나 클라우드 자원을 만들지는 않습니다.

각 폴더의 모든 파일을 함께 유지하세요. 수정할 때 원본은 보관하고 작업용 사본을 만드세요.
network의 traffic.pcap은 합성 DNS 2개와 TCP/HTTP 6개, 총 8프레임입니다.
별도 tls13.pcap은 메모리 안에서 실제 TLS 1.3 교환을 생성하고 합성 네트워크 헤더를 붙인 표본입니다.
network 정책·cloud 구성은 단순화한 교육 모델입니다. 실제 장비나 공급자에 그대로 적용할 형식이 아닙니다.
crypto의 고전 암호와 XOR 예제는 원리 관찰용이며 실제 보안에 사용하지 않습니다.
자세한 준비·예상 결과·한계·풀이가 제공된 묶음은 LAB-GUIDE.md를 먼저 읽으세요.
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
