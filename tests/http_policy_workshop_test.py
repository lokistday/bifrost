import copy
import importlib.util
import http.client
import json
from pathlib import Path
import threading
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name, file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
web=module('workshop_web','scripts/lab_sources/web/http_workshop.py')
cloud=module('workshop_cloud','scripts/lab_sources/cloud/policy_workshop.py')

class HttpWorkshop(unittest.TestCase):
    def setUp(self):
        self.server=web.make_server(0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.port=self.server.server_port;self.origin=f'http://127.0.0.1:{self.port}'
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def call(self,path,body=None,cookie=None,token=None,origin=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        headers={}
        if cookie:headers['Cookie']=cookie
        if token:headers['X-CSRF-Token']=token
        if body is not None:headers.update({'Origin':origin or self.origin,'Content-Type':'application/json'})
        c.request('GET' if body is None else 'POST',path,body=None if body is None else json.dumps(body),headers=headers)
        r=c.getresponse();raw=r.read();status=r.status;h=dict(r.getheaders());c.close()
        try:data=json.loads(raw)
        except ValueError:data=raw.decode()
        return status,h,data
    def login(self,user='alice',cookie=None):
        status,h,_=self.call('/api/login',{'user':user,'password':'student-'+user},cookie)
        self.assertEqual(status,200);self.assertIn('HttpOnly',h['Set-Cookie']);self.assertIn('SameSite=Lax',h['Set-Cookie'])
        cookie=h['Set-Cookie'].split(';')[0]
        _,_,me=self.call('/api/me',cookie=cookie)
        return cookie,me['csrf']
    def test_sessions_ownership_csrf_contract_and_revocation(self):
        self.assertEqual(self.call('/api/me')[0],401)
        cookie,token=self.login()
        self.assertEqual(self.call('/api/notes/1',cookie=cookie)[0],200)
        self.assertEqual(self.call('/api/notes/2',cookie=cookie)[0],403)
        for kwargs,body,status in [({}, {'text':'bad'},403),({'token':token,'origin':'http://other.invalid'},{'text':'bad'},403),({'token':token},{'text':'bad','role':'admin'},400),({'token':token},{'text':'x'*201},400)]:
            self.assertEqual(self.call('/api/notes/1',body,cookie,**kwargs)[0],status)
            self.assertEqual(self.call('/api/notes/1',cookie=cookie)[2]['text'],'Alice private note')
        self.assertEqual(self.call('/api/notes/1',{'text':'x'*200},cookie,token)[0],200)
        self.assertEqual(self.call('/api/notes/2',{'text':'bad'},cookie,token)[0],403)
        new_cookie,new_token=self.login(cookie=cookie)
        self.assertNotEqual(new_cookie,cookie)
        self.assertEqual(self.call('/api/me',cookie=cookie)[0],401)
        self.assertEqual(self.call('/api/logout',{},new_cookie,new_token)[0],200)
        self.assertEqual(self.call('/api/me',cookie=new_cookie)[0],401)
        bob,_=self.login('bob');self.assertEqual(self.call('/api/notes/2',cookie=bob)[0],200)
    def test_expiry_and_password_attempt_budget(self):
        cookie,_=self.login();sid=cookie.split('=',1)[1]
        self.server.state.sessions[sid]['expires']=time.monotonic()-1
        self.assertEqual(self.call('/api/me',cookie=cookie)[0],401)
        for _ in range(5):self.assertEqual(self.call('/api/login',{'user':'alice','password':'wrong'})[0],401)
        self.assertEqual(self.call('/api/login',{'user':'alice','password':'student-alice'})[0],429)
        self.server.state.attempts['loopback']=(5,time.monotonic()-1)
        self.login()
    def test_real_headers_and_browser_fixtures(self):
        status,h,page=self.call('/');self.assertEqual(status,200)
        self.assertIn("script-src 'self'",h['Content-Security-Policy']);self.assertNotIn('unsafe-inline',h['Content-Security-Policy'])
        self.assertIn('<script>',page);self.assertEqual(h['Cache-Control'],'no-store')
        for origin,exposed in [('http://127.0.0.1:8788',True),('http://other.invalid',False)]:
            c=http.client.HTTPConnection('127.0.0.1',self.port)
            c.request('GET','/api/public',headers={'Origin':origin});r=c.getresponse();r.read()
            self.assertEqual(r.getheader('Access-Control-Allow-Origin')==origin,exposed);c.close()
        self.assertNotIn('Access-Control-Allow-Origin',self.call('/api/me')[1])
        self.assertIn('http://127.0.0.1:8787',self.call('/probe')[1]['Content-Security-Policy'])

class Policies(unittest.TestCase):
    def setUp(self):
        self.policy=cloud.load(ROOT/'scripts/lab_sources/cloud/iam-reader.json')
        self.rbac=cloud.load(ROOT/'scripts/lab_sources/cloud/rbac-resources.json')
    def test_real_iam_shapes_and_negative_cases(self):
        allowed='arn:aws:s3:::bifrost-training-notes/readme.txt'
        self.assertEqual(cloud.iam(self.policy,'s3:GetObject',allowed),'ALLOW_MODEL')
        self.assertEqual(cloud.iam(self.policy,'s3:DeleteObject',allowed),'IMPLICIT_DENY_MODEL')
        self.assertEqual(cloud.iam(self.policy,'s3:GetObject','arn:aws:s3:::bifrost-training-notes/private/a'),'EXPLICIT_DENY_MODEL')
        self.assertEqual(cloud.iam(self.policy,'s3:ListBucket','arn:aws:s3:::bifrost-training-notes'),'IMPLICIT_DENY_MODEL')
        changed=copy.deepcopy(self.policy);changed['Statement'][0]['Action']='s3:*'
        self.assertEqual(cloud.iam(changed,'s3:DeleteObject',allowed),'ALLOW_MODEL')
        changed['Statement'][1]['Condition']={'StringEquals':{'x':'y'}}
        with self.assertRaises(ValueError):cloud.iam(changed,'s3:GetObject',allowed)
    def test_namespaced_rbac_and_role_change(self):
        args=['bifrost-learn','bifrost-learn','reader','get','pods']
        self.assertEqual(cloud.rbac(self.rbac,*args),'ALLOW_MODEL')
        for index,value in [(0,'bifrost-other'),(1,'bifrost-other'),(2,'unknown'),(3,'delete'),(4,'secrets')]:
            changed=args.copy();changed[index]=value
            self.assertEqual(cloud.rbac(self.rbac,*changed),'NO_ALLOW_IN_THIS_DOCUMENT')
        changed=copy.deepcopy(self.rbac);changed['items'][3]['rules'][0]['resources'].append('secrets')
        self.assertEqual(cloud.rbac(changed,*args[:-1],'secrets'),'ALLOW_MODEL')
        changed['items'][3]['rules'][0]['resourceNames']=['x']
        with self.assertRaises(ValueError):cloud.rbac(changed,*args)

if __name__=='__main__':unittest.main()
