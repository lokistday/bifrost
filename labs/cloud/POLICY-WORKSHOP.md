# 실제 정책 문서로 이어지는 클라우드 보안

## 구조부터 그리기

```text
계정 / 프로젝트  ─ 권한·소유권의 관리 경계
  ├ 사람 신원 / 워크로드 역할 ─ 어떤 작업을 어떤 자원에 허용할까?
  └ 리전 ─ 배치 지역 (IAM의 모든 자원이 리전별이라는 뜻은 아님)
      └ 가용 영역 ─ 장애 범위를 나누는 배치 단위
          └ VPC / 서브넷 / 경로 / 보안 그룹 ─ 어디로 도달할까?
데이터 저장소 ─ 누가 읽고, 무엇을 기록하고, 어떻게 복구할까?
```

역할의 신뢰 정책은 누가 그 역할을 맡을 수 있는지, 권한 정책은 맡은 뒤 무엇을 할 수 있는지 다룹니다.
네트워크 도달, TLS 신뢰, IAM 허용은 별도 조건입니다. 사설 주소만으로 권한이 생기지 않습니다.
직접 VM을 운영하는 경우와 SaaS를 사용하는 경우의 패치·신원·데이터 책임도 나누세요.

## 실제 AWS IAM 정책 JSON 읽기

cloud.zip 전체를 풀고 cloud 폴더에서 실행합니다. Windows는 python3 대신 py -3를 사용합니다.
`iam-reader.json`은 실제 IAM 정책 형식의 교육 문서입니다. 클라우드에 업로드하거나 자원을 만들지 않습니다.
Version은 정책 언어 버전, Statement는 규칙 묶음, Sid는 읽기용 식별자입니다.
Effect는 Allow/Deny, Action은 s3:GetObject 같은 서비스 작업, Resource는 대상 ARN입니다.
`arn:aws:s3:::bifrost-training-notes/*`는 객체 범위입니다. 버킷 자체 ARN과 같지 않습니다.
ListBucket은 버킷 범위의 별도 작업입니다. GetObject만으로 버킷 목록 조회가 허용되는 것은 아닙니다.
이 버킷 이름은 문서용 가정이며 실제 소유권·존재를 확인한 대상이 아닙니다.

```text
python3 policy_workshop.py iam
python3 policy_workshop.py iam --action s3:DeleteObject
python3 policy_workshop.py iam --resource arn:aws:s3:::bifrost-training-notes/private/key.txt
python3 policy_workshop.py iam --resource arn:aws:s3:::other-bucket/readme.txt
```

예상 결과: ALLOW_MODEL / IMPLICIT_DENY_MODEL / EXPLICIT_DENY_MODEL / IMPLICIT_DENY_MODEL.
모든 Statement를 읽고 넓은 Allow와 private/*의 명시적 Deny가 겹치는 이유를 설명하세요.
사본에서 Allow의 Action을 s3:*로 바꾸면 DeleteObject가 허용되는지 비교하고 변경 위험을 기록합니다.
검사기는 단일 신원 정책의 Action/Resource 와일드카드와 Effect만 평가합니다.
Condition·Principal·NotAction·정책 변수·리소스 정책·경계·SCP·신뢰 정책은 미지원이며 발견 시 종료 2입니다.
미지원 조건을 무시하고 Allow로 바꾸지 않습니다. 실제 AWS 허용 결과를 인증하는 도구가 아닙니다.
선택 확장: 승인된 별도 교육 계정에서 AWS 정책 시뮬레이터 결과와 대조하되, 정책 부착·유료 자원 생성은 이 과정에 필요하지 않습니다.

## Kubernetes 문서와 오프라인 판정

`role-example.yaml`은 실제 Role/RoleBinding 문법을 보여 줍니다.
`rbac-resources.json`은 같은 역할·바인딩과 준비 자원을 담은 실제 Kubernetes List입니다.
YAML/JSON은 표현 방식이며 둘 다 Kubernetes 리소스를 표현할 수 있습니다.
Role.metadata.namespace는 자원 범위, subjects.namespace는 ServiceAccount가 속한 곳입니다.
rules.apiGroups의 빈 문자열은 core API 그룹입니다. resources=pods와 verbs=get/list를 한 행씩 읽으세요.

```text
python3 policy_workshop.py rbac
python3 policy_workshop.py rbac --resource secrets
python3 policy_workshop.py rbac --namespace bifrost-other
python3 policy_workshop.py rbac --subject-namespace bifrost-other
```

예상: ALLOW_MODEL, 나머지는 NO_ALLOW_IN_THIS_DOCUMENT.
한 문서에 허용이 없다는 뜻이며 실제 클러스터의 모든 바인딩에서 거부된다는 판정이 아닙니다.
Role에 secrets/get을 추가한 사본에서 첫 거부 결과가 바뀌는지 확인합니다.
모형은 namespaced Role·RoleBinding·ServiceAccount만 지원합니다. ClusterRole, resourceNames, 서브리소스 등은 별도 과정입니다.

## 선택: 격리된 로컬 클러스터에서 실제 검증

Docker/Podman, kind, kubectl이 이미 준비된 학습자만 수행합니다. 설치·최초 이미지 다운로드에는 인터넷·디스크 공간이 필요합니다.
AWS/Azure/GCP 계정과 유료 클라우드 자원은 만들지 않습니다. 컨테이너 실행 환경의 이용 조건·자원은 별도 확인하세요.
현재 운영 클러스터에 적용하지 않고 아래 이름의 새 교육 클러스터만 사용합니다.

```text
kind create cluster --name bifrost-lab
kubectl --context kind-bifrost-lab apply -f rbac-resources.json
kubectl --context kind-bifrost-lab auth can-i get pods -n bifrost-learn --as=system:serviceaccount:bifrost-learn:reader
kubectl --context kind-bifrost-lab auth can-i get secrets -n bifrost-learn --as=system:serviceaccount:bifrost-learn:reader
kubectl --context kind-bifrost-lab auth can-i get pods -n bifrost-other --as=system:serviceaccount:bifrost-learn:reader
```

기본 교육 클러스터에서 예상 yes / no / no. --as는 관리자 권한으로 수행하는 인가 질의이며 실제 ServiceAccount 토큰 인증 시험은 아닙니다.
다른 바인딩이나 권한 설정이 있으면 결과가 달라질 수 있으므로 결과·정책·컨텍스트를 함께 기록합니다.
상태 코드/프로그램 종료 상태도 함께 보며 no의 종료 1을 도구 실행 오류와 구분합니다.
정리: `kind delete cluster --name bifrost-lab` (위에서 만든 해당 교육 클러스터만 삭제).
이 과정은 선택 실습이며 사이트 작성자가 모든 학습자 환경의 클러스터 실행을 검증했다는 뜻은 아닙니다.

## 독립 변경 검토

정상 pods 읽기는 유지하면서 secrets 조회·다른 네임스페이스 접근은 거부하는 문서를 직접 작성하세요.
변경 전후 정책 차이, 허용/거부 표, 미지원 항목, 실제 실행 여부, 정리 결과를 보고서로 묶습니다.
권한 판정과 네트워크 연결 성공, 실제 데이터 읽기 성공을 한 결론으로 합치지 않습니다.

참고: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html
참고: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
