# 사설 경로와 긴급 권한을 검증하는 변경 검토
구성 변경 뒤에도 정상 업무는 유지하고 다른 네임스페이스·만료된 긴급 권한은 거부해야 합니다. 결과를 보안 승인 보고서로 정리하세요.

## 준비
원본 ZIP 폴더를 보관하고 전체 폴더의 작업용 사본에서 진행하세요. Python 3.10 이상,
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3를 사용합니다.
Crypto는 별도 가상 환경과 requirements.txt가 필요합니다. C/GDB 프로젝트는 WSL/Linux 기준입니다.
예상 180~300분(설치 제외, 저자 추정). 여러 번 나누어 진행해도 됩니다.

## 출력 계약
각 JSON은 기본 boundary-models.json에 적용할 독립적인 변형입니다. role_namespace, subject_namespace, lease_revoked만 바꿉니다. 기존 rbac/private/lease 판정 함수를 사용하고 각 요청의 결과를 입력 순서대로 출력합니다.
project-answer-template.json의 키·타입을 유지하고 실제 계산 결과를 새 JSON에 저장합니다.
값은 결과로 채우세요. 템플릿의 0과 빈 목록은 정답이 아닙니다.

## 수행 순서
1. 변경 전 역할·신뢰 주체·DNS 경로·승인 수명을 연결한 경계 그림을 만듭니다.
2. 기본 입력을 깊게 복사한 뒤 A/B 변경을 적용해 세 판정 목록을 만듭니다.
3. 잘못된 subject namespace를 넓은 권한으로 해결하지 않고 신뢰 대상과 바인딩을 점검합니다.
4. 실제 Kubernetes Role/RoleBinding JSON 초안, 변경 영향·감사 전달·복원 목표·롤백 증거를 보고서에 포함합니다.

## 결과 검사
1. project-answer-template.json을 answers-a.json으로 복사하고 직접 구한 결과를 넣습니다.
2. `python3 project.py check answers-a.json --variant a`
3. 새 B 표본을 독립적으로 풀어 `python3 project.py check answers-b.json --variant b`
4. 막혔을 때만 `python3 project.py example --variant a`와 project_reference.py를 읽습니다.
   참조 구현은 숨긴 정답이 아니라 공개 해설입니다. 읽은 뒤 새 반례로 다시 확인하세요.
검사기는 답안 JSON만 읽습니다. 제출된 코드 실행·네트워크 전송·자동 진도 저장은 없습니다.
성공 0, 결과 불일치 1, 답안 형식 오류 2의 종료 상태를 사용합니다.

## 평가와 복습
- 네임스페이스·주체·행동과 사설 경로·인가를 분리했다.
- 회수된 긴급 권한의 모든 사용이 거부되는지 확인했다.
- 정상 기능과 거부 기능을 함께 검증하고 모형 밖의 조건을 적었다.
- 제한된 Role/RoleBinding 초안과 감사·RPO/RTO·롤백 계획이 연결된다.
각 항목 0(없음)·1(설명만)·2(재현 근거 있음), 합계 8점의 자기 평가입니다.
다음으로 넘어갈 기준은 각 항목의 근거를 확보하는 것입니다. 점수는 자격 인증이 아닙니다.
1~3일 뒤 답안을 닫고 B 또는 자신이 만든 변형을 풀어 재현 여부를 확인하세요.

## 실제 형식과 연결
제공된 project-role.json의 apiVersion/kind/metadata/rules를 Kubernetes 공식 예제와 대조합니다. 선택적으로 격리된 본인 로컬 클러스터에서만 auth can-i로 검증하고 실제 결과와 모형 차이를 기록하세요.

## 범위와 한계
오프라인 권한 모형입니다. Kubernetes API나 실제 공급자 정책을 호출하지 않습니다. 모형 통과는 실제 배포 승인이나 보안 인증이 아닙니다.
