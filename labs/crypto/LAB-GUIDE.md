# 실제 인증 암호와 서명 관찰

`lab.py`의 표현·해시·HMAC·고전 암호·nonce·비밀번호 실습은 Python 표준 라이브러리만 사용합니다. `aead.py`와 `signature.py`는 검증된 `cryptography` 라이브러리의 AES-GCM과 Ed25519 API를 호출하는 선택 실습입니다. 서버·계정·API 비용이 없으며 설치 이후 실행은 오프라인입니다.

## 환경 준비

Python 3.10 이상을 사용합니다. 파일을 한 폴더에 유지하고 ZIP을 푼 `crypto` 폴더에서 실행합니다.

Linux/WSL/macOS:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python aead.py
.venv/bin/python signature.py
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe aead.py
.\.venv\Scripts\python.exe signature.py
```

가상환경을 활성화하지 않고 해당 Python을 직접 실행하므로 PowerShell의 스크립트 실행 정책을 바꿀 필요가 없습니다. 설치할 때만 패키지 다운로드를 위해 인터넷이 필요합니다. 선택 패키지가 없으면 준비 명령을 안내하고 종료합니다. `No matching distribution`이 나오면 지원되는 64비트 CPython 환경과 최신 pip로 다시 확인합니다. Debian/Ubuntu에서 venv 생성 시 ensurepip 오류가 나면 배포판의 `python3-venv` 패키지를 설치합니다. 기존 표준 라이브러리 실습은 이 설치와 독립적입니다.

`requirements.txt`는 2026-10-23 검증 환경의 `cryptography==50.0.2`를 고정합니다. 장기 운영용 의존성 관리 정책이나 암호 프로토콜 전체를 제공하는 예제는 아닙니다.

## AES-GCM: 정상과 변조를 비교

```text
original=ACCEPT message=Bifrost lesson 17
tampered_ciphertext=REJECT
tampered_tag=REJECT
changed_aad=REJECT
changed_nonce=REJECT
wrong_key=REJECT
fresh_round_trip=True
```

`envelope.json`은 실제 암호문·12바이트 nonce·16바이트 태그를 Base64로 담습니다. Base64는 저장 표현이며 암호화가 아닙니다. `teaching-key.json`은 이 표본의 **공개 교육용 키**입니다. 비밀을 보장하려는 파일이 아니며 이 고정 키/nonce로 새 메시지를 암호화하면 안 됩니다. 스크립트의 새 암호화는 매번 새 무작위 키와 nonce를 만듭니다.

라이브러리는 암호문 뒤에 태그를 붙인 값을 반환합니다. `aead.py`는 저장할 때 나눠 둔 암호문과 태그를 합쳐 복호화합니다. AAD `record-id=17`은 암호화되지 않지만 인증됩니다. 값 하나라도 바뀌면 `InvalidTag`를 처리해 평문을 사용하지 않습니다. 이 예외만으로 공격, 파일 손상, 잘못된 키 중 원인을 구별할 수는 없습니다.

과제: 작업용 사본의 `aad_utf8`를 `record-id=18`로 바꾸고 실행 전 결과를 예상하세요. 원본 확인 단계의 `InvalidTag`를 처리해 `fixture=REJECT reason=authentication_failed`를 출력하고 종료 코드 2로 끝나야 합니다. 그다음 원본을 복구합니다. 프로그램의 정상 출력은 원본 파일을 기준으로 합니다. 실제 시스템은 이런 실패를 사용자에게 비밀 없이 안내하고 데이터를 거부해야 합니다.

해설: 공격자가 AAD와 암호문을 함께 바꿔도 올바른 새 태그를 만들 키가 없으면 검증이 실패합니다. “내용이 안 보이면 안전하다”는 설명은 무결성 조건을 빠뜨립니다. nonce는 비밀일 필요가 없지만 같은 키에서 재사용하면 안 되며, 실서비스에는 다중 프로세스·키 교체·저장 실패까지 고려한 관리가 필요합니다.

## Ed25519: 공개키로 검증

```text
original=VALID
tampered_message=INVALID
tampered_signature=INVALID
wrong_key=INVALID
fresh_round_trip=True
```

`signature.json`에는 공개키, 평문 메시지와 실제 Ed25519 서명이 있습니다. 스크립트는 공개키만으로 이 세 값을 검증하고 메시지·서명·키가 달라진 경우를 비교합니다. 마지막 줄에서는 새 개인키를 메모리에 생성해 서명한 뒤 그 공개키로 확인합니다. 개인키 파일을 운영용으로 저장하거나 외부로 보내지 않습니다.

과제: 메시지 끝의 공백 하나, 틀린 공개키, 원본 메시지의 세 경우를 비교표로 적으세요. 원본만 VALID여야 합니다. 문자열의 의미가 같아 보여도 검증 대상 바이트가 바뀌면 서명은 맞지 않습니다.

해설: 서명은 암호화가 아니므로 메시지는 읽을 수 있습니다. VALID는 “이 공개키와 이 바이트에 이 서명이 맞는다”는 뜻입니다. 누가 그 공개키를 소유하는지 알아내려면 별도의 신뢰 경로가 필요합니다. 공격자가 메시지·서명·공개키를 모두 자기 것으로 바꿔 내밀면 검증 성공만으로 원래 작성자를 확인할 수 없습니다. `protocol.md`의 키 역할 설계와 함께 비교하세요.

## 공식 참고 자료

- [AES-GCM, nonce와 InvalidTag](https://cryptography.io/en/50.0.2/hazmat/primitives/aead/#cryptography.hazmat.primitives.ciphers.aead.AESGCM)
- [Ed25519 서명·검증](https://cryptography.io/en/50.0.2/hazmat/primitives/asymmetric/ed25519/)
- [설치 환경](https://cryptography.io/en/50.0.2/installation/)
