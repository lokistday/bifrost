# 한 번의 호출: C → 프레임 → 레지스터 → 반환

Ubuntu/WSL, x86-64 System V AMD64, gcc·GDB 기준입니다. 이 실습의 rsp/rbp/rip/rdi/eax 명령은 AArch64용이 아닙니다.
`uname -m`이 x86_64인지 먼저 기록합니다. 다른 아키텍처는 C의 값/프레임 관찰까지만 하고 해당 ABI 자료로 연결합니다.
준비되지 않았다면 Ubuntu에서 `sudo apt install gcc gdb binutils`를 사용합니다.
pwn.zip을 풀고 pwn 폴더에서 진행합니다.

```sh
gcc -std=c11 -Wall -Wextra -Werror -g -O0 -fno-omit-frame-pointer call_bridge.c -o call-bridge
./call-bridge
gdb ./call-bridge
```
예상 출력: BIFROST value=7 answer=20. -O0와 프레임 포인터 옵션은 관찰용이며 운영 빌드 조건이 아닙니다.

## 먼저 값과 저장 구간을 그리기

```text
정적 저장: seed=7 (쓰기 가능한 초기화 데이터), banner="BIFROST" (읽기 전용 배치 관찰)
main 프레임: value=7 ──값 복사──▶ adjust 프레임: base=7
                                    bumped=10 → result=20
              answer=20 ◀──반환──
코드 영역: main/adjust 명령어. 실제 ELF 섹션·세그먼트/매핑과 C 저장기간은 구분한다.
```

| 멈춘 시점 | base | bumped | result | main.answer |
|---|---:|---|---|---|
| adjust 진입, 첫 대입 전 | 7 | 아직 읽지 않음 | 아직 읽지 않음 | 아직 대입 안 됨 |
| bumped 대입 뒤 | 7 | 10 | 아직 읽지 않음 | 아직 대입 안 됨 |
| result 대입 뒤 | 7 | 10 | 20 | 아직 대입 안 됨 |
| finish로 main 복귀 | adjust 프레임 종료 | 수명 종료 | 수명 종료 | 대입 완료 여부는 현재 명령 위치 확인 |

GDB 명령은 셸이 아니라 (gdb) 프롬프트에 한 줄씩 입력합니다.

```text
break adjust
run
list
info args
info locals
bt
frame 1
print value
frame 0
next
print bumped
next
print result
info registers rsp rbp rip rdi eax
x/4gx $rsp
info frame
x/gx ($rbp+8)
disassemble /m adjust
finish
print $eax
next
print answer
continue
quit
```

중단점 줄은 보통 다음 실행할 줄입니다. info locals에 숫자가 보여도 초기화 전 값은 근거로 사용하지 않습니다.
bt의 #0 adjust, #1 main은 서로 다른 호출 프레임입니다. frame은 관찰 대상을 바꾸며 실행을 진행시키지 않습니다.
RDI는 호출 진입 시 첫 정수 인자를 담는 규약입니다. 함수 내부에서는 재사용될 수 있으므로 어느 시점이든 항상 base라고 읽지 않습니다.
RSP는 현재 스택 위치, RBP는 이 빌드의 프레임 기준, RIP는 다음 명령 위치입니다.
x/4gx는 스택에서 8바이트 단위 네 개를 관찰합니다. 주소·잔여 바이트를 의미 있는 지역변수로 단정하지 않습니다.
이 x86-64 프레임 포인터 빌드에서 rbp+8은 저장된 복귀 주소 슬롯입니다. info frame의 saved rip 값과 대조합니다.
프로로그 전/에필로그 뒤·다른 ABI·최적화 빌드에서는 이 위치 규칙을 그대로 적용하지 않습니다.
finish는 현재 함수를 마치고 호출자로 돌아갑니다. 반환 직후 EAX=20을 확인하고 next 후 answer 대입을 확인합니다.
실제 멈춘 줄/명령을 함께 기록하세요. ASLR 주소 숫자가 다르거나 GDB의 ASLR 경고가 나와도 주소 일치를 완료 기준으로 삼지 않습니다.

코드/데이터 관찰: 셸에서 `readelf -S call-bridge`, GDB에서 `info files`, `info proc mappings`, `print &seed`, `print &banner`를 비교합니다.
이 프로그램은 힙 할당을 하지 않습니다. 기존 memory.c의 malloc 예제에서 힙을 따로 비교합니다. 모든 지역변수가 항상 스택에 있다는 규칙으로 일반화하지 않습니다.

직접 변경: base+3을 base+4로 바꾼 사본을 다시 빌드하고 bumped=11, result=22, 최종 answer=22를 예측·확인하세요.
최적화 -O2 빌드도 비교하되 지역변수/프레임이 사라지거나 이동하면 관찰 한계로 기록합니다.
보고서: 빌드·아키텍처 → 4행 상태표 → bt → 인자/반환 레지스터 → 복귀 주소 → 수정 전후. 관찰만으로 취약점 존재를 주장하지 않습니다.
