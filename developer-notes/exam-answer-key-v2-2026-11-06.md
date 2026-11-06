# 모의고사 v2 답안 검토표 · 2026-11-06

보기 순서 개편 후의 정답이다. 425문항 모두 기존 정답의 의미를 유지하고, 검토한 표현 보완을 반영했다.

## forensic-01 · 보존과 증거 읽기

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | forensic-m01-q01 | 3번 · 비교한 파일 내용 바이트의 일치 | forensic.integrity |
| 2 | forensic-m01-q02 | 3번 · 출처·수집 시각·담당자·파일 크기·도구 정보 | forensic.integrity |
| 3 | forensic-m01-q03 | 1번 · 보존용 원본과 작업 사본을 나누고 결과는 별도 폴더에 저장한다. | forensic.integrity |
| 4 | forensic-m01-q04 | 1번 · 원본 해시는 유지되고 사본 해시는 바뀐다. | forensic.integrity |
| 5 | forensic-m01-q05 | 4번 · 목록 자체를 신뢰할 수 있는 배포 경로나 서명 등 출처 근거 | forensic.integrity |
| 6 | forensic-m01-q06 | 2번 · 이름은 해시 입력이 아니므로 내용 해시는 같다. | forensic.integrity |
| 7 | forensic-m01-q07 | 1번 · 내용 바이트가 다르며 변경 원인은 작업 이력과 추가 비교가 필요하다. | forensic.integrity |
| 8 | forensic-m01-q08 | 1번 · 처음 수집한 자료 자체가 이미 잘못된 내용일 가능성은 별개이기 때문이다. | forensic.integrity |
| 9 | forensic-m01-q09 | 4번 · 이 실습의 증거 기록을 지칭하는 식별자 | forensic.logs |
| 10 | forensic-m01-q10 | 4번 · bob 계정의 로그인 거부 3건과 동일 출발지 | forensic.logs |
| 11 | forensic-m01-q11 | 2번 · 10초 | forensic.logs |
| 12 | forensic-m01-q12 | 3번 · 표본에 세션 식별자가 없기 때문이다. | forensic.logs |
| 13 | forensic-m01-q13 | 2번 · 모든 요청의 실제 행위자가 같은 사람이라는 것 | forensic.logs |
| 14 | forensic-m01-q14 | 2번 · 침해와 정상 사용 등 대안을 두고 세션·MFA·장치 자료를 추가 확인한다. | forensic.logs |
| 15 | forensic-m01-q15 | 4번 · MFA·장치·세션 기록과 사용자 확인·평소 로그인 패턴 | forensic.logs |
| 16 | forensic-m01-q16 | 3번 · 기록 시스템이 해당 계정의 로그인 성공을 남겼다. | forensic.logs |
| 17 | forensic-m01-q17 | 3번 · 대상 파일과 전송량·목적지·애플리케이션 기록을 추가 확인한다. | forensic.logs |
| 18 | forensic-m01-q18 | 2번 · 내용에 작성된 텍스트와 OS가 관리하는 소유자 속성은 출처가 다르다. | forensic.metadata |
| 19 | forensic-m01-q19 | 4번 · 추출·복사 환경의 현재 관찰값으로 남기고 사건 시각과 구분한다. | forensic.metadata |
| 20 | forensic-m01-q20 | 3번 · 두 파일의 내용 바이트가 완전히 같다는 주장 | forensic.metadata |
| 21 | forensic-m01-q21 | 3번 · 내용은 같아도 복사·추출 등으로 메타데이터가 다를 수 있다. | forensic.metadata |
| 22 | forensic-m01-q22 | 2번 · 마운트 설정과 캐시 등으로 접근 시각이 매번 갱신되지 않을 수 있다. | forensic.metadata |
| 23 | forensic-m01-q23 | 4번 · 플랫폼별 의미가 다르므로 생성 시각이라고 고정할 수 없다. | forensic.metadata |
| 24 | forensic-m01-q24 | 1번 · 나노초 단위 표현이 실제 나노초 정밀도를 보장하지는 않는다. | forensic.metadata |
| 25 | forensic-m01-q25 | 1번 · 경로·확장자가 달라도 동일한 내용 바이트일 수 있다. | forensic.metadata |

## forensic-02 · 시간 정규화와 보고

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | forensic-m02-q01 | 1번 · 2026-10-20T00:00:00+00:00 | forensic.timeline |
| 2 | forensic-m02-q02 | 4번 · 2026-10-19T16:30:00+00:00 | forensic.timeline |
| 3 | forensic-m02-q03 | 1번 · 표시 문자열 순서와 실제 순간 순서가 다를 수 있다. | forensic.timeline |
| 4 | forensic-m02-q04 | 3번 · 시각의 오프셋·시간대 정보 | forensic.timeline |
| 5 | forensic-m02-q05 | 4번 · 자료 출처의 시간대 설정과 가정을 확인한다. | forensic.timeline |
| 6 | forensic-m02-q06 | 1번 · 장비 시계 오차와 로그 수집 지연 | forensic.timeline |
| 7 | forensic-m02-q07 | 2번 · 원본 자료에 유지하고 정규화 결과와 연결한다. | forensic.timeline |
| 8 | forensic-m02-q08 | 1번 · 2026-10-20T00:02:00+00:00 | forensic.timeline |
| 9 | forensic-m02-q09 | 2번 · 아니다. 시간 순서는 관찰이며 인과에는 추가 근거가 필요하다. | forensic.timeline |
| 10 | forensic-m02-q10 | 1번 · 09:00+09:00의 사건 | forensic.timeline |
| 11 | forensic-m02-q11 | 3번 · 지역 시각에서 9시간을 빼 UTC를 구한다. | forensic.timeline |
| 12 | forensic-m02-q12 | 1번 · 표시 기준상 같은 순간이며 더 세밀한 선후·인과는 추가 근거가 필요하다. | forensic.timeline |
| 13 | forensic-m02-q13 | 3번 · E01 → E02 → E03 → E04 → E05 → E06 | forensic.timeline |
| 14 | forensic-m02-q14 | 2번 · 목적·자료와 해시·처리 절차·시간 기준·사실·해석·한계·후속 확인 | forensic.report |
| 15 | forensic-m02-q15 | 3번 · 해당 사실을 뒷받침하는 자료와 행·증거 ID | forensic.report |
| 16 | forensic-m02-q16 | 2번 · E06에 file_read 이벤트가 기록되어 있다. | forensic.report |
| 17 | forensic-m02-q17 | 2번 · 계정 탈취 후 파일을 열람했다. | forensic.report |
| 18 | forensic-m02-q18 | 4번 · 같은 대상·세션임을 확인할 연결 키가 추가로 필요하기 때문이다. | forensic.report |
| 19 | forensic-m02-q19 | 3번 · E05 세션 ID·MFA 결과와 E06 대상 파일·전송 기록을 확인한다. | forensic.report |
| 20 | forensic-m02-q20 | 4번 · 실제 외부 유출과 공격자 신원 | forensic.report |
| 21 | forensic-m02-q21 | 3번 · 확보한 자료만으로 유출 여부를 판단할 수 없다. | forensic.report |
| 22 | forensic-m02-q22 | 1번 · 관찰의 출처와 시간 변환을 독자가 추적하게 한다. | forensic.report |
| 23 | forensic-m02-q23 | 2번 · 보존된 원본을 기준으로 만든 작업 사본과 기록된 절차 | forensic.report |
| 24 | forensic-m02-q24 | 4번 · 검증할 질문과 필요한 자료를 적고 미확정으로 남긴다. | forensic.report |
| 25 | forensic-m02-q25 | 4번 · 보존 근거·시간 변환·증거 연결 관찰·대안 가설·한계·구체적 후속 요청 | forensic.report |

