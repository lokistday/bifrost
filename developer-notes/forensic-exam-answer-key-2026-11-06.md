# 디지털 포렌식 모의고사 답안 검토표 · 2026-11-06 · v2

보기 재배치 후 정답 번호다. 강의 근거는 forensic-exam-evidence-2026-11-06.json에, v1 대비 변경 내역은 exam-arrangements-2026-11-06.json에 기록했다.

## 1. 보존과 증거 읽기

| 번호 | 질문 | 정답 보기 | 출제 차시 |
|---|---|---|---|
| 1 | 원본과 작업 사본의 SHA-256이 같다는 결과가 직접 뒷받침하는 것은? | 3번 · 비교한 파일 내용 바이트의 일치 | forensic.integrity |
| 2 | 분석을 시작하기 전에 해시와 함께 남길 보존 기준으로 적절한 것은? | 3번 · 출처·수집 시각·담당자·파일 크기·도구 정보 | forensic.integrity |
| 3 | 보존용 파일과 분석 결과 파일을 다루는 방식으로 적절한 것은? | 1번 · 보존용 원본과 작업 사본을 나누고 결과는 별도 폴더에 저장한다. | forensic.integrity |
| 4 | 원본은 유지하고 사본 끝에 느낌표 1바이트를 붙였습니다. 이 강의의 비교 실험에서 기대하는 결과는? | 1번 · 원본 해시는 유지되고 사본 해시는 바뀐다. | forensic.integrity |
| 5 | 파일과 SHA256SUMS.txt가 함께 변조됐다면 해시 목록 대조에 추가로 필요한 것은? | 4번 · 목록 자체를 신뢰할 수 있는 배포 경로나 서명 등 출처 근거 | forensic.integrity |
| 6 | 파일 내용 바이트를 그대로 유지하고 이름만 바꿨습니다. 내용 SHA-256에 대한 설명은? | 2번 · 이름은 해시 입력이 아니므로 내용 해시는 같다. | forensic.integrity |
| 7 | 분석 후 원본과 사본의 해시가 달라졌습니다. 이 결과만으로 가능한 결론은? | 1번 · 내용 바이트가 다르며 변경 원인은 작업 이력과 추가 비교가 필요하다. | forensic.integrity |
| 8 | 수집 뒤 파일이 바뀌지 않았다는 근거와 사건 내용의 진실성이 구분되는 이유는? | 1번 · 처음 수집한 자료 자체가 이미 잘못된 내용일 가능성은 별개이기 때문이다. | forensic.integrity |
| 9 | auth.csv에서 id 열의 역할은? | 4번 · 이 실습의 증거 기록을 지칭하는 식별자 | forensic.logs |
| 10 | 기본 auth.csv에서 E02·E03·E04의 공통 관찰은? | 4번 · bob 계정의 로그인 거부 3건과 동일 출발지 | forensic.logs |
| 11 | 기본 표본 E02·E03·E04의 시각이 00:01:00, 00:01:10, 00:01:20 UTC입니다. 인접 거부 기록의 간격은? | 2번 · 10초 | forensic.logs |
| 12 | E02~E06의 계정과 출발지가 같아도 하나의 세션이라고 확정할 수 없는 직접적 이유는? | 3번 · 표본에 세션 식별자가 없기 때문이다. | forensic.logs |
| 13 | source IP가 같은 여러 요청에서 바로 단정할 수 없는 것은? | 2번 · 모든 요청의 실제 행위자가 같은 사람이라는 것 | forensic.logs |
| 14 | 거부 뒤 성공과 파일 읽기가 이어졌습니다. 강의의 근거 범위에 맞는 해석은? | 2번 · 침해와 정상 사용 등 대안을 두고 세션·MFA·장치 자료를 추가 확인한다. | forensic.logs |
| 15 | 계정 탈취 가설과 정상 사용자의 반복 오타 가설을 구별할 후속 확인은? | 4번 · MFA·장치·세션 기록과 사용자 확인·평소 로그인 패턴 | forensic.logs |
| 16 | login_ok 한 행을 보고 내릴 수 있는 결론으로 적절한 것은? | 3번 · 기록 시스템이 해당 계정의 로그인 성공을 남겼다. | forensic.logs |
| 17 | E06의 file_read와 실제 외부 유출을 구분할 때 필요한 검토는? | 3번 · 대상 파일과 전송량·목적지·애플리케이션 기록을 추가 확인한다. | forensic.logs |
| 18 | evidence.txt 안의 owner=alice 문자열을 OS 파일 소유자라고 바로 해석하면 안 되는 이유는? | 2번 · 내용에 작성된 텍스트와 OS가 관리하는 소유자 속성은 출처가 다르다. | forensic.metadata |
| 19 | ZIP을 풀고 stat에서 읽은 수정 시각의 적절한 기록 방식은? | 4번 · 추출·복사 환경의 현재 관찰값으로 남기고 사건 시각과 구분한다. | forensic.metadata |
| 20 | 두 파일의 바이트 크기가 같다는 사실만으로 부족한 주장은? | 3번 · 두 파일의 내용 바이트가 완전히 같다는 주장 | forensic.metadata |
| 21 | 내용 해시는 같은데 수정 시각이 다른 두 사본을 보았습니다. 해석은? | 3번 · 내용은 같아도 복사·추출 등으로 메타데이터가 다를 수 있다. | forensic.metadata |
| 22 | 파일을 읽은 뒤 접근 시각이 그대로였습니다. 바로 읽기 부재라고 결론 내리면 안 되는 이유는? | 2번 · 마운트 설정과 캐시 등으로 접근 시각이 매번 갱신되지 않을 수 있다. | forensic.metadata |
| 23 | st_ctime을 여러 OS에서 이식 가능한 파일 생성 시각으로 쓰는 설계의 문제는? | 4번 · 플랫폼별 의미가 다르므로 생성 시각이라고 고정할 수 없다. | forensic.metadata |
| 24 | st_mtime_ns의 ns 표현을 볼 때 주의할 점은? | 1번 · 나노초 단위 표현이 실제 나노초 정밀도를 보장하지는 않는다. | forensic.metadata |
| 25 | image.png와 확장자만 바꾼 renamed.txt의 내용 해시가 같습니다. 직접 확인한 관계는? | 1번 · 경로·확장자가 달라도 동일한 내용 바이트일 수 있다. | forensic.metadata |

