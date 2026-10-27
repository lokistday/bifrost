# Bifrost

GitHub Pages에서 운영하는 보안 학습 사이트입니다. {{COURSES}}개 분야·{{MODULES}}개 모듈·{{LESSONS}}개 차시를 설명, 시각 자료, 예제, 파일 실습, 해설과 자기 점검으로 연결합니다. 사이트 열람에 계정·서버·유료 클라우드 자원이 필요하지 않습니다.

| 분야 | 차시 |
| --- | ---: |
{{COURSE_TABLE}}

## 학습 중심 개편 · 2026-10-27

- 모든 차시에 고유한 독립 변형 과제·판단 기준·자기 평가·복습 안내를 제공합니다.
- `learn/`에서 제목·목표·핵심어·분야·난이도를 검색하고 다섯 목표별 경로를 이용합니다. 선행 차시와 프로젝트 준비 차시를 자동으로 앞에 배치합니다.
- `projects/`의 분야별 {{PROJECTS}}개 종합 프로젝트는 A/B 표본·결과 검사기·공개 참조 구현·보고서와 루브릭을 제공합니다. 검사 통과는 실력 인증이 아닙니다.
- `guides/bridges.html`의 6개 보충 연습은 객체·C·바이트·웹·증거·네트워크의 개념 간격을 연결합니다. 학습 시간은 저자 추정이며 실제 학습자 검증 결과가 아닙니다.
- ZIP은 새 임시 폴더에서 만들고 `content/lab-sources.json`에 등록한 파일만 복사합니다. 기존 `labs/`의 작업 사본은 보존하되 `labs/manifest.json`에 없으면 ZIP·배포에서 제외합니다.
- JSON 입력은 크기·깊이·항목 수·중복 키·비유한 수·필수 필드·정확한 타입을 검사합니다. 학습자용 검사기는 답안 JSON만 읽고 제출 코드나 외부 명령을 실행하지 않습니다. 별도 C 테스트 도구는 사용자가 선택한 자신의 C 소스를 로컬에서 실행하므로 샌드박스가 아닙니다.
- 학습 페이지는 meta CSP로 외부 스크립트·인라인 스크립트·네트워크 데이터 요청·플러그인·base 변경을 제한합니다. `frame-ancestors`, HSTS 같은 응답 헤더는 이 정적 코드로 설정했다고 주장하지 않습니다. 인라인 SVG/CSS 변수 때문에 스타일의 `unsafe-inline`은 남아 있습니다.
- README/공유 SVG의 현재 수치와 페이지 캐시 버전은 빌드 원본에서 생성합니다. 공유 PNG는 SVG가 바뀌면 `scripts/build_og.cjs`로 다시 만드세요.

## 학습 화면

