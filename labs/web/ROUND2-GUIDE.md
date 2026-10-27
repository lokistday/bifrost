# Web · 요청 계약과 상태의 수명

Python 3.10 이상에서 web_state.py를 실행합니다. Linux/WSL/macOS는 `python3`,
Windows PowerShell은 `py -3`를 사용합니다. Checkout은 Python의 sqlite3를 사용합니다.
모든 값은 공개 교육 표본이고 상태는 실행 중 메모리에만 있습니다. 실제 계정,
비밀번호 변경, 이메일 전송, HTTP 서버, 결제 기능을 사이트에 추가하지 않습니다.

## 1. 수정 가능 필드

```text
python3 web_state.py contract
```

```text
normal_name=Freya
role_assignment=REJECT
original_role=learner
original_name=Loki
```

소유자만 display_name/theme을 수정합니다. 이름은 공백만 아닌 1~40자 문자열,
테마는 dark/light입니다. role/owner 또는 알 수 없는 키가 섞이면 전체 요청을 거부합니다.
검증이 끝나야 새 dict를 반환하고 원본은 바꾸지 않습니다. 필드 허용과 사용자별
인가는 다른 검사입니다. 문자열 필드를 HTML·SQL 등에 쓸 때의 처리도 별도로 필요합니다.

## 2. 세션 갱신·로그아웃·만료

```text
python3 web_state.py sessions
```

```text
old_after_rotate=None
new_after_rotate=alice
at_expiry=None
after_logout=None
```

로그인 검증이 끝났다는 전제에서 90에 S-OLD를 지우고 S-NEW를 만듭니다.
새 만료값은 140이므로 139는 유효, 140은 무효입니다. at_expiry는 별도 표본이고,
원래 표본은 만료 전 92에 logout해도 무효가 되는지 확인합니다. 실제 쿠키나
비밀번호 검증·분산 저장소 동시성은 구현하지 않습니다. 공개 ID를 운영에 재사용하지 마세요.

## 3. 제한된 복구 토큰

```text
python3 web_state.py reset
```

```text
valid=ACCEPT
replay=REJECT
wrong_user=REJECT
expired=REJECT
wrong_purpose=REJECT
```

사용자 alice·목적 reset-password·만료 전·미사용·토큰 해시 일치를 함께 검사합니다.
틀린 시도는 used를 바꾸지 않습니다. 동일 토큰의 두 번째 사용은 거부합니다.
목적·시간 테스트는 별도 새 표본을 사용해 재사용 오류와 섞지 않습니다.
저장 해시는 원문의 엔트로피를 늘리지 않고 순차 used 검사도 동시 일회 사용을
보장하지 않습니다. 실제 발급·원자적 소비·전달·시도 제한·균일 응답은 별도 설계입니다.

## 4. 개인 응답과 공유 캐시

```text
python3 web_state.py cache
```

```text
public_alice=profile:alice
public_bob=profile:alice
no_store_bob=profile:bob
no_cache=STORE_REVALIDATE
private=PRIVATE_ONLY
```

개인 응답을 경로만 키로 public 저장한 앞의 두 줄은 의도적으로 잘못된 노출 표본입니다.
보호 표본은 새 캐시의 no-store이며 각 사용자 본문을 만들고 저장하지 않습니다.
이 결과는 과거 캐시 복사본 삭제의 증거가 아닙니다. 정책 변경만으로 기존 복사본이
자동 정리되지는 않으므로 실제 계층의 TTL·무효화·키·헤더를 따로 확인해야 합니다.

no-store는 저장 제한, private는 공유 캐시 저장 제한, no-cache는 재사용 전 검증입니다.
cache_rule은 정해진 부분 집합만 분류하고 실제 ETag/304·Vary·시간·Authorization
상호작용을 구현하지 않습니다. 실제 CDN·브라우저 집행을 검증했다고 주장하지 않습니다.

## 5. 재시도와 거래 상태

```text
python3 web_state.py checkout
```

```text
first=RESERVED stock=1
repeat=REPLAY stock=1
changed=CONFLICT stock=1
other=OUT_OF_STOCK stock=1
rollback_stock=1
```

초기 재고는 kit 3개입니다. 사용자+요청 키가 같은 같은 수량은 추가 차감하지 않고,
같은 키의 다른 수량은 충돌입니다. 재고 조건을 UPDATE에 결합하고 차감과 주문을
같은 트랜잭션에 둡니다. 중간 실패는 롤백하고 원래 예외를 다시 전달합니다.
정리 목적의 except를 실패 은폐와 혼동하지 마세요.

같은 alice/REQ-1/2를 세 번 호출하면 주문 1행·재고 1입니다. fail_after_update=True를
새 표본에서 실행하면 예외·재고 3·주문 0을 함께 확인합니다. 단일 SQLite 연결·한 제품·
순차 호출 모형이며 외부 결제나 분산 정확히 한 번 효과·운영 동시성을 증명하지 않습니다.

## 남길 것

허용 필드·권한 범위·수명·상태 불변 조건·정상/거부/복구 결과를 구분합니다.
고의 결함에서 검사가 실패하는지 확인하고 원본을 복구합니다. token·ID는 공개
표본임을 기록하며 실제 비밀이나 개인정보를 넣지 않습니다.
