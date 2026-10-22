# Bifrost

GitHub Pages에서 운영하는 무료 보안 학습 사이트입니다. 공통 기초 1개와 전문 분야 8개를 별도 과정으로 나누고, 모듈별 목차에서 개별 강의로 이동합니다. React·서버·계정·유료 클라우드 자원이 필요하지 않습니다.

## 학습 과정

| 경로 | 과정 | 모듈 | 차시 |
| --- | --- | ---: | ---: |
| `tracks/foundation/` | Foundation | 3 | 10 |
| `tracks/web/` | Web Hacking | 2 | 7 |
| `tracks/pwn/` | Pwn / System | 2 | 6 |
| `tracks/rev/` | Reverse Engineering | 2 | 5 |
| `tracks/forensic/` | Forensic | 2 | 5 |
| `tracks/network/` | Network Security | 3 | 9 |
| `tracks/crypto/` | Cryptography | 3 | 9 |
| `tracks/misc/` | Misc | 2 | 4 |
| `tracks/cloud/` | Cloud Security | 2 | 7 |
| **합계** | **9개 과정** | **21** | **62** |

- 메인의 실습·진로·공통 습관 설명은 하나의 학습 안내로 통합했습니다. 이해·범위 설정 → 실습·검증 → 기록·결과물의 세 단계로 정리하고, 외부 자료 링크는 안내 맨 아래에 둡니다.
- 메인 노드는 분야별 목차를 여는 일반 링크입니다. 새 탭·뒤로 가기·직접 접속을 지원합니다.
- `tracks/<분야>/lesson.html?id=<고정-ID>`가 개별 강의 주소입니다. GitHub Pages의 URL 재작성 없이 새로고침됩니다.
- 강의는 개념 설명 → 예제/예상 결과 → 파일 실습 → 힌트 → 결과물 확인 → 완료 표시로 이어집니다.
- 62개 차시 모두 첫 개념 문단 다음에 해당 예제와 연결한 SVG 도식을 표시합니다. 9개 분야 목차에도 각 분야의 학습 흐름을 표시합니다.
- 메인 Roadmap·Study Tracks 구역은 제거했습니다. 각 분야 목차 페이지에는 해당 분야 소개 카드만 표시하고, 강의 목차로 바로 이동할 수 있습니다.
- 선행 지식은 다른 차시의 링크로 안내합니다. 강의를 잠그거나 자동으로 완료 처리하지 않습니다.
- Network Security는 기초 복습 이후 TLS 가시성·망 분리·정책 회귀 검증·탐지·Zero Trust·종합 설계를 다룹니다.
- Cryptography는 암호 목적·수학·해시·MAC·키 관리에, Misc는 단서 추출·데이터 변환·자동화·풀이 기록에 집중합니다.
- Cloud Security는 공급자 계정 없이 가상 JSON 구성과 CSV 감사 로그로 학습합니다. 실제 자원을 생성하는 스크립트가 아닙니다.

## 파일 구조

- `index.html` — 방사형 분야 지도와 하나로 통합한 학습 안내
- `tracks/*/index.html`, `tracks/*/lesson.html` — 분야/차시 진입 문서
- `js/curriculum.js` — 강의 본문·모듈·실습·선행 차시·공식 참고 문서
- `js/learning.js`, `css/learning.css` — 분야 목차와 강의 읽기 화면
- `js/progress.js` — 고정 ID 진도, 이전 데이터 이관, 백업/병합
- `content/field-guides.json` — 각 분야 페이지에 표시하는 소개 카드
- `content/visuals.json` — 차시별 62개·분야별 9개 도식의 원본 내용과 배치
- `js/visual-data.js` — 생성된 정적 도식 데이터 번들
- `js/visuals.js`, `css/visuals.css` — 공유 테마를 따르는 인라인 SVG와 그림 설명
- `scripts/build_visuals.py` — 차시·분야 전체 포함 여부 검증과 데이터 번들 생성. 페이지 생성 시 함께 실행
- `labs/<분야>/` — 직접 작성한 예제·합성 로그·원본 C 소스·PCAP
- `labs/<분야>.zip` — 다운로드 묶음. README와 SHA256SUMS 포함
- `scripts/build_labs.py` — 표본과 재현 가능한 ZIP 생성
- `scripts/build_pages.py` — 정적 진입 문서와 메인 노드 링크 생성
- `js/theme.js`, `css/theme.css` — 모든 페이지의 공유 테마
- `css/mindmap.css` — 방사형 지도와 본문으로 이어지는 배경
- `js/splash.js`, `css/splash.css` — 탭 세션의 첫 방문에만 표시하는 무지개다리 시작 화면
- `guides/linux.html`, `js/linux-guide.js` — 단독 접속/메인 오버레이 Linux 안내