- Aurora Atlas 디자인은 광채를 절제한 배경과 12개의 분야·학습 가이드 일러스트를 사용합니다. 같은 분야 그림을 지도·분야 소개·차시 제목에 재사용하며, 개념 설명은 {{VISUALS}}개 SVG 도식이 담당합니다. 그림은 투명 WebP로 제공하고 크기를 미리 확보해 로딩 중 배치가 흔들리지 않게 합니다.
- 메인의 방사형 지도에서 분야별 목차를 엽니다. 중앙 원·움직이는 연결선·노드 배치는 유지합니다.
- 시작 화면은 큰 Bifrost 로고와 이름이 나타나고, 함께 확대되며 메인 화면으로 전환됩니다. 약 2초의 CSS 애니메이션으로 동작하며 동작 줄이기 설정에서는 확대 없이 바로 종료합니다.
- 시작 화면은 탭 첫 방문에 재생합니다. 강력 새로고침의 키 입력을 받으면 다음 같은 주소의 로드에서 재생하며, 키 이벤트가 전달되지 않아도 HTML과 인트로 스크립트가 모두 완전한 응답 본문으로 재전송된 reload를 보조 신호로 사용합니다. 타이밍 정보가 늦게 기록되는 경우 DOMContentLoaded/load에서 다시 확인하며 일반 화면을 가리지 않습니다. 캐시 적중·304 재검증·뒤로 가기는 자동 재생하지 않습니다. 이 보조 신호는 특정 단축키를 증명하지 않으므로 완전히 캐시가 없는 일반 새로고침이나 파일이 바뀐 새로고침에서도 한 번 재생할 수 있습니다. 브라우저가 단축키와 타이밍을 모두 제공하지 않는 경우에는 `?intro=1` 매개변수로 직접 재생을 확인할 수 있습니다. 재생 매개변수는 주소에서 즉시 제거해 다음 일반 새로고침에서 반복하지 않습니다. 브라우저 고유의 캐시 우회 동작은 가로채지 않습니다.
- {{LESSONS}}개 차시마다 개념 설명, 단계별 따라하기, 예상 결과, 변경 과제, 접어 둔 해설, 오개념 정리, 두 개의 자기 점검 문제, 선행 차시와 공식 참고 문서가 있습니다.
- 분야별 {{COURSES}}개와 차시별 {{LESSONS}}개의 SVG 도식은 밝은/어두운 테마를 따르며 텍스트 설명도 제공합니다. 픽셀 차시는 내려받는 P3 표본의 RGB 값·좌표와 같은 색을 실제 격자로 표시합니다.
- 자기 점검은 정답과 오답 이유를 즉시 확인합니다. 점수를 저장하거나 자동으로 차시를 완료하지 않습니다. 해설은 JavaScript 없이도 펼쳐 읽을 수 있습니다.
- `tracks/web/sessions.html`처럼 차시마다 본문·제목·설명이 들어 있는 정적 HTML을 생성합니다. JavaScript를 끄거나 링크를 공유해도 해당 차시 내용과 메타데이터를 제공합니다.
- 기존 `tracks/web/lesson.html?id=web.sessions` 주소도 유지합니다. 이 형식은 JavaScript로 차시를 선택하며, JavaScript가 꺼져 있으면 정적 차시 목차를 제공합니다. 새 링크와 canonical URL은 정적 주소를 사용합니다.
- 진도는 기존 브라우저 저장 기능을 유지합니다. 회원가입·계정별 동기화·진도 저장 개선은 이번 작업에서 보류했습니다. 영구 차시 ID와 기존 저장 키도 유지합니다.

## 저작 원본과 생성 파일

생성된 HTML이나 JS를 직접 고치면 다음 빌드에서 덮어씁니다. 아래 원본을 수정하세요.

| 원본 | 역할 | 생성 결과 |
| --- | --- | --- |
| `content/site.json` | 분야 순서·표시 번호·색상 연결·사이트 주소 | 지도·페이지·공유 주소 |
| `content/courses/*.json` | 분야별 강의 내용과 모듈 | `js/curriculum.js`, `js/catalog.js`, `js/courses/*.js` |
| `content/transfer-exercises.txt` + `content/learning-paths.json` | 차시별 독립 과제와 목표 경로 | 과제 패널·학습 도서관 |
| `content/projects.json` + `scripts/lab_sources/*/project*` | 종합 프로젝트 계약·표본·검사 | 프로젝트 페이지와 ZIP |
| `templates/README.md`, `templates/og-image.svg` | 수치가 자동 반영되는 설명·공유 원본 | README·공유 SVG |
| `content/fields.json` | 분야별 소개 카드의 구조화된 문장 | 각 분야 목차의 소개 |
| `content/lesson-ids.json` | 보존할 영구 차시 ID | 삭제·누락 검증 |
| `content/visuals.json` | {{VISUALS}}개 도식의 내용·배치 | `js/visual-data.js` |
| `templates/index.html` | 메인의 승인된 디자인 | `index.html` |
| `templates/learning.html` + `js/learning-view.js` | 공유 페이지 틀과 HTML 뷰 | `tracks/*/*.html`, `sitemap.xml` |
| `scripts/build_labs.py`, `scripts/lab_sources/` | 실습 원본·설명서·검사기 | `labs/`, 9개 ZIP·SHA256SUMS |
| `content/lab-fixtures/tls13.json` | 고정된 합성 TLS 표본 | TLS PCAP·키 로그·출처 설명 |
| `assets/og-image.svg` | 공유 이미지 원본 | `og-image.png` |

