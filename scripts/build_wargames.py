"""Deterministic, account-free practice artifacts. Flags are educational, not secrets."""
from pathlib import Path
import base64
import csv
import hashlib
import io
import json
import socket
import sqlite3
import struct
import tempfile
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]


def build():
    target = ROOT/'wargame'/'files'
    target.mkdir(parents=True, exist_ok=True)
    records = []

    def add(key, title, course, level, description, objective, files, flag, hints, related, solution):
        readme = f'# {title}\n\n{description}\n\n목표: {objective}\n\n이 ZIP 안의 교육용 표본만 사용합니다. 원본을 보관하고 작업 사본에서 진행하세요.\nFLAG 형식: BIFROST{{...}}\n실행 중인 외부 서비스나 타인의 자료는 대상이 아닙니다.\n'
        files = {'README.md':readme.encode(), **{name:data.encode() if isinstance(data,str) else data for name,data in files.items()}}
        filename = key+'.zip'
        # Store tiny fixtures uncompressed so zlib versions cannot change ZIP hashes.
        with zipfile.ZipFile(target/filename,'w',compression=zipfile.ZIP_STORED) as archive:
            for name,data in sorted(files.items()):
                info=zipfile.ZipInfo(name, date_time=(2026,1,1,0,0,0));info.create_system=3;info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o100644<<16
                archive.writestr(info,data)
        records.append(dict(id=key,title=title,course=course,level=level,description=description,objective=objective,
            archive=filename,sha256=hashlib.sha256((target/filename).read_bytes()).hexdigest(),flagHash=hashlib.sha256(flag.encode()).hexdigest(),
            hints=hints,lessons=related,solution=solution))

    flag='BIFROST{csv_records_not_commas}'
    add('foundation-log','쉼표 뒤에 숨은 기록','foundation','입문',
        '감사 로그에서 status=denied인 레코드만 골라 seq 순서대로 fragment를 이어 붙이세요. 따옴표 안의 쉼표는 열 구분자가 아닙니다.',
        'CSV를 올바르게 읽고 조건에 맞는 기록을 정렬해 FLAG를 복원합니다.',
        {'events.csv':'seq,user,status,fragment\n3,"lee, min",denied,not_commas}\n1,alice,denied,BIFROST{csv_\n2,bob,ok,decoy\n2,bob,denied,records_\n'},flag,
        ['먼저 csv 모듈의 DictReader로 각 레코드를 출력하세요.','status가 denied인 레코드만 남기고 seq를 정수로 정렬합니다.','fragment를 공백 없이 이어 붙입니다. user의 쉼표를 split으로 나누지 마세요.'],
        ['foundation.python-files','foundation.python-flow'], 'DictReader → denied 필터 → int(seq) 정렬 → fragment 결합. 거부 기록은 세 개이며 OK 기록의 decoy를 제외합니다.')

    flag='BIFROST{object_scope_is_server_side}'
    encoded=base64.b64encode(flag.encode()).decode()
    server=f'''# Python 3.10+ · localhost only. Deliberately missing an ownership check.
from http.server import BaseHTTPRequestHandler, HTTPServer
import base64
class App(BaseHTTPRequestHandler):
    def do_GET(self):
        notes = {{'/notes/1': b'alice: shopping list', '/notes/2': base64.b64decode({encoded!r})}}
        body = notes.get(self.path,b'not found')
        self.send_response(200 if self.path in notes else 404)
        self.send_header('Content-Type','text/plain; charset=utf-8');self.end_headers();self.wfile.write(body)
if __name__=='__main__':
    print('Training app: http://127.0.0.1:8899/notes/1 ; stop with Ctrl+C')
    HTTPServer(('127.0.0.1',8899),App).serve_forever()
'''
    add('web-notes','다른 사람의 노트','web','입문',
        'ZIP의 server.py를 python3 server.py(Windows: py -3 server.py)로 실행하고 /notes/1을 여세요. 주소의 숫자를 바꾸면 다른 사용자의 노트가 보이는지 확인하세요. 종료는 Ctrl+C입니다.',
        '객체 식별자와 소유자 인가의 차이를 설명하고 유출된 FLAG를 찾습니다.',{'server.py':server},flag,
        ['127.0.0.1:8899는 직접 실행한 내 컴퓨터의 실습 서버입니다.','/notes/1의 숫자를 바꾸어 응답을 비교하세요.','찾은 뒤 소유자를 확인하지 않는 do_GET의 위치를 찾아 수정 방향을 적으세요.'],
        ['web.authorization','web.sessions'],'/notes/2에서 FLAG를 얻습니다. 실제 수정에는 신뢰한 세션 주체와 노트 소유자를 서버에서 비교하는 검사가 필요합니다. URL을 숨기는 것으로 해결되지 않습니다.')

    flag='BIFROST{narrow_cast_wide_input}'
    masked=','.join(str(b^0x5a) for b in flag.encode())
    c=f'''#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>
int main(void) {{
    uint32_t requested=0;
    if(scanf("%" SCNu32,&requested)!=1) return 1;
    uint16_t accepted=(uint16_t)requested;
    if(requested>65535 && accepted==0) {{
        unsigned char data[]={{{masked}}};
        for(size_t i=0;i<sizeof data;i++) putchar(data[i]^0x5a);
        putchar('\\n');return 0;
    }}
    puts("locked");return 1;
}}
'''
    add('pwn-length','좁아지는 길이','pwn','기초',
        'Ubuntu/WSL의 GCC로 gate.c를 gcc -std=c11 -Wall -Wextra gate.c -o gate로 빌드합니다. ./gate에 정수 하나를 입력해 requested는 크지만 accepted는 0이 되게 하세요. 메모리 손상은 일으키지 않는 정수 변환 모형입니다.',
        '32비트 입력을 16비트로 줄일 때의 값 변화를 계산해 FLAG를 출력합니다.',{'gate.c':c},flag,
        ['uint16_t가 표현할 수 있는 정수 범위를 계산하세요.','unsigned 변환 후에는 2의 16제곱을 기준으로 값이 남습니다.','65536을 입력한 경우를 종이에 계산한 뒤 실행하세요.'],
        ['pwn.integer-input','pwn.allocation-size'],'65536은 uint16_t로 변환하면 0입니다. 원래 크기를 검증한 뒤 변환해야 합니다. 이 문제는 임의 코드 실행을 재현하는 문제가 아닙니다.')

    flag='BIFROST{reverse_the_transform}'
    lock='BRIDGE'
    reverse=f'''import base64
target={list(bytes(b^0x23 for b in lock.encode()[::-1]))!r}
key=input('key: ')
if [b^0x23 for b in key.encode()[::-1]]==target:
    print(base64.b64decode({base64.b64encode(flag.encode()).decode()!r}).decode())
else:
    print('locked')
'''
    add('rev-lock','변환을 거꾸로','rev','기초','python3 lock.py로 프로그램을 실행하세요. 비교 직전의 바이트 변환을 역으로 적용해 올바른 key를 찾아 입력하세요.',
        '역순과 XOR의 역연산으로 입력을 복원합니다.',{'lock.py':reverse},flag,
        ['비교 대상은 평문 문자열이 아니라 변환된 바이트 목록입니다.','XOR 0x23을 다시 적용하면 원래 바이트가 됩니다.','XOR을 되돌린 뒤 바이트 순서를 뒤집고 ASCII로 읽으세요.'],
        ['rev.static','rev.data-flow'],'비교 목록의 각 값에 0x23을 XOR하고 역순으로 읽으면 BRIDGE입니다. 입력해 출력된 FLAG를 제출합니다.')

    flag='BIFROST{ordered_evidence_not_guess}'
    with tempfile.TemporaryDirectory() as temp:
        db=Path(temp)/'events.sqlite';con=sqlite3.connect(db)
        con.execute('CREATE TABLE events(seq INTEGER, session TEXT, action TEXT, fragment TEXT)')
        con.executemany('INSERT INTO events VALUES(?,?,?,?)',[(3,'S7','read','not_guess}'),(1,'S7','read','BIFROST{ordered_'),(2,'S9','read','wrong'),(2,'S7','read','evidence_'),(4,'S7','deny','decoy')]);con.commit();con.close();dbbytes=bytearray(db.read_bytes())
        # Header bytes 96..99 identify the writer's SQLite build, not schema/data.
        dbbytes[96:100]=bytes(4)
        dbbytes=bytes(dbbytes)
    add('forensic-session','S7 세션의 흔적','forensic','기초','실제 SQLite 파일 events.sqlite에서 session=S7이며 action=read인 기록의 fragment를 seq 순서로 복원하세요. 원본 복사본을 읽기 전용으로 조사하세요.',
        'SQL 필터와 순서를 근거로 FLAG를 복원합니다.',{'events.sqlite':dbbytes},flag,
        ['Python sqlite3 또는 SQLite 도구로 events 테이블을 확인하세요.','WHERE session=\'S7\' AND action=\'read\' 조건이 필요합니다.','ORDER BY seq를 적용하고 fragment만 결합하세요. 파일에 보이는 문자열 순서와 사건 순서를 혼동하지 마세요.'],
        ['forensic.browser-sqlite','forensic.timeline'],'SELECT fragment FROM events WHERE session=\'S7\' AND action=\'read\' ORDER BY seq. 관찰된 세션 기록에서 복원했으며 실제 사용자 의도까지 증명하지 않습니다.')

    flag='BIFROST{follow_the_cleartext_stream}'
    # Classic PCAP containing Ethernet/IPv4/UDP frames. UDP checksum 0 is allowed in IPv4.
    header=struct.pack('<IHHIIII',0xa1b2c3d4,2,4,0,0,65535,1);frames=[]
    pieces=[('noise',b'not-this-flow'),('wanted',flag[:18].encode()),('wanted',flag[18:].encode())]
    for i,(kind,payload) in enumerate(pieces):
        src='192.0.2.8' if kind=='wanted' else '192.0.2.99';udp=struct.pack('!HHHH',4444,9000,8+len(payload),0)+payload
        ip=bytearray(struct.pack('!BBHHHBBH4s4s',0x45,0,20+len(udp),i,0,64,17,0,socket.inet_aton(src),socket.inet_aton('192.0.2.10')))
        total=sum(struct.unpack('!10H',ip));total=(total&65535)+(total>>16);total=(total&65535)+(total>>16);ip[10:12]=struct.pack('!H',(~total)&65535)
        packet=bytes.fromhex('0200000000020200000000010800')+ip+udp;frames.append(struct.pack('<IIII',1700000000+i,0,len(packet),len(packet))+packet)
    add('network-stream','두 패킷의 메시지','network','기초','Wireshark에서 capture.pcap을 열고 192.0.2.8에서 목적지 UDP 9000으로 보낸 페이로드를 순서대로 읽으세요. 모두 합성 문서용 주소이며 실제 통신은 하지 않습니다.',
        '출발지·포트 필터와 페이로드 순서를 이용해 FLAG를 복원합니다.',{'capture.pcap':header+b''.join(frames)},flag,
        ['ip.src == 192.0.2.8 && udp.dstport == 9000으로 필터링합니다.','UDP 상세 아래 Data 또는 Follow UDP Stream을 확인하세요.','선택한 두 프레임의 데이터만 시간 순서대로 결합합니다.'],
        ['network.pcap','network.transport'],'지정된 출발지의 두 UDP 데이터 조각을 이어 붙입니다. 다른 출발지의 noise는 제외합니다. 암호화되지 않은 UDP 표본입니다.')

    flag='BIFROST{xor_is_not_encryption_security}'
    add('crypto-xor','한 바이트의 열쇠','crypto','입문','cipher.hex는 ASCII 메시지의 모든 바이트에 같은 1바이트 키를 XOR한 결과입니다. 메시지가 BIFROST{로 시작한다는 단서를 이용하세요. 실제 보안 암호화가 아닌 고전적인 모형입니다.',
        '알려진 평문의 첫 바이트로 XOR 키를 구하고 전체 메시지를 복원합니다.',{'cipher.hex':bytes(b^0x37 for b in flag.encode()).hex()+'\n'},flag,
        ['bytes.fromhex로 hex 문자열을 바이트로 바꿉니다.','첫 암호 바이트 XOR ord(\'B\')가 키입니다.','구한 키를 모든 바이트에 XOR하고 ASCII로 읽습니다.'],
        ['crypto.representation','crypto.classical'],'키는 0x37입니다. bytes(b ^ key for b in cipher)를 복호합니다. Base64·XOR과 현대 인증 암호의 보장을 구분하세요.')

    flag='BIFROST{check_length_before_unpack}'
    plain=flag.encode()
    packed=b'\x78\x01\x01'+struct.pack('<HH',len(plain),len(plain)^0xffff)+plain+struct.pack('!I',zlib.adler32(plain))
    add('misc-container','작은 컨테이너','misc','기초','sample.bf의 형식은 BF01(4바이트), 압축 전 길이(4바이트 big-endian), zlib 데이터입니다. 길이를 읽고 본문을 최대 4096바이트로 제한해 해제하세요.',
        '헤더·길이·압축 본문의 경계를 읽어 FLAG를 복원합니다.',{'sample.bf':b'BF01'+struct.pack('!I',len(flag))+packed},flag,
        ['파일 전체를 UTF-8로 읽지 말고 read_bytes로 읽으세요.','int.from_bytes(raw[4:8],\'big\')가 선언 길이입니다.','raw[8:]을 decompressobj().decompress(data,4096)로 해제하고 eof·길이·남은 데이터를 확인하세요.'],
        ['misc.bounded-decompression','foundation.text-bytes'],'magic 확인 → big-endian 길이 → 한도 있는 zlib 해제 → 길이·eof 확인. 출력 한도가 있다는 이유만으로 모든 파일을 안전하게 처리한다고 일반화하지 않습니다.')

    flag='BIFROST{explicit_deny_before_allow}'
    config={'rules':[{'effect':'Allow','principal':'*','action':'read','resource':'training'},{'effect':'Deny','principal':'guest','action':'read','resource':'training'}], 'object':{'resource':'training','body':base64.b64encode(flag.encode()).decode()}}
    policy='''import json,base64
from fnmatch import fnmatchcase
policy=json.load(open('policy.json',encoding='utf-8'))
principal=input('principal: ')
matches=[r for r in policy['rules'] if fnmatchcase(principal,r['principal']) and r['action']=='read' and r['resource']=='training']
if any(r['effect']=='Deny' for r in matches): print('DENY')
elif any(r['effect']=='Allow' for r in matches): print(base64.b64decode(policy['object']['body']).decode())
else: print('DENY')
'''
    add('cloud-policy','허용 뒤의 거부','cloud','입문','policy.json과 policy.py는 명시적 거부를 우선하는 작은 로컬 정책 모형입니다. python3 policy.py를 실행해 guest와 auditor의 차이를 비교하고, 읽을 수 있는 주체로 FLAG를 얻으세요.',
        '명시적 거부와 넓은 허용의 조합을 설명합니다. 실제 클라우드 계정은 사용하지 않습니다.',{'policy.json':json.dumps(config,indent=2),'policy.py':policy},flag,
        ['규칙 순서가 아니라 매칭된 Deny의 존재를 먼저 확인하세요.','guest에는 Allow와 Deny가 모두 매칭됩니다.','auditor로 읽기를 시도한 뒤 왜 다른 결과인지 설명하세요.'],
        ['cloud.iam','cloud.effective-permissions'],'auditor는 Allow만 매칭되어 FLAG가 나옵니다. guest는 Deny 때문에 거부됩니다. 이 엔진이 특정 공급자의 전체 정책 평가를 구현한 것은 아닙니다.')
    (ROOT/'content/wargames.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (ROOT/'js/wargames.js').write_text('/* Generated practice catalog: no plaintext flags. */\nwindow.BifrostWargames='+json.dumps({x['id']:{k:x[k] for k in ('id','title','course','flagHash')} for x in records},ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8',newline='\n')
    return records

if __name__=='__main__':
    print(f'Built {len(build())} practice challenges.')