## 2. 시간 정규화와 보고

| 번호 | 질문 | 정답 보기 | 출제 차시 |
|---|---|---|---|
| 1 | 2026-10-20T09:00:00+09:00과 같은 순간인 UTC 시각은? | 1번 · 2026-10-20T00:00:00+00:00 | forensic.timeline |
| 2 | 2026-10-20T01:30:00+09:00을 UTC로 바꾸면? | 4번 · 2026-10-19T16:30:00+00:00 | forensic.timeline |
| 3 | 서로 다른 오프셋의 로그 시각 문자열을 그대로 정렬하면 생길 수 있는 문제는? | 1번 · 표시 문자열 순서와 실제 순간 순서가 다를 수 있다. | forensic.timeline |
| 4 | timezone-aware datetime이 갖는 정보는? | 3번 · 시각의 오프셋·시간대 정보 | forensic.timeline |
| 5 | 시간대 없는 naive 시각을 받았습니다. UTC로 변환하기 전에 필요한 일은? | 4번 · 자료 출처의 시간대 설정과 가정을 확인한다. | forensic.timeline |
| 6 | UTC 정규화를 마친 뒤에도 따로 남는 검토는? | 1번 · 장비 시계 오차와 로그 수집 지연 | forensic.timeline |
| 7 | 정규화한 타임라인을 만들 때 원본 time 문자열의 취급은? | 2번 · 원본 자료에 유지하고 정규화 결과와 연결한다. | forensic.timeline |
| 8 | 기본 표본 E05의 2026-10-20T09:02:00+09:00을 UTC로 바꾼 결과는? | 1번 · 2026-10-20T00:02:00+00:00 | forensic.timeline |
| 9 | A가 B보다 1분 앞서 기록됐다는 사실이 곧 A가 B의 원인이라는 뜻인가요? | 2번 · 아니다. 시간 순서는 관찰이며 인과에는 추가 근거가 필요하다. | forensic.timeline |
| 10 | 2026-10-20T09:00:00+09:00과 2026-10-20T00:30:00+00:00 중 실제로 먼저인 것은? | 1번 · 09:00+09:00의 사건 | forensic.timeline |
| 11 | +09:00 오프셋의 의미에 맞는 계산은? | 3번 · 지역 시각에서 9시간을 빼 UTC를 구한다. | forensic.timeline |
| 12 | 실제 순간이 같게 정규화된 두 로그에 대한 적절한 서술은? | 1번 · 표시 기준상 같은 순간이며 더 세밀한 선후·인과는 추가 근거가 필요하다. | forensic.timeline |
| 13 | 시간대가 섞인 auth.csv를 실제 순간 기준으로 정렬한 ID 순서는? | 3번 · E01 → E02 → E03 → E04 → E05 → E06 | forensic.timeline |
| 14 | 근거가 추적되는 보고서의 구성으로 적절한 것은? | 2번 · 목적·자료와 해시·처리 절차·시간 기준·사실·해석·한계·후속 확인 | forensic.report |
| 15 | 분석에 참여하지 않은 독자를 위해 사실 문장에 연결해야 할 것은? | 3번 · 해당 사실을 뒷받침하는 자료와 행·증거 ID | forensic.report |
| 16 | 관찰 사실에 해당하는 문장은? | 2번 · E06에 file_read 이벤트가 기록되어 있다. | forensic.report |
| 17 | 관찰과 구분해야 하는 해석에 해당하는 것은? | 2번 · 계정 탈취 후 파일을 열람했다. | forensic.report |
| 18 | Network 흐름 로그와 시각이 닮았다는 이유만으로 같은 사건에 연결하면 안 되는 이유는? | 4번 · 같은 대상·세션임을 확인할 연결 키가 추가로 필요하기 때문이다. | forensic.report |
| 19 | 구체적인 후속 요청으로 적절한 것은? | 3번 · E05 세션 ID·MFA 결과와 E06 대상 파일·전송 기록을 확인한다. | forensic.report |
| 20 | 제공된 로그인·파일 읽기 기록만으로 보고서에서 확정할 수 없는 것은? | 4번 · 실제 외부 유출과 공격자 신원 | forensic.report |
| 21 | 외부 전송 기록을 확보하지 못했습니다. 보고서의 적절한 한계 문장은? | 3번 · 확보한 자료만으로 유출 여부를 판단할 수 없다. | forensic.report |
| 22 | 사실마다 E01~E06을 인용하고 원문 time으로 돌아갈 수 있게 하는 목적은? | 1번 · 관찰의 출처와 시간 변환을 독자가 추적하게 한다. | forensic.report |
| 23 | 다른 분석자가 보고서를 재현할 때 사용할 자료는? | 2번 · 보존된 원본을 기준으로 만든 작업 사본과 기록된 절차 | forensic.report |
| 24 | 후속 자료를 아직 받지 못한 가설은 어떻게 기록하나요? | 4번 · 검증할 질문과 필요한 자료를 적고 미확정으로 남긴다. | forensic.report |
| 25 | 보고서의 완성 기준으로 가장 적절한 조합은? | 4번 · 보존 근거·시간 변환·증거 연결 관찰·대안 가설·한계·구체적 후속 요청 | forensic.report |

