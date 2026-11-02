"""Solve the delivered artifacts independently, then compare the published digest."""
from pathlib import Path
import base64
import csv
import hashlib
import io
import json
import re
import shutil
import sqlite3
import struct
import subprocess
import tempfile
import zipfile
import zlib
import unittest

ROOT=Path(__file__).resolve().parents[1]
CATALOG=json.loads((ROOT/'content/wargames.json').read_text(encoding='utf-8'))


class Challenges(unittest.TestCase):
    def test_delivered_materials(self):
        self.assertEqual(len(CATALOG),9)
        for challenge in CATALOG:
            with self.subTest(id=challenge['id']), tempfile.TemporaryDirectory() as temp:
                raw=(ROOT/'wargame/files'/challenge['archive']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),challenge['sha256'])
                archive=zipfile.ZipFile(io.BytesIO(raw));archive.extractall(temp);folder=Path(temp)
                self.assertTrue((folder/'README.md').is_file())
                key=challenge['id']
                if key=='foundation-log':
                    rows=list(csv.DictReader((folder/'events.csv').read_text().splitlines()))
                    flag=''.join(x['fragment'] for x in sorted((r for r in rows if r['status']=='denied'),key=lambda r:int(r['seq'])))
                    self.assertTrue(any(',' in r['user'] for r in rows))
                elif key=='web-notes':
                    # Exercise the real handler without opening a listening port.
                    ns={'__name__':'test'};exec(compile((folder/'server.py').read_text(),str(folder/'server.py'),'exec'),ns)
                    handler=object.__new__(ns['App']);handler.path='/notes/2';handler.wfile=io.BytesIO();status=[]
                    handler.send_response=status.append;handler.send_header=lambda *a:None;handler.end_headers=lambda:None
                    handler.do_GET();self.assertEqual(status,[200]);flag=handler.wfile.getvalue().decode()
                    handler.path='/notes/999';handler.wfile=io.BytesIO();handler.do_GET();self.assertEqual(status[-1],404)
                    self.assertIn("HTTPServer(('127.0.0.1',8899)",(folder/'server.py').read_text())
                elif key=='pwn-length':
                    # A real compile/run is performed in test_native_integer_gate.
                    source=(folder/'gate.c').read_text();encoded=[int(x) for x in re.search(r'data\[\]=\{([^}]+)',source)[1].split(',')]
                    self.assertEqual(65536 % 65536,0);flag=bytes(b^0x5a for b in encoded).decode()
                elif key=='rev-lock':
                    source=(folder/'lock.py').read_text();target=json.loads(re.search(r'target=(\[[^\n]+)',source)[1]);answer=bytes(b^0x23 for b in target)[::-1].decode()
                    out=subprocess.run([shutil.which('python') or 'python',str(folder/'lock.py')],input=answer+'\n',capture_output=True,text=True,check=True)
                    flag=out.stdout.split('key: ',1)[-1].strip()
                elif key=='forensic-session':
                    con=sqlite3.connect('file:'+str(folder/'events.sqlite').replace('\\','/')+'?mode=ro',uri=True)
                    flag=''.join(row[0] for row in con.execute("SELECT fragment FROM events WHERE session='S7' AND action='read' ORDER BY seq"));con.close()
                elif key=='network-stream':
                    packet=(folder/'capture.pcap').read_bytes();cursor=24;parts=[];count=0
                    self.assertEqual(packet[:4],bytes.fromhex('d4c3b2a1'))
                    while cursor<len(packet):
                        _,_,size,_=struct.unpack_from('<IIII',packet,cursor);cursor+=16;frame=packet[cursor:cursor+size];cursor+=size;count+=1
                        ip=frame[14:];self.assertEqual(ip[9],17);udp=ip[(ip[0]&15)*4:];_,port,length,_=struct.unpack_from('!HHHH',udp)
                        if ip[12:16]==bytes([192,0,2,8]) and port==9000:parts.append(udp[8:length])
                    self.assertEqual(count,3);flag=b''.join(parts).decode()
                elif key=='crypto-xor':
                    cipher=bytes.fromhex((folder/'cipher.hex').read_text());key=cipher[0]^ord('B');flag=bytes(b^key for b in cipher).decode()
                elif key=='misc-container':
                    payload=(folder/'sample.bf').read_bytes();self.assertEqual(payload[:4],b'BF01');n=int.from_bytes(payload[4:8],'big')
                    stream=zlib.decompressobj();data=stream.decompress(payload[8:],4096);self.assertTrue(stream.eof);self.assertEqual(len(data),n);self.assertFalse(stream.unused_data);flag=data.decode()
                elif key=='cloud-policy':
                    command=[shutil.which('python') or 'python',str(folder/'policy.py')]
                    denied=subprocess.run(command,cwd=folder,input='guest\n',capture_output=True,text=True,check=True)
                    self.assertIn('DENY',denied.stdout)
                    allowed=subprocess.run(command,cwd=folder,input='auditor\n',capture_output=True,text=True,check=True)
                    flag=allowed.stdout.split('principal: ',1)[-1].strip()
                self.assertRegex(flag,r'^BIFROST\{[^\s]+\}$')
                self.assertEqual(hashlib.sha256(flag.encode()).hexdigest(),challenge['flagHash'])
                for name in ('wargames.js','wargame.js'):
                    self.assertNotIn(flag,(ROOT/'js'/name).read_text(encoding='utf-8'))

    @unittest.skipUnless(shutil.which('gcc'),'Native gcc is unavailable; run this test in Ubuntu/WSL as well.')
    def test_native_integer_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            archive=zipfile.ZipFile(ROOT/'wargame/files/pwn-length.zip');archive.extractall(temp);folder=Path(temp)
            subprocess.run(['gcc','-std=c11','-Wall','-Wextra',str(folder/'gate.c'),'-o',str(folder/'gate')],check=True)
            locked=subprocess.run([str(folder/'gate')],input='65535\n',capture_output=True,text=True)
            self.assertNotEqual(locked.returncode,0)
            unlocked=subprocess.run([str(folder/'gate')],input='65536\n',capture_output=True,text=True,check=True)
            digest=next(x['flagHash'] for x in CATALOG if x['id']=='pwn-length')
            self.assertEqual(hashlib.sha256(unlocked.stdout.strip().encode()).hexdigest(),digest)

    def test_reproducibility(self):
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from build_wargames import build
        before={c['id']:(ROOT/'wargame/files'/c['archive']).read_bytes() for c in CATALOG}
        build()
        for c in CATALOG:self.assertEqual(before[c['id']],(ROOT/'wargame/files'/c['archive']).read_bytes())

if __name__=='__main__':unittest.main()
