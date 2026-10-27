# 암호 레코드와 안전한 사용

이 표본의 키·nonce·서명 시드·비밀번호는 **모두 공개 교육값**입니다. 실제 비밀이나 서비스 데이터에 재사용하지 않습니다. 예제는 계정·로그인·암호 저장 서버를 만들지 않습니다.

ZIP 전체를 풀고 이 폴더에서 실행하세요. Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`입니다. Python 3.10 이상이 필요합니다.

- `migration`, `sampling`은 표준 라이브러리만 사용합니다.
- `aad`, `envelope`, `context`는 기존 crypto 실습과 같은 선택 의존성 `cryptography`를 사용합니다. 이미 준비한 가상환경이면 추가 설치 없이 실행합니다. 없다면 기존 `LAB-GUIDE.md`의 운영체제별 가상환경·`python -m pip install -r requirements.txt` 안내를 따릅니다. 설치 없이 읽을 때도 본문·도식·해설은 제공됩니다. 패키지가 없으면 해당 세 모드는 안내와 함께 종료하고 표준 라이브러리 모드는 계속 사용할 수 있습니다.

| 명령 | 검증하는 내용 |
| --- | --- |
| `python3 record_crypto.py aad` | 실제 AES-GCM이 다른 문서·테넌트 문맥을 거부하고 평문을 반환하지 않음 |
| `python3 record_crypto.py migration` | 잘못된 후보는 갱신하지 않고 성공한 오래된 값만 새 정책으로 이전 |
| `python3 record_crypto.py envelope` | 실제 AES Key Wrap 재포장 후 새 envelope에서 원래 평문 복호화 |
| `python3 record_crypto.py context` | Ed25519 서명 유효성과 서명된 의미·업무 권한의 차이 |
| `python3 record_crypto.py sampling` | 나머지 편향·거부 표본·secrets 범위 확인 |

## 문맥 결합

표본 암호문은 `["bifrost-record-v1","blue","17","1"]` AAD로 한 번 생성했습니다. 문서18·테넌트red·버전2를 주면 InvalidTag입니다. 복호화만 하며 수정한 평문을 같은 키·nonce로 다시 암호화하지 않습니다. AAD는 암호화되지 않으므로 비밀 공간이 아니고 기대 문맥은 인가된 요청과 연결해야 합니다.

버전 반례는 아래처럼 확인할 수 있습니다. 예외는 검증 실패를 보여주며 정상 평문은 반환되지 않습니다.

```text
python3 -c "from record_crypto import load,decrypt_record;decrypt_record(load()['record'],'blue','17','2')"
```

## 검증값 이전

공개 training-pass의 PBKDF2-SHA256 형식·비용·salt·검증값을 함께 읽습니다. 비용1000·목표2000·상한100000은 빠른 동작 관찰과 입력 제한용 교육값이며 운영 권장 비용이 아닙니다. 실제 정책은 최신 지침과 성능·용량을 기준으로 정합니다. 새 salt는 `secrets.token_bytes`로 생성하지만 출력은 검증 상태만 보여줍니다. 잘못된 후보를 재해시하거나 더 높은 비용을 낮추지 않습니다. 실제 저장의 원자적 갱신과 동시 비밀번호 변경은 구현하지 않았습니다.

## DEK 재포장

`rewrap_envelope`는 새 객체를 반환합니다. KEK v1→v2에서 감싼 DEK와 kek_id가 바뀌고 데이터 암호문·nonce는 유지됩니다. 새 KEK로 DEK를 풀어 실제 AES-GCM 복호화를 확인합니다. 포장 한 바이트 변조는 InvalidUnwrap, 데이터 변조는 InvalidTag입니다. AES-KW가 주변 JSON의 업무 권한이나 키 ID 신뢰를 모두 보장하지는 않습니다.

이전 KEK와 이전 포장 사본이 노출되었다면 재포장만으로 과거 노출이 사라지지 않습니다. DEK 교체·데이터 재암호화·백업·영향 범위를 검토해야 합니다.

## 서명 의미와 인가

실제 Ed25519로 review/approve/note-17을 서명합니다. deploy로 바꾸면 InvalidSignature입니다. 서명은 맞아도 publish 요청을 허용하지 않으며 권한 목록에 publish를 추가해도 서명된 행동 불일치가 남습니다. 신뢰한 공개키-주체 매핑·만료·회수·중복 사용·업무 상태는 실제 서비스에서 추가해야 합니다. 공개된 고정 시드는 실제 신원 증명이 아닙니다.

## 난수와 범위 변환

0~255를 전부 세면 %10의0~5는26개,6~9는25개입니다.250 이상을 버리면 각25개로 맞춰집니다.250·251·249는 분기를 재현하는 통제 입력이며 보안 난수원으로 사용하지 않습니다. 실제 선택은 `secrets.randbelow`를 사용합니다. 출력의 범위 True 한 번이나 작은 빈도 표가 예측 불가능성을 증명하지 않습니다.

`round2-crypto.json` 변경은 사본을 만들어 `--input crypto-work.json`으로 읽고 예상·실제 결과·보장하지 않는 내용을 함께 기록하세요.