## forensic-03 · 수집과 호스트 근거

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | forensic-m03-q01 | 3번 · 조사 질문·승인 범위·대상 시스템과 시간 범위 | forensic.collection-plan |
| 2 | forensic-m03-q02 | 2번 · 메모리와 현재 연결 상태 | forensic.collection-plan |
| 3 | forensic-m03-q03 | 4번 · 진행 중인 피해·안전·운영 영향·조직 절차를 함께 고려한다. | forensic.collection-plan |
| 4 | forensic-m03-q04 | 2번 · 증거 ID·출처·수집 시각/시간대·담당자·도구·보관 위치·해시·인계 이력 | forensic.collection-plan |
| 5 | forensic-m03-q05 | 2번 · 지정한 order대로 합성 수집 계획을 표시한다. | forensic.collection-plan |
| 6 | forensic-m03-q06 | 1번 · 메모리·현재 연결 같은 휘발성 자료를 잃을 수 있다. | forensic.collection-plan |
| 7 | forensic-m03-q07 | 2번 · 사용 도구·조건과 상태 변경 가능성·실패·누락을 남긴다. | forensic.collection-plan |
| 8 | forensic-m03-q08 | 2번 · 승인자·예상 영향·보존할 근거와 순서 변경의 득실 | forensic.collection-plan |
| 9 | forensic-m03-q09 | 4번 · 부모·사용자·시작 시각·연결 등과 교차해 추가 조사 단서로 삼는다. | forensic.host-triage |
| 10 | forensic-m03-q10 | 2번 · viewer → helper → 203.0.113.44:443 | forensic.host-triage |
| 11 | forensic-m03-q11 | 4번 · PID 재사용이나 수집 시각 차이로 다른 프로세스를 붙일 수 있다. | forensic.host-triage |
| 12 | forensic-m03-q12 | 3번 · UNKNOWN으로 남기고 종료·수집 간격·권한·누락 가능성을 확인한다. | forensic.host-triage |
| 13 | forensic-m03-q13 | 3번 · 그 조인이 사라지므로 C01의 프로세스를 UNKNOWN으로 남긴다. | forensic.host-triage |
| 14 | forensic-m03-q14 | 1번 · 실행 경로·해시/서명, 명령줄·부모 시작 이벤트, 전송량·패킷 | forensic.host-triage |
| 15 | forensic-m03-q15 | 1번 · 실제 위험 인프라 접속과 데이터 유출 | forensic.host-triage |
| 16 | forensic-m03-q16 | 3번 · 호스트·수집 시각·프로세스 시작 시각 또는 고유 이벤트 ID | forensic.host-triage |
| 17 | forensic-m03-q17 | 1번 · 독자적인 합성 스키마와 ISO 시각을 쓰는 교육 표본 | forensic.browser-sqlite |
| 18 | forensic-m03-q18 | 4번 · 표시 2행 / 전체 3행 | forensic.browser-sqlite |
| 19 | forensic-m03-q19 | 3번 · 표시 3행 / 전체 3행 | forensic.browser-sqlite |
| 20 | forensic-m03-q20 | 1번 · 특정 사람이 의도적으로 페이지 내용을 읽었다는 것 | forensic.browser-sqlite |
| 21 | forensic-m03-q21 | 3번 · 최근 트랜잭션이 WAL에 남아 있을 수 있기 때문이다. | forensic.browser-sqlite |
| 22 | forensic-m03-q22 | 4번 · 질의 조건·전체 행수·표시 행수·제외 행 ID | forensic.browser-sqlite |
| 23 | forensic-m03-q23 | 1번 · 제품·버전별 스키마·시간 epoch·WAL과 수집 절차 | forensic.browser-sqlite |
| 24 | forensic-m03-q24 | 2번 · 실제 사용자의 신원과 행위 의도 | forensic.browser-sqlite |
| 25 | forensic-m03-q25 | 4번 · 메모리 DB이며 실제 사용자 프로필을 열지 않는다. | forensic.browser-sqlite |

## forensic-04 · 조각·상관·사고 대응

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | forensic-m04-q01 | 1번 · 확장자만 믿지 않고 시그니처와 내부 구조를 함께 확인한다. | forensic.file-signatures |
| 2 | forensic-m04-q02 | 4번 · 3바이트 | forensic.file-signatures |
| 3 | forensic-m04-q03 | 1번 · INCOMPLETE: 선언 길이보다 실제 사용 가능한 본문이 짧다. | forensic.file-signatures |
| 4 | forensic-m04-q04 | 2번 · XYZ12, 실제 본문 5바이트가 되어 가상 길이 계약상 COMPLETE | forensic.file-signatures |
| 5 | forensic-m04-q05 | 2번 · 아홉 번째 바이트 | forensic.file-signatures |
| 6 | forensic-m04-q06 | 2번 · 4바이트 | forensic.file-signatures |
| 7 | forensic-m04-q07 | 1번 · 화면에 인쇄하기 어려운 바이트의 표시일 수 있다. | forensic.file-signatures |
| 8 | forensic-m04-q08 | 2번 · 89 50 4e 47 0d 0a 1a 0a | forensic.file-signatures |
| 9 | forensic-m04-q09 | 2번 · 데이터 길이를 big-endian으로 나타낸다. | forensic.file-signatures |
| 10 | forensic-m04-q10 | 4번 · 25바이트 | forensic.file-signatures |
| 11 | forensic-m04-q11 | 1번 · 청크 종류와 청크 데이터 | forensic.file-signatures |
| 12 | forensic-m04-q12 | 3번 · 이미지 속성·압축 픽셀 데이터·끝 | forensic.file-signatures |
| 13 | forensic-m04-q13 | 2번 · 도구가 64×64 이하 RGB8 비인터레이스의 좁은 교육 계약만 지원한다. | forensic.file-signatures |
| 14 | forensic-m04-q14 | 1번 · 이 도구는 식별 단서를 표시했으며 내부 전체 디코딩·검증은 별도다. | forensic.file-signatures |
| 15 | forensic-m04-q15 | 3번 · 구조 검증 뒤 새 파일에 추출하고 원본 PNG와 바이트·SHA-256을 비교하며 뷰어로 확인한다. | forensic.file-signatures |
| 16 | forensic-m04-q16 | 2번 · host와 session이 모두 지정값과 일치한다. | forensic.log-correlation |
| 17 | forensic-m04-q17 | 4번 · host와 session이 다르므로 제외한다. | forensic.log-correlation |
| 18 | forensic-m04-q18 | 1번 · 5건, 00:00:10 | forensic.log-correlation |
| 19 | forensic-m04-q19 | 4번 · 시간대 가정을 숨기지 않도록 오류로 거부한다. | forensic.log-correlation |
| 20 | forensic-m04-q20 | 4번 · 다운로드가 실행의 원인이라는 주장은 파일 해시·실행 인자 등 독립 근거가 더 필요하다. | forensic.log-correlation |
| 21 | forensic-m04-q21 | 3번 · 확인된 관찰이 있는 호스트 집합이며 전체 침해 범위 증명은 아니다. | forensic.incident-response |
| 22 | forensic-m04-q22 | 4번 · 승인·영향 검토·증거 보존이 모두 참 | forensic.incident-response |
| 23 | forensic-m04-q23 | 3번 · HOLD | forensic.incident-response |
| 24 | forensic-m04-q24 | 3번 · 종료는 휘발성 근거를 잃을 수 있고 격리는 이미 저장된 자료·내부 실행을 모두 제거하지 않는다. | forensic.incident-response |
| 25 | forensic-m04-q25 | 3번 · 원인 수정·정상 기능·허용/거부 정책·모니터링과 재발 징후·관찰 기간을 정한다. | forensic.incident-response |

