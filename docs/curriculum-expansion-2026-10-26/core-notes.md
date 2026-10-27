# Foundation / Web / Pwn 확장 검토

2026-10-26. 기존 차시는 삭제하거나 ID를 바꾸지 않고 15차시를 추가했습니다.

| 분야 | 기존 | 추가 | 합계 | 보완한 공백 |
| --- | ---: | ---: | ---: | --- |
| Foundation | 10 | 5 | 15 | 문자열/바이트, JSON 계약, 예외, CLI, 경계 테스트 |
| Web | 7 | 5 | 12 | CSRF/CORS/CSP 역할 구분, 파일 경계, SSRF |
| Pwn / System | 6 | 5 | 11 | 숫자 변환, 크기 wrap, 서식/잘림, 소유권, 바이너리 길이 |

## 영구 ID

- foundation.text-bytes
- foundation.structured-data
- foundation.exceptions
- foundation.cli
- foundation.unit-tests
- web.csrf
- web.cors
- web.csp
- web.file-boundary
- web.ssrf
- pwn.integer-input
- pwn.allocation-size
- pwn.format-strings
- pwn.ownership
- pwn.binary-parser

각 차시에 5개 개념 설명, 선행 학습, 구체 환경, 3단계 따라하기, 예상 결과,
변경 과제와 풀이, 오개념 2개, 상황형 자기 점검 2개, 공식 참고 문서를 포함했습니다.
도식 15개는 core-visuals.json에 ID별 flow/table/compare/timeline/cells로 작성했습니다.
새로운 범용 UI나 계정·진도 기능을 추가하지 않았습니다.

## 실습 원본

- scripts/lab_sources/foundation/: data_tools.py, record.json, record-invalid.json,
  test_data_tools.py, LAB-GUIDE.md
- scripts/lab_sources/web/: web_controls.py, response-policy.txt, LAB-GUIDE.md
- scripts/lab_sources/pwn/: parse_count.c, allocation_size.c, format_data.c,
  ownership.c, packet_parse.c, LAB-GUIDE.md
- tests/core_expansion_test.py: 입력 경계, JSON 계약, 오류 상태, 고의 결함,
  C 과제 변형과 파서 결함 검출 검사

## 근거 확인

2026-10-26 웹 조회로 Python 공식 문서(Unicode, str/bytes, json, 오류·예외,
argparse, sys.exit, unittest, assert, hmac, pathlib, urllib.parse), MDN(CORS,
동일 출처 정책, CSP와 CSP 헤더), OWASP CSRF/File Upload/SSRF Cheat Sheet,
SEI CERT C ERR34/INT30/FIO30/MEM30/MEM31/ARR30, GCC Warning/Instrumentation
문서를 확인했습니다. 위키의 예전 CMU URL은 가져오기 오류가 있어 현재
cmu-sei.github.io의 공식 이전 문서 URL을 사용했습니다. 각 차시의 references에
해당 문서 링크를 직접 저장했습니다. 원문 문단을 복제하지 않았습니다.

## 실행 검증

공유 빌드 전에는 BIFROST_CORE_LABS를 scripts/lab_sources로 설정해 저작 원본을
검사했습니다. 기본 CI는 이 변수를 생략하고 generated labs/를 검사합니다.

```text
python -m unittest discover -s tests -p core_expansion_test.py -v
```

- Windows Python: Python/Web 검사 통과. C는 native gcc 부재로 건너뜁니다.
- WSL Python/GCC: 19개 검사 모두 통과, 건너뜀 없음.
- C 5개 모두 -std=c11 -Wall -Wextra -Werror -Wformat=2 빌드 통과.
- ownership·packet_parse를 AddressSanitizer+UBSan으로 실행, 정상 결과와 진단 없음 확인.
- Foundation의 >=를 >로 바꾼 사본에서 동등 경계 검사 실패를 확인하고 원본 유지.
- C 변경 과제(count 5→28바이트, 버퍼 10→완전 출력, 길이 불일치 거부,
  빈 payload 허용)와 파서 경계 조건을 약화한 결함의 검출 가능성을 확인.

## 검증 범위

Web 스크립트는 순수 오프라인 모형입니다. 실제 브라우저 CORS/CSP 집행·쿠키·세션,
DNS·리다이렉트·HTTP 요청, 파일 열기/경합을 구현하거나 검증했다고 주장하지 않습니다.
C는 Ubuntu/WSL C11 기준이고 다른 ABI·컴파일러 GUI 상호작용은 검증하지 않았습니다.
통합 페이지·도식 렌더링·정적 경로·전체 실습 빌드 검증은 부모 작업에서 수행합니다.
