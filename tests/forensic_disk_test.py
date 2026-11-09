"""Real FAT12 bytes, independent Sleuth Kit extraction and malformed chains."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'labs/forensic/fat12_lab.py'
spec = importlib.util.spec_from_file_location('fat12_exercise',SOURCE)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

def run(*args):
    return subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8',timeout=30)

class DiskExercise(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)/'evidence'
        result=run(sys.executable,SOURCE,'setup',self.folder)
        self.assertEqual(result.returncode,0,result.stderr)
        self.image=self.folder/'volume.img'
        self.before=self.image.read_bytes()

    def test_real_bpb_directory_offsets_and_fragmented_chain(self):
        data=self.before
        self.assertEqual(len(data),1474560)
        self.assertEqual(data[510:512],b'\x55\xaa')
        self.assertEqual(struct.unpack_from('<H',data,11)[0],512)
        self.assertEqual(data[13],1)
        self.assertEqual(struct.unpack_from('<H',data,17)[0],224)
        self.assertEqual(data[9728:9739],b'README  TXT')
        self.assertEqual(struct.unpack_from('<H',data,9728+26)[0],2)
        self.assertEqual(struct.unpack_from('<I',data,9728+28)[0],1100)
        report=lab.analyse(self.image)[1]
        self.assertEqual(report['geometry']['data_sector'],33)
        self.assertEqual(report['geometry']['cluster_count'],2847)
        self.assertEqual(report['entries'][0]['chain'],[2,5,3])
        self.assertEqual(report['entries'][2]['chain'],[])
        self.assertTrue(report['entries'][3]['deleted'])
        self.assertIsNone(report['entries'][3]['chain'])

    def test_extract_follows_links_and_excludes_slack(self):
        output=self.folder/'result.txt'
        result=run(sys.executable,SOURCE,'extract',self.image,'README.TXT',output)
        self.assertEqual(result.returncode,0,result.stderr)
        expected=(b'BIFROST FAT12 evidence: follow cluster links, not physical order.\n'*20)[:1100]
        self.assertEqual(output.read_bytes(),expected)
        self.assertNotEqual(self.before[16896:16896+1100],expected)
        self.assertNotIn(b'OUTSIDE_FILE_SIZE',output.read_bytes())
        metadata=json.loads(result.stdout)
        self.assertEqual(metadata['sha256'],hashlib.sha256(expected).hexdigest())
        self.assertEqual(self.image.read_bytes(),self.before)
        empty=self.folder/'empty.txt'
        self.assertEqual(run(sys.executable,SOURCE,'extract',self.image,'EMPTY.TXT',empty).returncode,0)
        self.assertEqual(empty.read_bytes(),b'')

    def test_damaged_samples_are_rejected_without_output(self):
        cases={'loop.img':'cycle','early-end.img':'ends before','fat-mismatch.img':'copies differ','truncated.img':'length'}
        for name,message in cases.items():
            with self.subTest(name=name):
                result=run(sys.executable,SOURCE,'inspect',self.folder/name)
                self.assertEqual(result.returncode,2)
                self.assertIn(message,result.stderr)
                output=self.folder/(name+'.txt')
                result=run(sys.executable,SOURCE,'extract',self.folder/name,'README.TXT',output)
                self.assertEqual(result.returncode,2)
                self.assertFalse(output.exists())
        self.assertEqual(self.image.read_bytes(),self.before)

    def test_existing_outputs_and_source_are_never_replaced(self):
        output=self.folder/'keep.txt';output.write_bytes(b'learner work')
        self.assertEqual(run(sys.executable,SOURCE,'extract',self.image,'README.TXT',output).returncode,2)
        self.assertEqual(output.read_bytes(),b'learner work')
        self.assertEqual(run(sys.executable,SOURCE,'extract',self.image,'README.TXT',self.image).returncode,2)
        self.assertEqual(run(sys.executable,SOURCE,'setup',self.folder).returncode,2)
        self.assertEqual(self.image.read_bytes(),self.before)
        self.assertEqual(run(sys.executable,SOURCE,'extract',self.image,'?LDNOTE.TXT',self.folder/'deleted').returncode,2)
        self.assertFalse((self.folder/'deleted').exists())

    def test_label_is_not_type_and_source_generation_is_deterministic(self):
        data=bytearray(self.before);data[54:62]=b'FAT16   '
        variant=self.folder/'misleading.img';variant.write_bytes(data)
        self.assertEqual(lab.analyse(variant)[1]['geometry']['cluster_count'],2847)
        other=Path(self.tmp.name)/'second'
        self.assertEqual(run(sys.executable,SOURCE,'setup',other).returncode,0)
        self.assertEqual((other/'volume.img').read_bytes(),self.before)
        hashes=json.loads((self.folder/'sample-hashes.json').read_text())
        for name,digest in hashes.items():
            self.assertEqual(hashlib.sha256((self.folder/name).read_bytes()).hexdigest(),digest)

    def test_invalid_markers_geometry_and_crosslink(self):
        for marker in [0,1,0xff0,0xff7,3500]:
            data=bytearray(self.before)
            for offset in [512,5120]:
                table=bytearray(data[offset:offset+4608]);lab.set_fat(table,2,marker);data[offset:offset+4608]=table
            path=self.folder/'bad.img';path.write_bytes(data)
            with self.assertRaises(ValueError):lab.analyse(path)
        data=bytearray(self.before);data[510]=0;path.write_bytes(data)
        with self.assertRaises(ValueError):lab.analyse(path)
        data=bytearray(self.before);data[13]=2;path.write_bytes(data)
        with self.assertRaises(ValueError):lab.analyse(path)
        data=bytearray(self.before)
        struct.pack_into('<HI',data,9728+32+26,2,1100)
        path.write_bytes(data)
        with self.assertRaisesRegex(ValueError,'cross-link'):lab.analyse(path)

    @unittest.skipUnless(all(shutil.which(x) for x in ['fsstat','fls','icat']),'Sleuth Kit required (CI/WSL)')
    def test_independent_sleuthkit_detection_listing_and_extraction(self):
        result=run('fsstat',self.image)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('File System Type: FAT12',result.stdout)
        listing=run('fls',self.image)
        self.assertEqual(listing.returncode,0,listing.stderr)
        inode=re.search(r'r/r (\d+):\s+README\.TXT',listing.stdout)
        self.assertIsNotNone(inode,listing.stdout)
        result=subprocess.run(['icat','-f','fat12',str(self.image),inode[1]],capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        output=self.folder/'python-result.txt'
        self.assertEqual(run(sys.executable,SOURCE,'extract',self.image,'README.TXT',output).returncode,0)
        self.assertEqual(result.stdout,output.read_bytes())
        self.assertIn('EVIDENCE.TXT',listing.stdout)
        self.assertIn('_LDNOTE.TXT',listing.stdout)

if __name__=='__main__':unittest.main(verbosity=2)
