# TLS와 평문을 같은 요청으로 비교하기

외부 서버나 계정이 필요 없습니다. 기존 `traffic.pcap`과 `tls13.pcap`을 각각 열어 `GET /lesson`을 관찰합니다. `traffic.pcap`은 8프레임의 평문 합성 표본이며, `tls13.pcap`의 TLS 바이트는 실제 OpenSSL 연결에서 생성했습니다. TCP 헤더와 타임스탬프는 합성했습니다. `tls-notes.txt`에 필터, 키 로그 비교 방법과 한계를 자세히 적었습니다.

## 준비와 실행

ZIP을 풀고 `network` 폴더에서 Linux/WSL/macOS는 `python3 analyze_tls.py`, Windows PowerShell은 `py -3 analyze_tls.py`를 실행합니다. Python 3.10 이상의 표준 라이브러리만 사용합니다. 스크립트는 파일만 읽고 네트워크에 접속하지 않습니다.

Wireshark는 선택 도구입니다. 처음에는 TLS 키 로그 설정이 비어 있는 별도 프로필에서 관찰하세요. 키 없이 `http.request`가 0개여도 요청이 없었다고 결론 내릴 수 없습니다.

## 기록할 것

| 비교 항목 | traffic.pcap | tls13.pcap, 키 없이 |
| --- | --- | --- |
| 상대 IP·방향·전송 포트 | 관측 가능 | 관측 가능 |
| 요청 경로 `/lesson` | 평문 HTTP에서 보임 | 암호화돼 보이지 않음 |
| ClientHello / ServerHello | 없음 | 각 1개 |
| SNI | 해당 없음 | 이 표본에서는 `bifrost.test` |
| TLS 버전 | 해당 없음 | ServerHello 확장: TLS 1.3 |
| 서버 인증서 | 해당 없음 | TLS 1.3에서는 암호화됨 |

## 변경 과제와 풀이 기준

과제: `tls` 필터가 0인 파일과 `http.request` 필터가 0인 파일에서 각각 무엇을 결론 내릴 수 있는지 두 문장씩 적으세요. 그다음 제공한 교육용 `tls13.keys`를 Wireshark에 지정해 같은 요청을 확인하고 키 없이 관찰한 표와 비교합니다.

좋은 기록은 ① 파일 이름과 필터, ② 직접 보인 값, ③ 관측되지 않은 값, ④ 키 설정 여부, ⑤ 일반화할 수 없는 조건을 구분합니다. 예: “tls13.pcap은 키 없이 HTTP 경로를 확인할 수 없지만 ClientHello와 ServerHello가 있으며 암호화된 레코드가 있다. 키 로그를 적용하면 같은 바이트에서 /lesson 요청이 복호화된다.”

오답 예: “http.request=0이므로 웹 요청이 없다”, “443이면 무조건 안전하다”, “Application Data가 8개니까 웹 요청도 8개다”. 각각 관측 범위, 인증·설정 검증, 외부 레코드와 내부 메시지 구분을 놓친 주장입니다.

## 출처와 재현

사이트 저장소의 `scripts/refresh_lab_fixtures.py`가 소켓 없이 `ssl.MemoryBIO`로 연결을 만들고, `content/lab-fixtures/tls13.json`에 원본 TLS 바이트와 이 교육 연결의 키 로그를 고정합니다. 일반 빌드는 이 원본에서 결정적으로 PCAP을 만듭니다. 실제 사람의 트래픽을 가져온 자료가 아닙니다. 인증서와 키 로그는 이 표본에만 쓰는 공개 교육 데이터입니다.