## forensic-05 · 운영체제 기록의 의미

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | forensic-m05-q01 | 1번 · Provider·채널·버전과 출처 | forensic.windows-events |
| 2 | forensic-m05-q02 | 3번 · Data의 Name 속성 | forensic.windows-events |
| 3 | forensic-m05-q03 | 3번 · 동일한 필드 값이 추출된다. | forensic.windows-events |
| 4 | forensic-m05-q04 | 2번 · Event가 사용하는 XML 네임스페이스 | forensic.windows-events |
| 5 | forensic-m05-q05 | 3번 · 로그온 실패·로그온 성공 | forensic.windows-events |
| 6 | forensic-m05-q06 | 1번 · 네트워크 로그온 맥락이며 대화형 데스크톱 사용 증명은 아니다. | forensic.windows-events |
| 7 | forensic-m05-q07 | 1번 · 출처·컴퓨터·채널·기록 ID를 함께 사용한다. | forensic.windows-events |
| 8 | forensic-m05-q08 | 4번 · 중복 ID 오류이며 오류 전 일부 출력만으로 전체 성공이라 하지 않는다. | forensic.windows-events |
| 9 | forensic-m05-q09 | 4번 · 합성 XML이며 실제 EVTX 바이너리 파싱은 하지 않는다. | forensic.windows-events |
| 10 | forensic-m05-q10 | 1번 · 텍스트 파일·journal·수집기 등 기록 형식과 위치가 다를 수 있다. | forensic.linux-auth |
| 11 | forensic-m05-q11 | 3번 · 동일 프로세스의 재시도나 공격 성공으로 바로 확정하지 않는다. | forensic.linux-auth |
| 12 | forensic-m05-q12 | 4번 · 해당 키의 선행 성공 기록과 허용된 sudo 요청 | forensic.linux-auth |
| 13 | forensic-m05-q13 | 4번 · 표본에서 연결된 선행 성공이 없고 요청은 거부로 기록됐다. | forensic.linux-auth |
| 14 | forensic-m05-q14 | 1번 · linked-login=False가 되고 allow 자체는 유지된다. | forensic.linux-auth |
| 15 | forensic-m05-q15 | 2번 · 명령 시작/종료 감사, 종료 코드·출력 또는 실행 기록 | forensic.linux-auth |
| 16 | forensic-m05-q16 | 1번 · 호스트·사용자·세션 | forensic.linux-auth |
| 17 | forensic-m05-q17 | 2번 · 활동 부재로 바로 바꾸지 않고 관측 가능성과 누락을 검토한다. | forensic.linux-auth |
| 18 | forensic-m05-q18 | 4번 · 하드링크로 여러 이름이 같은 파일 객체를 참조한다. | forensic.filesystem-records |
| 19 | forensic-m05-q19 | 2번 · 이름 2개와 파일 객체 1개 | forensic.filesystem-records |
| 20 | forensic-m05-q20 | 2번 · 장치 간 번호 중복과 시간에 따른 inode 재사용이 가능하다. | forensic.filesystem-records |
| 21 | forensic-m05-q21 | 1번 · 메타데이터 상태 변경 시각 | forensic.filesystem-records |
| 22 | forensic-m05-q22 | 4번 · UNKNOWN으로 남긴다. | forensic.filesystem-records |
| 23 | forensic-m05-q23 | 3번 · 관찰 이름 1개와 선언 링크 2의 불일치로 부분 수집 등을 확인한다. | forensic.filesystem-records |
| 24 | forensic-m05-q24 | 3번 · 특정 사용자가 특정 명령으로 조작했다는 것 | forensic.filesystem-records |
| 25 | forensic-m05-q25 | 2번 · 관찰 누락과 실제 unlink·내용 삭제를 별도로 검증한다. | forensic.filesystem-records |

## forensic-06 · 메모리 단서와 관측 한계

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | forensic-m06-q01 | 3번 · 합성 프로세스/영역 JSON이며 실제 RAM 덤프·VAD 파싱은 하지 않는다. | forensic.memory-triage |
| 2 | forensic-m06-q02 | 1번 · [8192,12288) | forensic.memory-triage |
| 3 | forensic-m06-q03 | 4번 · 12288 | forensic.memory-triage |
| 4 | forensic-m06-q04 | 4번 · private 백킹이며 쓰기 w와 실행 x가 모두 있다. | forensic.memory-triage |
| 5 | forensic-m06-q05 | 3번 · 추가 조사가 필요할 수 있는 모형 규칙의 일치 | forensic.memory-triage |
| 6 | forensic-m06-q06 | 4번 · 0개 | forensic.memory-triage |
| 7 | forensic-m06-q07 | 3번 · 다른 권한의 악성 동작이나 자료 누락은 이 규칙 밖에 남을 수 있어서 | forensic.memory-triage |
| 8 | forensic-m06-q08 | 2번 · 유효 영역이 아닌 입력 오류로 거부한다. | forensic.memory-triage |
| 9 | forensic-m06-q09 | 1번 · JIT 같은 동적 코드 생성 기능 | forensic.memory-triage |
| 10 | forensic-m06-q10 | 2번 · 프로세스·모듈 출처, 스레드 관계, 실제 바이트·페이지 상태·로그 | forensic.memory-triage |
| 11 | forensic-m06-q11 | 1번 · start가 정수이고 0 이상, size가 정수이고 양수 | forensic.memory-triage |
| 12 | forensic-m06-q12 | 3번 · 실행 x가 없어 private-WX 규칙에 일치하지 않는다. | forensic.memory-triage |
| 13 | forensic-m06-q13 | 2번 · 표시 기준 맞추기와 장비 오차 보정은 다른 작업이다. | forensic.evidence-coverage |
| 14 | forensic-m06-q14 | 4번 · recorded - clock_ahead | forensic.evidence-coverage |
| 15 | forensic-m06-q15 | 2번 · [90,94] | forensic.evidence-coverage |
| 16 | forensic-m06-q16 | 4번 · [93,99] | forensic.evidence-coverage |
| 17 | forensic-m06-q17 | 1번 · ORDER-UNCERTAIN | forensic.evidence-coverage |
| 18 | forensic-m06-q18 | 3번 · ORDER-UNCERTAIN | forensic.evidence-coverage |
| 19 | forensic-m06-q19 | 1번 · A-BEFORE-B | forensic.evidence-coverage |
| 20 | forensic-m06-q20 | 1번 · [92,92], [96,96], A-BEFORE-B | forensic.evidence-coverage |
| 21 | forensic-m06-q21 | 2번 · 오차 범위를 줄일 동기화·측정·수집 지연 근거가 별도로 필요하다. | forensic.evidence-coverage |
| 22 | forensic-m06-q22 | 3번 · 지정 시간 범위의 모든 행이 빠짐없이 수집됐다는 것 | forensic.evidence-coverage |
| 23 | forensic-m06-q23 | 4번 · 그 자료만으로 프로세스 실행 부재를 확정할 수 없다. | forensic.evidence-coverage |
| 24 | forensic-m06-q24 | 3번 · 아니다. 설정 표시는 바뀌지만 기존 사건과 시간 구간은 그대로다. | forensic.evidence-coverage |
| 25 | forensic-m06-q25 | 2번 · B-BEFORE-A | forensic.evidence-coverage |