## 3. 수집과 호스트 근거

| 번호 | 질문 | 정답 보기 | 출제 차시 |
|---|---|---|---|
| 1 | 수집 도구 실행 순서를 정하기 전에 확인할 사항은? | 3번 · 조사 질문·승인 범위·대상 시스템과 시간 범위 | forensic.collection-plan |
| 2 | 전원 종료로 사라질 수 있는 휘발성 자료의 예는? | 2번 · 메모리와 현재 연결 상태 | forensic.collection-plan |
| 3 | 휘발성 우선 원칙을 적용할 때 적절한 판단은? | 4번 · 진행 중인 피해·안전·운영 영향·조직 절차를 함께 고려한다. | forensic.collection-plan |
| 4 | 증거 인계 기록에서 함께 연결할 항목은? | 2번 · 증거 ID·출처·수집 시각/시간대·담당자·도구·보관 위치·해시·인계 이력 | forensic.collection-plan |
| 5 | casework.py plan 명령이 실제로 하는 일은? | 2번 · 지정한 order대로 합성 수집 계획을 표시한다. | forensic.collection-plan |
| 6 | 디스크 수집을 먼저 하는 동안 장비가 재부팅됐습니다. 계획 검토에서 적을 손실은? | 1번 · 메모리·현재 연결 같은 휘발성 자료를 잃을 수 있다. | forensic.collection-plan |
| 7 | 획득 도구 실행으로 시스템 상태가 바뀌거나 수집이 실패했습니다. 기록 방식은? | 2번 · 사용 도구·조건과 상태 변경 가능성·실패·누락을 남긴다. | forensic.collection-plan |
| 8 | 진행 중인 피해 때문에 증거 수집보다 격리를 앞당기는 계획을 검토합니다. 필요한 기록은? | 2번 · 승인자·예상 영향·보존할 근거와 순서 변경의 득실 | forensic.collection-plan |
| 9 | 프로세스 이름이 낯설다는 사실에 대한 적절한 조치는? | 4번 · 부모·사용자·시작 시각·연결 등과 교차해 추가 조사 단서로 삼는다. | forensic.host-triage |
| 10 | 기본 스냅샷에서 C01은 PID 300, helper의 부모는 PID 200 viewer입니다. 관찰 연결은? | 2번 · viewer → helper → 203.0.113.44:443 | forensic.host-triage |
| 11 | 서로 다른 시각의 프로세스 표를 PID만으로 조인할 때의 위험은? | 4번 · PID 재사용이나 수집 시각 차이로 다른 프로세스를 붙일 수 있다. | forensic.host-triage |
| 12 | C03의 PID 999가 프로세스 표에 없습니다. 적절한 해석은? | 3번 · UNKNOWN으로 남기고 종료·수집 간격·권한·누락 가능성을 확인한다. | forensic.host-triage |
| 13 | 사본에서 C01의 PID만 300에서 999로 바꿨습니다. 원래 viewer→helper 연결의 취급은? | 3번 · 그 조인이 사라지므로 C01의 프로세스를 UNKNOWN으로 남긴다. | forensic.host-triage |
| 14 | C01이 실제 의심 행위인지 조사할 후속 자료 조합은? | 1번 · 실행 경로·해시/서명, 명령줄·부모 시작 이벤트, 전송량·패킷 | forensic.host-triage |
| 15 | 제공된 합성 스냅샷의 프로세스·연결 표를 모두 확인했을 때에도 확정할 수 없는 것은? | 1번 · 실제 위험 인프라 접속과 데이터 유출 | forensic.host-triage |
| 16 | 실제 프로세스 동일성 검토에 PID와 함께 사용할 근거는? | 3번 · 호스트·수집 시각·프로세스 시작 시각 또는 고유 이벤트 ID | forensic.host-triage |
| 17 | 이 강의의 visits(id,time,url,transition) 데이터베이스는? | 1번 · 독자적인 합성 스키마와 ISO 시각을 쓰는 교육 표본 | forensic.browser-sqlite |
| 18 | 기본 history.sql은 3행이고 auto 한 행을 제외합니다. 표시 수/전체 수는? | 4번 · 표시 2행 / 전체 3행 | forensic.browser-sqlite |
| 19 | B03의 transition만 auto에서 link로 바꿨습니다. 표시 수와 전체 수는? | 3번 · 표시 3행 / 전체 3행 | forensic.browser-sqlite |
| 20 | 방문 기록에 URL이 있다는 사실만으로 확정하기 어려운 것은? | 1번 · 특정 사람이 의도적으로 페이지 내용을 읽었다는 것 | forensic.browser-sqlite |
| 21 | 실행 중인 실제 SQLite에서 DB 파일 하나만 복사할 때 최근 자료가 누락될 수 있는 이유는? | 3번 · 최근 트랜잭션이 WAL에 남아 있을 수 있기 때문이다. | forensic.browser-sqlite |
| 22 | 필터가 분석 범위에 준 영향을 추적하기 위해 남길 것은? | 4번 · 질의 조건·전체 행수·표시 행수·제외 행 ID | forensic.browser-sqlite |
| 23 | 실제 브라우저 DB를 추가로 분석한다면 별도로 확인할 사항은? | 1번 · 제품·버전별 스키마·시간 epoch·WAL과 수집 절차 | forensic.browser-sqlite |
| 24 | transition=typed라는 합성 분류가 직접 증명하지 않는 것은? | 2번 · 실제 사용자의 신원과 행위 의도 | forensic.browser-sqlite |
| 25 | 이 실습이 history.sql을 실행하는 데이터베이스 위치는? | 4번 · 메모리 DB이며 실제 사용자 프로필을 열지 않는다. | forensic.browser-sqlite |

