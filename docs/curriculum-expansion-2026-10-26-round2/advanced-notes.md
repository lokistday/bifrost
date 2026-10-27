# 2차 확장: 네트워크·클라우드·암호

2026-10-26. 기존 108개 차시·실습·해설을 보존하며 이 그룹에서15개 차시를 추가했습니다. 네트워크14→19, 클라우드12→17, 암호14→19입니다. 각 분야에 모듈1개씩 추가했습니다.

## 추가 차시와 보완한 공백

기존 경로·NAT·연결 상태·탐지·사건 연결에 이어 프로토콜 해석과 관측의 경계 조건을 다룹니다.

- `network.ipv6-boundaries` — IPv6 주소 범위와 정책의 빈틈
- `network.stream-reassembly` — 스트림 재조립과 누락·겹침
- `network.dns-cache` — DNS TTL과 부정 응답 캐시
- `network.path-mtu` — MTU·PMTUD와 큰 전송의 실패
- `network.event-time-windows` — 사건 시각·지연 도착과 세션 경계

기존 워크로드 신뢰·IaC·공급망·감사·복구에서 다른 워크로드와 정책 경계로 확장합니다.

- `cloud.effective-permissions` — 실효 권한과 허용 범위의 교집합
- `cloud.kubernetes-rbac` — Kubernetes 네임스페이스와 RBAC
- `cloud.metadata-credentials` — 메타데이터 서비스와 자격 증명 경계
- `cloud.private-endpoint-paths` — 프라이빗 엔드포인트와 DNS 경로
- `cloud.breakglass-access` — 긴급 접근의 만료·회수·증거

기존 키 수명·HKDF·인증서·재전송·메시지 표현을 실제 레코드 연산과 사용 규칙으로 연결합니다.

- `crypto.aad-record-binding` — AEAD와 레코드 문맥의 결합
- `crypto.verifier-migration` — 비밀번호 검증값의 버전과 재해시
- `crypto.envelope-keywrap` — 봉투 암호화와 DEK 재포장
- `crypto.signature-authorization` — 서명 문맥과 업무 권한
- `crypto.unbiased-randomness` — 난수의 예측 가능성과 나머지 편향

각 차시에4개 개념 단락,3개 실행 단계와 정확한 예상 출력, 구체적인 변경 과제와 풀이,2개 오개념,2개 상황형 문제, 선행 차시·일차 출처를 넣었습니다. 고유 도식15개는 `advanced-visuals.json`에서 공통 원본에 병합합니다.

## 정규 저작 원본

- `content/courses/network.json`, `cloud.json`, `crypto.json` — 새 모듈만 추가
- `scripts/lab_sources/network/protocol_models.py`, `protocol-models.json`, `ROUND2-GUIDE.md`
- `scripts/lab_sources/cloud/boundary_models.py`, `boundary-models.json`, `ROUND2-GUIDE.md`
- `scripts/lab_sources/crypto/record_crypto.py`, `round2-crypto.json`, `ROUND2-GUIDE.md`
- `tests/advanced_round2_expansion_test.py`

기존 `requirements.txt`는 변경하지 않았습니다. 암호의 aad/envelope/context 세 모드만 기존 선택 패키지 cryptography가 필요합니다. 나머지12개 차시는 표준 라이브러리입니다. 패키지는 설치하지 않고 이미 존재한 `.lab-test-deps`를 시험에 재사용했습니다. 방문자는 기존 가상환경·설치 안내를 이용하거나 본문·해설을 읽을 수 있습니다.

임시 author 스크립트는 제거했습니다. 공유 생성기·레지스트리·HTML·JS·실습 ZIP은 부모 작업에서 통합합니다.

## 검증 결과

```text
# 이미 있는 선택 패키지를 재사용한 Windows PowerShell 검증
$env:PYTHONPATH='D:\Bifrost\.lab-test-deps'
python -m unittest discover -s tests -p advanced_round2_expansion_test.py -v
```

**24개 테스트 통과, 건너뜀0.** 새로운15개 본 예제와45개 단계 명령의 출력을 직접 비교했습니다. 환경 의존성이 없을 때의 세 암호 모드 안내와 표준 라이브러리 모드의 독립 동작도 `-I -S`로 확인했습니다.

추가 반례:

- IPv4/IPv6 규칙 분리·link-local 인터페이스와 허용의 독립성
- 스트림 순서 변경·동일 중복·누락·충돌·음수와 범위 밖 offset
- DNS TTL 정확한 만료·부정 TTL 최솟값·NXDOMAIN/NODATA 타입 범위
- IPv4/IPv6·옵션 헤더의 MTU 예산, IPv6 최소 MTU 미지원 조건 거부
- watermark와 같은 시각 수락, timeout과 같은 간격 분리, 지연 사건으로 세션 병합, 비정상 시각 입력
- 권한 경계의 비부여 성질·명시적 거부 우선·자원 정책 미지원 표시
- RBAC 주체/자원 네임스페이스·API 그룹·다른 ServiceAccount
- 메타데이터 토큰 요구·네트워크 차단·엔드포인트 비활성의 독립성
- 사설 DNS와 신원·엔드포인트 권한의 독립성
- 긴급 권한 시작/만료·마이크로초 경계·회수·행동/자원/승인·timezone 검증
- 잘못된 비밀번호의 갱신 금지·비용 하향 금지·알고리즘/형식/비용/길이 검증
- 실제 AES-GCM의 tenant/document/version AAD 거부와 평문 미반환
- 실제 새 envelope의 원본 불변·동일 암호문·새 DEK 포장·실제 복호화
- 잘못된 KEK·포장 변조·암호문 변조의 실제 암호 연산 거부
- 실제 Ed25519의 문맥/행동/자원/공개키 변경 거부, 서명 의미와 업무 인가의 독립성
- 나머지별 정확한 대응 수·거부 샘플링 경계·잘못된 bound·무한 거부 제한

