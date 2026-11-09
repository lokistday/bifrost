# C 배열·문자열·함수를 주소 실습에 연결

Ubuntu/WSL에서 gcc와 텍스트 편집기를 사용합니다. gcc가 없으면 환경 준비 안내에 따라 설치합니다.
foundation.zip을 풀고 foundation 폴더에서 진행합니다.

1. c_basics.c를 읽고 출력부터 예상합니다. 배열 values는 int 객체 세 개, 인덱스는 0·1·2입니다.
2. `gcc -std=c11 -Wall -Wextra -Werror -g -O0 c_basics.c -o c-basics` 후 `./c-basics`를 실행합니다.
3. 예상은 count=3 first=2 sum=15 / capacity=4 text_length=3 terminator=0입니다.

| sum_values 반복 전 i | 읽는 값 | 더한 뒤 total |
|---|---|---|
| 0 | 2 | 2 |
| 1 | 5 | 7 |
| 2 | 8 | 15 |
| 3 | 읽지 않음: i < count가 거짓 | 반환 15 |

sum_values는 배열 첫 원소의 위치와 개수를 인자로 받습니다. return은 합계를 호출자로 돌려줍니다.
배열이 선언된 main 범위에서는 sizeof values / sizeof values[0]로 원소 수를 계산할 수 있습니다.
함수의 items는 포인터이므로 sizeof items로 원본 배열 길이를 알아낼 수 없습니다.
이 함수는 작은 정수의 유효한 배열과 정확한 개수를 받는 연습입니다. 임의 크기/포인터/정수합의 안전성을 보장하지 않습니다.

char label[]="LAB"의 저장 바이트는 [L][A][B][00]입니다. 마지막 00은 문자 '0'(0x30)과 다릅니다.
sizeof label은 저장공간 4바이트, strlen은 첫 NUL 앞의 길이 3입니다. label[3]은 유효하지만 values[3]은 경계 밖입니다.
확인한다며 경계 밖 값을 읽지 않습니다. C에서 범위 밖 읽기는 정해진 오류 출력이 아니라 정의되지 않은 동작입니다.

직접 작성: 원본은 남기고 c_basics.c를 c_basics_practice.c로 복사합니다.
values를 {3,6,9,12}, label을 "HI"로 바꾸고 같은 함수로 빌드하세요.
예상 count=4 first=3 sum=30 / capacity=3 text_length=2입니다.
이때 종결자 출력의 label[3]도 label[2]로 바꿔야 합니다. 새 배열 범위를 먼저 확인하세요.
다음에는 함수 이름과 출력문을 유지한 채 for 합계를 while 합계로 직접 바꾸어 결과를 비교합니다.
포인터 상자 그림 → 배열의 연속 원소 → 길이를 명시한 함수 호출 → 시스템 보안의 경계/수명 순서로 이어갑니다.
