# 실제 HTTP로 이어지는 웹 보안 실습

## 준비와 종료

web.zip 전체를 풀고 그 안의 web 폴더에서 `python3 http_workshop.py`를 실행합니다.
Windows는 `py -3 http_workshop.py`입니다. Python 3.10 이상 표준 라이브러리만 사용합니다.
브라우저에서 반드시 http://127.0.0.1:8787/ 을 여세요. 파일을 더블클릭하는 방식이 아닙니다.
종료는 터미널에서 Ctrl+C입니다. 세션·수정 내용은 메모리에만 있으며 재시작하면 초기화됩니다.
실제 사이트의 계정 기능과 별개인 교육용 앱이며 외부 서비스로 요청하지 않습니다.
이 서버는 127.0.0.1에만 바인딩합니다. 제공 계정 alice/student-alice, bob/student-bob 외의 비밀번호는 넣지 마세요.
HTTP 개발 환경이므로 쿠키의 Secure는 생략했습니다. 운영 HTTPS의 쿠키 설정으로 복사하지 마세요.

## 1. 요청 → 처리 → 응답 → 화면

F12 → Network → Preserve log를 켜고 로그인합니다.
POST /api/login의 JSON 요청과 200 응답, Set-Cookie를 확인하세요.
이어서 GET /api/me의 Cookie와 응답 user/csrf를 관찰합니다. 비밀번호를 URL에 넣지 않습니다.
Application/Storage에서 HttpOnly·SameSite=Lax·Path=/를 확인합니다.
화면에 나온 csrf는 실습용 세션별 토큰입니다. 세션 쿠키를 JavaScript로 읽는 것과 다릅니다.
요청을 수정할 때는 개발자 도구의 Edit and Resend 또는 Copy as fetch 기능을 사용합니다.
브라우저마다 이름이 다릅니다. Copy as fetch는 해당 로컬 페이지의 Console에서만 실행하고 쿠키·토큰을 외부에 공유하지 마세요.

## 2. 인증과 소유자 권한

| 사용자 / 요청 | 예상 상태 | 확인할 근거 |
| --- | --- | --- |
| 로그인 전 GET /api/me | 401 | 세션 없음 |
| alice → GET /api/notes/1 | 200 | owner=alice |
| alice → GET /api/notes/2 | 403 | 로그인과 자료 소유권은 별개 |
| bob → GET /api/notes/2 | 200 | owner=bob |
| 로그아웃 후 이전 쿠키 재사용 | 401 | 서버 세션 폐기 |

계정 전환에는 별도 브라우저 프로필을 쓰거나 로그아웃 후 다시 로그인하세요.
두 탭은 같은 쿠키를 공유합니다. 로그인하면 이전 세션 ID를 폐기하고 새 ID를 발급합니다.
세션은 5분 후 만료됩니다. 새 로그인 전후 쿠키 값과 옛 쿠키 재사용 결과를 비교하세요.
잘못된 비밀번호 5회 이후에는 30초 예산 창이 끝날 때까지 429가 반환됩니다.
제한은 단일 로컬 클라이언트의 전체 시도에 적용됩니다. 운영용 분산·계정별 제한 구현이 아닙니다.
비밀번호는 실행 시 무작위 salt와 PBKDF2-HMAC-SHA256으로 해시합니다. 교육용 반복 횟수는 운영 보안 기준이 아닙니다.

## 3. 상태 변경과 입력 계약

alice 로그인 → 자료 1을 정상 수정합니다. Origin, X-CSRF-Token, JSON 본문을 기록하세요.
토큰 없이 수정 버튼은 403이고 내용은 바뀌면 안 됩니다.
같은 요청의 Origin을 다른 출처로 바꾸면 유효한 쿠키/토큰이 있어도 403입니다.
role 필드를 추가하는 버튼은 400이며 기존 내용이 유지돼야 합니다.
텍스트 200자/201자, text가 숫자인 경우, 알 수 없는 필드를 추가한 경우도 재전송해 보세요.
SameSite와 Origin/토큰 검사는 서로 다른 통제입니다. 포트가 다른 localhost는 다른 origin이지만 같은 site일 수 있습니다.
Cookie는 포트별로 격리되지 않습니다. 이 예제에서는 단일 로컬 교육 환경만 사용하세요.

## 4. 브라우저 CORS 관찰

새 터미널에서 `python3 http_workshop.py --port 8788`을 실행하고 http://127.0.0.1:8788/probe 를 엽니다.
공개 자료 버튼은 8787/api/public의 공개 JSON을 읽습니다. ACAO가 정확한 8788 출처와 일치합니다.
개인 자료 버튼은 credentials를 생략한 8787/api/me 요청입니다. 서버는 401을 보내지만 CORS 허용 헤더가 없어 JavaScript는 응답을 읽지 못합니다.
Network의 실제 HTTP 결과와 화면의 fetch 오류를 구분하세요. CORS 차단이 요청을 전송하지 않았다는 뜻은 아닙니다.
8787/probe에서 같은 공개 버튼을 누르면 동일 출처이므로 CORS 검증 비교가 되지 않습니다. 주소창의 8788을 확인하세요.
서버의 Access-Control-Allow-Origin 생성 조건을 사본에서 바꾼 뒤 허용 출처·거부 출처의 읽기 결과를 비교하세요.
개인 API에 임의 출처 허용을 추가하지 않습니다. CORS는 인증·인가를 대신하지 않습니다.
두 서버를 각각 Ctrl+C로 종료합니다.

## 5. CSP와 XSS 출력 경계

메인 페이지의 CSP 예제에는 의도적으로 인라인 스크립트 하나가 있습니다.
응답 헤더 script-src 'self'에 의해 실행이 차단되어 csp-result 문장이 유지돼야 합니다.
Console의 차단 이유와 Network 응답의 Content-Security-Policy를 함께 기록하세요.
외부 app.js는 허용되어 버튼이 작동합니다. 단순 서버 문자열 검사와 브라우저 집행의 차이입니다.
문자열 입력을 `<b>Bifrost</b>`로 넣고 표시하면 textContent로 문자 그대로 보여야 합니다.
DOM에 b 요소가 생겼는지 Elements에서 확인하세요. 임의 공격 코드를 실행할 필요는 없습니다.

## 독립 과제와 보고서

새 사용자에게 적용할 개인 자료 접근표를 먼저 작성하고 테스트를 구현하세요.
정상 수정, 타인 자료, 토큰 누락, 잘못된 Origin, 추가 필드, 로그아웃 후 재사용을 포함합니다.
한 조건씩 바꾸고 상태·본문·변경 전후 자료를 기록합니다. 200이나 403 하나만으로 전체 안전을 판정하지 않습니다.
이 앱은 실습용 최소 구현이며 실서비스용 프레임워크·영속 DB·TLS·업로드·OAuth를 제공하지 않습니다.

기준 문서: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