## 모형과 실제 보장의 한계

- 네트워크 모형은 실제 스택·DNS 리졸버·PCAP 재조립기가 아닙니다. IPv6 분류는 일부만 제공하며 `other-ipv6`는 전역 주소 판정이 아닙니다.
- 스트림 offset은 정규화했다고 가정했고 sequence wrap·연결 식별·IP 조각을 생략했습니다. 누락·충돌을 임의로 채우지 않습니다.
- MTU의 STALLED는 다른 회복이 없는 시나리오 가정입니다. 모든 스택의 PLPMTUD·회복 실패를 주장하지 않습니다.
- 시각 집계는 한 분석 키만 다룹니다. timeout 이상은 새 세션, watermark 미만은 지연이라는 정확한 경계를 명시했습니다.
- 권한 교집합은 제한된 신원 정책 경로입니다. 실제 자원 정책·세션·조직 정책을 단순 교집합으로 일반화하지 않고 미지원으로 남깁니다.
- RBAC는 한 Role/RoleBinding만 다룹니다. 실제 허용은 다른 바인딩에서 더해질 수 있습니다. namespace는 완전 격리가 아닙니다.
- 메타데이터의 token_valid는 가정된 입력이며 실제 토큰·URL을 처리하지 않습니다. IMDSv2만으로 모든 SSRF·코드 실행 영향을 해결하지 않습니다.
- 사설 DNS는 자원 권한·공용 접근 비활성·TLS를 대신하지 않습니다. 긴급 접근의 실제 권한 회수 지연·승인자 인증·세션은 미구현입니다.
- AES-GCM/AES-KW/Ed25519는 실제 검증된 라이브러리 연산입니다. 모든 고정 키는 공개 시험값이고 이 표본으로 서비스를 만들지 않습니다.
- AAD 기대값은 인가된 요청에 결합해야 하며 비밀을 숨기지 않습니다. 실패한 평문은 반환하지 않습니다.
- KEK 재포장은 DEK 교체가 아니며 과거 KEK·포장 사본 노출은 별도 대응이 필요합니다. 주변 키 ID·권한은 별도 신뢰 매핑 대상입니다.
- 서명 검증은 신뢰한 키 매핑·업무 권한·만료·재사용을 대신하지 않습니다. 재해시 예제의 비용은 운영 권장값이 아닙니다.
- 고정 난수 입력은 분기 시험용입니다. 실제 범위 검사의 True 한 번으로 난수 품질을 주장하지 않습니다.

## 웹에서 직접 확인한 일차 출처

2026-10-26 직접 열어 내용을 확인했고, 새 차시별로2개 이상을 연결했습니다. 원문을 복사하지 않고 독자 설명과 합성 표본으로 구성했습니다.

- RFC4291: https://www.rfc-editor.org/rfc/rfc4291
- RFC4890: https://www.rfc-editor.org/rfc/rfc4890
- RFC8201: https://www.rfc-editor.org/rfc/rfc8201
- RFC9293: https://www.rfc-editor.org/rfc/rfc9293
- RFC1035: https://www.rfc-editor.org/rfc/rfc1035
- RFC2308: https://www.rfc-editor.org/rfc/rfc2308
- Wireshark 재조립: https://www.wireshark.org/docs/wsug_html_chunked/ChAdvReassemblySection.html
- Apache Flink 시각: https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/
- Python 정렬: https://docs.python.org/3/howto/sorting.html
- AWS IAM 평가와 경계: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html · https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
- Kubernetes RBAC·주체: https://kubernetes.io/docs/reference/access-authn-authz/rbac/ · https://kubernetes.io/docs/concepts/security/service-accounts/
- AWS 메타데이터·역할 자격: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html · https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-metadata-security-credentials.html
- AWS 사설 경로·정책: https://docs.aws.amazon.com/vpc/latest/privatelink/privatelink-access-aws-services.html · https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-access.html
- AWS 권한 회수: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_disable-perms.html
- NIST 사고 대응: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- cryptography AEAD·Key Wrap·Ed25519: https://cryptography.io/en/latest/hazmat/primitives/aead/ · https://cryptography.io/en/latest/hazmat/primitives/keywrap/ · https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
- RFC3394·RFC9421: https://www.rfc-editor.org/rfc/rfc3394 · https://www.rfc-editor.org/rfc/rfc9421
- NIST GCM: https://csrc.nist.gov/pubs/sp/800/38/d/final
- OWASP 비밀번호: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- Python hashlib·secrets: https://docs.python.org/3/library/hashlib.html · https://docs.python.org/3/library/secrets.html
- PEP506: https://peps.python.org/pep-0506/

열리지 않은 AWS 긴급 접근 문서 경로는 차시 참고 자료에 넣지 않고 확인된 IAM 회수 문서와 NIST 지침을 사용했습니다.