## foundation-01 · 실습 환경과 파일

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | env-01 | 1번 · py -3 hello.py | foundation.environment |
| 2 | env-02 | 3번 · python3 --version | foundation.environment |
| 3 | env-03 | 4번 · Python 인터프리터 | foundation.environment |
| 4 | env-04 | 4번 · python3 hello.py | foundation.environment |
| 5 | env-05 | 4번 · 현재 디렉터리와 hello.py의 실제 위치를 확인한다 | foundation.environment |
| 6 | env-06 | 1번 · 현재 셸이 python3 명령을 찾지 못했다 | foundation.environment |
| 7 | env-07 | 1번 · 편집한 파일과 실행한 파일의 경로가 같은지 비교한다 | foundation.environment |
| 8 | env-08 | 3번 · Hello, Mina / Study: 50 minutes | foundation.environment |
| 9 | env-09 | 3번 · Python 3와 텍스트 편집기를 준비하고 자신의 OS에 맞는 터미널 명령을 사용한다 | foundation.environment |
| 10 | env-10 | 2번 · 운영 환경과 패키지 관리자가 다르기 때문이다 | foundation.environment |
| 11 | env-11 | 2번 · OS·셸·Python 버전·파일 위치·실행 명령·실제 출력을 남긴다 | foundation.environment |
| 12 | env-12 | 3번 · python3는 프로그램 이름이고 hello.py는 전달하는 파일 인자다 | foundation.environment |
| 13 | paths-01 | 1번 · /home/learner/labs/work/copy.txt | foundation.paths |
| 14 | paths-02 | 2번 · /home/learner/labs/notes.txt | foundation.paths |
| 15 | paths-03 | 4번 · /home/learner/labs/notes.txt | foundation.paths |
| 16 | paths-04 | 1번 · pwd | foundation.paths |
| 17 | paths-05 | 1번 · cp notes.txt work/copy.txt | foundation.paths |
| 18 | paths-06 | 2번 · printf 'Only in copy\n' >> work/copy.txt | foundation.paths |
| 19 | paths-07 | 2번 · 기존 사본 내용을 덮어쓰고 새 출력이 저장된다 | foundation.paths |
| 20 | paths-08 | 4번 · 원본 3줄·사본 4줄 | foundation.paths |
| 21 | paths-09 | 4번 · 필요한 디렉터리를 만들고 이미 디렉터리가 있어도 진행할 수 있게 한다 | foundation.paths |
| 22 | paths-10 | 3번 · cat "my notes.txt"처럼 이름 전체를 따옴표로 감싼다 | foundation.paths |
| 23 | paths-11 | 3번 · 상대 경로의 기준인 현재 디렉터리가 달라졌기 때문이다 | foundation.paths |
| 24 | paths-12 | 2번 · ~는 사용자 홈으로 확장되고 /는 루트 디렉터리다 | foundation.paths |
| 25 | paths-13 | 2번 · 원본과 사본을 각각 읽어 수정 전후 내용과 경로를 대조한다 | foundation.paths |

## foundation-02 · Python을 작은 단계로

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | m2-q01 | 2번 · 30 | foundation.python-values |
| 2 | m2-q02 | 1번 · 1515 | foundation.python-values |
| 3 | m2-q03 | 3번 · 20 | foundation.python-values |
| 4 | m2-q04 | 1번 · 25 | foundation.python-values |
| 5 | m2-q05 | 2번 · TypeError | foundation.python-values |
| 6 | m2-q06 | 4번 · ValueError | foundation.python-values |
| 7 | m2-q07 | 3번 · 15 | foundation.python-values |
| 8 | m2-q08 | 4번 · Study: 40 minutes | foundation.python-values |
| 9 | m2-q09 | 3번 · 2020 | foundation.python-values |
| 10 | m2-q10 | 1번 · 3 | foundation.python-flow |
| 11 | m2-q11 | 3번 · 1 | foundation.python-flow |
| 12 | m2-q12 | 1번 · return status == "denied"로 불리언을 돌려준다. | foundation.python-flow |
| 13 | m2-q13 | 4번 · 0 | foundation.python-flow |
| 14 | m2-q14 | 3번 · 1 | foundation.python-flow |
| 15 | m2-q15 | 1번 · False | foundation.python-flow |
| 16 | m2-q16 | 3번 · 1 | foundation.python-flow |
| 17 | m2-q17 | 3번 · 실행할 줄들을 같은 들여쓰기 깊이의 블록에 둔다. | foundation.python-flow |
| 18 | m2-q18 | 2번 · kim, mina | foundation.python-files |
| 19 | m2-q19 | 2번 · str | foundation.python-files |
| 20 | m2-q20 | 4번 · 헤더에 status라는 열 이름이 정확히 있는지 확인한다. | foundation.python-files |
| 21 | m2-q21 | 1번 · 프로그램이 해석한 입력 파일 경로와 해당 파일의 존재 여부 | foundation.python-files |
| 22 | m2-q22 | 4번 · 원본 바이트를 보존하고 파일의 실제 인코딩과 읽기 설정을 확인한다. | foundation.python-files |
| 23 | m2-q23 | 2번 · 실행한 스크립트가 있는 폴더 | foundation.python-files |
| 24 | m2-q24 | 2번 · events=5 denied=3 | foundation.python-files |
| 25 | m2-q25 | 4번 · 0, 0 | foundation.python-files |

## foundation-03 · 시스템·통신·기록

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | m3-q01 | 4번 · 수정한 소스를 다시 컴파일한 뒤 새 실행 파일을 실행한다. | foundation.c-memory |
| 2 | m3-q02 | 3번 · value 객체에 저장된 정수 값 | foundation.c-memory |
| 3 | m3-q03 | 3번 · 9 | foundation.c-memory |
| 4 | m3-q04 | 1번 · %p와 (void *) 변환을 사용하며, 실제 주소는 실행마다 달라질 수 있다. | foundation.c-memory |
| 5 | m3-q05 | 4번 · 디버깅 정보를 포함한다. | foundation.c-memory |
| 6 | m3-q06 | 1번 · 소유자 읽기·쓰기, 그룹과 그 외 사용자 권한 없음 | foundation.permissions |
| 7 | m3-q07 | 2번 · 소유자 읽기만 허용 | foundation.permissions |
| 8 | m3-q08 | 2번 · 그 디렉터리를 경로로 통과할 수 있는 권한 | foundation.permissions |
| 9 | m3-q09 | 1번 · 앞 명령의 표준 출력을 뒤 명령의 표준 입력으로 연결한다. | foundation.permissions |
| 10 | m3-q10 | 2번 · grep Bifrost working.txt > matched.txt | foundation.permissions |
| 11 | m3-q11 | 2번 · IP 주소와 포트, 사용하는 전송 프로토콜 | foundation.network |
| 12 | m3-q12 | 2번 · 이름 조회와 서비스 연결은 별도 단계이므로 목적지 포트·도달 가능성 등을 확인한다. | foundation.network |
| 13 | m3-q13 | 1번 · DNS 조회 → 목적지 TCP 연결 → TLS → HTTP | foundation.network |
| 14 | m3-q14 | 3번 · UDP는 데이터그램을 보내며 응용 계층이 추가 신뢰성 기능을 구현할 수 있다. | foundation.network |
| 15 | m3-q15 | 2번 · 서비스가 정상 동작하고 안전하게 구현됐다는 보장 | foundation.network |
| 16 | m3-q16 | 4번 · GET, /notes/1 | foundation.http |
| 17 | m3-q17 | 3번 · hello | foundation.http |
| 18 | m3-q18 | 1번 · 응답 상태 코드 | foundation.http |
| 19 | m3-q19 | 3번 · 쿠키가 존재한다는 사실과 특정 자료에 접근할 권한은 별도로 검증해야 한다. | foundation.http |
| 20 | m3-q20 | 4번 · 표시 형식과 프로토콜 차이를 고려하며 메서드·상태·헤더·본문의 역할을 확인한다. | foundation.http |
| 21 | m3-q21 | 4번 · 이전 git add 시점에 스테이징한 내용 | foundation.git |
| 22 | m3-q22 | 1번 · git diff --staged | foundation.git |
| 23 | m3-q23 | 4번 · 로컬 저장소에 선택한 내용의 커밋이 생성됐다. | foundation.git |
| 24 | m3-q24 | 3번 · 환경·입력 파일·실행 명령·실제 출력·예상과 다른 점 | foundation.git |
| 25 | m3-q25 | 4번 · 과거 커밋에 남을 수 있으므로 유출 대응과 기록 정리를 별도로 검토해야 한다. | foundation.git |

