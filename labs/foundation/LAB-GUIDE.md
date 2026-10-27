# Foundation · 데이터와 재현 가능한 도구

이 폴더의 기본 예제는 Python 3.10 이상의 표준 라이브러리만 사용합니다.
압축을 풀고 foundation 폴더에서 실행하세요. Linux/WSL/macOS는 `python3`,
Windows PowerShell은 같은 명령의 `python3`를 `py -3`로 바꿉니다.
새 가상환경이나 외부 계정은 필요하지 않습니다. 파일을 바꿀 때 원본은 보관하세요.

## 1. 문자열과 바이트

```text
python3 data_tools.py text
```

```text
codepoints=2 bytes=4 hex=41eab080
roundtrip=True
wrong_encoding=UnicodeDecodeError
```

`A가`의 코드 포인트 수와 UTF-8 바이트 수를 비교합니다. 잘못된 ASCII
해석은 오류로 구분하며 바이트를 삭제하지 않습니다. `len(str)`은 화면상의
글자 묶음 수까지 계산하는 함수가 아닙니다. 사본에서 `A가!`로 바꾸면
`codepoints=3 bytes=5 hex=41eab08021`이 되어야 합니다.

## 2. JSON 문법과 데이터 계약

```text
python3 data_tools.py json record.json
python3 data_tools.py json record-invalid.json
```

정상 문서는 `learner=Loki minutes=30`과 공백 없는 정규화 표시를 출력합니다.
문자열 `"30"`이 있는 두 번째 문서는 stderr에 `INVALID: ValueError`를 쓰고
종료 상태 2로 끝납니다. 계약은 정확히 learner/minutes 두 키, 비어 있지 않은
이름, 불리언을 제외한 정수 0~1440입니다. JSON 파싱 성공은 계약 충족이 아닙니다.

## 3. 예외와 실패 상태

```text
python3 data_tools.py errors
```

```text
ok=30
text=INVALID
negative=INVALID
boolean=INVALID
```

이 모드는 예상 오류를 관찰하는 실험을 마쳐 상태 0으로 끝납니다.
실제 `json` 작업의 잘못된 문서는 상태 2입니다. 오류를 정상 값 0으로
바꾸면 잘못된 자료와 실제 0분 자료를 구분할 수 없습니다.

## 4. 명령행 계약

```text
python3 data_tools.py summary --help
python3 data_tools.py summary record.json --minimum 30
python3 data_tools.py summary record.json --minimum 31
```

순서대로 도움말, `selected=True`, `selected=False`를 확인합니다.
`--minimum abc`는 숫자 구문 오류, `--minimum -1` 또는 1441은 업무 범위 오류입니다.
`0`과 `1440`은 유효한 기준값입니다. 직접 지정한 상대 입력 경로는 현재 폴더를
기준으로 하고, 생략한 기본 입력은 스크립트 옆 record.json입니다.

## 5. 테스트와 고의 실패

```text
python3 -m unittest -v test_data_tools
```

`Ran 4 tests`와 `OK`가 기준입니다. 실행 시간은 달라집니다.
작업 폴더에 data_tools.py와 test_data_tools.py를 함께 복사하고,
사본에서 `>= minimum`을 `> minimum`으로 바꾸면
`test_selection_boundary`가 실패해야 합니다. 고의 오류를 복구한 뒤 다시 통과시킵니다.
기대값을 구현에 맞추어 바꾸는 것으로 실패를 없애지 마세요.

## 학습 산출물과 범위

입력·계약·예상·실제·종료 상태·해석을 표로 남깁니다. 정상·거부·동등 경계를
함께 기록합니다. 이 도구는 계정별 진도를 저장하지 않습니다. JSON 정규화 표시는
암호 서명용 표준 정규화가 아니며, 작은 고정 표본 테스트가 모든 파일 크기·성능·
중복 키 정책까지 증명하지는 않습니다.