## 4. 조각·상관·사고 대응

| 번호 | 질문 | 정답 보기 | 출제 차시 |
|---|---|---|---|
| 1 | 파일 확장자와 내부 바이트 시그니처가 다릅니다. 적절한 다음 판단은? | 1번 · 확장자만 믿지 않고 시그니처와 내부 구조를 함께 확인한다. | forensic.file-signatures |
| 2 | BF 가상 형식의 길이 바이트가 Hex 03 00입니다. little-endian으로 해석한 payload 길이는? | 4번 · 3바이트 | forensic.file-signatures |
| 3 | fragments.hex의 오프셋 10 후보는 5바이트 본문을 선언했지만 XY 2바이트만 있습니다. 판정과 근거는? | 1번 · INCOMPLETE: 선언 길이보다 실제 사용 가능한 본문이 짧다. | forensic.file-signatures |
| 4 | 불완전한 두 번째 BF 후보 뒤에 Hex 5a3132를 붙였습니다. 본문은 XY에서 어떻게 바뀌나요? | 2번 · XYZ12, 실제 본문 5바이트가 되어 가상 길이 계약상 COMPLETE | forensic.file-signatures |
| 5 | 0부터 세는 Hex 오프셋 00000008은 몇 번째 바이트를 가리키나요? | 2번 · 아홉 번째 바이트 | forensic.file-signatures |
| 6 | Hex 덤프에서 바이트 열 4개가 89 50 4e 47로 보입니다. 바이트 수는? | 2번 · 4바이트 | forensic.file-signatures |
| 7 | Hex 덤프의 ASCII 쪽에 표시된 점(.)의 의미로 적절한 것은? | 1번 · 화면에 인쇄하기 어려운 바이트의 표시일 수 있다. | forensic.file-signatures |
| 8 | PNG의 시작 8바이트 시그니처는? | 2번 · 89 50 4e 47 0d 0a 1a 0a | forensic.file-signatures |
| 9 | PNG 청크의 길이 4바이트 필드에 대한 설명은? | 2번 · 데이터 길이를 big-endian으로 나타낸다. | forensic.file-signatures |
| 10 | PNG 청크의 데이터 길이가 13바이트입니다. 길이 4·종류 4·CRC 4를 포함한 청크 전체 크기는? | 4번 · 25바이트 | forensic.file-signatures |
| 11 | PNG 청크 CRC가 계산 대상으로 삼는 바이트는? | 1번 · 청크 종류와 청크 데이터 | forensic.file-signatures |
| 12 | IHDR·IDAT·IEND의 역할 조합으로 맞는 것은? | 3번 · 이미지 속성·압축 픽셀 데이터·끝 | forensic.file-signatures |
| 13 | 정상 PNG가 이 실습 도구에서 UNVERIFIED가 될 수 있는 이유는? | 2번 · 도구가 64×64 이하 RGB8 비인터레이스의 좁은 교육 계약만 지원한다. | forensic.file-signatures |
| 14 | JPEG·ZIP 접두 후보가 표시된 결과의 올바른 해석은? | 1번 · 이 도구는 식별 단서를 표시했으며 내부 전체 디코딩·검증은 별도다. | forensic.file-signatures |
| 15 | mixed.bin의 오프셋 17에서 추출한 PNG를 확인하는 절차로 적절한 것은? | 3번 · 구조 검증 뒤 새 파일에 추출하고 원본 PNG와 바이트·SHA-256을 비교하며 뷰어로 확인한다. | forensic.file-signatures |
| 16 | casework.py correlate가 선택하는 연결 조건은? | 2번 · host와 session이 모두 지정값과 일치한다. | forensic.log-correlation |
| 17 | W02는 시각이 가깝지만 workstation-8/S11입니다. 기본 선택 결과에서의 취급은? | 4번 · host와 session이 다르므로 제외한다. | forensic.log-correlation |
| 18 | W02의 host와 session을 모두 workstation-7/S10으로 바꾼 경우 선택 수와 삽입 UTC 시각은? | 1번 · 5건, 00:00:10 | forensic.log-correlation |
| 19 | 상관 표본에 오프셋 없는 시각을 넣었을 때 이 도구의 처리는? | 4번 · 시간대 가정을 숨기지 않도록 오류로 거부한다. | forensic.log-correlation |
| 20 | 다운로드→프로세스 시작→연결의 시간 순서를 확인했습니다. 남는 한계는? | 4번 · 다운로드가 실행의 원인이라는 주장은 파일 해시·실행 인자 등 독립 근거가 더 필요하다. | forensic.log-correlation |
| 21 | response.json에서 confirmed-hosts의 뜻은? | 3번 · 확인된 관찰이 있는 호스트 집합이며 전체 침해 범위 증명은 아니다. | forensic.incident-response |
| 22 | 모형의 조치가 READY-FOR-REVIEW가 되기 위한 조건은? | 4번 · 승인·영향 검토·증거 보존이 모두 참 | forensic.incident-response |
| 23 | 격리 조치의 authorized만 false로 바꾸고 나머지 두 조건은 true입니다. 모형의 표시는? | 3번 · HOLD | forensic.incident-response |
| 24 | 전원 종료와 네트워크 격리를 비교할 때 맞는 설명은? | 3번 · 종료는 휘발성 근거를 잃을 수 있고 격리는 이미 저장된 자료·내부 실행을 모두 제거하지 않는다. | forensic.incident-response |
| 25 | 복구 검증 계획으로 적절한 것은? | 3번 · 원인 수정·정상 기능·허용/거부 정책·모니터링과 재발 징후·관찰 기간을 정한다. | forensic.incident-response |

