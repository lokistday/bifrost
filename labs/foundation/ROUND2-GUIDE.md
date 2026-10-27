# Foundation · 상태와 실행 경계

Python 3.10 이상의 표준 라이브러리만 사용합니다. 압축을 푼 foundation 폴더에서
실행합니다. Linux/WSL/macOS의 `python3`는 Windows PowerShell에서 `py -3`로 바꿉니다.
workflow.py와 argv_worker.py는 같은 폴더에 유지하세요. 변경 실험은 사본에서 합니다.
이 자료는 계정이나 사용자별 진도를 저장하는 기능이 아닙니다.

## 1. 별칭·얕은 복사·깊은 복사

```text
python3 workflow.py copy
```

```text
alias_same=True
shallow_nested_same=True
original_tags=start,review
separate_tags=start,safe
```

alias는 같은 dict, shallow는 바깥 dict만 다른 객체입니다. tags 목록은 공유됩니다.
tagged_copy는 일반 dict/list를 깊은 복사한 뒤 태그를 더해 원본을 보존합니다.
`is`와 `==`를 구분하고, 원본 tags와 더 깊은 nested.counts 목록을 고정 기대값으로
검사하세요. deepcopy를 dict로 바꾼 사본은 원본 보존 검사가 실패해야 합니다.
열린 파일·잠금·외부 연결의 복제와 큰 자료의 복사 비용은 별도 문제입니다.

## 2. 자원 종료와 파일 교체

```text
python3 workflow.py atomic
```

```text
after_failure={"version":1}
after_success={"version":2}
pending_files=0
```

프로그램이 만든 자기 임시 폴더만 사용합니다. 대상과 같은 폴더의 임시 파일을
완성하고 닫은 뒤 os.replace로 교체합니다. 교체 전 예외에서는 이전 대상이 남고
finally가 임시 파일을 정리합니다. JSON 직렬화 자체가 실패해도 이전 대상이 보존되어야 합니다.

단일 파일 이름 교체는 여러 파일의 트랜잭션·동시 작성자 충돌 해결·모든 전원 장애
내구성과 다릅니다. 이 함수는 파일 fsync를 하지만 디렉터리 메타데이터 fsync와
권한·소유권 보존 정책을 구현하지 않습니다.

## 3. 설정 우선순위

```text
python3 workflow.py config
```

```text
default=5 source=default
file=10 source=file
environment=20 source=environment
cli=30 source=cli
empty_environment=INVALID
```

실제 PC 환경을 바꾸지 않고 명시적 dict로 비교합니다. 기본값 < 파일 < 환경 < CLI이며
timeout은 1~60 범위의 정수입니다. 60은 유효하고 61·0·불리언은 오류입니다.
키 누락은 미지정, 빈 환경값은 오류입니다. 낮은 계층의 잘못된 값도 높은 계층으로
숨기지 않는 엄격한 계약입니다. 선택한 값과 출처만 기록하고 환경 전체는 덤프하지 않습니다.

## 4. 자식 프로세스

```text
python3 workflow.py process
```

```text
argv=["two words","x;echo NOT_A_COMMAND"]
exit=0
child_failure=3
timeout=EXPIRED
```

고정 Python 실행 파일·고정 argv_worker.py·목록 인자·shell=False를 사용합니다.
세미콜론 문자열은 자식의 데이터이고 셸 명령이 아닙니다. --fail은 상태 3과 stderr
진단을, --sleep은 2초 지연을 요청해 짧은 제한에서 TimeoutExpired를 관찰합니다.
정상 출력·실패 상태·시간 초과를 구분하세요. 임의 실행 파일이나 옵션의 안전성,
전체 자손 프로세스·출력 크기·권한 제한까지 검증하는 도구가 아닙니다.

## 5. 구조화 로그

```text
python3 workflow.py logging
```

```text
{"event":"profile.update","request_id":"REQ-001","result":"denied","status":403}
secret_values_present=False
physical_lines=1
```

event/request_id/result/status만 선택하며 password·authorization은 제외합니다.
JSON은 값의 줄바꿈을 이스케이프해 물리적 한 줄을 유지합니다. 왕복 파싱도 검사하세요.
하지만 허용된 request_id에 비밀을 넣으면 그 값은 남습니다. 이것은 범용 비밀 탐지기가
아닙니다. 실제 로그 전송·보관·접근 제어·회전·시간 신뢰는 별도로 설계합니다.

## 남길 것

입력 계약·원본 보존·선택 출처·실패 상태·실제 결과·검증 한계를 기록합니다.
임시 파일 정리 누락, 깊은 복사를 얕은 복사로 변경, 자식 실패 상태 변경 같은
고의 결함에서 검사가 실패하는지 확인한 뒤 원본을 복구합니다.
