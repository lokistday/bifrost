"""Execute bridge exercises against independent expected values, including GDB."""
from pathlib import Path
import ctypes
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'labs'

def run(*args, cwd=None):
    return subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=45)

def compile_c(source, output, *extra):
    result = run('gcc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-g', '-O0', *extra, source, '-o', output)
    if result.returncode: raise AssertionError(result.stdout + result.stderr)

class CollectionsBridge(unittest.TestCase):
    def test_prediction_and_learner_completion(self):
        result = run(sys.executable, LAB/'foundation/collections_predict.py')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'first=alice\nmissing=UNKNOWN\ndenied=bob,kim\n')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ['collections_check.py', 'collections_practice.py']:
                shutil.copyfile(LAB/'foundation'/name, folder/name)
            result = run(sys.executable, '-B', 'collections_check.py', cwd=folder)
            self.assertEqual(result.returncode, 1)
            self.assertIn('NOT YET', result.stdout)
            shutil.copyfile(LAB/'foundation/collections_reference.py', folder/'collections_practice.py')
            result = run(sys.executable, '-B', 'collections_check.py', cwd=folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('3 cases passed', result.stdout)

@unittest.skipUnless(shutil.which('gcc'), 'GCC needed; execute under Linux/WSL')
class NativeBridges(unittest.TestCase):
    def test_c_basics_and_changed_array_and_string(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'basics.c'; binary=Path(tmp)/'basics'
            original=(LAB/'foundation/c_basics.c').read_text(encoding='utf-8')
            source.write_text(original,encoding='utf-8');compile_c(source,binary)
            self.assertEqual(run(binary).stdout, 'count=3 first=2 sum=15\ncapacity=4 text_length=3 terminator=0\n')
            source.write_text(original.replace('{2, 5, 8}', '{3, 6, 9, 12}').replace('"LAB"', '"HI"').replace('(int)label[3]', '(int)label[2]'),encoding='utf-8')
            compile_c(source,binary)
            self.assertEqual(run(binary).stdout, 'count=4 first=3 sum=30\ncapacity=3 text_length=2 terminator=0\n')

    def test_call_bridge_and_one_condition_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'call.c';binary=Path(tmp)/'call'
            original=(LAB/'pwn/call_bridge.c').read_text(encoding='utf-8')
            for text,answer in [(original,20),(original.replace('base + 3','base + 4'),22)]:
                source.write_text(text,encoding='utf-8');compile_c(source,binary,'-fno-omit-frame-pointer')
                self.assertEqual(run(binary).stdout, f'BIFROST value=7 answer={answer}\n')

    @unittest.skipUnless(shutil.which('gdb') and platform.machine().lower() in ('x86_64','amd64'), 'x86-64 GDB required')
    def test_real_gdb_frames_saved_return_and_register_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'call';compile_c(LAB/'pwn/call_bridge.c',binary,'-fno-omit-frame-pointer')
            commands=['set pagination off','break adjust','run','info args','bt','frame 1','print value','frame 0',
                      'next','printf "BUMP=%d\\n", bumped','next','printf "RESULT=%d\\n", result',
                      'info frame','printf "SAVED=%p\\n", *(void **)($rbp+8)',
                      'finish','printf "RETURN=%d\\n", $eax','next','printf "ANSWER=%d\\n", answer','continue']
            args=['gdb','-q','-nx','-batch']
            for cmd in commands:args+=['-ex',cmd]
            result=run(*args,binary)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            for value in ['base = 7','BUMP=10','RESULT=20','RETURN=20','ANSWER=20']:
                self.assertIn(value,result.stdout)
            self.assertRegex(result.stdout,r'#0\s+adjust')
            self.assertRegex(result.stdout,r'#1\s+.*main')
            saved=re.search(r'saved rip = (0x[0-9a-f]+)',result.stdout)
            slot=re.search(r'SAVED=(0x[0-9a-f]+)',result.stdout)
            self.assertIsNotNone(saved,result.stdout);self.assertIsNotNone(slot,result.stdout)
            self.assertEqual(int(saved[1],16),int(slot[1],16))

    @unittest.skipUnless(platform.machine().lower() in ('x86_64','amd64'), 'x86-64 assembly only')
    def test_assembly_flags_boundaries_and_unsigned_wrap(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'trace';shared=Path(tmp)/'trace.so'
            result=run('gcc','-Wall','-Wextra','-Werror',LAB/'rev/trace_driver.c',LAB/'rev/trace_steps.s','-o',binary)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(run(binary).stdout,'x=5 result=9\nx=7 result=11\nx=8 result=9\n')
            result=run('gcc','-shared','-fPIC',LAB/'rev/trace_steps.s','-o',shared)
            self.assertEqual(result.returncode,0,result.stderr)
            f=ctypes.CDLL(str(shared)).trace_steps;f.argtypes=[ctypes.c_uint];f.restype=ctypes.c_uint
            for value,expected in [(0,2),(6,8),(7,11),(8,9),(9,10),(0xfffffffd,1),(0xffffffff,3)]:
                self.assertEqual(f(value),expected)

    @unittest.skipUnless(shutil.which('strip') and shutil.which('nm'), 'binutils required')
    def test_stripped_challenge_inputs_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'challenge'
            result=run(sys.executable,LAB/'rev/build_blind.py',folder)
            self.assertEqual(result.returncode,0,result.stderr)
            binary=folder/'mystery';before=binary.read_bytes()
            symbols=run('nm',binary)
            self.assertNotRegex(symbols.stdout,r'\b(gate|main)$')
            for value,expected in [('KKK7','accept'),('KJL7','accept'),('KAA7','reject'),('KJF7','reject'),('KKK8','reject'),('XKK7','reject'),('KKK77','reject'),('','reject')]:
                result=run(binary,value);self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(result.stdout.strip(),expected,value)
            self.assertEqual(run(binary).returncode,2)
            self.assertEqual(run(sys.executable,LAB/'rev/build_blind.py',folder).returncode,2)
            self.assertEqual(binary.read_bytes(),before)

if __name__ == '__main__': unittest.main(verbosity=2)