## 5. 운영체제 기록의 의미

| 번호 | 질문 | 정답 보기 | 출제 차시 |
|---|---|---|---|
| 1 | Windows 이벤트 번호를 해석할 때 함께 확인할 맥락은? | 1번 · Provider·채널·버전과 출처 | forensic.windows-events |
| 2 | EventData에서 TargetUserName 값을 찾는 적절한 기준은? | 3번 · Data의 Name 속성 | forensic.windows-events |
| 3 | Data 요소의 순서만 바꾸고 각 Name과 값을 유지했습니다. 이름 기반 파서의 기대 결과는? | 3번 · 동일한 필드 값이 추출된다. | forensic.windows-events |
| 4 | XML에서 Event 이름만 검색했더니 지원 기록을 놓쳤습니다. 이 표본에서 확인할 것은? | 2번 · Event가 사용하는 XML 네임스페이스 | forensic.windows-events |
| 5 | 강의의 4625·4624 합성 이벤트의 의미 조합은? | 3번 · 로그온 실패·로그온 성공 | forensic.windows-events |
| 6 | 합성 성공 이벤트의 LogonType=3을 해석한 설명은? | 1번 · 네트워크 로그온 맥락이며 대화형 데스크톱 사용 증명은 아니다. | forensic.windows-events |
| 7 | 서로 다른 컴퓨터에서 EventRecordID가 같습니다. 실제 통합 분석의 적절한 식별 방식은? | 1번 · 출처·컴퓨터·채널·기록 ID를 함께 사용한다. | forensic.windows-events |
| 8 | 단일 컴퓨터/채널 합성 내보내기의 두 RecordID를 동일하게 만든 경우 적절한 결과 해석은? | 4번 · 중복 ID 오류이며 오류 전 일부 출력만으로 전체 성공이라 하지 않는다. | forensic.windows-events |
| 9 | artifacts_round2.py windows 실습이 읽는 형식과 수행 범위는? | 4번 · 합성 XML이며 실제 EVTX 바이너리 파싱은 하지 않는다. | forensic.windows-events |
| 10 | Linux 인증 기록을 분석할 때 배포판·설정을 확인하는 이유는? | 1번 · 텍스트 파일·journal·수집기 등 기록 형식과 위치가 다를 수 있다. | forensic.linux-auth |
| 11 | L11 실패와 L12 성공의 사용자 이름이 같지만 PID·세션이 다릅니다. 타당한 해석은? | 3번 · 동일 프로세스의 재시도나 공격 성공으로 바로 확정하지 않는다. | forensic.linux-auth |
| 12 | L13이 alice/S22의 선행 성공과 연결되고 result=allow입니다. 직접 확인한 범위는? | 4번 · 해당 키의 선행 성공 기록과 허용된 sudo 요청 | forensic.linux-auth |
| 13 | L14 bob/S23의 deny 요청에 연결된 선행 성공 기록이 없습니다. 적절한 서술은? | 4번 · 표본에서 연결된 선행 성공이 없고 요청은 거부로 기록됐다. | forensic.linux-auth |
| 14 | L13 세션만 S22에서 S99로 바꿨습니다. 선행 연결과 허용 결과의 변화는? | 1번 · linked-login=False가 되고 allow 자체는 유지된다. | forensic.linux-auth |
| 15 | 허용된 sudo 요청이 실제로 완료됐는지 확인할 후속 자료는? | 2번 · 명령 시작/종료 감사, 종료 코드·출력 또는 실행 기록 | forensic.linux-auth |
| 16 | 이 모형이 선행 성공과 sudo 요청을 연결할 때 보는 키는? | 1번 · 호스트·사용자·세션 | forensic.linux-auth |
| 17 | 원본의 감사 설정·수집 범위가 부족할 때 기록 부재의 해석은? | 2번 · 활동 부재로 바로 바꾸지 않고 관측 가능성과 누락을 검토한다. | forensic.linux-auth |
| 18 | 같은 파일시스템·같은 시점의 여러 이름이 하나의 inode를 가리킬 때 가능한 관계는? | 4번 · 하드링크로 여러 이름이 같은 파일 객체를 참조한다. | forensic.filesystem-records |
| 19 | R1 notes.txt와 R2 alias.txt가 inode 42·links=2를 공유합니다. 이 표본의 관찰은? | 2번 · 이름 2개와 파일 객체 1개 | forensic.filesystem-records |
| 20 | 다른 장치 또는 다른 시점에서 같은 inode 번호를 발견했습니다. 추가 확인이 필요한 이유는? | 2번 · 장치 간 번호 중복과 시간에 따른 inode 재사용이 가능하다. | forensic.filesystem-records |
| 21 | Linux 계열 ctime의 일반적인 의미는? | 1번 · 메타데이터 상태 변경 시각 | forensic.filesystem-records |
| 22 | birth 정보가 없는 파일의 생성 시각은 이 강의에서 어떻게 기록하나요? | 4번 · UNKNOWN으로 남긴다. | forensic.filesystem-records |
| 23 | R2를 수집 목록에서만 제거했지만 R1의 links=2는 유지했습니다. 결과 해석은? | 3번 · 관찰 이름 1개와 선언 링크 2의 불일치로 부분 수집 등을 확인한다. | forensic.filesystem-records |
| 24 | mtime과 ctime이 다르다는 사실만으로 확정하기 어려운 것은? | 3번 · 특정 사용자가 특정 명령으로 조작했다는 것 | forensic.filesystem-records |
| 25 | 수집 목록에서 파일 이름 하나를 찾지 못했습니다. 적절한 판단은? | 2번 · 관찰 누락과 실제 unlink·내용 삭제를 별도로 검증한다. | forensic.filesystem-records |