`js/learning.js`는 정적 본문에 복사·문제 피드백·기존 진도 조작을 연결합니다. 일반 차시에서 본문을 다시 렌더링하지 않아 열린 해설과 포커스를 유지합니다. 과거 쿼리 주소의 차시 선택에만 공유 HTML 뷰와 SVG 렌더러를 사용합니다. 일반 페이지는 가벼운 전체 목차와 현재 분야 내용만 불러옵니다.

`css/theme.css`는 공유 색상 토큰과 테마를, `css/main.css`는 공통 화면을, `css/mindmap.css`는 지도와 애니메이션을, `css/learning.css`는 강의 화면을 담당합니다. 사용하지 않는 과거 Roadmap·트랙 선택 UI 규칙을 제거했습니다.

## 내용 수정과 빌드

1. 해당 분야 JSON에서 이름 있는 필드를 수정합니다. `prerequisites`, `environment`, `concepts`, `walkthrough`, `code`, `expected`, `task`, `hint`, `solution`, `questions`, `pitfalls`, `checks`, `files`, `references`가 차시의 저작 항목입니다.
2. 제목·순서가 바뀌어도 `web.sessions` 같은 영구 ID는 바꾸거나 재사용하지 않습니다. 새 차시는 ID 목록과 도식에도 등록합니다.
3. 실습 원본을 수정했다면 자료와 강의의 명령·결과·해설을 함께 검토합니다. 생성된 `labs/`만 수정하지 않습니다.
4. Python 3.10 이상과 Node.js로 빌드합니다. 사이트 방문자에게 이 도구들이 필요하지는 않습니다.

```text
python scripts/build_labs.py
python scripts/build_pages.py
```

생성기는 필수 학습 항목·정답 인덱스·선행 ID·실습 파일·도식 전체 포함 여부를 검증합니다. 원본 템플릿에서 생성하므로 이전 HTML을 정규식으로 다시 고치는 누적 수정은 없습니다.

## 실습의 범위

기본 Python 예제는 표준 라이브러리로 실행합니다. C·Linux 예제는 Ubuntu/WSL의 GCC·binutils·GDB를 기준으로 하며, 차시마다 필요한 환경과 해석 범위를 적습니다.

- **TLS:** 기존 `traffic.pcap`은 DNS·평문 HTTP 8프레임입니다. 별도 `tls13.pcap`은 메모리 안에서 실제 OpenSSL TLS 1.3 교환을 만들고 Ethernet/IP/TCP 헤더를 합성한 15프레임 표본입니다. 실제 이용자 트래픽은 없습니다. 제공 키 로그는 이 공개 교육 표본에만 사용합니다. 제작용 난수 생성은 일반 빌드에서 실행하지 않습니다.
- **현대 암호:** `aead.py`는 실제 AES-GCM 복호화·변조 거부를, `signature.py`는 실제 Ed25519 서명·검증을 실행합니다. `record_crypto.py`의 aad·envelope·context 모드는 같은 선택 패키지로 AAD 결합·DEK 재래핑·서명 문맥을 검증합니다. 공개 교육용 키와 고정 표본을 실제 서비스에 재사용하지 않습니다. 선택 패키지 설치와 OS별 가상환경 명령은 `labs/crypto/LAB-GUIDE.md`, 후속 차시는 `ROUND2-GUIDE.md`에 있습니다. 기존 `lab.py`와 새 migration·sampling 모드에는 이 패키지가 필요하지 않습니다.
- **클라우드:** 실제 공급자 계정이나 자원을 만들지 않습니다. `review.py`는 JSON 형식 오류를 `INVALID`, 모형 위험 조건을 `REVIEW`, 이름 붙인 규칙의 충족을 `PASS`로 구분합니다. `8/8`을 실제 운영 보안이나 최소 권한의 증명으로 사용하지 않습니다.
- **네트워크 정책·웹 권한:** 단순한 로컬 모형입니다. stateful 방화벽이나 실제 인증 서비스를 구현했다고 해석하지 않습니다. 정상 동작과 거부해야 할 사례를 함께 확인합니다.

