# Reverse · 2차 확장 실습

이 문서는 새 다섯 차시의 자료를 설명합니다. 기존 `LAB-GUIDE.md`와 모든 기존 실습은 그대로 사용합니다. 분석 대상은 직접 작성한 C/Python 소스이며 타인의 실행 파일이나 실제 서비스가 아닙니다.

## 환경

- Python: 3.10 이상, 외부 패키지 없음. Linux/macOS `python3`, Windows PowerShell `py -3`.
- ELF와 C: Ubuntu/WSL x86-64, GCC·GNU binutils. 아래 컴파일 명령은 Bash 기준입니다.
- 결과 주소·섹션 인덱스·명령어와 최적화 형태는 버전에 따라 다릅니다. 지정한 동작과 표의 의미를 비교하세요.

## 1. 섹션과 적재

```sh
gcc -g -O0 -Wall -Wextra layout.c -o layout
./layout
readelf -SW layout
readelf -sW layout
readelf -lW layout
```

출력은 `BF-LAYOUT init=7 zero=0`입니다. `.bss`의 NOBITS, `zeroed` 심볼 크기 1024, LOAD의 파일/메모리 크기를 연결하세요. 사본의 배열을 2048로 늘려도 파일 크기가 반드시 1024바이트 증가하는 것은 아닙니다. 파일 오프셋·가상주소·런타임 매핑은 다른 관찰입니다.

## 2. 자체 공유 라이브러리

```sh
gcc -g -O0 -c linkmain.c -o linkmain.o
readelf -rW linkmain.o
gcc -g -O0 -fPIC -shared linkpart.c -o libbfmath.so
gcc linkmain.o -L. -lbfmath -Wl,-rpath,'$ORIGIN' -o linkdemo
./linkdemo
nm -D libbfmath.so
readelf -dW linkdemo
```

`adjusted=12`가 기준입니다. `$ORIGIN`의 작은따옴표를 유지하세요. 객체의 `U adjust`, 라이브러리의 `T adjust`, NEEDED의 `libbfmath.so`를 구분합니다. `linkpart.c` 사본의 +7을 +9로 바꾸고 같은 라이브러리만 다시 빌드한 뒤 **새 프로세스**를 실행하면 14입니다. 이미 실행 중인 프로세스의 자동 코드 교체라는 뜻은 아닙니다. 시스템 라이브러리나 전역 검색 경로를 변경하지 않습니다.

## 3. 정수 표현

`python3 integer_views.py`는 u16=65534, s16=-2, zero32=0000fffe, sign32=fffffffe를 출력합니다. flags=0xa5는 version5/urgent1/reserved2입니다. `ff7f`와 `0080`으로 부호 경계를, `--flags 0x85`와 `--flags 0x05`로 bit7만의 변화를 비교하세요. 이 배치는 자체 비트 마스크 모형이고 실제 C 비트필드 배치 규칙이 아닙니다.

## 4. switch 구현

```sh
gcc -g -O0 -Wall -Wextra switches.c -o switch-o0
gcc -g -O2 -Wall -Wextra switches.c -o switch-o2
./switch-o0
./switch-o2
objdump -d -Mintel --disassemble=classify switch-o2
```

두 출력은 `-1:-1 0:11 1:17 2:23 3:31 4:47 5:59 6:-1`입니다. 비교 체인·값 표·점프 표는 서로 다릅니다. 특정 형식을 반드시 찾아야 한다고 가정하지 마세요. case2의 23을 29로 바꾼 사본에서는 입력2의 결과만 바뀌어야 합니다.

## 5. 상태기계

`python3 state_machine.py HELLO DATA END`는 data=1로 허용합니다. `HELLO END`는 data=0, `DATA END`는 시작 위반, `HELLO DATA`는 미완료, `HELLO END DATA`는 종료 후 입력이라 거부됩니다. 거부는 종료 상태2입니다. 이 도구는 토큰 순서 모형이며 실제 네트워크·인증·재전송·시간 제한을 구현하지 않습니다.