## foundation-04 · 데이터 경계와 도구 만들기

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | m4-q01 | 2번 · 2 4 | foundation.text-bytes |
| 2 | m4-q02 | 3번 · text.encode("utf-8") | foundation.text-bytes |
| 3 | m4-q03 | 1번 · UnicodeDecodeError | foundation.text-bytes |
| 4 | m4-q04 | 4번 · 해석할 수 없는 바이트가 빠질 수 있어 원본과 같은 자료라고 볼 수 없다. | foundation.text-bytes |
| 5 | m4-q05 | 4번 · read_bytes()로 원본 바이트를 읽는다. | foundation.text-bytes |
| 6 | m4-q06 | 2번 · 파싱은 성공하지만 minutes가 문자열이므로 계약 검증에서 거부한다. | foundation.structured-data |
| 7 | m4-q07 | 3번 · True False | foundation.structured-data |
| 8 | m4-q08 | 2번 · 추가 키가 금지된 계약이므로 거부한다. | foundation.structured-data |
| 9 | m4-q09 | 3번 · 0과 1440 | foundation.structured-data |
| 10 | m4-q10 | 1번 · 파싱 뒤 문서 형태 검증에서 객체가 아님을 확인한다. | foundation.structured-data |
| 11 | m4-q11 | 2번 · 호출자가 CLI·테스트 등 문맥에 맞게 실패를 처리할 수 있다. | foundation.exceptions |
| 12 | m4-q12 | 4번 · 실패와 개발 결함을 성공처럼 숨겨 후속 자동화가 잘못된 결과를 사용할 수 있다. | foundation.exceptions |
| 13 | m4-q13 | 2번 · 2 | foundation.exceptions |
| 14 | m4-q14 | 4번 · stdout에 정상 결과, stderr에 진단 | foundation.exceptions |
| 15 | m4-q15 | 3번 · 예상한 입력 오류와 구분하고 결함을 재현해 수정한다. | foundation.exceptions |
| 16 | m4-q16 | 4번 · True | foundation.cli |
| 17 | m4-q17 | 1번 · False | foundation.cli |
| 18 | m4-q18 | 3번 · 정수 변환은 성공하므로 별도로 범위를 검사해야 한다. | foundation.cli |
| 19 | m4-q19 | 1번 · 현재 작업 폴더 | foundation.cli |
| 20 | m4-q20 | 4번 · 긴 옵션의 축약 입력을 허용하지 않아 옵션 해석을 명확히 한다. | foundation.cli |
| 21 | m4-q21 | 3번 · 요구 사항에서 독립적으로 고정 기대값을 정한다. | foundation.unit-tests |
| 22 | m4-q22 | 1번 · -1, 0, 1440, 1441 | foundation.unit-tests |
| 23 | m4-q23 | 1번 · minutes=30, minimum=30에서 True를 기대하는 테스트 | foundation.unit-tests |
| 24 | m4-q24 | 2번 · assertRaises(ValueError)를 사용한다. | foundation.unit-tests |
| 25 | m4-q25 | 1번 · 검사한 사례가 기대와 일치하며, 미검사 조건은 추가 검증이 필요하다. | foundation.unit-tests |

## foundation-05 · 상태와 실행 경계 다루기

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | m5-q01 | 4번 · 2 | foundation.mutable-data |
| 2 | m5-q02 | 4번 · 2 | foundation.mutable-data |
| 3 | m5-q03 | 2번 · A | foundation.mutable-data |
| 4 | m5-q04 | 2번 · True False | foundation.mutable-data |
| 5 | m5-q05 | 4번 · 일반 중첩 자료의 복사에 유용하지만 열린 파일·잠금·외부 연결은 별도 설계가 필요하다. | foundation.mutable-data |
| 6 | m5-q06 | 2번 · 같은 폴더의 임시 파일에 완성 → flush·fsync·닫기 → os.replace | foundation.atomic-output |
| 7 | m5-q07 | 3번 · 1 | foundation.atomic-output |
| 8 | m5-q08 | 1번 · 성공·실패와 관계없이 실행되는 finally 절 | foundation.atomic-output |
| 9 | m5-q09 | 3번 · 블록을 벗어나며 파일을 닫지만 예외가 자동으로 성공으로 바뀌지는 않는다. | foundation.atomic-output |
| 10 | m5-q10 | 1번 · 여러 작성자의 충돌 해결과 여러 파일 전체의 트랜잭션 | foundation.atomic-output |
| 11 | m5-q11 | 3번 · 30, CLI | foundation.config-precedence |
| 12 | m5-q12 | 3번 · 빈 환경값을 잘못된 설정으로 거부한다. | foundation.config-precedence |
| 13 | m5-q13 | 3번 · 파일 설정 오류를 보고하며 CLI로 숨기지 않는다. | foundation.config-precedence |
| 14 | m5-q14 | 2번 · 정수 변환과 1~60 범위 검사를 모두 한다. | foundation.config-precedence |
| 15 | m5-q15 | 4번 · 필요한 비밀이 아닌 선택 값과 그 출처 | foundation.config-precedence |
| 16 | m5-q16 | 3번 · 세미콜론을 포함한 하나의 문자 그대로의 인자 | foundation.subprocess |
| 17 | m5-q17 | 3번 · 출력이 있어도 상태 3이라는 실패 계약을 확인해 처리한다. | foundation.subprocess |
| 18 | m5-q18 | 1번 · subprocess.TimeoutExpired | foundation.subprocess |
| 19 | m5-q19 | 2번 · 2 | foundation.subprocess |
| 20 | m5-q20 | 4번 · 실행 파일·옵션·권한·작업 폴더·환경·출력 크기 등 | foundation.subprocess |
| 21 | m5-q21 | 4번 · 허용한 네 필드만 새 dict에 구성해 기록한다. | foundation.structured-logging |
| 22 | m5-q22 | 1번 · 0 | foundation.structured-logging |
| 23 | m5-q23 | 1번 · 아니요. 허용된 필드 안의 비밀 내용까지 자동 탐지하는 것은 아니다. | foundation.structured-logging |
| 24 | m5-q24 | 2번 · False | foundation.structured-logging |
| 25 | m5-q25 | 1번 · 기록한 사건 내용이 사실이라는 보장과 보관·접근 제어의 적절성 | foundation.structured-logging |

