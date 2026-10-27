# 길이·NUL·부분 입력에 견디는 작은 C 파서
표본 레코드의 첫 2바이트는 big-endian 본문 길이입니다. 최대 8바이트 본문만 허용하고 잘림·후행 데이터·중간 NUL을 구분하세요.

## 준비
원본 ZIP 폴더를 보관하고 전체 폴더의 작업용 사본에서 진행하세요. Python 3.10 이상,
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3를 사용합니다.
Crypto는 별도 가상 환경과 requirements.txt가 필요합니다. C/GDB 프로젝트는 WSL/Linux 기준입니다.
예상 180~270분(설치 제외, 저자 추정). 여러 번 나누어 진행해도 됩니다.

## 출력 계약
한 레코드는 정확히 2+선언 길이 바이트여야 합니다. 길이 0은 허용하며 8 초과는 거부합니다. accepted_ids는 입력 순서, payload_sum은 허용 본문의 unsigned 바이트 합, nul_ids는 허용 본문에 NUL이 있는 ID입니다.
project-answer-template.json의 키·타입을 유지하고 실제 계산 결과를 새 JSON에 저장합니다.
값은 결과로 채우세요. 템플릿의 0과 빈 목록은 정답이 아닙니다.

## 수행 순서
1. project-parser-starter.c의 parse 함수만 완성하세요. 호출자가 가진 버퍼와 출력 포인터의 계약도 적습니다.
2. 자체 C 테스트 main을 만들어 A/B의 Hex를 바이트 배열로 실행합니다.
3. 길이 0/8/9·1바이트 헤더·잘림·후행 데이터·NUL을 검사하고 Sanitizer에서도 실행합니다.
4. 결과를 JSON으로 모아 검사기에 전달하고 메모리 소유권·부분 I/O 연결의 한계를 보고합니다.

## 결과 검사
1. project-answer-template.json을 answers-a.json으로 복사하고 직접 구한 결과를 넣습니다.
2. `python3 project.py check answers-a.json --variant a`
3. 새 B 표본을 독립적으로 풀어 `python3 project.py check answers-b.json --variant b`
4. 막혔을 때만 `python3 project.py example --variant a`와 project_reference.py를 읽습니다.
   참조 구현은 숨긴 정답이 아니라 공개 해설입니다. 읽은 뒤 새 반례로 다시 확인하세요.
검사기는 답안 JSON만 읽습니다. 제출된 코드 실행·네트워크 전송·자동 진도 저장은 없습니다.
성공 0, 결과 불일치 1, 답안 형식 오류 2의 종료 상태를 사용합니다.

## 평가와 복습
- 경계·잘림·후행 바이트를 정확히 판정하고 두 표본 결과가 일치한다.
- 길이를 검사하기 전에 헤더/본문을 읽지 않는다.
- 본문 길이를 strlen으로 대체하지 않고 호출자 객체의 수명을 지킨다.
- 정상·거부 테스트와 컴파일 옵션·Sanitizer 기록을 제공한다.
각 항목 0(없음)·1(설명만)·2(재현 근거 있음), 합계 8점의 자기 평가입니다.
다음으로 넘어갈 기준은 각 항목의 근거를 확보하는 것입니다. 점수는 자격 인증이 아닙니다.
1~3일 뒤 답안을 닫고 B 또는 자신이 만든 변형을 풀어 재현 여부를 확인하세요.

## 실제 형식과 연결
gcc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined로 자체 C 테스트를 실행하고 Python 참조 결과와 비교합니다.

## 범위와 한계
작은 완성 버퍼의 파서입니다. 실제 네트워크 프레이밍·재시도·파일 경쟁 조건까지 이 함수가 해결하는 것은 아닙니다.
