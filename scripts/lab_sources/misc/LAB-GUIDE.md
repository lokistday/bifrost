# Misc · 구조화·탐색·재현성 확장

Python 3.10 이상, 표준 라이브러리만 사용합니다. ZIP을 풀고 misc 폴더에서 Linux/macOS는 `python3`, Windows PowerShell은 `py -3`로 실행하세요. 원래 Base64 퍼즐과 새 자료는 별도 실습입니다. 새 도구는 외부 주소에 접속하거나 파일을 추출하지 않습니다.

| 명령 | 기준 결과 | 사본 과제 |
| --- | --- | --- |
| `python3 toolbox.py parse` | denied=L02,L04 / accepted=3 rejected-lines=3 | 중복 L02 추가, 잡음 행 수정 |
| `python3 toolbox.py archive` | notes.txt 후보, ../outside.txt 거부 / extracted=0 | 경로 후보 직접 비교 |
| `python3 toolbox.py graph` | start→inspect→report / edges=2 | 간선 제거로 길이 3·도달 불가 |
| `python3 toolbox.py constraints` | alice=2 bob=3 carol=1 / solutions=1 | 조건 제거 3해, 모순 추가 0해 |
| `python3 toolbox.py verify` | 순서 독립·값 변화 구별 모두 True | 입력 순서와 상태값 각각 변경 |

archive는 메모리의 고정 자료만 검사합니다. 나머지 명령의 사본은 `--source 파일명`으로 선택하세요.

## 실습 범위와 해설

**파싱:** fullmatch는 앞뒤 잡음이 붙은 행을 거부하고 이름 있는 그룹으로 필드를 추출합니다. ID 중복은 문법과 별도의 검사입니다. L02를 다섯 번째 줄에 추가하면 accepted=3, rejected-lines=3,5입니다. 원본 3번 줄을 정확히 `id=L03 user=carol status=denied`로 고치면 accepted=4이고 거부 행이 없어집니다. 실제 CSV/JSON에는 해당 형식의 파서를 먼저 검토하세요.

**압축 목록:** ../outside.txt는 의도적으로 위험한 이름이지만 실제로 추출되지 않습니다. safe_member는 이름의 절대경로·상위 이동·콜론만 검사하는 모형입니다. CON 같은 장치 이름도 통과하므로 CANDIDATE를 SAFE로 읽지 마세요. 링크·실제 대상 경로·덮어쓰기·대소문자 충돌·파일 수·총/개별 해제량·시간·중첩 깊이 등을 다루는 범용 안전 추출기가 아닙니다.

**그래프:** 모든 간선 비용이 같은 문제에서 BFS는 간선 수가 적은 경로를 찾습니다. inspect의 이웃을 []로 만들면 decode→parse를 거치는 3간선 경로, parse도 []이면 UNREACHABLE입니다. visited는 decode→start 순환을 막습니다. 실제 작업 시간이나 비용이 다르면 최소 단계 경로가 최소 비용을 뜻하지 않습니다.

**제약:** 세 사람의 6개 순열을 모두 검사합니다. not_at을 없애면 세 해가 남고 before에 bob<alice를 추가하면 모순이라 0해입니다. 답의 존재와 유일성을 구분하세요. 더 큰 문제에는 n! 증가 때문에 가지치기나 적합한 알고리즘이 필요합니다.

**재현성:** 이 모형의 events는 순서를 의미로 보지 않기로 계약했습니다. ID 정렬·키 정렬·고정 JSON 구분자로 정규화하며 값 변화는 보존합니다. 원본 정규화 SHA-256은 `b9d3a37611682440379f60a8ba04705e66a71a7b5f5e0f6bd8975c5b3b2a191c`입니다. 순서를 뒤집어도 같고 R02 상태를 바꾸면 달라집니다. 시간순 자체가 의미인 자료에는 이 정렬을 적용하지 마세요. 해시와 함께 입력·코드·명령·환경·계약을 남겨야 재현을 검토할 수 있습니다.
