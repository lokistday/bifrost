# 네트워크·클라우드·암호 확장 검토

2026-10-26 작성. 기존 차시와 ID를 유지하고 각 분야 5개씩, 총 15개 차시를 추가했습니다.

## 학습 결손과 추가한 흐름

기존 네트워크 과정에는 패킷·정책·기본 탐지가 있지만 경로와 NAT/연결 상태를 연결하거나 탐지 성능을 수치로 검토할 실습이 부족했습니다. 다음 5개를 `04 · 경로·상태·운영 검증`에 추가했습니다.

1. `network.routing` — 최장 접두사와 돌아오는 경로
2. `network.nat-correlation` — NAT 주소·포트·시간으로 로그 연결
3. `network.connection-state` — 연결 상태와 응답 허용의 조건
4. `network.detection-metrics` — 정밀도·재현율과 탐지 임계값
5. `network.incident-correlation` — 네트워크 증거 연결과 대응 판단

클라우드는 책임·구성의 기초 이후 배포 주체·변경 계획·공급망·감사 범위·복구를 연결할 필요가 있었습니다. `03 · 배포·공급망·복구 운영`의 5개입니다.

1. `cloud.workload-trust` — 워크로드 신원과 역할 신뢰 조건
2. `cloud.iac-review` — 인프라 변경 계획과 영향 범위
3. `cloud.container-supply-chain` — 컨테이너 이미지와 공급망 근거
4. `cloud.audit-coverage` — 중앙 감사 로그의 범위와 중복
5. `cloud.recovery-exercise` — 백업 무결성과 RPO·RTO 복구 연습

암호는 기본 도구의 동작을 넘어 키 수명·키 유도·서버 신뢰·메시지 경계·신선도를 구분하도록 `04 · 키 수명과 프로토콜 검증`을 추가했습니다. 메시지 표현을 배운 뒤 재전송 모형으로 연결하도록 순서와 선행 조건을 맞췄습니다.

1. `crypto.key-lifecycle` — 키 상태·교체·침해 대응
2. `crypto.hkdf-context` — HKDF 추출·확장과 용도 분리
3. `crypto.certificate-trust` — 인증서 이름·기간·신뢰 경로
4. `crypto.message-encoding` — 메시지 경계와 인증할 바이트
5. `crypto.replay-protection` — 유효한 태그와 재전송 방지

모든 차시에 4개 이상의 개념 설명, 3개 실행 단계, 예상 출력, 변경 과제, 구체적 해설, 2개의 오개념, 2개의 상황형 문제, 선행 차시와 공식 출처가 있습니다. 15개의 고유한 의미 도식은 `advanced-visuals.json`에서 root가 공통 원본으로 병합합니다.

## 정규 저작 파일

- `content/courses/network.json`, `cloud.json`, `crypto.json`
- `scripts/lab_sources/network/defense_models.py`, `defense-models.json`, `ADVANCED-GUIDE.md`
- `scripts/lab_sources/cloud/operations.py`, `operations.json`, `backup-records.json`, `ADVANCED-GUIDE.md`
- `scripts/lab_sources/crypto/design_checks.py`, `design-records.json`, `ADVANCED-GUIDE.md`
- `tests/advanced_expansion_test.py`

추가 패키지·계정·유료 자원 없이 Python 표준 라이브러리로 실행됩니다. 공통 생성기는 이 파일들을 `labs/`로 복사하고 ZIP·해시를 다시 만듭니다. 저작 보조 스크립트는 최종 산출물에서 제거합니다.

## 검증

`python -m unittest discover -s tests -p advanced_expansion_test.py -v` — 20개 테스트 통과.

테스트는 15개 본 예제와 45개 단계의 명령·출력을 직접 실행해 대조하고 다음 반례를 검증합니다.

