"""Loopback-only HTTP training app. In-memory fixtures, no external requests."""
import argparse
import hashlib
import hmac
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent

def unique_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result: raise ValueError('duplicate JSON key')
        result[key]=value
    return result

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 120000)

class State:
    def __init__(self):
        self.users = {}
        for user in ['alice', 'bob']:
            salt = secrets.token_bytes(16)
            self.users[user] = (salt, password_hash('student-'+user, salt))
        self.sessions = {}
        self.attempts = {}
        self.notes = {'1': {'owner':'alice', 'text':'Alice private note'}, '2': {'owner':'bob', 'text':'Bob private note'}}
        self.lock = threading.RLock()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Do not log passwords, tokens or cookies.

    @property
    def origin(self):
        return f'http://127.0.0.1:{self.server.server_port}'

    def reply(self, status, value, content_type='application/json; charset=utf-8', cookie=None, cors=False):
        data = json.dumps(value, ensure_ascii=False).encode() if isinstance(value, (dict,list)) else value.encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        connect = " connect-src 'self' http://127.0.0.1:8787;" if urlsplit(self.path).path == '/probe' else " connect-src 'self';"
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'self';"+connect)
        if cookie:
            self.send_header('Set-Cookie', cookie)
        if cors:
            self.send_header('Vary', 'Origin')
            if self.headers.get('Origin') == self.server.cors_origin:
                self.send_header('Access-Control-Allow-Origin', self.server.cors_origin)
                self.send_header('Access-Control-Allow-Methods', 'GET')
        self.end_headers()
        self.wfile.write(data)

    def valid_host(self):
        if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
            self.reply(400, {'error':'use the printed 127.0.0.1 URL'})
            return False
        return True

    def session(self):
        jar = SimpleCookie()
        try:
            jar.load(self.headers.get('Cookie',''))
            sid = jar['bifrost_lab'].value if 'bifrost_lab' in jar else ''
        except Exception:
            return '', None
        state = self.server.state
        record = state.sessions.get(sid)
        if record and record['expires'] <= time.monotonic():
            state.sessions.pop(sid, None)
            record = None
        return sid, record

    def do_OPTIONS(self):
        if not self.valid_host(): return
        self.reply(204, '', cors=urlsplit(self.path).path=='/api/public')

    def do_GET(self):
        if not self.valid_host(): return
        path = urlsplit(self.path).path
        static = {'/':'http-workshop.html','/app.js':'http-workshop.js','/style.css':'http-workshop.css','/probe':'cors-probe.html','/probe.js':'cors-probe.js'}
        if path in static:
            name = static[path]
            kind = 'text/javascript' if name.endswith('.js') else 'text/css' if name.endswith('.css') else 'text/html'
            return self.reply(200,(HERE/name).read_text(encoding='utf-8'),kind+'; charset=utf-8')
        if path == '/api/public':
            return self.reply(200,{'message':'public learning material'},cors=True)
        with self.server.state.lock:
            _, session = self.session()
            if not session: return self.reply(401,{'error':'authentication required'})
            if path == '/api/me':
                return self.reply(200,{'user':session['user'],'csrf':session['csrf']})
            if path.startswith('/api/notes/'):
                note = self.server.state.notes.get(path.removeprefix('/api/notes/'))
                if not note: return self.reply(404,{'error':'not found'})
                if note['owner'] != session['user']: return self.reply(403,{'error':'owner permission required'})
                return self.reply(200,note)
        self.reply(404,{'error':'not found'})

    def do_POST(self):
        if not self.valid_host(): return
        if self.headers.get('Origin') != self.origin:
            return self.reply(403,{'error':'origin rejected'})
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json':
            return self.reply(415,{'error':'JSON required'})
        try:
            if self.headers.get('Transfer-Encoding'): raise ValueError('unsupported transfer encoding')
            length = int(self.headers.get('Content-Length','-1'))
            if not 0 <= length <= 4096: raise ValueError('body size')
            data = json.loads(self.rfile.read(length), object_pairs_hook=unique_object)
            if not isinstance(data,dict): raise ValueError('object required')
        except (ValueError, UnicodeError, RecursionError):
            return self.reply(400,{'error':'invalid JSON/body'})
        path = urlsplit(self.path).path
        state = self.server.state
        with state.lock:
            if path == '/api/login':
                user, password = data.get('user'), data.get('password')
                if set(data)!={'user','password'} or not isinstance(user,str) or not isinstance(password,str):
                    return self.reply(400,{'error':'user/password strings required'})
                if len(user)>64 or len(password)>128: return self.reply(400,{'error':'input too long'})
                try: user.encode('utf-8'); password.encode('utf-8')
                except UnicodeError: return self.reply(400,{'error':'invalid Unicode'})
                now = time.monotonic()
                # Single loopback client: global budget prevents unbounded username allocation.
                count, until = state.attempts.get('loopback',(0,now+30))
                if now >= until: count, until = 0, now+30
                if count >= 5: return self.reply(429,{'error':'wait 30 seconds before retrying'})
                salt, expected = state.users.get(user,(b'unknown-user-salt', b'\0'*32))
                if not hmac.compare_digest(password_hash(password,salt),expected):
                    state.attempts['loopback']=(count+1,until)
                    return self.reply(401,{'error':'invalid credentials'})
                old, _ = self.session()
                state.sessions.pop(old,None)
                sid = secrets.token_urlsafe(32)
                state.sessions[sid]={'user':user,'csrf':secrets.token_urlsafe(24),'expires':now+300}
                return self.reply(200,{'user':user},cookie=f'bifrost_lab={sid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=300')
            sid, session = self.session()
            if not session: return self.reply(401,{'error':'authentication required'})
            token = self.headers.get('X-CSRF-Token','')
            if not hmac.compare_digest(token.encode(),session['csrf'].encode()): return self.reply(403,{'error':'CSRF token rejected'})
            if path == '/api/logout':
                state.sessions.pop(sid,None)
                return self.reply(200,{'logged_out':True},cookie='bifrost_lab=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0')
            if path.startswith('/api/notes/'):
                note = state.notes.get(path.removeprefix('/api/notes/'))
                if not note: return self.reply(404,{'error':'not found'})
                if note['owner'] != session['user']: return self.reply(403,{'error':'owner permission required'})
                if set(data)!={'text'} or not isinstance(data['text'],str) or len(data['text'])>200:
                    return self.reply(400,{'error':'only text (max 200 characters) is accepted'})
                try: data['text'].encode('utf-8')
                except UnicodeError: return self.reply(400,{'error':'invalid Unicode'})
                note['text']=data['text']
                return self.reply(200,note)
        self.reply(404,{'error':'not found'})

def make_server(port=8787, cors_origin='http://127.0.0.1:8788'):
    server = ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.state = State()
    server.cors_origin = cors_origin
    return server

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8787)
    args=parser.parse_args()
    with make_server(args.port) as server:
        print(f'BIFROST training: http://127.0.0.1:{server.server_port}/ ; Ctrl+C to stop',flush=True)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
