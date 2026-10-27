# Forensic · 운영체제 근거와 관측 한계

모든 입력은 독자적으로 만든 작은 합성 자료입니다. 실제 EVTX·journal·NTFS/ext4·RAM 덤프를 파싱하거나 획득하지 않습니다. 기존 자료·`LAB-GUIDE.md`는 유지합니다. Python 3.10 이상, 표준 라이브러리만 필요합니다. Linux/macOS는 `python3`, Windows PowerShell은 `py -3`를 사용하세요.

| 명령 | 자료 | 기준 결과 |
| --- | --- | --- |
| `python3 artifacts_round2.py windows` | events-synthetic.xml | record101 실패·102 성공, UTC 10초 차이 |
| `python3 artifacts_round2.py linux` | linux-auth.jsonl | L13 선행 연결 True, L14 False |
| `python3 artifacts_round2.py filesystem` | fs-records.json | inode42 이름2/링크2, inode77 이름1/링크1 |
| `python3 artifacts_round2.py memory` | memory-model.json | M2 REVIEW, review=1 |
| `python3 artifacts_round2.py coverage` | coverage.json | [90,94]와 [93,99], ORDER-UNCERTAIN |

사본 입력은 `--source 파일명`으로 선택합니다. 원본을 보관하고 별도 사본에서 과제를 수행하세요. 오류 전 일부 출력은 전체 성공 결과가 아닙니다.

## XML의 출처와 필드

EventData는 위치가 아니라 `Data Name`으로 읽습니다. 필드 순서를 바꿔도 값이 같아야 합니다. 두 번째 시각 +09:00은 UTC로 정규화합니다. EventRecordID 중복 검사는 **한 컴퓨터/채널의 단일 합성 내보내기** 기준입니다. 실제 서로 다른 장비·채널의 같은 번호는 유효한 별도 기록일 수 있습니다. 출처·컴퓨터·채널을 포함한 키가 필요합니다. 4624와 LogonType3만으로 사람의 대화형 데스크톱 사용을 확정하지 않습니다. 제공한 신뢰 XML만 사용하며 임의의 대용량/적대적 XML 처리기는 아닙니다.

## 인증 요청과 실행 결과

Linux 표본은 UTC·ID로 정렬한 뒤 host/user/session이 같은 선행 인증 성공을 sudo 요청에 연결합니다. 파일 행 순서를 역순으로 저장해도 결과가 같습니다. L13의 session만 S99로 바꾸면 linked-login=False입니다. 선행 기록의 존재는 현재 활성 세션이나 명령 성공을 증명하지 않습니다. 프로그램은 `/usr/bin/id` 문자열만 표시하며 실제로 실행하지 않습니다.

## 이름·객체·시간

FS 자료는 **동일 파일시스템의 한 스냅샷**입니다. inode 숫자는 장치와 시점에 관계없이 전역적으로 유일하지 않습니다. R2를 수집 목록에서 빼면 관찰 이름1/선언 링크2가 되지만 실제 unlink나 내용 삭제를 증명하지 않습니다. ctime은 일반적으로 상태 변경 시각이고 birth가 없으면 UNKNOWN으로 남깁니다. 실제 파일을 삭제하는 실습은 없습니다.

## 메모리 규칙의 범위

M2의 private+rwx 조건은 우선 조사 규칙입니다. [8192,12288)은 끝 주소를 제외합니다. JIT 등 정상 기능에서도 일치할 수 있고 다른 권한의 악성 동작은 놓칠 수 있습니다. M2를 rx로 바꾸면 review=0이며 안전 판정은 아닙니다. size=0은 형식 오류입니다. 실제 바이트·모듈·스레드·출처는 제공하지 않으므로 추가 증거가 필요합니다.

## 시간 오차와 기록 부재

보정 중심은 recorded-clock_ahead, 구간은 중심±uncertainty입니다. UTC 변환과 시계 오차 보정은 다릅니다. 겹치거나 접하는 구간은 엄격한 선후를 확정하지 않습니다. 두 uncertainty를 0으로 바꾸면 [92,92]와 [96,96]으로 A-BEFORE-B가 되지만 실제 오차0의 근거를 얻은 것은 아닙니다. logging-enabled는 설정 정보이며 수집 완전성 보증이 아닙니다. 비활성 process 로그의 부재로 실행 부재를 단정하지 마세요.