- 경로의 fallback·미일치, NAT 목적지·포트·종료 경계·복수 매핑
- 연결 응답 생략·다른 연결·종료 뒤 데이터, 정밀도·재현율 분모 0
- 사고 관측 제거 뒤 잘못된 고정 집계·완전한 결론이 남지 않음
- OIDC 조건 누락·다른 주체·잘못된 형식, 이미지 digest와 실행 권한의 독립성
- 감사 로그의 계정·지역별 ID 범위와 중복
- RPO/RTO 정확한 경계와 1초 초과, 복구 전 대기 시간 포함, 잘못된 시각·목표 거부
- 실제 백업 파일의 SHA-256과 변조 바이트 불일치
- RFC 5869 A.1 시험 벡터, HKDF 문맥·길이 범위
- 퇴역·침해 키 권한 차이, 인증서 이름·기간·루트 표시의 독립성
- 유효한 태그의 재전송, 변경된 메서드·경로·본문·순번의 거부와 상태 불변
- 단순 연결이 같은 입력과 길이 접두사 구분, UTF-8 바이트 길이

## 실제 구현과 모형의 경계

- 네트워크는 패킷 전송·실제 NAT/라우터/방화벽 구현이 아닙니다. TCP 시퀀스·재전송·타임아웃 등이 생략되어 있습니다.
- R-17 연결 ID는 학습용 합성 근거입니다. 실제 DNS·방화벽 로그에 공통 애플리케이션 ID가 있다고 가정하지 않습니다.
- OIDC는 이미 인증된 메타데이터의 조건 비교이며 JWT 서명·시간 검증과 STS를 구현하지 않았습니다.
- IaC는 Terraform 계획이 아닌 합성 변경 표이며 자동 적용하지 않습니다.
- 컨테이너의 digest와 출처 표시는 가상입니다. 실제 레지스트리·서명·스캔은 수행하지 않습니다.
- 감사 범주 미관측은 활동 부재나 로깅 비활성화의 증명이 아닙니다.
- 복구는 시간 계산과 실제 표본 해시 비교입니다. 실제 서비스 restore 성공을 주장하지 않습니다.
- HKDF와 HMAC은 실제 표준 연산이지만 모든 키는 공개 교육값입니다. 인증서는 X.509 검증이 아닌 JSON 모형입니다. 메시지 표현·재전송은 독자 운영 프로토콜로 사용할 수 없습니다.

## 직접 열어 확인한 주요 일차 출처

- RFC 1812, 3022, 5382, 9293: https://www.rfc-editor.org/rfc/rfc1812 · https://www.rfc-editor.org/rfc/rfc3022 · https://www.rfc-editor.org/rfc/rfc5382 · https://www.rfc-editor.org/rfc/rfc9293
- NIST SP 800-41r1: https://csrc.nist.gov/pubs/sp/800/41/r1/final
- NIST SP 800-61r3: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- Google 정밀도·재현율: https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall
- AWS OIDC 역할·조건: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html · https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_iam-condition-keys.html
- Terraform plan: https://developer.hashicorp.com/terraform/tutorials/cli/plan
- Docker digest·런타임 보안: https://docs.docker.com/dhi/explore/security-concepts/digests/ · https://docs.docker.com/engine/security/
- SLSA provenance v1.2: https://slsa.dev/spec/v1.2/provenance
- AWS CloudTrail 데이터 이벤트·무결성: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/logging-data-events-with-cloudtrail.html · https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html
- AWS DR: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html
- NIST 키 관리: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final
- OWASP 키 관리: https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html
- RFC 5869, 5280, 9525, 9421, 2104: https://www.rfc-editor.org/rfc/rfc5869 · https://www.rfc-editor.org/rfc/rfc5280 · https://www.rfc-editor.org/rfc/rfc9525 · https://www.rfc-editor.org/rfc/rfc9421 · https://www.rfc-editor.org/rfc/rfc2104
- Python ipaddress·hashlib·hmac·struct: https://docs.python.org/3/library/ipaddress.html · https://docs.python.org/3/library/hashlib.html · https://docs.python.org/3/library/hmac.html · https://docs.python.org/3/library/struct.html

위 웹 출처는 2026-10-26 직접 열어 확인했습니다. 원문을 복사하지 않고 합성 데이터와 독자 설명·과제로 구성했습니다. 검토 중 구버전 철회 표기가 있는 NIST SP 800-34 경로와 열리지 않는 AWS whitepapers 경로는 본문 참고 링크에 사용하지 않았습니다.
