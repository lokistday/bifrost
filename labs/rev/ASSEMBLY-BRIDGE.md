# 어셈블리 상태표 → 심볼 없는 분석

rev.zip을 풀고 rev 폴더에서 진행합니다. Ubuntu/WSL의 gcc·binutils·Python 3가 필요합니다.
PART A는 x86-64 전용입니다. `uname -m`이 x86_64인지 확인하세요. AArch64에서는 이 .s를 빌드하지 않습니다.
PART B는 현재 Linux 아키텍처로 빌드되므로 디스어셈블리와 호출 규약을 그 아키텍처 기준으로 읽습니다.

## A. 짧은 명령을 한 줄씩 읽기

trace_steps.s는 GNU AT&T 문법으로 원본, 목적지 순서입니다. Intel 문법과 순서가 다릅니다.
%edi는 입력 x, %eax는 계산/반환값입니다. x는 unsigned int(32비트)이며 여기서는 작은 입력만 사용합니다.
$3은 즉시값 3, %eax는 레지스터입니다. 메모리 피연산자의 예인 (%rdi)는 그 주소의 메모리로, %rdi 값 자체와 다릅니다.
이 함수에는 간접 메모리 읽기가 없습니다. 기존 C 포인터 관찰에서 주소와 내용을 다시 대조하세요.

```sh
gcc -Wall -Wextra -Werror trace_driver.c trace_steps.s -o trace-steps
./trace-steps
objdump -d trace-steps
```

출력을 보기 전에 아래 표를 채웁니다. cmp는 eax-10의 비교 플래그만 바꾸며 eax를 쓰지 않습니다.
jbe는 unsigned 이하(CF=1 또는 ZF=1)일 때 분기합니다. signed 비교의 jle와 혼동하지 않습니다.

| 실행한 명령 | x=5의 EAX | x=7의 EAX | x=8의 EAX |
|---|---:|---:|---:|
| movl %edi,%eax | 5 | 7 | 8 |
| addl $3,%eax | 8 | 10 | 11 |
| cmpl $10,%eax | 8; CF=1,ZF=0 | 10; CF=0,ZF=1 | 11; CF=0,ZF=0 |
| jbe .Lsmall | 분기 | 분기 | 통과 |
| 분기별 마지막 계산 | 8 XOR 1 = 9 | 10 XOR 1 = 11 | 11-2 = 9 |
| ret | 반환 9 | 반환 11 | 반환 9 |

동적 확인 예상: x=5 result=9 / x=7 result=11 / x=8 result=9.
add는 32비트 범위에서 wrap할 수 있습니다. 이 표의 작은 수 결과를 임의 정수나 signed 비교로 일반화하지 않습니다.
직접 과제: driver 사본의 입력을 {0,6,9}로 바꾸고 예상 {2,8,10}을 먼저 적어 확인합니다.
다음으로 자신의 C 함수로 같은 동작을 작성하고 각 입력의 출력이 일치하는지 대조하세요.

## B. 소스를 보지 않고 자체 제작 ELF 분석

배포 ZIP은 재현성을 위해 reference 소스를 포함하지만 먼저 열지 않습니다. 아래 빌더는 내용을 출력하지 않습니다.
이 과정은 사전 제공된 완전 비공개 바이너리 과제와 다르며, 소스 열람 전 분석 연습입니다.

```sh
python3 build_blind.py blind-work
file blind-work/mystery
nm blind-work/mystery
readelf --dyn-syms blind-work/mystery
strings blind-work/mystery
objdump -d blind-work/mystery > mystery-disassembly.txt
./blind-work/mystery XXXX
```

nm은 일반 심볼이 없다는 안내를 낼 수 있습니다. 동적 연결용 이름/문자열은 남을 수 있어 완전 무정보 파일이 아닙니다.
문자열 accept/reject와 strlen/puts 같은 동적 호출 단서를 시작점으로 사용합니다.
사용자 함수 이름 gate와 소스 줄 번호에 의존하지 말고 진입·호출·비교·ret 후보의 주소와 연결을 표시하세요.
함수 경계는 한 가지 프로로그 패턴만으로 확정하지 않습니다. 분기·호출 대상과 복귀 흐름을 함께 확인합니다.

1. 입력 길이만 바꿔 최소 길이 조건을 추정합니다. 출력과 셸 종료 상태를 따로 기록합니다.
2. 각 위치의 바이트 비교와 두 바이트 합산 흐름을 찾아 입력 계약을 글로 적습니다.
3. 받아들여질 서로 다른 ASCII 입력 두 개와 한 조건씩 깨는 반례 세 개를 먼저 예상하고 실행합니다.
4. 모든 문자 조합을 유일한 정답이라고 단정하지 말고 조건을 만족하는 입력의 집합으로 설명합니다.
5. 보고서를 저장한 뒤 blind_reference.c를 열고 함수 경계/분기 가설을 교정합니다.

정답 예시와 검증은 이 문서 뒤의 별도 해설에 있습니다. 처음에는 여기서 멈추고 수행하세요.

## B 해설: 보고서 작성 후 확인

길이 4, 첫 바이트 K, 마지막 7, 가운데 unsigned 바이트 두 개의 합 150입니다.
KAA7(65+65)은 reject, KKK7(75+75)과 KJF7(74+70)은 각각 accept와 reject입니다.
서로 다른 정상 예로 KKK7과 KJL7(74+76)을 사용합니다.
KKK8은 끝 조건, XKK7은 첫 조건, KKK77은 길이 조건을 깨므로 reject입니다.
인자 하나가 있으면 accept/reject 모두 종료 0입니다. 인자 수가 다를 때만 종료 2입니다.
운영 인증이나 비밀번호 크래킹이 아니라 교육용으로 자체 제작한 짧은 판정 함수 분석입니다.
