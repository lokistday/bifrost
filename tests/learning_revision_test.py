"""Independent final-project results, invalid inputs, packaging and native code."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile
from contextlib import closing

ROOT=Path(__file__).resolve().parents[1]
LABS=ROOT/'labs'
ENV={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1'}


def run(track,*args,cwd=None):
    return subprocess.run([sys.executable,*args],cwd=cwd or LABS/track,env=ENV,
                          capture_output=True,text=True,encoding='utf-8',timeout=40)


EXPECTED={
 'foundation':[
  dict(total=6,valid=4,denied=3,denied_users=['bob','lee, min'],invalid_rows=[6,7]),
  dict(total=7,valid=5,denied=2,denied_users=['dana','eve'],invalid_rows=[6,7])],
 'web':[
  dict(outcomes=['RESERVED','REPLAY','CONFLICT','UNAUTHENTICATED','OUT_OF_STOCK'],stock=2,orders=1),
  dict(outcomes=['RESERVED','RESERVED','UNAUTHENTICATED','REPLAY','RESERVED'],stock=0,orders=3)],
 'pwn':[
  dict(accepted_ids=['P1','P3'],payload_sum=131,nul_ids=['P1']),
  dict(accepted_ids=['P7','P8','P9'],payload_sum=167,nul_ids=['P8'])],
 'rev':[
  dict(states=[0,1,1,1,0,0],accepted=3),dict(states=[1,1,0,0,1,1,1],accepted=5)],
 'forensic':[
  dict(timeline=['E1','E3'],reads=['E3'],suspect_actor='UNKNOWN'),
  dict(timeline=['E5','E1'],reads=[],suspect_actor='UNKNOWN')],
 'network':[
  dict(decisions=['ALLOW','ALLOW','DENY','DENY','DENY','DENY'],TP=1,FP=1,FN=1),
  dict(decisions=['ALLOW','ALLOW','DENY','ALLOW','DENY','DENY'],TP=2,FP=0,FN=1)],
 'crypto':[
  dict(outcomes=['AUTH_FAIL','ACCEPT','REPLAY','AUTH_FAIL','ACCEPT'],last=2),
  dict(outcomes=['ACCEPT','AUTH_FAIL','REPLAY','ACCEPT'],last=6)],
 'misc':[
  dict(outcomes=['ACCEPT','ACCEPT','REJECT','REJECT','REJECT'],hashes=[hashlib.sha256(x).hexdigest() for x in [b'Bifrost',b'A'*16]]),
  dict(outcomes=['ACCEPT','ACCEPT','REJECT','REJECT','REJECT'],hashes=[hashlib.sha256(x).hexdigest() for x in [b'',b'new case']])],
 'cloud':[
  dict(rbac=[False,False,False,True],private=['ALLOW_MODEL','PUBLIC_PATH','DENY_IDENTITY','DENY_ENDPOINT_POLICY'],leases=['ALLOW_MODEL','DENY_TIME','DENY_SCOPE']),
  dict(rbac=[True,False,False,False],private=['ALLOW_MODEL','PUBLIC_PATH','DENY_IDENTITY','DENY_ENDPOINT_POLICY'],leases=['DENY_REVOKED']*3)]}


class ProjectResults(unittest.TestCase):
    def test_all_projects_match_independently_calculated_results_and_reject_wrong_answers(self):
        with tempfile.TemporaryDirectory(prefix='bifrost-project-answers-') as tmp:
            answer=Path(tmp)/'answer.json'
            for track,variants in EXPECTED.items():
                if track=='crypto' and importlib.util.find_spec('cryptography') is None:
                    self.fail('Install the pinned crypto dependency to verify all projects')
                for variant,expected in zip('ab',variants):
                    with self.subTest(track=track,variant=variant):
                        result=run(track,'project.py','example','--variant',variant)
                        self.assertEqual(result.returncode,0,result.stderr)
                        self.assertEqual(json.loads(result.stdout),expected)
                        answer.write_text(json.dumps(expected),encoding='utf-8')
                        self.assertEqual(run(track,'project.py','check',str(answer),'--variant',variant).returncode,0)
                        wrong={**expected,'not_a_real_result':True}
                        answer.write_text(json.dumps(wrong),encoding='utf-8')
                        result=run(track,'project.py','check',str(answer),'--variant',variant)
                        self.assertEqual(result.returncode,1)
                        self.assertNotIn('RESULT MATCH',result.stdout)
                        answer.write_text(json.dumps(EXPECTED[track][0]),encoding='utf-8')
                        self.assertEqual(run(track,'project.py','check',str(answer),'--variant','b').returncode,1,
                                         'A answers must not pass the different B input')

    def test_answer_type_mismatch_and_hostile_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'answer.json'
            correct=EXPECTED['foundation'][0]
            p.write_text(json.dumps({**correct,'total':True}),encoding='utf-8')
            self.assertEqual(run('foundation','project.py','check',str(p)).returncode,1)
            for text in ['{','{"total":1,"total":2}','[NaN]','[1e999]','['*10000+']'*10000,'"'+'x'*262144+'"','"'+'x'*9000+'"','{"n":'+'9'*10000+'}']:
                p.write_text(text,encoding='utf-8')
                result=run('foundation','project.py','check',str(p))
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertNotIn('Traceback',result.stderr)

    def test_crypto_sequence_is_authenticated_and_invalid_record_does_not_advance_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'crypto'; shutil.copytree(LABS/'crypto',folder)
            p=folder/'project-input-a.json'; rows=json.loads(p.read_text())
            rows[1]['seq']=50000  # A valid ciphertext cannot authorize a changed sequence.
            p.write_text(json.dumps(rows),encoding='utf-8')
            result=run('crypto','project.py','example',cwd=folder)
            self.assertEqual(result.returncode,0,result.stderr)
            result=json.loads(result.stdout)
            self.assertEqual(result['outcomes'][1],'AUTH_FAIL')
            self.assertEqual(result['outcomes'][2],'ACCEPT')
            self.assertEqual(result['last'],2)

    def test_sqlite_artifact_is_real_readable_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'forensic'; shutil.copytree(LABS/'forensic',folder)
            for variant in 'ab':
                result=run('forensic','project-build-db.py','--variant',variant,cwd=folder)
                self.assertEqual(result.returncode,0,result.stderr)
                p=folder/f'project-{variant}.sqlite'
                self.assertTrue(p.read_bytes().startswith(b'SQLite format 3\0'))
                with closing(sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)) as db:
                    rows=db.execute("SELECT id FROM events WHERE host=? AND session=? ORDER BY julianday(at),id",('lab-1','S7')).fetchall()
                self.assertEqual([r[0] for r in rows],EXPECTED['forensic']['ab'.index(variant)]['timeline'])
                before=p.read_bytes()
                self.assertNotEqual(run('forensic','project-build-db.py','--variant',variant,cwd=folder).returncode,0)
                self.assertEqual(p.read_bytes(),before)

    @unittest.skipUnless(shutil.which('gcc'),'GCC required (CI/WSL runs this)')
    def test_native_parser_contract_reference_and_faulty_starter(self):
        result=run('pwn','project-c-tests.py','--source','project-parser-reference.c','--sanitize')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        result=run('pwn','project-c-tests.py','--source','project-parser-starter.c')
        self.assertNotEqual(result.returncode,0,'Incomplete starter must fail the positive cases')

    @unittest.skipUnless(shutil.which('gcc'),'GCC required (CI/WSL runs this)')
    def test_reverse_native_machine_matches_recovered_transitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'machine'
            for option in ['-O0','-O2']:
                subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror',option,str(LABS/'rev/project-machine.c'),'-o',str(output)],check=True,capture_output=True,timeout=30)
                for variant,expected in zip('ab',EXPECTED['rev']):
                    source=json.loads((LABS/f'rev/project-input-{variant}.json').read_text())
                    result=subprocess.run([str(output),*source['tokens']],check=True,capture_output=True,text=True,timeout=5)
                    values=[int(line.split('=')[1]) for line in result.stdout.splitlines()]
                    self.assertEqual(values[:-1],expected['states'])
                    self.assertEqual(values[-1],expected['accepted'])


class InputFeedback(unittest.TestCase):
    def test_missing_wrong_nested_type_and_duplicate_fields_report_without_traceback(self):
        cases=[('cloud','boundary_models.py','breakglass','boundary-models.json','lease_requests'),
               ('network','protocol_models.py','dns','protocol-models.json','queries'),
               ('crypto','record_crypto.py','migration','round2-crypto.json','password_record')]
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input.json'
            for track,script,mode,fixture,field in cases:
                original=json.loads((LABS/track/fixture).read_text(encoding='utf-8'))
                for data in [{}, {**original,field:None}, {**original,field:'wrong'}]:
                    p.write_text(json.dumps(data),encoding='utf-8')
                    result=run(track,script,mode,'--input',str(p))
                    self.assertEqual(result.returncode,2,result.stderr)
                    self.assertIn('INVALID input:',result.stderr)
                    self.assertNotIn('Traceback',result.stderr)
            original=json.loads((LABS/'cloud/boundary-models.json').read_text())
            original['lease']['revoked']='false'
            p.write_text(json.dumps(original),encoding='utf-8')
            result=run('cloud','boundary_models.py','breakglass','--input',str(p))
            self.assertEqual(result.returncode,2)
            self.assertIn('$.lease.revoked',result.stderr)


class CleanPackaging(unittest.TestCase):
    def test_stray_source_and_existing_output_never_enter_zip_or_public_manifest(self):
        with tempfile.TemporaryDirectory(prefix='bifrost-clean-build-') as tmp:
            root=Path(tmp)
            (root/'scripts').mkdir(); (root/'content').mkdir()
            shutil.copy(ROOT/'scripts/build_labs.py',root/'scripts/build_labs.py')
            shutil.copytree(ROOT/'scripts/lab_sources',root/'scripts/lab_sources')
            shutil.copytree(ROOT/'scripts/lab_common',root/'scripts/lab_common')
            shutil.copytree(ROOT/'content/lab-fixtures',root/'content/lab-fixtures')
            for name in ['lab-sources.json','site.json']: shutil.copy(ROOT/'content'/name,root/'content'/name)
            (root/'labs/web').mkdir(parents=True)
            scratch=root/'labs/web/REVIEW-STRAY.txt'; scratch.write_text('local learner work')
            (root/'scripts/lab_sources/web/UNLISTED.txt').write_text('not approved')
            subprocess.run([sys.executable,str(root/'scripts/build_labs.py')],check=True,capture_output=True,env=ENV,timeout=40)
            self.assertEqual(scratch.read_text(),'local learner work','Do not delete learner scratch files')
            names=json.loads((root/'labs/manifest.json').read_text())
            self.assertNotIn('web/REVIEW-STRAY.txt',names)
            self.assertNotIn('web/UNLISTED.txt',names)
            with zipfile.ZipFile(root/'labs/web.zip') as z:
                self.assertNotIn('web/REVIEW-STRAY.txt',z.namelist())
                self.assertNotIn('web/UNLISTED.txt',z.namelist())
            checksums=(root/'labs/web/SHA256SUMS.txt').read_text()
            self.assertNotIn('REVIEW-STRAY',checksums)
            self.assertNotIn('UNLISTED',checksums)


class SequentialExamples(unittest.TestCase):
    def test_environment_baseline_then_mutation_has_distinct_expected_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp); source=(LABS/'foundation/hello.py').read_text(encoding='utf-8')
            p=folder/'hello.py'; p.write_text(source,encoding='utf-8')
            self.assertIn('Hello, Bifrost',run('foundation','hello.py',cwd=folder).stdout)
            p.write_text(source.replace('name = "Bifrost"','name = "Mina"'),encoding='utf-8')
            self.assertIn('Hello, Mina',run('foundation','hello.py',cwd=folder).stdout)
            html=(ROOT/'tracks/foundation/environment.html').read_text(encoding='utf-8')
            self.assertLess(html.index('id="exampleCode"'),html.index('class="walkthrough"'))
            self.assertIn('변경 전 기준',html)


if __name__=='__main__': unittest.main(verbosity=2)
