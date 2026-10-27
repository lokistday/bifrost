# 키 수명과 프로토콜 검증 실습

이 파일들의 키·인증서 메타데이터·레이블은 공개 교육 자료입니다. 실제 비밀·회원가입·인증 프로토콜에 재사용하지 마세요. Python 3.10 이상 표준 라이브러리만 필요하며 네트워크 접속·추가 암호 패키지 설치는 없습니다.

ZIP 전체를 풀고 이 폴더에서 실행합니다. Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`입니다. `design-records.json` 변경은 사본을 만든 뒤 `--input design-work.json`으로 지정하세요.

| 명령 | 예상 핵심 결과 |
| --- | --- |
| `python3 design_checks.py lifecycle` | active 양쪽 허용, retired 기존 복호화만 허용, compromised·destroyed 정상 사용 금지 |
| `python3 design_checks.py hkdf` | `rfc5869_case1=True length=42`, `different_context=True` |
| `python3 design_checks.py certificate` | T1 이름·기간 일치, T2 이름 불일치, T3 기간 불일치 |
| `python3 design_checks.py replay` | 첫 요청 ACCEPT, 반복 REPLAY, 변조 BAD_TAG, 다음 순번 ACCEPT |
| `python3 design_checks.py encoding` | naive_same=True, framed_same=False, framed_tag_same=False |

## 실습 범위와 중요한 구분

1. **키 수명:** 상태 정책 표이며 KMS·키 삭제를 수행하지 않습니다. 퇴역은 유출과 다릅니다. 침해 키는 조사·통제된 복구 절차가 필요하며 정상 권한과 구분합니다. 과거 백업이 필요한 키를 성급히 파기하면 복구 가능성을 잃을 수 있습니다.
2. **HKDF:** RFC 5869 A.1 시험 벡터와 HMAC-SHA256 연산을 실제 대조합니다. Extract·Expand의 문맥 레이블은 용도 분리입니다. 약한 비밀번호의 추측 비용을 높이는 전용 KDF를 대신하지 않습니다. 운영은 검증된 구현과 프로토콜 키 일정을 사용합니다.
3. **인증서:** 실제 X.509 파일이 아닌 JSON입니다. 정확한 DNS 이름·고정 형식 날짜·가상 루트 이름만 비교합니다. 서명·경로·키 사용 목적·폐기·와일드카드 검증을 하지 않습니다. 세 값이 True여도 실제 TLS 인증에 성공한 것이 아닙니다.
4. **재전송:** 실제 HMAC-SHA256을 쓰지만 키는 공개 상수이고 프로토콜은 모형입니다. 한 키·한 주체의 순차 요청, 단조 증가 순번만 가정하며 빈 순번은 허용합니다. 상태를 잃거나 여러 서버가 따로 처리하면 중복 요청을 받을 수 있습니다. 키·사용자·세션 범위, 원자적 상태와 업무 처리, 재시도·만료·키 교체가 남습니다.
5. **메시지 표현:** [ab,c]와 [a,bc]의 단순 연결은 같은 abc이므로 같은 태그는 HMAC 충돌이 아닙니다. 길이 접두사는 필드 경계를 보존하며 실제 UTF-8 바이트 길이를 씁니다. 타입·순서·버전·최대 길이·정규화도 합의해야 합니다. 이 형식은 HTTP Message Signatures 구현이 아닙니다.

## 보고할 내용

예측·명령·출력·반례·보장하지 않는 내용을 함께 씁니다. 인증서 검사와 재전송 모형을 서비스에 붙이지 않습니다. 암호 도구 자체가 맞는 것과 도구 주변의 상태·이름·표현·키 정책이 맞는 것을 구분하세요.
