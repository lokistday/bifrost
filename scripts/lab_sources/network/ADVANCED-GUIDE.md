# 경로·상태·운영 검증 실습

이 자료의 주소·로그·정답 라벨은 직접 만든 합성 표본입니다. 외부 접속, 패킷 전송, 방화벽 변경은 하지 않습니다. Python 3.10 이상과 표준 라이브러리만 필요합니다. ZIP 전체를 풀고 이 폴더에서 실행하세요.

Linux/WSL/macOS는 `python3`, Windows PowerShell은 `py -3`를 사용합니다.

## 실행과 핵심 관찰

| 명령 | 핵심 결과 |
| --- | --- |
| `python3 defense_models.py routing` | `prefix=10.20.0.0/16 next_hop=app` |
| `python3 defense_models.py nat` | NAT01은 10.20.1.7, NAT02는 UNKNOWN, NAT03은 10.20.1.8 |
| `python3 defense_models.py state` | S1~S4 허용, S5 거부, S6 종료, S7 거부 |
| `python3 defense_models.py metrics` | TP=2 FP=2 FN=1 TN=3, 정밀도 0.500·재현율 0.667 |
| `python3 defense_models.py response` | R-17의 세 관측, 시도 관측·영향 미확인 |

## 작업 사본으로 반례 만들기

`defense-models.json`을 `defense-work.json`으로 복사하고 수정합니다. Linux의 `cp`와 PowerShell의 `Copy-Item` 또는 파일 탐색기를 사용할 수 있습니다. 명령은 `python3 defense_models.py routing --input defense-work.json`처럼 사본을 지정합니다. 원본과 사본의 결과를 각각 기록하세요.

1. **경로:** /16 항목을 제거하면 /8의 core로 바뀝니다. 기본 경로도 없고 일치하는 경로가 없으면 `route=NONE`입니다. 라우팅 성공은 정책 허용이나 서버 정상성을 증명하지 않습니다.
2. **NAT:** NAT01의 외부 포트를 40002로 바꾸면 10.20.1.8과 연결됩니다. 유효 시간은 시작 포함·종료 제외입니다. TCP 한 종류만 가정하며 실제 분석에는 프로토콜·장비·다단계 변환·시계 오차도 필요합니다. 매핑이 여러 개면 임의로 하나를 선택하지 않습니다. 주소 식별은 사람 식별이 아닙니다.
3. **상태:** S2를 제외하면 S3·S4가 pending에서 거부됩니다. 실제 TCP의 시퀀스·재전송·윈도·시간 만료·종료는 생략했습니다. 운영 방화벽으로 사용하지 않습니다.
4. **탐지:** `--threshold 5`는 TP=2 FP=0 FN=1 TN=5, `--threshold 6`은 TP=1 FP=0 FN=2 TN=5입니다. `--threshold 99`에서는 경보가 없어서 정밀도는 undefined, 재현율은 0.000입니다. 학습 표본에서 고른 임계값을 운영 성능으로 주장하지 않습니다.
5. **사건 연결:** R-17의 app 행을 제거하면 `correlated=2 conclusion=insufficient_evidence impact=UNCONFIRMED`입니다. 실제 DNS·방화벽 로그에 공통 요청 ID가 있다고 가정하지 않습니다. 연결 필드와 오차를 검증하고 R-18의 200을 R-17 성공으로 합치지 않습니다.

## 남길 결과

입력 사본·명령·예측·실제 출력·차이 원인을 남깁니다. 대응 판단은 확인한 사실, 미확인 영향, 추가 증거, 차단의 서비스 영향과 되돌리기 조건으로 나누어 씁니다.
