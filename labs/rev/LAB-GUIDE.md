# Reverse · 형식과 흐름 확장 실습

모든 자료는 Bifrost가 직접 작성한 작은 교육 프로그램입니다. 악성코드·실제 서비스·타인의 바이너리를 다루지 않습니다. 이 ZIP에는 소스만 제공하며 실행 파일은 직접 빌드합니다. 기존 `check.c`와 새 자료를 함께 유지하세요.

## 준비

- Python 3.10 이상: Linux/macOS `python3`, Windows PowerShell `py -3`.
- `calling.c`, `flow.c`와 디버깅: Ubuntu/WSL x86-64, GCC·GDB·GNU binutils. C 명령은 Bash에서 실행합니다.
- 결과 주소·기계어 배치·GDB 번호는 컴파일러와 실행마다 달라집니다. 값과 경로를 비교하세요.

## 파일과 실행

| 차시 | 실행 | 기준 결과 |
| --- | --- | --- |
| 바이트 순서 | `python3 binary_lab.py` | little=3, big=768, payload=ABC |
| 호출 규약 | `gcc -g -O0 -Wall -Wextra calling.c -o calling` 후 `./calling` | result=20 |
| 제어 흐름 | `gcc -g -O0 -Wall -Wextra flow.c -o flow` 후 `./flow 4 -2 6 0 99` | sum=10 |
| 데이터 흐름 | `python3 dataflow.py BIF` | hex=626a68, roundtrip=True |
| 차등 검증 | `python3 differential.py` | cases=5 mismatches=1 |

## 해석과 변경 과제

`binary_lab.py`의 BF는 서명 2바이트, little-endian 길이 2바이트, 본문이라는 가상의 형식입니다. 전체 길이 일치와 64바이트 상한을 검증합니다. 잘린 입력·여분 입력·서명 오류를 서로 다른 반례로 기록하세요. 실제 ELF 파서나 문서 복구기가 아닙니다.

`calling.c`는 x86-64 System V ABI의 int 인자 예제입니다. GDB에서 `break *combine`, `run`, `info registers edi esi edx`로 3·5·7을 관찰하고 `finish`, `print $eax`로 20을 확인합니다. 프롤로그 전의 소스 변수 표시는 아직 유효하지 않을 수 있습니다. Windows x64 규약에 그대로 적용하지 마세요. 두 번째 인자를 6으로 바꾼 사본의 함수 결과는 22이며 main의 고정 비교식 때문에 종료 상태는 1입니다.

`flow.c`는 음수에서 continue, 0에서 break입니다. 원소는 1~8개, -100~100으로 제한합니다. `4 -2 6 0 99`는 10, 0을 제거하면 109, 첫 원소가 0이면 0입니다. 최종 합뿐 아니라 방문 원소와 누적 상태를 적으세요.

`dataflow.py`는 `(byte ^ 32) + index`와 그 역변환을 추적합니다. 암호화 도구가 아닙니다. 잘못된 역순도 AAA에서 우연히 통과하지만 A?에서는 실패합니다. 같은 입력만 반복하지 말고 비트 연산의 경계를 넘는 반례를 만드세요.

`differential.py`의 candidate는 의도적으로 여분 바이트를 허용합니다. 원본은 보존하고 사본에서 `<`를 `!=`로 수정한 뒤 다섯 사례 및 `b'BF\x00\x00!'` 최소 반례를 비교하세요. 고정 사례 통과는 모든 입력의 동등성이나 보안성 증명이 아닙니다.
