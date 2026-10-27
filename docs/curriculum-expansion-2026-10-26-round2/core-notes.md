# Foundation / Web / Pwn · 두 번째 확장

2026-10-26. 기존 차시·영구 ID·이전 실습·설명서·검사를 유지하고 15차시를 추가했습니다.

| 분야 | 이전 | 추가 | 최종 |
| --- | ---: | ---: | ---: |
| Foundation | 15 | 5 | 20 |
| Web | 12 | 5 | 17 |
| Pwn / System | 11 | 5 | 16 |

## 추가 ID

- foundation.mutable-data
- foundation.atomic-output
- foundation.config-precedence
- foundation.subprocess
- foundation.structured-logging
- web.mass-assignment
- web.session-lifecycle
- web.reset-tokens
- web.private-caching
- web.idempotency
- pwn.struct-layout
- pwn.binary-strings
- pwn.file-descriptors
- pwn.partial-io
- pwn.atomic-open

각 차시는 개념 5문단, 환경·선행 학습, 따라하기 3단계, 구체 예상 결과,
변경 과제와 풀이, 오개념 2개, 상황형 문제 2개, 공식 참고 문서를 포함합니다.
도식 15개는 core-visuals.json에 작성했습니다. 기존 차시의 내용을 반복하는 대신
자료 공유·실패 복구·권한 수명·재시도·OS 객체 등의 다음 학습 단계로 연결했습니다.

## 원본 파일

- content/courses/{foundation,web,pwn}.json
- scripts/lab_sources/foundation/{workflow.py,argv_worker.py,ROUND2-GUIDE.md}
- scripts/lab_sources/web/{web_state.py,ROUND2-GUIDE.md}
- scripts/lab_sources/pwn/{struct_wire.c,embedded_nul.c,fd_lifetime.c,stream_chunks.c,open_boundary.c,ROUND2-GUIDE.md}
- tests/core_round2_expansion_test.py
- docs/curriculum-expansion-2026-10-26-round2/core-visuals.json

## 출처 검토

웹 조회로 Python copy/with/tempfile/os.replace/os.environ/subprocess/logging/json/
argparse/shlex/secrets, OWASP Mass Assignment/Input Validation/Session Management/
Forgot Password/Logging, RFC 9111·MDN Cache-Control, SQLite 트랜잭션·테이블 제약,
SEI CERT C DCL39/STR32/FIO45, Linux man-pages의 offsetof/strlen/read/write/dup/open/stat
문서를 확인했습니다. 차시 references에 직접 연결했습니다. Open Group·GNU 일부
주소가 403/timeout을 반환해 해당 API의 Linux man-pages 원본으로 검증했습니다.

## 검증

공유 생성 전 저작 원본을 확인할 때에만 BIFROST_CORE_ROUND2_LABS를
scripts/lab_sources로 지정했습니다. CI 기본값은 generated labs/입니다.

```text
python -m unittest discover -s tests -p core_round2_expansion_test.py -v
```

- Windows Python: 22개 중 Python/Web 17개 통과, native GCC 부재의 C 5개는 건너뜀.
- WSL Python/GCC: 22개 모두 통과, 건너뜀 없음.
- C 5개 모두 C11 -Wall -Wextra -Werror -Wformat=2 빌드 및 고정 출력 확인.
- 고의 결함: 얕은 복사, 임시 정리 누락, reset 재사용 검사 누락, 롤백 누락,
  decode 바이트 순서, FD의 int 별칭, 부분 읽기 조기 거부, O_NOFOLLOW 제거.
- C 변경 과제의 독립 예상값: code Hex, NUL 이동, 숫자 파일 입력, chunk=1 호출 수.
- Python 따라하기 inline/파일 코드는 독립 자식 Python에서 추가 실행 확인합니다.
- 전체 페이지·레지스트리·도식 렌더링·실습 ZIP 검증은 부모 작업에서 통합합니다.

## 확인 범위

실제 계정·복구 이메일·결제·HTTP 서버·사이트 진도 기능을 추가하지 않았습니다.
고정 세션 ID/토큰은 공개 표본입니다. reset·세션은 순차 메모리 상태 모형이고
Checkout은 실제 SQLite 트랜잭션을 쓰는 단일 연결·제품 한 종류·순차 호출입니다.
운영 인증·분산 일회 사용·외부 결제의 정확히 한 번 효과를 증명하지 않습니다.

no-store 보호 표본은 새 캐시에서 시작합니다. 정책 변경은 과거 복사본 자동 삭제가
아니고, cache_rule은 RFC 전체 구현이 아닙니다. 로그 허용 필드 선택은 그 필드 안의
모든 비밀을 탐지하지 않습니다. 원자적 파일 교체는 디렉터리 fsync·다중 파일 거래·
다중 작성자 충돌을 보장하지 않습니다.

C는 Linux/WSL API·자기 임시 파일만 사용합니다. 구조체 layout은 ABI별 관찰이고
stream_chunks는 실제 네트워크 대신 결정적 부분 I/O 어댑터입니다. open 표본은
통제된 디렉터리·단일 이름 전제의 비교이며 실제 공격자 경합 실험은 아닙니다.