실제 서비스는 HTML·CSS·JavaScript와 정적 자료만 사용합니다. `package.json`의 LinkeDOM은 개발용 DOM 테스트에만 쓰며 사이트 방문자에게 전송하지 않습니다.

## 강의 수정과 확장

1. `js/curriculum.js`에서 과정의 모듈에 차시를 추가합니다.
2. `foundation.python-values`처럼 영구 ID를 부여합니다. 제목·순서를 바꿔도 ID를 변경하거나 재사용하지 않습니다.
3. `concepts`, `code`, `expected`, `task`, `hint`, `checks`를 작성합니다. 미작성 차시를 완료 가능한 항목으로 등록하지 않습니다.
4. 필요한 자료를 `scripts/build_labs.py`에 추가하고 ZIP을 다시 생성합니다. 차시의 `files`는 해당 분야 폴더의 실제 파일명을 가리킵니다.
5. 새 분야를 만들 때는 `scripts/build_pages.py`의 과정 메타데이터, 노드 색·좌표와 메인 색 매핑도 함께 확장합니다.
6. `python scripts/build_pages.py`와 `python scripts/build_labs.py`를 실행하고 생성된 HTML·자료·ZIP도 배포합니다. 배포 시 생성기나 패키지 설치를 실행할 필요가 없습니다.

차시를 추가할 때는 `content/visuals.json`의 `lessons`에 같은 고정 ID의 도식을 작성합니다. 새 분야는 `courses`에도 학습 흐름을 넣습니다. 생성기는 누락·불필요한 ID, 빈 설명, 연결 대상 오류를 거부합니다. `flow`, `sequence`, `compare`, `table`, `timeline`, `map`, `cells`, `wheel` 형식으로 관계에 맞는 그림을 구성하며 `title`, `description`, `takeaway`는 필수입니다. 실제 실습 수치와 설명용 예시·한계를 구분합니다.

도식은 외부 이미지·유료 서비스·런타임 라이브러리를 요청하지 않습니다. 화면 읽기 도구용 제목·설명, 펼쳐 읽는 텍스트 설명, 키보드로 조작하는 가로 스크롤을 제공합니다. 작은 화면에서는 글자를 과도하게 축소하지 않고 그림 안에서 스크롤합니다.

예제는 Python 3.10 이상과 표준 라이브러리, C·셸은 Ubuntu/WSL의 GCC·binutils·GDB를 기준으로 합니다. 제공 PCAP은 8프레임의 DNS·평문 HTTP 합성 표본으로, TLS 분석용 캡처는 아닙니다. 암호 봉투·공개키 차시는 설계 검토이며 실제 AES/RSA 구현을 포함하지 않습니다. 상세 공급자 정책 엔진·stateful 방화벽도 구현하지 않은 교육 모델입니다.

## 진도와 이전 버전 데이터