## pwn-01 · 실행과 메모리 모델

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | pwn-m01-q01 | 3번 · 컴파일러가 번역하고 링커가 연결한다. | pwn.build |
| 2 | pwn-m01-q02 | 1번 · 디버깅 정보를 넣고 최적화 영향을 줄여 관찰을 단순하게 한다. | pwn.build |
| 3 | pwn-m01-q03 | 4번 · 이번 빌드의 성공 여부와 실행 파일이 이전 산출물인지 확인한다. | pwn.build |
| 4 | pwn-m01-q04 | 2번 · file 결과와 실행 환경의 OS·CPU 정보 | pwn.build |
| 5 | pwn-m01-q05 | 1번 · 바로 앞의 file 명령 | pwn.build |
| 6 | pwn-m01-q06 | 4번 · 해당 빌드와 입력에서 기대한 동작을 관찰했다. | pwn.build |
| 7 | pwn-m01-q07 | 1번 · GCC 버전·CPU·정확한 빌드 명령·file 결과·실제 출력 | pwn.build |
| 8 | pwn-m01-q08 | 2번 · local=8이 되고 heap=9 및 배열 값은 유지된다. | pwn.build |
| 9 | pwn-m01-q09 | 2번 · 포인터 변수와 대상 영역은 서로 다른 객체이며 수명도 구분한다. | pwn.lifetime |
| 10 | pwn-m01-q10 | 2번 · 역참조하지 않고 실패 경로로 종료한다. | pwn.lifetime |
| 11 | pwn-m01-q11 | 4번 · 읽기 전에 필요한 값을 명시적으로 초기화해야 한다. | pwn.lifetime |
| 12 | pwn-m01-q12 | 4번 · 대상 수명이 끝났으므로 alias를 통한 읽기도 허용되지 않는다. | pwn.lifetime |
| 13 | pwn-m01-q13 | 3번 · 대상 객체의 수명이 끝나 유효한 지역 객체를 계속 참조할 수 없다. | pwn.lifetime |
| 14 | pwn-m01-q14 | 2번 · 누가 해제 책임을 지는지 정한다. | pwn.lifetime |
| 15 | pwn-m01-q15 | 3번 · 할당 → 실패 검사 → 초기화 → 사용 → 해제 → 재접근 금지 | pwn.lifetime |
| 16 | pwn-m01-q16 | 3번 · 언어의 저장 기간과 실제 구현 위치를 구분한다. | pwn.lifetime |
| 17 | pwn-m01-q17 | 3번 · 0, 1, 2 | pwn.bounds |
| 18 | pwn-m01-q18 | 4번 · i < 3 | pwn.bounds |
| 19 | pwn-m01-q19 | 1번 · sizeof values / sizeof values[0] | pwn.bounds |
| 20 | pwn-m01-q20 | 3번 · 포인터 자체의 크기이며 호출자 배열의 전체 길이는 복원할 수 없다. | pwn.bounds |
| 21 | pwn-m01-q21 | 1번 · 호출자가 실제 유효 영역과 일치하는 길이를 전달해야 한다. | pwn.bounds |
| 22 | pwn-m01-q22 | 2번 · 배열 접근 전에 | pwn.bounds |
| 23 | pwn-m01-q23 | 4번 · 10 / 20 / 30 세 값 | pwn.bounds |
| 24 | pwn-m01-q24 | 4번 · sizeof values는 전체 바이트 수이고 원소 개수는 원소 크기로 나눠야 하기 때문이다. | pwn.bounds |
| 25 | pwn-m01-q25 | 1번 · 포인터와 유효 원소 수를 함께 받고 그 범위 안에서 순회한다. | pwn.bounds |

## pwn-02 · 관찰·진단·완화

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | pwn-m02-q01 | 1번 · main에 도달하면 실행을 멈춰 상태를 관찰한다. | pwn.debugger |
| 2 | pwn-m02-q02 | 3번 · next는 소스 줄을 진행하고 step은 호출한 함수 안으로 들어갈 수 있다. | pwn.debugger |
| 3 | pwn-m02-q03 | 3번 · 그 대입이 이미 실행됐는지, 다음에 실행될 줄인지 확인한다. | pwn.debugger |
| 4 | pwn-m02-q04 | 3번 · 앞은 포인터 값, 뒤는 대상 정수 값이다. | pwn.debugger |
| 5 | pwn-m02-q05 | 1번 · ASLR 등으로 주소가 바뀔 수 있으므로 대입·값 관계와 실행 조건을 함께 비교한다. | pwn.debugger |
| 6 | pwn-m02-q06 | 4번 · 입력·빌드 옵션·중단 위치·실행한 스텝·관찰값 | pwn.debugger |
| 7 | pwn-m02-q07 | 2번 · 관찰하려는 변수가 유효하게 보이는 스택 프레임과 시점인지 확인한다. | pwn.debugger |
| 8 | pwn-m02-q08 | 2번 · 9 | pwn.debugger |
| 9 | pwn-m02-q09 | 3번 · 충돌하지 않아도 정의되지 않은 동작일 수 있다. | pwn.errors |
| 10 | pwn-m02-q10 | 1번 · -fsanitize=address | pwn.errors |
| 11 | pwn-m02-q11 | 3번 · 오류 유형·접근 크기·처음 사용자 코드가 나오는 줄 | pwn.errors |
| 12 | pwn-m02-q12 | 4번 · 그 값은 범위 밖 읽기의 결과여서 보장된 출력이 아니기 때문이다. | pwn.errors |
| 13 | pwn-m02-q13 | 2번 · 세 유효 원소가 정확히 한 번씩 출력되는 정상 기능 | pwn.errors |
| 14 | pwn-m02-q14 | 4번 · 같은 입력과 같은 Sanitizer 빌드 옵션으로 재검사한다. | pwn.errors |
| 15 | pwn-m02-q15 | 3번 · 검사한 입력·경로·빌드에서 해당 진단이 없었다. | pwn.errors |
| 16 | pwn-m02-q16 | 1번 · 처음 등장한 사용자 코드 줄과 values의 유효 인덱스를 연결한다. | pwn.errors |
| 17 | pwn-m02-q17 | 2번 · 프로세스의 주소 배치를 바꾼다. | pwn.mitigations |
| 18 | pwn-m02-q18 | 1번 · 실행 불가능한 메모리 영역에서의 코드 실행 | pwn.mitigations |
| 19 | pwn-m02-q19 | 2번 · 일부 스택 손상을 함수 반환 전에 탐지한다. | pwn.mitigations |
| 20 | pwn-m02-q20 | 3번 · 요청된 스택 권한에 실행 플래그가 없다는 단서 | pwn.mitigations |
| 21 | pwn-m02-q21 | 4번 · readelf -W -l memory | pwn.mitigations |
| 22 | pwn-m02-q22 | 2번 · 유효 인덱스만 접근하도록 경계 조건을 고친다. | pwn.mitigations |
| 23 | pwn-m02-q23 | 4번 · 컴파일·링크 옵션, 바이너리 특징, OS 설정과 실제 실행을 함께 확인한다. | pwn.mitigations |
| 24 | pwn-m02-q24 | 4번 · 원인 수정과 기능 재검증 | pwn.mitigations |
| 25 | pwn-m02-q25 | 1번 · 각 수단의 역할과 근거·한계를 구분하기 위해서 | pwn.mitigations |

