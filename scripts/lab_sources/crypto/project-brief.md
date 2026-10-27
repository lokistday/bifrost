# 레코드 이동·재전송·키 교체의 검증 계획
실제 AES-GCM 표본을 문서별 문맥에 묶고 재전송 상태와 함께 검사합니다. 유효한 암호문이라는 사실과 지금 처리해도 된다는 결정을 분리하세요.

## 준비
원본 ZIP 폴더를 보관하고 전체 폴더의 작업용 사본에서 진행하세요. Python 3.10 이상,
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3를 사용합니다.
Crypto는 별도 가상 환경과 requirements.txt가 필요합니다. C/GDB 프로젝트는 WSL/Linux 기준입니다.
예상 180~270분(설치 제외, 저자 추정). 여러 번 나누어 진행해도 됩니다.

## 출력 계약
기존 round2-crypto.json의 공개 DEK를 사용합니다. AAD는 UTF-8 JSON 배열 ["project-v1",tenant,document,version,seq]를 공백 없이 직렬화한 바이트입니다. seq도 인증 대상입니다. 인증 실패는 AUTH_FAIL, 인증 성공 후 seq>last일 때만 ACCEPT하고 last를 갱신하며 그 외에는 REPLAY입니다. last는 이 연습의 단일 blue/17/1 스트림 상태입니다.
project-answer-template.json의 키·타입을 유지하고 실제 계산 결과를 새 JSON에 저장합니다.
값은 결과로 채우세요. 템플릿의 0과 빈 목록은 정답이 아닙니다.

## 수행 순서
1. 가상 환경에서 고정 requirements.txt를 설치하고 공개 교육 키라는 범위를 적습니다.
2. AES-GCM 검증과 시퀀스 검사 순서를 구현하고 A/B를 비교합니다.
3. 인증 실패 요청의 큰 seq가 정상 요청을 막지 않도록 실패 후 last 상태를 확인합니다.
4. 실제 봉투 재포장 예제를 실행한 증거와 정기 교체·유출 대응·서명 권한 검토를 함께 보고합니다.

## 결과 검사
1. project-answer-template.json을 answers-a.json으로 복사하고 직접 구한 결과를 넣습니다.
2. `python3 project.py check answers-a.json --variant a`
3. 새 B 표본을 독립적으로 풀어 `python3 project.py check answers-b.json --variant b`
4. 막혔을 때만 `python3 project.py example --variant a`와 project_reference.py를 읽습니다.
   참조 구현은 숨긴 정답이 아니라 공개 해설입니다. 읽은 뒤 새 반례로 다시 확인하세요.
검사기는 답안 JSON만 읽습니다. 제출된 코드 실행·네트워크 전송·자동 진도 저장은 없습니다.
성공 0, 결과 불일치 1, 답안 형식 오류 2의 종료 상태를 사용합니다.

## 평가와 복습
- 실제 인증 실패와 재전송 거부를 구분했다.
- 인증 실패한 요청이 상태를 갱신하거나 평문을 노출하지 않는다.
- A/B와 재시작·동시 처리의 한계를 설명한다.
- KEK/DEK 교체와 과거 노출·현재 권한을 구분해 검증 계획을 썼다.
각 항목 0(없음)·1(설명만)·2(재현 근거 있음), 합계 8점의 자기 평가입니다.
다음으로 넘어갈 기준은 각 항목의 근거를 확보하는 것입니다. 점수는 자격 인증이 아닙니다.
1~3일 뒤 답안을 닫고 B 또는 자신이 만든 변형을 풀어 재현 여부를 확인하세요.

## 실제 형식과 연결
실제 cryptography AESGCM.decrypt의 InvalidTag와 정상 평문을 관찰합니다. 통과해도 새 암호 프로토콜을 배포할 자격을 의미하지 않습니다.

## 범위와 한계
단일 스트림·단일 프로세스 교육 모형이며 실제 서비스의 원자성·지속 상태·nonce 발급 설계는 포함하지 않습니다. 공개 키·nonce를 운영에 재사용하지 않습니다.