- 새 키: `bifrost_progress_v2`. `completed`는 고정 차시 ID를 키로, `true`를 값으로 저장합니다.
- 예전 `whl_progress_v1`의 인덱스 배열은 삭제하지 않습니다. 유효한 이전 기록을 새 데이터의 `legacy`에도 보관합니다.
- `js/progress.js`의 명시적인 대응표로 동등한 차시만 한 번 이관합니다. 여러 새 차시로 쪼갠 Python, 재구성한 네트워크 설계 등은 자동 완료하지 않습니다.
- Crypto의 이전 5~7차시(작은 도구·CTF 분류·풀이 기록)는 Misc의 대응 차시로 이동합니다.
- 완료 해제를 다시 덮어쓰지 않도록 이관 여부를 저장합니다. 분야/모듈 집계는 모두 같은 완료 기록을 참조합니다.
- JSON 내보내기와 가져오기를 지원합니다. 가져오기는 알려진 ID의 완료 기록을 합치며 현재 완료 기록을 지우지 않습니다. 1MB 이하, 버전 2 파일을 받습니다.
- 탭 간 storage 이벤트와 뒤로 가기 캐시 복원 시 기록을 갱신합니다. 저장 실패 시 경고하고 현재 메모리 기록을 내보낼 수 있게 합니다.
- 손상되어 읽을 수 없는 새 저장값은 자동 덮어쓰지 않습니다. 유효한 백업을 명시적으로 가져오면 복구합니다.
- 다른 기기와 자동 동기화하지 않습니다. 같은 출처에서도 브라우저·프로필이 다르면 별도 기록입니다.

## 검증

사이트 실행·배포에 Node 패키지가 필요하지 않습니다. 개발 테스트만 실행하려면 `pnpm install --frozen-lockfile` 후 다음을 사용합니다.

```text
node tests/learning.test.cjs
node tests/visuals.test.cjs
node tests/splash.test.cjs
python tests/labs_test.py
# Linux/WSL에서 GCC가 설치된 경우
sh tests/c_labs.sh
```

DOM 테스트는 브라우저나 HTTP 서버를 열지 않고 모든 분야·차시의 깊은 링크, 자료 링크, 완료 표시, 진도 이관·백업·저장 실패를 검사합니다. Python 테스트는 예제 출력, 정책 수정, 구성 수정, PCAP 체크섬, ZIP·해시 일치, 생성기 재현성을 검사합니다. C 테스트는 빌드·실행·메모리 오류 진단·수정·최적화 전후 입력을 검사합니다. GDB 상호작용과 실제 화면 레이아웃은 별도 수동 확인 대상입니다.

도식 테스트는 전체 71개 그림의 배치·텍스트 대안·화살표 경로·실습 수치 일치를 검사합니다. 선택적 개발 도구 `scripts/render_visuals.cjs`는 Sharp로 실제 SVG 자산을 밝은/어두운 테마의 PNG와 검토 시트로 변환합니다. `scripts/audit_visuals.cjs`는 그 결과에서 실제 한글 글꼴 폭, 글자 겹침·잘림과 4.5:1 이상의 텍스트 대비를 검사합니다. 두 도구의 `BIFROST_SHARP_MODULE`은 Sharp 모듈 경로, `BIFROST_KOREAN_FONT`는 로컬 한글 글꼴 파일 경로입니다. 기본 출력은 운영체제 임시 폴더의 `bifrost-visual-review`이며 사이트에는 검토용 PNG를 배포하지 않습니다.

## 기존 디자인

중앙 원의 궤도 애니메이션과 움직이는 연결선을 유지하고, Misc·Cloud를 포함한 9개 노드를 배치했습니다. 메인 지도와 본문은 같은 `--paper` 바탕을 공유하고, 배경 광채가 다음 실습 안내 구역까지 이어집니다. 새 과정도 공유 테마를 head에서 먼저 적용하므로 저장된 테마로 시작합니다.

메인 시작 화면은 기존 8개 무지개 빛줄기의 무작위 하강과 BIFROST 로고 연출을 유지합니다. 강의 페이지에는 시작 화면을 넣지 않습니다. 모션 줄이기, Escape 건너뛰기, 숨겨진 탭·뒤로 가기 캐시 정리 동작도 유지합니다.
