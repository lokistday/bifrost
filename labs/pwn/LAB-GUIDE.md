# Pwn / System · 정수·출력·수명·파싱

Ubuntu/WSL의 GCC를 사용하며 바이너리는 제공하지 않습니다.
압축을 풀고 pwn 폴더에서 `gcc --version`을 확인하세요.
Windows PowerShell에서 직접 C 명령을 실행하지 말고 WSL 터미널에서 진행합니다.
시스템 보호를 끄거나 외부 대상을 사용하지 않습니다.

## 빌드 기준

각 파일은 다음과 같이 개별 빌드합니다. 출력 이름만 해당 파일명으로 바꿉니다.

```text
gcc -std=c11 -Wall -Wextra -Werror -Wformat=2 -g -O0 parse_count.c -o parse_count
```

### 1. 숫자 변환

```text
./parse_count 30
./parse_count 1024
./parse_count 1025
./parse_count -1
./parse_count 30x
```

30과 1024는 `count=...`, 나머지는 `INVALID_COUNT`와 종료 상태 2입니다.
0·0003도 허용합니다. ASCII 십진 문법, 변환 오류·끝 포인터, 0~1024 범위 검사를
마친 뒤 size_t로 바꿉니다. 실패할 때 자동화가 계속되어야 한다면 예상 실패를
셸의 if 분기로 처리하세요. 모든 실패를 성공으로 바꾸지는 않습니다.

### 2. 크기 계산

allocation_size.c를 같은 옵션으로 빌드해 실행하면 다음과 같습니다.

```text
small=OK bytes=20
huge=REJECT
empty=OK bytes=8
zero-element=REJECT
```

곱셈·덧셈 전에 `(SIZE_MAX-header)/element`로 상한을 비교합니다.
작은 사례의 count를 3에서 5로 바꾸면 28바이트입니다.
이 모형은 큰 메모리를 실제로 할당하지 않습니다. 표현 범위와 실제 할당 성공,
업무 자원 예산은 별도로 검증해야 합니다.

### 3. 서식 문자열과 잘림

format_data.c의 기본 실행은 `%s%n`을 데이터로 그대로 출력합니다.

```text
literal=%s%n
required=6 capacity=8 truncated=no
stored=[%s%n]
```

`./format_data Bifrost`는 `required=9 capacity=8 truncated=yes`이고 저장값은
`[Bifros`입니다. needed는 NUL을 제외하고 capacity는 NUL도 포함하므로
`needed < capacity`일 때만 잘리지 않습니다. 사본의 버퍼를 10으로 늘리면
`stored=[Bifrost]`, truncated=no가 되어야 합니다. 입력은 고정 서식의 데이터로만 전달합니다.

### 4. 소유권

ownership.c의 정상 출력은 다음 두 줄입니다.

```text
borrowed=Bifrost
owner_is_null=yes
```

main이 소유하고 show_note는 호출 중 빌립니다. free 후 owner=NULL은 owner 변수만
바꾸며 다른 별칭까지 지우지 않습니다. const 포인터도 객체 수명을 보장하지 않습니다.

### 5. 바이너리 파서

packet_parse.c는 가상의 2바이트 big-endian 길이+본문 형식만 읽습니다.

```text
normal=OK length=3
short-header=REJECT
short-body=REJECT
extra-byte=REJECT
```

헤더에 접근하기 전에 size>=2를 확인하고 선언 길이를 실제 남은 크기와 비교합니다.
정상 길이 필드만 3에서 2로 바꾸면 거부되어야 합니다. 빈 표본 `{0,0}`은
이번 계약에서 `OK length=0`입니다. 내용·인증·네트워크 스트림 처리는 포함하지 않습니다.

## 선택 계측

```text
gcc -std=c11 -Wall -Wextra -g -O0 -fsanitize=address,undefined -fno-omit-frame-pointer packet_parse.c -o packet-asan
./packet-asan
```

ownership.c도 같은 방식으로 계측할 수 있습니다. 정상 표본에서는 같은 출력과
진단 없는 실행을 확인합니다. 지원 여부와 진단 형식은 도구에 따라 다릅니다.
계측 통과는 실행한 경로에 대한 관찰이며 모든 경로·플랫폼의 안전성 증명은 아닙니다.

## 남길 것

입력 계약·검사 순서·정상/거부 결과·종료 상태·수정 이유·검증 한계를 기록하세요.
파싱 실패의 출력 인자를 성공 값으로 쓰지 않고, 소유권과 원인 수정·완화·계측을 구분합니다.
