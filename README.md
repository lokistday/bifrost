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

- 메인 노드는 분야별 목차를 여는 일반 링크입니다. 새 탭·뒤로 가기·직접 접속을 지원합니다.
- `tracks/<분야>/lesson.html?id=<고정-ID>`가 개별 강의 주소입니다. GitHub Pages의 URL 재작성 없이 새로고침됩니다.
- 강의는 개념 설명 → 예제/예상 결과 → 파일 실습 → 힌트 → 결과물 확인 → 완료 표시로 이어집니다.
- 선행 지식은 다른 차시의 링크로 안내합니다. 강의를 잠그거나 자동으로 완료 처리하지 않습니다.
- Network Security는 기초 복습 이후 TLS 가시성·망 분리·정책 회귀 검증·탐지·Zero Trust·종합 설계를 다룹니다.
- Cryptography는 암호 목적·수학·해시·MAC·키 관리에, Misc는 단서 추출·데이터 변환·자동화·풀이 기록에 집중합니다.
- Cloud Security는 공급자 계정 없이 가상 JSON 구성과 CSV 감사 로그로 학습합니다. 실제 자원을 생성하는 스크립트가 아닙니다.

## 파일 구조

- `index.html` — 방사형 지도, 로드맵, 분야별 진도 요약
- `tracks/*/index.html`, `tracks/*/lesson.html` — 분야/차시 진입 문서
- `js/curriculum.js` — 강의 본문·모듈·실습·선행 차시·공식 참고 문서
- `js/learning.js`, `css/learning.css` — 분야 목차와 강의 읽기 화면
- `js/progress.js` — 고정 ID 진도, 이전 데이터 이관, 백업/병합
- `js/app.js` — 메인 과정 목록과 진도 집계
- `labs/<분야>/` — 직접 작성한 예제·합성 로그·원본 C 소스·PCAP
- `labs/<분야>.zip` — 다운로드 묶음. README와 SHA256SUMS 포함
- `scripts/build_labs.py` — 표본과 재현 가능한 ZIP 생성
- `scripts/build_pages.py` — 정적 진입 문서와 메인 노드 링크 생성
- `js/theme.js`, `css/theme.css` — 모든 페이지의 공유 테마
- `css/mindmap.css` — 방사형 지도와 본문으로 이어지는 배경
- `js/splash.js`, `css/splash.css` — 기존 무지개다리 시작 화면
- `guides/linux.html`, `js/linux-guide.js` — 단독 접속/메인 오버레이 Linux 안내

실제 서비스는 HTML·CSS·JavaScript와 정적 자료만 사용합니다. `package.json`의 LinkeDOM은 개발용 DOM 테스트에만 쓰며 사이트 방문자에게 전송하지 않습니다.

## 강의 수정과 확장

1. `js/curriculum.js`에서 과정의 모듈에 차시를 추가합니다.
2. `foundation.python-values`처럼 영구 ID를 부여합니다. 제목·순서를 바꿔도 ID를 변경하거나 재사용하지 않습니다.
3. `concepts`, `code`, `expected`, `task`, `hint`, `checks`를 작성합니다. 미작성 차시를 완료 가능한 항목으로 등록하지 않습니다.
4. 필요한 자료를 `scripts/build_labs.py`에 추가하고 ZIP을 다시 생성합니다. 차시의 `files`는 해당 분야 폴더의 실제 파일명을 가리킵니다.
5. 새 분야를 만들 때는 `scripts/build_pages.py`의 과정 메타데이터, 노드 색·좌표와 메인 색 매핑도 함께 확장합니다.
6. `python scripts/build_pages.py`와 `python scripts/build_labs.py`를 실행하고 생성된 HTML·자료·ZIP도 배포합니다. 배포 시 생성기나 패키지 설치를 실행할 필요가 없습니다.

예제는 Python 3.10 이상과 표준 라이브러리, C·셸은 Ubuntu/WSL의 GCC·binutils·GDB를 기준으로 합니다. 제공 PCAP은 8프레임의 DNS·평문 HTTP 합성 표본으로, TLS 분석용 캡처는 아닙니다. 암호 봉투·공개키 차시는 설계 검토이며 실제 AES/RSA 구현을 포함하지 않습니다. 상세 공급자 정책 엔진·stateful 방화벽도 구현하지 않은 교육 모델입니다.

## 진도와 이전 버전 데이터

- 새 키: `bifrost_progress_v2`. `completed`는 고정 차시 ID를 키로, `true`를 값으로 저장합니다.
- 예전 `whl_progress_v1`의 인덱스 배열은 삭제하지 않습니다. 유효한 이전 기록을 새 데이터의 `legacy`에도 보관합니다.
- `js/progress.js`의 명시적인 대응표로 동등한 차시만 한 번 이관합니다. 여러 새 차시로 쪼갠 Python, 재구성한 네트워크 설계 등은 자동 완료하지 않습니다.
- Crypto의 이전 5~7차시(작은 도구·CTF 분류·풀이 기록)는 Misc의 대응 차시로 이동합니다.
- 완료 해제를 다시 덮어쓰지 않도록 이관 여부를 저장합니다. 분야/모듈/메인 집계는 모두 같은 완료 기록을 참조합니다.
- JSON 내보내기와 가져오기를 지원합니다. 가져오기는 알려진 ID의 완료 기록을 합치며 현재 완료 기록을 지우지 않습니다. 1MB 이하, 버전 2 파일을 받습니다.
- 탭 간 storage 이벤트와 뒤로 가기 캐시 복원 시 기록을 갱신합니다. 저장 실패 시 경고하고 현재 메모리 기록을 내보낼 수 있게 합니다.
- 손상되어 읽을 수 없는 새 저장값은 자동 덮어쓰지 않습니다. 유효한 백업을 명시적으로 가져오면 복구합니다.
- 다른 기기와 자동 동기화하지 않습니다. 같은 출처에서도 브라우저·프로필이 다르면 별도 기록입니다.

## 검증

사이트 실행·배포에 Node 패키지가 필요하지 않습니다. 개발 테스트만 실행하려면 `pnpm install --frozen-lockfile` 후 다음을 사용합니다.

```text
node tests/learning.test.cjs
python tests/labs_test.py
# Linux/WSL에서 GCC가 설치된 경우
sh tests/c_labs.sh
```

DOM 테스트는 브라우저나 HTTP 서버를 열지 않고 모든 분야·차시의 깊은 링크, 자료 링크, 완료 표시, 진도 이관·백업·저장 실패를 검사합니다. Python 테스트는 예제 출력, 정책 수정, 구성 수정, PCAP 체크섬, ZIP·해시 일치, 생성기 재현성을 검사합니다. C 테스트는 빌드·실행·메모리 오류 진단·수정·최적화 전후 입력을 검사합니다. GDB 상호작용과 실제 화면 레이아웃은 별도 수동 확인 대상입니다.

## 기존 디자인

중앙 원의 궤도 애니메이션과 움직이는 연결선을 유지하고, Misc·Cloud를 포함한 9개 노드를 배치했습니다. 메인 지도와 본문은 같은 `--paper` 바탕을 공유하고, 배경 광채가 로드맵까지 이어집니다. 새 과정도 공유 테마를 head에서 먼저 적용하므로 저장된 테마로 시작합니다.

메인 시작 화면은 기존 8개 무지개 빛줄기의 무작위 하강과 BIFROST 로고 연출을 유지합니다. 강의 페이지에는 시작 화면을 넣지 않습니다. 모션 줄이기, Escape 건너뛰기, 숨겨진 탭·뒤로 가기 캐시 정리 동작도 유지합니다.
