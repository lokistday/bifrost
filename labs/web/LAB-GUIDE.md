# Web · 서로 다른 보안 경계를 구분하기

Python 3.10 이상의 표준 라이브러리만 사용합니다. 압축을 푼 web 폴더에서
Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`로 실행합니다.
외부 요청·서버·실제 쿠키·계정은 없습니다. `.invalid` 주소와 토큰은 공개 교육 표본입니다.

## CSRF: 인증된 사용자와 변경 의도

```text
python3 web_controls.py csrf
```

```text
valid=ALLOW
no-token=DENY
foreign=DENY
get-change=DENY
```

POST, alice, 정확한 Origin, 공개 표본 TOKEN을 모두 만족해야 허용하는 단일 세션
모형입니다. 실제 세션별 토큰 발급·만료는 구현하지 않습니다. `compare_digest`가
고정된 공개 토큰을 비밀로 만들지는 않습니다. CORS만으로 CSRF 방어가 완성되지 않습니다.

## CORS: 브라우저의 응답 접근

```text
python3 web_controls.py cors
```

정확한 SITE 하나만 `EXPOSE`, 다른 출처·유사 접미 호스트·null은
`NO_CORS_HEADERS`입니다. 마지막 줄은 `authorization=SEPARATE_CHECK`입니다.
이는 응답 헤더 생성 모형이며 실제 요청 전송이나 서버 인가 결과가 아닙니다.
허용 헤더에는 정확한 Origin, Credentials=true, Vary=Origin이 있습니다.

## CSP: 표본 체크리스트와 실제 집행

```text
python3 web_controls.py csp
```

```text
enforced=CHECKLIST_PASS
report-only=REPORT_ONLY
inline=REVIEW
browser_enforcement=NOT_TESTED
```

`response-policy.txt`는 가상의 응답 예시입니다. Bifrost나 GitHub Pages의 헤더를
바꾸지 않습니다. `review_csp`는 고정 문자열 체크리스트이며 일반 CSP 파서가 아닙니다.
브라우저의 중복 지시문 처리·nonce·해시·실제 집행을 검증하지 않습니다.
보고 전용 정책은 차단을 증명하지 않고, CSP도 안전한 출력 처리를 대신하지 않습니다.

## 파일: 이름·폴더·소유자·내용

```text
python3 web_controls.py files
```

`note.txt`만 `ALLOW_NAME`, 나머지 네 표본은 `DENY`입니다.
단일 ASCII txt 이름만 허용하고 해석한 경로가 관리 폴더 안인지 확인합니다.
실제 파일을 열지 않으므로 존재·내용·소유자 인가는 검사하지 않습니다.
링크를 동시 변경할 수 있는 저장소에서는 검사와 사용 사이 경합도 별도 문제입니다.
과제 표본 note_1.txt는 허용, note..txt·/tmp/note.txt·note.TXT는 거부입니다.

## SSRF: URL 구문과 실제 연결

```text
python3 web_controls.py ssrf
```

```text
allowed=ALLOW_SYNTAX
loopback=DENY
userinfo=DENY
redirect-param=DENY
network_requests=0
```

https, 정확한 assets.example.invalid 호스트, 443 포트, 허용한 두 경로를 검사합니다.
userinfo·쿼리·fragment·제어 문자는 허용하지 않습니다. 네트워크 요청은 전혀 없고,
DNS·리다이렉트·프록시·출구 정책 검증도 실행하지 않습니다. `ALLOW_SYNTAX`를
안전한 실제 연결의 증명으로 쓰지 마세요. 실제 기능은 URL 전체 대신 서버가 정한
자료 ID를 받는 방법도 검토할 수 있습니다.

## 남길 것

각 경계에서 정상 요청 하나와 거부 요청 둘 이상을 기록합니다. 입력·변경한 조건·
예상·실제·검증하지 않은 부분을 분리하세요. 이 자료는 프레임워크 보안 기능,
인증 서버, 범용 CSP/URL 파서, 운영 파일 저장 라이브러리의 대체물이 아닙니다.
