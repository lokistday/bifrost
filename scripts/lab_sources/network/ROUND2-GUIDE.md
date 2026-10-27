# 프로토콜 경계와 관측 품질

이 자료는 합성 JSON과 작은 바이트 모델입니다. 패킷·DNS 질의를 보내거나 실제 방화벽·라우터를 변경하지 않습니다. Python 3.10 이상 표준 라이브러리만 필요합니다. ZIP 전체를 풀고 이 폴더에서 실행하세요. Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`입니다.

| 차시 | 실행 | 기본 결과 |
| --- | --- | --- |
| IPv6 경계 | `python3 protocol_models.py ipv6` | F1 ALLOW, F2 DENY, F3 SCOPE_REQUIRED, F4 DENY |
| 스트림 재조립 | `python3 protocol_models.py reassembly` | 8바이트·누락0·충돌0·BIFROST! |
| DNS 캐시 | `python3 protocol_models.py dns` | 양성·NXDOMAIN 모두29에 사용,30에 만료 |
| 경로 MTU | `python3 protocol_models.py mtu` | 1500>1280, 기본 IPv6/TCP 예산1220 |
| 사건 시각 | `python3 protocol_models.py sessions` | 수락3·지연1·2세션, 전체 사후1세션 |

## 작업 사본과 반례

`protocol-models.json`을 `protocol-work.json`으로 복사해 변경하고 `python3 protocol_models.py ipv6 --input protocol-work.json`처럼 읽습니다. 파일 탐색기, PowerShell의 `Copy-Item`, Linux의 `cp` 중 편한 방법으로 복사하세요. 원본을 덮어쓰지 않습니다.

1. **IPv6:** `family_rules`에 `{"network":"2001:db8:20::/64","port":443}`를 추가하면 F2만 ALLOW로 바뀝니다. F3에 `interface: lab0`을 추가하면 범위 누락은 해결되지만 허용 규칙이 없어 DENY입니다. scope는 일부 범주만 구분합니다. other-ipv6는 공인·인터넷 도달 가능이라는 뜻이 아닙니다. 문서 주소에는 실제 접속하지 않습니다.
2. **재조립:** `--case gap`은 누락2, `--case conflict`는 충돌1과 UNAVAILABLE입니다. conflict의 마지막 hex=58을46으로 바꾸면 같은 바이트의 중복이 되어 BIFROST!입니다. offset은 이미 정규화한 상대 위치입니다. 실제 TCP 연결 식별·순번 wrap·SYN/FIN·IP 조각 재조립과 수신자별 겹침 정책은 생략했습니다.
3. **DNS:** 부정 응답의 `soa_minimum`을5로 바꾸면 받은 시각10+5=15에 만료되어 Q3도 MISS입니다. NXDOMAIN은 이 IN 클래스의 이름, NODATA는 이름·질의 타입에 적용합니다. MISS는 이름 부재의 증명이 아닙니다. CNAME·위임·DNSSEC·오래된 응답 제공은 구현하지 않았습니다.
4. **MTU:** `path_mtu=1500`은 oversized=False·기본 예산1440입니다. IPv6 기본40+TCP20+옵션12를1280에서 빼면1208입니다. 표본의 STALLED는 PTB 피드백에 의존하고 다른 회복이 없다고 정한 가정입니다. 실제 스택의 PLPMTUD·작은 세그먼트 회복을 보장하거나 부정하지 않습니다. IPv6 1280미만 링크 처리도 모형 밖입니다.
5. **시각:** `lateness=8`이면 watermark6과 같은 E4를 수락해4사건·0지연·1세션입니다. 사건 간격이 timeout **이상**이면 새 세션, 사건 시각이 watermark보다 **작으면** 지연이라는 두 경계를 구분하세요. 한 호스트·한 분석 키만 가정합니다. 실제 집계는 사용자·호스트 등 키별로 나눕니다.

## 남길 기록

원본·사본 파일, 명령, 예상·실제 결과와 차이를 남깁니다. 지연 자료를 별도로 보존하고 재처리 버전·수정 경보·보고서 정정 기준을 적습니다. 패킷 누락과 바이트 충돌은 결론을 유보할 근거이며 임의의 값으로 채워 완전한 원문이라고 쓰지 않습니다.