## 6. 메모리 단서와 관측 한계

| 번호 | 질문 | 정답 보기 | 출제 차시 |
|---|---|---|---|
| 1 | memory-model.json 실습의 자료와 범위는? | 3번 · 합성 프로세스/영역 JSON이며 실제 RAM 덤프·VAD 파싱은 하지 않는다. | forensic.memory-triage |
| 2 | 시작 8192, 크기 4096인 M2의 반열린 주소 구간은? | 1번 · [8192,12288) | forensic.memory-triage |
| 3 | 구간 [8192,12288)에 포함되지 않는 주소는? | 4번 · 12288 | forensic.memory-triage |
| 4 | 이 모형에서 REVIEW 조건을 만족하는 영역 조합은? | 4번 · private 백킹이며 쓰기 w와 실행 x가 모두 있다. | forensic.memory-triage |
| 5 | private-WX=REVIEW 결과가 직접 의미하는 것은? | 3번 · 추가 조사가 필요할 수 있는 모형 규칙의 일치 | forensic.memory-triage |
| 6 | M2의 permission만 rwx에서 rx로 바꾸면 이 표본의 검토 수는? | 4번 · 0개 | forensic.memory-triage |
| 7 | 위 변경 후 review=0을 보고도 안전 판정으로 확정하면 안 되는 이유는? | 3번 · 다른 권한의 악성 동작이나 자료 누락은 이 규칙 밖에 남을 수 있어서 | forensic.memory-triage |
| 8 | M2의 size를 0으로 바꾼 입력의 취급은? | 2번 · 유효 영역이 아닌 입력 오류로 거부한다. | forensic.memory-triage |
| 9 | private WX가 정상 기능에서도 생길 수 있다는 강의의 예는? | 1번 · JIT 같은 동적 코드 생성 기능 | forensic.memory-triage |
| 10 | 메모리 영역의 실제 위협성을 추가로 조사할 자료는? | 2번 · 프로세스·모듈 출처, 스레드 관계, 실제 바이트·페이지 상태·로그 | forensic.memory-triage |
| 11 | 영역 주소 연산 전에 모형이 확인하는 범위 조건은? | 1번 · start가 정수이고 0 이상, size가 정수이고 양수 | forensic.memory-triage |
| 12 | private 영역의 permission=rw라면 이 모형의 결과는? | 3번 · 실행 x가 없어 private-WX 규칙에 일치하지 않는다. | forensic.memory-triage |
| 13 | 시간대 UTC 변환과 장비 시계 오차 보정의 관계는? | 2번 · 표시 기준 맞추기와 장비 오차 보정은 다른 작업이다. | forensic.evidence-coverage |
| 14 | 이 모형의 보정 중심 계산식은? | 4번 · recorded - clock_ahead | forensic.evidence-coverage |
| 15 | E31의 recorded=100, clock_ahead=8, uncertainty=2입니다. 보정 구간은? | 2번 · [90,94] | forensic.evidence-coverage |
| 16 | E32의 recorded=96, clock_ahead=0, uncertainty=3입니다. 보정 구간은? | 4번 · [93,99] | forensic.evidence-coverage |
| 17 | E31 [90,94]와 E32 [93,99]에 대한 이 모형의 관계 판정은? | 1번 · ORDER-UNCERTAIN | forensic.evidence-coverage |
| 18 | A [90,94], B [94,99]처럼 경계가 접할 때 판정은? | 3번 · ORDER-UNCERTAIN | forensic.evidence-coverage |
| 19 | A [90,92], B [93,99]일 때 판정은? | 1번 · A-BEFORE-B | forensic.evidence-coverage |
| 20 | 기본 E31·E32의 uncertainty만 모두 0으로 바꾼 모형 결과는? | 1번 · [92,92], [96,96], A-BEFORE-B | forensic.evidence-coverage |
| 21 | uncertainty를 파일에서 0으로 바꿨다는 사실이 실제 장비의 정확도를 증명하지 않는 이유는? | 2번 · 오차 범위를 줄일 동기화·측정·수집 지연 근거가 별도로 필요하다. | forensic.evidence-coverage |
| 22 | auth logging-enabled=True가 직접 보장하지 않는 것은? | 3번 · 지정 시간 범위의 모든 행이 빠짐없이 수집됐다는 것 | forensic.evidence-coverage |
| 23 | process logging-enabled=False이고 실행 행도 없습니다. 적절한 결론은? | 4번 · 그 자료만으로 프로세스 실행 부재를 확정할 수 없다. | forensic.evidence-coverage |
| 24 | 합성 coverage에서 process enabled만 false에서 true로 바꾸면 실제 새 사건 행도 생기나요? | 3번 · 아니다. 설정 표시는 바뀌지만 기존 사건과 시간 구간은 그대로다. | forensic.evidence-coverage |
| 25 | A의 보정 구간이 [95,100], B가 [80,90]이면 이 모형의 엄격한 순서는? | 2번 · B-BEFORE-A | forensic.evidence-coverage |
