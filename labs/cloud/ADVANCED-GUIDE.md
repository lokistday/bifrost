# 배포·공급망·복구 운영 실습

Python 3.10 이상, 표준 라이브러리만 사용합니다. 실제 클라우드 계정·과금 자원·Docker·Terraform이 필요하지 않습니다. JSON은 공급자 형식이 아닌 합성 모형입니다. 어떤 명령도 외부 서비스에 연결하거나 배포하지 않습니다.

ZIP을 풀고 이 폴더에서 실행하세요. Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`를 씁니다. 전체 파일을 함께 유지하고 원본은 보관하세요.

| 명령 | 핵심 결과 |
| --- | --- |
| `python3 operations.py trust` | C1 MATCH, 다른 주체 C2와 다른 수신자 C3는 DENY |
| `python3 operations.py iac` | 공개 관리 접근·데이터 삭제·복제 수 변경 각각 검토 |
| `python3 operations.py image` | I1 네 항목 False, I2 네 항목 True |
| `python3 operations.py audit` | 3행·고유 사건 2개·중복 1개, object-read 미관측 |
| `python3 operations.py restore` | 잠재 손실 구간 20분·복구 45분, RPO 실패·RTO 충족·백업 해시 일치 |

## 각 결과가 뜻하는 범위

- **신뢰 조건:** claims는 실제 서명 검증을 마쳤다고 가정한 메타데이터입니다. 문자열 조건 MATCH는 인증 성공이 아닙니다. 서명·만료·키 갱신·재전송·STS는 미구현입니다. 역할을 맡을 신뢰와 맡은 후의 권한을 따로 검토합니다.
- **변경 계획:** 공개 확대와 데이터 삭제는 다른 영향이 있습니다. 일반 CHANGE_REVIEW도 승인 표시가 아닙니다. 데이터 자원을 되살리는 것과 데이터를 복원하는 것은 다릅니다.
- **이미지:** I2의 digest는 가상 문자열입니다. 존재 여부만 보는 provenance 표시는 실제 파일·서명 검증이 아닙니다. 태그·콘텐츠 식별·출처·취약점·실행 권한은 서로 다른 검토입니다.
- **감사:** 한 가상 공급자 안에서 account·region·event_id로 중복을 셉니다. 원본은 삭제하지 않습니다. object-read 행이 없다는 것은 현재 자료에서 못 봤다는 뜻이며 활동 없음이나 수집 비활성화를 증명하지 않습니다. 설정·통제 시험·전달 경로를 확인해야 합니다.
- **복구:** 사고에서 기능 확인까지의 시간을 RTO 실측으로 봅니다. 작업 시작 전 대기도 포함합니다. RPO는 사고와 최신 검증 백업 사이의 시간이고 실제 손실 건수와는 다릅니다. 초 단위로 목표와 비교합니다. 백업 해시는 공개 기준값과 바이트가 같은지 확인할 뿐 기준값의 진위나 서비스 복구 성공을 보장하지 않습니다.

## 과제의 작업 방법

`operations.json`을 `operations-work.json`으로 복사하세요. `python3 operations.py restore --input operations-work.json`처럼 실행합니다.

1. C1의 aud를 삭제하면 조건 DENY입니다. 주체 조건을 지워 다른 저장소까지 허용하는 것을 편의로 정당화하지 않습니다.
2. notes-data 삭제의 승인·복원·검증 계획을 별도로 씁니다.
3. I2의 uid=0, privileged=true로 바꾸면 pinned와 provenance_present는 True지만 두 실행 권한 항목은 False입니다.
4. 감사 행의 event_id만 모으면 잘못된 1개 사건이 됩니다. 복합 키 결과 2개와 비교합니다.
5. 최신 백업 시각을 09:45:00Z로 바꾸면 RPO15분 충족, 09:44:59Z는 한 초 초과로 실패합니다. 백업 파일이 같은 해시여도 데이터 시점 목표는 별도입니다.

`backup-records.json`은 수정 전 사본을 만들어 바이트 해시를 비교할 수 있습니다. `operations.py`는 이 파일을 스크립트 폴더에서 읽으며 구성 사본의 `backup_file`을 다른 위치로 바꾸지 않아도 됩니다. 자료 손상 실험은 작업용 폴더 전체를 복사해서 진행하세요.