## pwn-03 · 정수와 출력의 경계

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | pwn-m03-q01 | 4번 · 0003 | pwn.integer-input |
| 2 | pwn-m03-q02 | 1번 · 1024는 허용, 1025는 거부 | pwn.integer-input |
| 3 | pwn-m03-q03 | 3번 · 이전 오류 값과 이번 변환의 범위 오류를 구분하기 위해서 | pwn.integer-input |
| 4 | pwn-m03-q04 | 1번 · 전체 문자열이 숫자로 변환되지 않았으므로 전체 숫자 계약을 만족하지 않는다. | pwn.integer-input |
| 5 | pwn-m03-q05 | 3번 · 캐스팅에서 원래 값의 범위 정보가 사라질 수 있기 때문이다. | pwn.integer-input |
| 6 | pwn-m03-q06 | 1번 · 십진수 3 | pwn.integer-input |
| 7 | pwn-m03-q07 | 2번 · 실패를 확인하면 즉시 오류 경로로 반환한다. | pwn.integer-input |
| 8 | pwn-m03-q08 | 1번 · 이후 크기 곱셈·덧셈 및 실제 자원 요구를 별도로 검토한다. | pwn.integer-input |
| 9 | pwn-m03-q09 | 1번 · 곱셈·덧셈 결과가 size_t의 표현 범위를 넘을 수 있어서 | pwn.allocation-size |
| 10 | pwn-m03-q10 | 2번 · count <= (SIZE_MAX - header) / element | pwn.allocation-size |
| 11 | pwn-m03-q11 | 4번 · 검사식의 0 나눗셈을 피하고 실습 계약상 거부하기 위해서 | pwn.allocation-size |
| 12 | pwn-m03-q12 | 2번 · 작아진 크기를 할당한 뒤 원래 큰 개수만큼 쓰면 경계를 넘을 수 있다. | pwn.allocation-size |
| 13 | pwn-m03-q13 | 3번 · 28 | pwn.allocation-size |
| 14 | pwn-m03-q14 | 3번 · size_t의 표현 범위가 플랫폼에 따라 달라질 수 있기 때문이다. | pwn.allocation-size |
| 15 | pwn-m03-q15 | 1번 · 아니다. 업무 상한·자원 예산·할당 실패 처리가 별도로 필요하다. | pwn.allocation-size |
| 16 | pwn-m03-q16 | 4번 · 목적이 다른 조건이므로 필요한 조건을 각각 검사한다. | pwn.allocation-size |
| 17 | pwn-m03-q17 | 3번 · printf("%s", text) | pwn.format-strings |
| 18 | pwn-m03-q18 | 4번 · printf("%s", message) | pwn.format-strings |
| 19 | pwn-m03-q19 | 2번 · %s%n을 데이터 문자열로 출력한다. | pwn.format-strings |
| 20 | pwn-m03-q20 | 3번 · 충분한 공간이 있었다면 만들었을 바이트 수이며 마지막 NUL은 제외한다. | pwn.format-strings |
| 21 | pwn-m03-q21 | 2번 · 반환값이 capacity 이상이므로 잘렸다. | pwn.format-strings |
| 22 | pwn-m03-q22 | 2번 · 출력 오류로 처리한다. | pwn.format-strings |
| 23 | pwn-m03-q23 | 4번 · needed=8, 잘림 yes | pwn.format-strings |
| 24 | pwn-m03-q24 | 4번 · 10바이트 | pwn.format-strings |
| 25 | pwn-m03-q25 | 1번 · 메모리 경계와 별도로 식별자의 의미가 유지되는지 정책을 정한다. | pwn.format-strings |

## pwn-04 · 소유권과 작은 파서

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | pwn-m04-q01 | 4번 · 소유자의 해제 책임과 빌린 포인터의 사용 기간을 명확히 한다. | pwn.ownership |
| 2 | pwn-m04-q02 | 1번 · 호출자인 main | pwn.ownership |
| 3 | pwn-m04-q03 | 1번 · 유효한 빌림 기간에 읽어 출력하고 해제하지 않는다. | pwn.ownership |
| 4 | pwn-m04-q04 | 2번 · 다른 별칭의 변경 금지와 대상 수명 유지 | pwn.ownership |
| 5 | pwn-m04-q05 | 2번 · 실패를 기록하고 버퍼 사용 경로로 들어가지 않는다. | pwn.ownership |
| 6 | pwn-m04-q06 | 1번 · 해제 뒤에는 같은 대상에 대한 빌림 접근도 유효하지 않기 때문이다. | pwn.ownership |
| 7 | pwn-m04-q07 | 3번 · 대상 블록을 해제하고 owner 변수만 NULL로 바꾼다. | pwn.ownership |
| 8 | pwn-m04-q08 | 3번 · 한 블록에 중복 해제 책임이 생긴다. | pwn.ownership |
| 9 | pwn-m04-q09 | 4번 · 실행하지 않은 성공·실패 경로의 수명 문제까지 증명한 것은 아니기 때문이다. | pwn.ownership |
| 10 | pwn-m04-q10 | 3번 · make_note 성공 → main 소유 → show_note 빌림 → main에서 해제 | pwn.ownership |
| 11 | pwn-m04-q11 | 4번 · 해당 표본의 복사·소유권 흐름이며 임의 거대 입력용 범용 라이브러리는 아니다. | pwn.ownership |
| 12 | pwn-m04-q12 | 1번 · 실패는 상태 2로 종료하고 성공 경로의 빌림·해제 절차를 실행하지 않는다. | pwn.ownership |
| 13 | pwn-m04-q13 | 2번 · big-endian으로 표현한 payload 바이트 길이 | pwn.binary-parser |
| 14 | pwn-m04-q14 | 4번 · 유효 버퍼라는 전제에서 size>=2인지 확인한다. | pwn.binary-parser |
| 15 | pwn-m04-q15 | 3번 · 258 | pwn.binary-parser |
| 16 | pwn-m04-q16 | 4번 · 앞에서 size>=2를 확인했다. | pwn.binary-parser |
| 17 | pwn-m04-q17 | 2번 · 거부한다. 선언 2와 실제 본문 3이 다르다. | pwn.binary-parser |
| 18 | pwn-m04-q18 | 3번 · 허용하고 payload 길이 0 | pwn.binary-parser |
| 19 | pwn-m04-q19 | 4번 · 둘 다 거부한다. | pwn.binary-parser |
| 20 | pwn-m04-q20 | 2번 · 정렬·padding·엔디언·실제 길이 가정을 분리하기 위해서 | pwn.binary-parser |
| 21 | pwn-m04-q21 | 1번 · payload 내용의 인증과 업무상 유효성 | pwn.binary-parser |
| 22 | pwn-m04-q22 | 3번 · 성공한 파싱 결과처럼 사용하지 않는다. | pwn.binary-parser |
| 23 | pwn-m04-q23 | 2번 · 바이트의 부호 확장 혼동을 줄이고 순서를 명시한다. | pwn.binary-parser |
| 24 | pwn-m04-q24 | 1번 · 한 번의 read와 한 메시지가 같다고 가정하지 않고 필요한 입력을 모은다. | pwn.binary-parser |
| 25 | pwn-m04-q25 | 4번 · OK, length=3 | pwn.binary-parser |

