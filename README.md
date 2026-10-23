# Bifrost

GitHub Pages에서 운영하는 보안 학습 사이트입니다. 9개 분야·21개 모듈·62개 차시를 설명, 시각 자료, 예제, 파일 실습, 해설과 자기 점검으로 연결합니다. 사이트 열람에 계정·서버·유료 클라우드 자원이 필요하지 않습니다.

| 분야 | 차시 |
| --- | ---: |
| Foundation | 10 |
| Web Hacking | 7 |
| Pwn / System | 6 |
| Reverse Engineering | 5 |
| Forensic | 5 |
| Network Security | 9 |
| Cryptography | 9 |
| Misc | 4 |
| Cloud Security | 7 |

## 학습 화면

- 메인의 방사형 지도에서 분야별 목차를 엽니다. 중앙 원·움직이는 연결선·노드 배치와 무지개 시작 화면은 유지합니다.
- 시작 화면은 탭 첫 방문에 재생합니다. 강력 새로고침의 키 입력을 받으면 다음 같은 주소의 로드에서 재생하며, 키 이벤트가 전달되지 않아도 HTML과 인트로 스크립트가 모두 완전한 응답 본문으로 재전송된 reload를 보조 신호로 사용합니다. 타이밍 정보가 늦게 기록되는 경우 DOMContentLoaded/load에서 다시 확인하며 일반 화면을 가리지 않습니다. 캐시 적중·304 재검증·뒤로 가기는 자동 재생하지 않습니다. 이 보조 신호는 특정 단축키를 증명하지 않으므로 완전히 캐시가 없는 일반 새로고침이나 파일이 바뀐 새로고침에서도 한 번 재생할 수 있습니다. 브라우저가 단축키와 타이밍을 모두 제공하지 않는 경우에는 `?intro=1` 매개변수로 직접 재생을 확인할 수 있습니다. 재생 매개변수는 주소에서 즉시 제거해 다음 일반 새로고침에서 반복하지 않습니다. 브라우저 고유의 캐시 우회 동작은 가로채지 않습니다.
- 62개 차시마다 개념 설명, 단계별 따라하기, 예상 결과, 변경 과제, 접어 둔 해설, 오개념 정리, 두 개의 자기 점검 문제, 선행 차시와 공식 참고 문서가 있습니다.
- 분야별 9개와 차시별 62개의 SVG 도식은 밝은/어두운 테마를 따르며 텍스트 설명도 제공합니다.
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
| `content/fields.json` | 분야별 소개 카드의 구조화된 문장 | 각 분야 목차의 소개 |
| `content/lesson-ids.json` | 보존할 영구 차시 ID | 삭제·누락 검증 |
| `content/visuals.json` | 71개 도식의 내용·배치 | `js/visual-data.js` |
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
- **현대 암호:** `aead.py`는 실제 AES-GCM 복호화·변조 거부를, `signature.py`는 실제 Ed25519 서명·검증을 실행합니다. 공개 교육용 키와 고정 표본을 실제 서비스에 재사용하지 않습니다. 선택 패키지 설치와 OS별 가상환경 명령은 `labs/crypto/LAB-GUIDE.md`에 있습니다. 기존 `lab.py`에는 이 패키지가 필요하지 않습니다.
- **클라우드:** 실제 공급자 계정이나 자원을 만들지 않습니다. `review.py`는 JSON 형식 오류를 `INVALID`, 모형 위험 조건을 `REVIEW`, 이름 붙인 규칙의 충족을 `PASS`로 구분합니다. `8/8`을 실제 운영 보안이나 최소 권한의 증명으로 사용하지 않습니다.
- **네트워크 정책·웹 권한:** 단순한 로컬 모형입니다. stateful 방화벽이나 실제 인증 서비스를 구현했다고 해석하지 않습니다. 정상 동작과 거부해야 할 사례를 함께 확인합니다.

## 검증과 배포 준비

개발용 DOM 테스트에는 잠긴 `pnpm-lock.yaml`을 사용합니다. 암호/TLS 독립 인증 검사까지 실행하려면 선택 패키지를 먼저 설치합니다.

```text
pnpm install --frozen-lockfile
python -m pip install -r labs/crypto/requirements.txt
pnpm test
python tests/labs_test.py
# Linux/WSL
sh tests/c_labs.sh
python scripts/package_site.py
```

검사는 전체 차시의 정적 본문·실제 배포 스크립트 순서·정답/오답 피드백·기존 주소·앵커·테마·기존 진도 동작을 확인합니다. 실습 검사는 잘못된 JSON, 정상·변조 암호 자료, TLS 레코드의 독립 복호화·서명·Finished 검증, 패킷 체크섬, Windows/Linux ZIP 재현성을 다룹니다. 선택 패키지가 없으면 해당 암호 검사는 건너뛰며 CI에서는 설치해 모두 실행합니다.

실제 브라우저의 화면 배치·키보드 사용, Wireshark GUI와 GDB 상호작용은 별도 수동 확인 대상입니다. DOM 검사나 SVG 자산 렌더링을 브라우저 검증으로 표현하지 않습니다.

`.github/workflows/pages.yml`은 생성·테스트에 성공한 `_site` 산출물만 배포하도록 `deploy`가 `verify`에 의존합니다. 실제 적용 시 GitHub Pages의 게시 소스를 **GitHub Actions**로 선택해야 합니다. 기존 브랜치 게시 방식은 이 워크플로만 추가해도 자동으로 전환되지 않습니다. 로컬에서 작성한 워크플로를 원격 CI에서 실행했다고 간주하지 않습니다.

`scripts/package_site.py`는 HTML·CSS·JS·실습·이미지만 `_site`에 묶습니다. 저작 원본, 테스트, 개발 의존성, 임시 패키지는 배포 묶음에서 제외합니다.

선택적 SVG 자산 검토는 Sharp와 로컬 한글 글꼴을 지정해 `node scripts/render_visuals.cjs`, `node scripts/audit_visuals.cjs`로 실행합니다. 실제 글꼴 폭·겹침·영역·양쪽 테마의 4.5:1 텍스트 대비를 검사합니다. `scripts/build_og.cjs`도 같은 환경으로 공유 PNG를 다시 생성합니다. 준비된 PNG는 저장소에 포함되므로 사이트 빌드에 Sharp는 필요하지 않습니다.
