import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'scripts/lab_sources/forensic'
spec = importlib.util.spec_from_file_location('signature_lab', SRC/'signature_lab.py')
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
DATA = {k:bytes.fromhex(v) for k,v in json.loads((SRC/'signature-fixtures.json').read_text()).items()}

class Signatures(unittest.TestCase):
    def test_real_png_and_carving(self):
        end, chunks = lab.png_end(DATA['image.png'])
        self.assertEqual(end, len(DATA['image.png']))
        self.assertEqual(chunks[0], b'IHDR')
        self.assertEqual(chunks[-1], b'IEND')
        start = DATA['mixed.bin'].index(lab.MAGIC)
        self.assertEqual(start, 17)
        end, _ = lab.png_end(DATA['mixed.bin'], start)
        self.assertEqual(DATA['mixed.bin'][start:end], DATA['image.png'])
        self.assertEqual(DATA['renamed.txt'], DATA['image.png'])

    def test_every_truncation_is_rejected(self):
        data = DATA['image.png']
        for n in range(len(data)):
            with self.subTest(n=n), self.assertRaises(ValueError):
                lab.png_end(data[:n])

    def test_crc_and_missing_chunks(self):
        for name in ['bad-crc.png','prefix-only.png','truncated.png']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                lab.png_end(DATA[name])

if __name__ == '__main__':
    unittest.main()