## pwn-05 · 메모리 표현과 데이터 계약

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | pwn-m05-q01 | 1번 · ABI와 정렬에 따라 필드 사이·끝에 padding이 있을 수 있다. | pwn.struct-layout |
| 2 | pwn-m05-q02 | 1번 · 그 환경의 메모리 배치 정보이며 보편적인 전송 명세는 아니다. | pwn.struct-layout |
| 3 | pwn-m05-q03 | 4번 · padding·엔디언·정수 표현 등 호스트 세부가 경계를 넘는다. | pwn.struct-layout |
| 4 | pwn-m05-q04 | 3번 · padding 등 바이트 차이와 논리 필드 동일성은 다를 수 있다. | pwn.struct-layout |
| 5 | pwn-m05-q05 | 1번 · 7바이트 | pwn.struct-layout |
| 6 | pwn-m05-q06 | 4번 · 둘 다 big-endian | pwn.struct-layout |
| 7 | pwn-m05-q07 | 2번 · 입력 크기가 정확히 7이다. | pwn.struct-layout |
| 8 | pwn-m05-q08 | 1번 · 010a0b0c0d0506 | pwn.struct-layout |
| 9 | pwn-m05-q09 | 2번 · 독립된 고정 기대 Hex와 왕복 결과를 둘 다 검사한다. | pwn.struct-layout |
| 10 | pwn-m05-q10 | 1번 · padding 조정과 바이트 순서·자료 표현 계약은 별개이기 때문이다. | pwn.struct-layout |
| 11 | pwn-m05-q11 | 2번 · 메시지 인증과 사용자 권한까지 모두 검증됐다. | pwn.struct-layout |
| 12 | pwn-m05-q12 | 4번 · --layout은 호스트 크기·오프셋 관찰, 기본 모드는 고정 전송 형식과 왕복 확인 | pwn.struct-layout |
| 13 | pwn-m05-q13 | 1번 · C 문자열은 첫 NUL에서 끝나지만 바이너리는 명시적 길이로 읽기 때문이다. | pwn.binary-strings |
| 14 | pwn-m05-q14 | 3번 · 2 | pwn.binary-strings |
| 15 | pwn-m05-q15 | 2번 · 4142004344 | pwn.binary-strings |
| 16 | pwn-m05-q16 | 4번 · 종료를 찾다가 유효 배열 범위 밖까지 읽을 수 있어서 | pwn.binary-strings |
| 17 | pwn-m05-q17 | 2번 · 서로 다른 개념이므로 구분하며, 수치가 같을 수도 있다. | pwn.binary-strings |
| 18 | pwn-m05-q18 | 2번 · 1~32바이트의 출력 가능한 ASCII | pwn.binary-strings |
| 19 | pwn-m05-q19 | 3번 · NUL이 범위에 포함되므로 거부 | pwn.binary-strings |
| 20 | pwn-m05-q20 | 2번 · 버퍼 5바이트, strlen 4 | pwn.binary-strings |
| 21 | pwn-m05-q21 | 4번 · 마지막 NUL도 범위에 포함되어 거부 | pwn.binary-strings |
| 22 | pwn-m05-q22 | 3번 · 검사한 대상과 실제 사용한 대상이 달라질 수 있다. | pwn.binary-strings |
| 23 | pwn-m05-q23 | 4번 · HTML·SQL 등 사용 맥락의 안전성이나 임의의 UTF-8 문자열 지원 | pwn.binary-strings |
| 24 | pwn-m05-q24 | 3번 · 바이트와 유효 길이를 함께 전달한다. | pwn.binary-strings |
| 25 | pwn-m05-q25 | 3번 · 4142434400 | pwn.binary-strings |

## pwn-06 · 열린 객체와 스트림 경계

| 번호 | 문항 ID | 정답 | 복습 차시 |
|---|---|---|---|
| 1 | pwn-m06-q01 | 4번 · 정수 대입은 새 FD를 만들지 않고 dup는 새 FD로 같은 열린 파일 설명을 참조한다. | pwn.file-descriptors |
| 2 | pwn-m06-q02 | 2번 · 파일 오프셋 | pwn.file-descriptors |
| 3 | pwn-m06-q03 | 4번 · CD | pwn.file-descriptors |
| 4 | pwn-m06-q04 | 2번 · 남은 참조로 열린 객체를 계속 사용할 수 있다. | pwn.file-descriptors |
| 5 | pwn-m06-q05 | 4번 · 새 FD가 없으므로 닫힌 번호로 읽게 되어 실패한다. | pwn.file-descriptors |
| 6 | pwn-m06-q06 | 1번 · 12 → 34 → 56 | pwn.file-descriptors |
| 7 | pwn-m06-q07 | 1번 · 이름 제거와 열린 객체 참조의 수명은 다르기 때문이다. | pwn.file-descriptors |
| 8 | pwn-m06-q08 | 1번 · EINTR은 재시도하되 EOF·다른 오류·EAGAIN은 같은 성공으로 뭉치지 않는다. | pwn.file-descriptors |
| 9 | pwn-m06-q09 | 3번 · 헤더·본문 일부만 반환될 수 있어 일대일로 보장되지 않는다. | pwn.partial-io |
| 10 | pwn-m06-q10 | 3번 · 결정적 메모리 어댑터로 짧은 반환을 모형화한다. | pwn.partial-io |
| 11 | pwn-m06-q11 | 3번 · 받은 2바이트를 누적하고 다음 위치에서 남은 3바이트를 요청한다. | pwn.partial-io |
| 12 | pwn-m06-q12 | 2번 · 헤더를 모아 길이를 해석한 뒤 본문을 읽기 전에 | pwn.partial-io |
| 13 | pwn-m06-q13 | 3번 · 불완전 입력으로 거부한다. | pwn.partial-io |
| 14 | pwn-m06-q14 | 4번 · 진행 정지로 거부한다. | pwn.partial-io |
| 15 | pwn-m06-q15 | 4번 · 7회 | pwn.partial-io |
| 16 | pwn-m06-q16 | 1번 · 6회: 헤더 2 + 본문 3 + EOF 확인 1 | pwn.partial-io |
| 17 | pwn-m06-q17 | 2번 · 두 시점 사이 이름이 다른 객체를 가리킬 수 있다. | pwn.atomic-open |
| 18 | pwn-m06-q18 | 2번 · O_CREAT과 O_EXCL | pwn.atomic-open |
| 19 | pwn-m06-q19 | 1번 · 마지막 경로 구성 요소가 심볼릭 링크인 열기를 거부한다. | pwn.atomic-open |
| 20 | pwn-m06-q20 | 3번 · 실제 열린 객체가 일반 파일인지 확인하기 위해서 | pwn.atomic-open |
| 21 | pwn-m06-q21 | 4번 · 결과를 임의 상위 경로 전체의 안전 보장으로 확대하지 않기 위해서 | pwn.atomic-open |
| 22 | pwn-m06-q22 | 1번 · 대상은 일반 파일이어도 마지막 symlink 거부 정책은 사라질 수 있다. | pwn.atomic-open |
| 23 | pwn-m06-q23 | 3번 · 이름 수명과 열린 객체 수명의 차이 | pwn.atomic-open |
| 24 | pwn-m06-q24 | 2번 · second_create=EXISTS | pwn.atomic-open |
| 25 | pwn-m06-q25 | 3번 · 상위 경로·hard link·동시 경합·소유자 검증을 모두 증명한 실험은 아니다. | pwn.atomic-open |
