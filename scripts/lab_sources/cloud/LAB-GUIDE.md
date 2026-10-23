# 모형 구성의 형식과 위험 조건 구분하기

Python 3.10 이상의 표준 라이브러리만 사용합니다. ZIP을 풀고 `cloud` 폴더에서 Linux/WSL/macOS는 `python3 review.py`, Windows PowerShell은 `py -3 review.py`를 실행합니다. 파일만 읽고 클라우드 계정이나 실제 자원에 접근하지 않습니다.

## 세 가지 결과

| 상태 | 의미 | 예 |
| --- | --- | --- |
| INVALID | 검사에 필요한 형식·자료형·값이 올바르지 않음 | `admin_source`가 빈 문자열, `encrypted`가 문자열 `"true"` |
| REVIEW | 형식은 유효하지만 이 모형의 검토 기준에 걸림 | `database_public: true`, `admin_source: "::/0"` |
| PASS | 이 항목의 로컬 모형 규칙을 만족함 | 암호화 참, 전체 인터넷보다 좁은 유효 CIDR |

`config.json`은 8개 REVIEW로 시작합니다. `python3 review.py config-reviewed.json`은 8개 PASS를 보여 줍니다. 두 파일을 비교하고 왜 그 설정이 필요한지 적으세요. 형식이 유효한 문서는 REVIEW가 있어도 종료 코드 0이며, 읽기/JSON/스키마 오류가 있으면 종료 코드 2입니다. 자동 배포 승인용 종료 코드가 아닙니다.

## 형식 규칙

- 최상위 값은 객체이며 `workload`, `provider`는 빈 문자열이 아니어야 합니다.
- 이름 오타를 숨기지 않도록 정의되지 않은 항목과 중복 JSON 키를 거부합니다. NaN·Infinity도 표준 JSON 값이 아니므로 거부합니다. `storage.name`도 빈 문자열이 아니어야 합니다.
- `storage`, `identity`, `network`, `audit`는 객체여야 합니다. 필수 항목을 지우면 INVALID입니다.
- 참/거짓은 JSON의 `true`/`false`를 사용합니다. 문자열, 숫자 0/1, null은 대체할 수 없습니다.
- `action`, `resource`는 앞뒤 공백 없는 식별자입니다. 빈 문자열은 INVALID이며 `*`, `?`를 포함하는 범위는 REVIEW입니다.
- 관리 출발지는 `192.0.2.0/24`처럼 네트워크 주소/접두사 형식으로 씁니다. `192.0.2.1/24`처럼 host bit가 남는 값, 접두사 없는 IP, 잘못된 IP는 INVALID입니다. IPv4·IPv6 전체인 `0.0.0.0/0`, `::/0`은 모두 REVIEW입니다.
- `retention_days`는 0~36500의 정수이며 이 모형에서 30일 미만은 REVIEW입니다. 실제 보관 기간은 목적·조직 정책에 따라 결정해야 합니다.

## 반례 과제와 해설

작업용 사본에서 `action`, `resource`, `admin_source`를 빈 문자열로 바꿔 보세요. `identity.scope`, `network.admin`은 INVALID이며 8/8이 될 수 없습니다. 다음에는 `encrypted`를 `"false"`로 바꾸세요. 비어 있지 않은 문자열을 참으로 취급하지 않고 INVALID로 구분합니다. `retention_days: true`도 정수가 아닙니다.

좋은 답안은 “값을 지워 경고를 없애기”와 “필요한 동작·자원·관리 대역을 구체적으로 지정하기”의 차이를 설명합니다. `config-reviewed.json`의 문서용 대역을 실제 운영에 복사하는 것은 답이 아닙니다. 승인된 관리자와 필요한 접속 경로를 근거로 정해야 합니다.

## PASS로 결론 내릴 수 없는 것

이 도구는 실제 공급자의 IAM 문법, 정책 우선순위, 신뢰 관계, 라우팅, 방화벽, 데이터 민감도, 키 접근 권한, 로그 전달·변조 방지 상태를 검사하지 않습니다. `identity.scope`는 와일드카드가 없다는 것만 보며 그 권한이 실제 최소 권한인지 판단하지 않습니다. `network.admin`도 CIDR이 유효하고 `/0`이 아니라는 것만 확인하므로 넓은 공인 대역이 PASS여도 안전한 관리자 경로라는 뜻이 아닙니다.

검사 결과와 함께 ① 실제 검증할 공급자 설정, ② 허용·거부 테스트, ③ 필요한 증거, ④ 남은 위험을 남기세요. `audit.csv`의 C04는 익명 읽기가 허용된 교육용 기록이므로, 구성 파일만 수정한 뒤 과거 로그까지 안전해졌다고 해석하면 안 됩니다.
