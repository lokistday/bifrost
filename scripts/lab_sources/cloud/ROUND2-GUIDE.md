# 권한 조합과 워크로드 경계

이 자료는 한정된 규칙을 설명하는 합성 모형입니다. AWS IAM/Kubernetes 평가기·IMDS·PrivateLink·권한 회수 API를 구현하지 않았습니다. 계정·클러스터·유료 자원·네트워크 접속이 필요하지 않습니다.

ZIP 전체를 풀고 Python 3.10 이상으로 실행하세요. Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`입니다. 표준 라이브러리만 사용합니다.

| 명령 | 핵심 결과 |
| --- | --- |
| `python3 boundary_models.py effective` | Read 허용, Write 경계 거부, 명시적 거부 우선, 자원 정책 미지원 |
| `python3 boundary_models.py rbac` | learn/viewer의 learn/pods get만 허용 |
| `python3 boundary_models.py metadata` | 토큰 누락·경로 차단·역할 행동을 별도 표시 |
| `python3 boundary_models.py private` | 사설 경로 허용, 공용 해석, 신원 거부, 엔드포인트 거부 구분 |
| `python3 boundary_models.py breakglass` | 만료1초 전 허용, 정확한 만료 시점·범위 밖 행동 거부 |

## 사본으로 바꾸어 볼 조건

`boundary-models.json`을 `boundary-work.json`으로 복사하고 `python3 boundary_models.py effective --input boundary-work.json`처럼 읽으세요. 원본과 변경 결과를 함께 보관합니다.

- **권한 교집합:** boundary_allow에 WriteNotes를 넣으면 P2 ALLOW_MODEL입니다. P3의 명시적 거부는 유지되고 P4는 계속 UNMODELED_RESOURCE_POLICY입니다. 실제 AWS 자원 정책의 직접 부여·주체 종류·세션 ARN은 조합 규칙이 달라 이 단순 교집합을 일반화하면 안 됩니다. 자원·조건·와일드카드·교차 계정도 모형 밖입니다.
- **RBAC:** binding.subject.namespace를 other로 바꾸면 K1 거부·K4 허용입니다. 자원 범위는 learn 그대로입니다. 같은 ServiceAccount 이름도 네임스페이스가 다르면 다른 주체입니다. 실제 RBAC는 다른 바인딩의 허용이 더해지며, 한 Role의 불허를 전역 Deny로 볼 수 없습니다. ClusterRoleBinding·서브리소스·resourceNames 등은 생략했습니다.
- **메타데이터:** tokens_required=false면 M1은 REACHABLE_MODEL로 바뀝니다. M3의 경로 차단과 역할의 DeleteNotes=False는 그대로입니다. token_valid는 실제 검증 결과를 가정한 입력입니다. IMDSv2는 모든 SSRF·코드 실행을 막는 완전한 신원 경계가 아니며 역할 최소 권한·불필요한 요청 경로 차단·노출 후 회수와 감사를 따로 검토합니다. 실제 메타데이터 주소는 요청하지 않습니다.
- **프라이빗 경로:** E2의 dns_target만 private-endpoint로 바꾸면 다른 조건이 모두 맞는 이 표본에서는 ALLOW_MODEL입니다. E3은 여전히 DENY_IDENTITY입니다. 사설 경로가 자원 공용 접근을 끄거나 IAM·TLS를 대신하지 않습니다. PUBLIC_PATH는 경로 분류이고 실제 허용·거부 결과가 아닙니다.
- **긴급 접근:** lease.revoked=true면 B1도 DENY_REVOKED입니다. 시간 구간은 시작 포함·만료 제외이며 timezone을 포함한 정확한 시각으로 비교합니다. 실제 권한 회수는 정책 전파·세션 종류에 영향을 받을 수 있어 기존 세션으로 효과를 확인해야 합니다. approved_by는 표시 문자열이며 승인자 인증 기능이 아닙니다.

## 결과물

요청의 주체·자원·행동·조건과 평가한 정책 범위를 적습니다. 미지원 결과를 운영 허용이나 거부로 바꾸어 쓰지 않습니다. 긴급 접근은 승인·활성화·수행 행동·회수·사후 검토를 같은 사건에 연결하고, 실제 권한이 사라졌다는 증거와 정상 관리 경로의 복구도 계획합니다.
