# Pwn / System · 자료 표현과 열린 객체

Ubuntu/WSL GCC에서 C11로 실행합니다. Windows PowerShell이 아니라 WSL 터미널을
사용합니다. 바이너리는 제공하지 않으며 다음 옵션으로 각각 빌드합니다.

```text
gcc -std=c11 -Wall -Wextra -Werror -Wformat=2 -g -O0 struct_wire.c -o struct_wire
```

나머지도 파일명과 출력 이름만 바꿉니다. 자기 임시 파일 외의 파일·설정은 건드리지 않습니다.

## 1. 구조체와 전송 형식

```text
./struct_wire
```

```text
wire_bytes=7 hex=01010203040506
roundtrip=True
short=REJECT
```

type 1바이트, code 4바이트 big-endian, count 2바이트 big-endian입니다.
`./struct_wire --layout`은 호스트 크기·오프셋을 따로 보여 줍니다. 이번 WSL ABI는
크기 12와 오프셋 0/4/8이지만 이 값은 다른 플랫폼의 고정 전송 규칙이 아닙니다.
padding을 덤프하지 않고 멤버를 명시적으로 인코딩합니다. code만 0x0A0B0C0D로
바꾸면 Hex는 010a0b0c0d0506입니다. 독립 Hex와 왕복을 둘 다 검사하세요.

## 2. 중간 NUL과 버퍼 길이

```text
./embedded_nul
```

```text
buffer_bytes=5 string_length=2
hex=4142004344
text_contract=REJECT_NUL
plain_text=ACCEPT
```

A B NUL C D의 뒤 바이트는 버퍼에 남습니다. plain 배열에는 NUL이 없으므로
strlen을 호출하지 않습니다. 텍스트 계약은 출력 가능한 ASCII 1~32바이트이며
UTF-8·HTML·파일명을 위한 범용 검사가 아닙니다. 사본의 data를 A B C D NUL로
바꾸면 문자열 길이 4, Hex 4142434400이고 전체 5바이트 텍스트 계약은 여전히 거부입니다.
NUL을 완전히 제거한 뒤 strlen을 호출하는 실험은 하지 마세요.

## 3. dup와 공유 오프셋

```text
./fd_lifetime
```

```text
first=AB
via_dup=CD
after_close=EF
last_read=EOF
```

프로그램이 만든 자기 임시 파일을 생성 직후 unlink하고 열린 FD로 다룹니다.
dup는 새 FD를 만들지만 같은 열린 파일 설명과 offset을 공유합니다. 원본 FD를
닫아도 복제 FD는 읽을 수 있습니다. 단순한 int 대입은 새 FD를 만들지 않습니다.
ABCDEF를 123456으로 바꾸면 12/34/56을 읽습니다. dup를 정수 대입으로 바꾼 사본은
원본 close 뒤 읽기에 실패하고 상태 2가 되어야 합니다. 실제 FD 번호는 고정하지 않습니다.

## 4. 짧은 읽기·쓰기 누적

```text
./stream_chunks
```

```text
complete=OK payload=BIFRO reads=4
truncated=REJECT reads=4
written=7 calls=4
stalled=REJECT
```

결정적 메모리 어댑터가 최대 2바이트만 처리하도록 합니다. 실제 socket이나 OS
스케줄러 실험이 아닙니다. 헤더 2는 1회, 본문 5는 3회이고 중간 EOF는 거부합니다.
정상 reader 둘과 writer의 chunk를 1로 바꾸면 읽기 7/6회, 쓰기 7회입니다.
실제 syscall의 EINTR·EAGAIN·타임아웃·반닫힘은 별도 정책이 필요합니다.
payload는 고정 ASCII 표본이며 일반 바이너리 출력은 명시적 크기를 유지해야 합니다.

## 5. 파일 열기와 객체 검증

```text
./open_boundary
```

```text
regular=ACCEPT
second_create=EXISTS
symlink=REJECT
opened_object=STILL_REGULAR
```

자기 mkdtemp 디렉터리·고정 dirfd·단일 이름을 사용합니다. 새 생성의 O_EXCL,
마지막 구성 요소의 O_NOFOLLOW, 열린 객체의 fstat 검증을 구분합니다.
O_NOFOLLOW 제거 사본은 자기 note.txt 링크가 열려 상태 2가 됩니다. 외부 파일을
향하는 링크는 만들 필요가 없습니다. 원본을 복구한 뒤 정상 결과를 확인하세요.

이 결정적 표본은 모든 상위 경로·hard link·마운트·소유자·내용·실제 동시 경합을
검증하지 않습니다. 이름을 제거해도 이미 열린 객체는 FD가 끝날 때까지 남을 수 있습니다.

## 선택적 계측과 기록

일반 C 표본은 -fsanitize=address,undefined -fno-omit-frame-pointer로 계측할 수 있습니다.
도구 지원과 진단 형식은 환경에 따라 달라집니다. 계측 통과는 실행한 경로에 대한 관찰입니다.
입력·바이트 규칙·반환량·객체 수명·고의 결함 결과·미검증 범위를 함께 남기세요.
