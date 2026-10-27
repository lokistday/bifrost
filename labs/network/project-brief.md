# 이중 스택 서비스의 정책과 관측 검증
웹·DB·관리 경로를 가진 서비스에 IPv6를 추가합니다. 주소 계열, 기본 거부, 순서가 있는 규칙을 함께 검증하고 탐지 오탐과 관측 공백을 설명하세요.

## 준비
원본 ZIP 폴더를 보관하고 전체 폴더의 작업용 사본에서 진행하세요. Python 3.10 이상,
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3를 사용합니다.
Crypto는 별도 가상 환경과 requirements.txt가 필요합니다. C/GDB 프로젝트는 WSL/Linux 기준입니다.
예상 180~300분(설치 제외, 저자 추정). 여러 번 나누어 진행해도 됩니다.

## 출력 계약
정책은 first-match이며 src/dst CIDR와 port가 모두 맞을 때 action을 적용합니다. 기본 DENY입니다. decisions는 흐름 순서의 판정입니다. TP/FP/FN은 별도 alerts 표본의 predicted/actual bool에서 계산합니다.
project-answer-template.json의 키·타입을 유지하고 실제 계산 결과를 새 JSON에 저장합니다.
값은 결과로 채우세요. 템플릿의 0과 빈 목록은 정답이 아닙니다.

## 수행 순서
1. A 표본의 IPv6 서비스 흐름이 왜 거부되는지 경계 그림을 그립니다.
2. 입력을 하드코딩하지 않는 정책 평가기를 작성하고 B의 좁은 IPv6 규칙을 비교합니다.
3. 탐지 혼동 행렬을 계산하고 수치가 정책의 안전성을 직접 입증하지 않는 이유를 적습니다.
4. traffic.pcap과 tls13.pcap에서 볼 수 있는 근거와 볼 수 없는 사용자·본문 정보를 구분하고 지연 로그·재조립 누락의 대응 계획을 씁니다.

## 결과 검사
1. project-answer-template.json을 answers-a.json으로 복사하고 직접 구한 결과를 넣습니다.
2. `python3 project.py check answers-a.json --variant a`
3. 새 B 표본을 독립적으로 풀어 `python3 project.py check answers-b.json --variant b`
4. 막혔을 때만 `python3 project.py example --variant a`와 project_reference.py를 읽습니다.
   참조 구현은 숨긴 정답이 아니라 공개 해설입니다. 읽은 뒤 새 반례로 다시 확인하세요.
검사기는 답안 JSON만 읽습니다. 제출된 코드 실행·네트워크 전송·자동 진도 저장은 없습니다.
성공 0, 결과 불일치 1, 답안 형식 오류 2의 종료 상태를 사용합니다.

## 평가와 복습
- 주소 계열·규칙 순서·기본 거부를 정확히 적용했다.
- 정상 웹·DB 흐름과 관리·다른 IPv6 목적지 거부를 함께 확인했다.
- TP/FP/FN과 정밀도·재현율을 정확히 설명했다.
- PCAP 프레임 근거·TLS 가시성·관측 공백·롤백 조건을 포함했다.
각 항목 0(없음)·1(설명만)·2(재현 근거 있음), 합계 8점의 자기 평가입니다.
다음으로 넘어갈 기준은 각 항목의 근거를 확보하는 것입니다. 점수는 자격 인증이 아닙니다.
1~3일 뒤 답안을 닫고 B 또는 자신이 만든 변형을 풀어 재현 여부를 확인하세요.

## 실제 형식과 연결
제공된 실제 형식 PCAP을 Wireshark 또는 tshark -r로 읽고 프레임 번호를 보고서에 붙입니다. 라이브 스캔이나 외부 패킷 전송은 필요 없습니다.

## 범위와 한계
모형 정책은 실제 방화벽 설정이 아닙니다. NAT·상태 추적·IPv6 확장 헤더·공급자 의미는 별도 검증이 필요합니다.