## 검증과 배포 준비

개발용 DOM 테스트에는 잠긴 `pnpm-lock.yaml`을 사용합니다. 암호/TLS 독립 인증 검사까지 실행하려면 선택 패키지를 먼저 설치합니다.

```text
pnpm install --frozen-lockfile
python -m pip install -r labs/crypto/requirements.txt
pnpm test
python tests/labs_test.py
python tests/learning_revision_test.py
python -m unittest discover -s tests -p '*_expansion_test.py' -v
# Linux/WSL
sh tests/c_labs.sh
python scripts/package_site.py
```

검사는 전체 차시의 정적 본문·실제 배포 스크립트 순서·정답/오답 피드백·기존 주소·앵커·테마·기존 진도 동작을 확인합니다. 실습 검사는 잘못된 JSON, 정상·변조 암호 자료, TLS 레코드의 독립 복호화·서명·Finished 검증, 패킷 체크섬, Windows/Linux ZIP 재현성을 다룹니다. 선택 패키지가 없으면 해당 암호 검사는 건너뛰며 CI에서는 설치해 모두 실행합니다.

실제 브라우저의 화면 배치·키보드 사용, Wireshark GUI와 GDB 상호작용은 별도 수동 확인 대상입니다. DOM 검사나 SVG 자산 렌더링을 브라우저 검증으로 표현하지 않습니다.

2026-10-26 확장에서는 기존 62개 차시를 보존하고 46개 차시를 추가했습니다. 바이트·JSON·CLI·자동 테스트, 웹 요청 경계, 정수·소유권·파싱, 역공학의 호출·흐름 복원, 포렌식 수집·상관·대응, 네트워크 운영 검증, 암호 키·프로토콜 조건, 데이터 탐색, 클라우드 배포·복구를 보강했습니다. [검토 내용과 분야별 추가 범위](docs/curriculum-expansion-2026-10-26/review.md)에 실습의 범위와 검증 결과를 정리합니다. 메인의 차시 수는 실제 목차에서 생성합니다.

같은 날 2차 확장에서는 기존 108개 차시를 보존하고 분야별 5개씩 45개를 추가해 153개로 늘렸습니다. 도구의 실행 조건, 웹 서비스 상태, OS 파일 경계, ELF·링크, 운영체제 흔적과 관측 오차, IPv6·재조립·캐시, 실제 암호 조합, 자료·자원 처리, 클라우드 접근 수명으로 연결합니다. [2차 검토 기록](docs/curriculum-expansion-2026-10-26-round2/review.md)에 추가 범위와 실제 검증 결과를 정리합니다.

`.github/workflows/pages.yml`은 생성·테스트에 성공한 `_site` 산출물만 배포하도록 `deploy`가 `verify`에 의존합니다. 실제 적용 시 GitHub Pages의 게시 소스를 **GitHub Actions**로 선택해야 합니다. 기존 브랜치 게시 방식은 이 워크플로만 추가해도 자동으로 전환되지 않습니다. 로컬에서 작성한 워크플로를 원격 CI에서 실행했다고 간주하지 않습니다.

`scripts/package_site.py`는 HTML·CSS·JS·실습·이미지만 `_site`에 묶습니다. 저작 원본, 테스트, 개발 의존성, 임시 패키지는 배포 묶음에서 제외합니다.

선택적 SVG 자산 검토는 Sharp와 로컬 한글 글꼴을 지정해 `node scripts/render_visuals.cjs`, `node scripts/audit_visuals.cjs`로 실행합니다. 실제 글꼴 폭·겹침·영역·양쪽 테마의 4.5:1 텍스트 대비를 검사합니다. `scripts/build_og.cjs`도 같은 환경으로 공유 PNG를 다시 생성합니다. 준비된 PNG는 저장소에 포함되므로 사이트 빌드에 Sharp는 필요하지 않습니다.

이번 개편의 범위·보안 설계·검증·남은 확인 항목은 [개편 기록](docs/learning-revision-2026-10-27/review.md)에 정리합니다.
