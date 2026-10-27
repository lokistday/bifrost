# Forensic · 합성 사건 BF-IR-002

이 묶음은 실제 개인자료·브라우저 DB·메모리 덤프가 아닙니다. 원래 `auth.csv`, `timeline.py`, `evidence.txt`와 새 합성 자료를 함께 사용합니다. 모든 분석은 오프라인이며 실제 PC를 조사하거나 격리·종료·삭제하지 않습니다.

Python 3.10 이상에서 ZIP을 풀고 forensic 폴더로 이동하세요. Linux/macOS는 `python3`, Windows PowerShell은 `py -3`를 사용합니다. 변경 과제는 원본을 보존한 사본에서 수행합니다.

| 명령 | 자료 | 확인하는 범위 |
| --- | --- | --- |
| `python3 casework.py plan` | case.json | E01→E02→E03, records=3, 계획 표시만 |
| `python3 casework.py host` | snapshot.json | C01 viewer→helper, C03 PID 999 UNKNOWN |
| `python3 casework.py browser` | history.sql | 합성 방문 3행 중 2행 표시 |
| `python3 casework.py carve` | fragments.hex | offset 2 COMPLETE, offset 10 INCOMPLETE |
| `python3 casework.py correlate` | crosslog.csv | UTC 네 행 연결, 다른 호스트 한 행 제외 |
| `python3 casework.py respond` | response.json | 격리 검토 준비, 나머지 HOLD, execution=NONE |

사본은 `--source 파일명`으로 선택합니다. 형식 오류는 `INVALID`와 종료 상태 2로 표시합니다. 이 도구의 검증은 교육 모형의 범위에 한정됩니다.

## 계획·관찰·판단 구분

- **수집 계획:** order는 사람이 지정한 계획입니다. 휘발성 우선 원칙을 참고하되 피해·안전·업무 영향을 함께 검토합니다. 이 명령이 메모리를 획득하거나 올바른 순서를 자동 인증하지 않습니다. 인계 기록에 출처·도구·시각/시간대·담당자·보관 위치·해시·이동 이력을 연결하세요.
- **호스트:** PID 300은 같은 합성 스냅샷에서 helper와 연결됩니다. 다른 시점의 표는 PID 재사용 때문에 시작시각·호스트·고유 이벤트 식별자를 더 확인해야 합니다. 이름이나 443 연결만으로 악성·유출을 판정하지 마세요.
- **SQLite:** 신뢰하는 제공 SQL만 메모리 DB에서 실행합니다. 이 스키마와 ISO 시각은 실제 브라우저 제품의 형식이 아닙니다. 임의 출처 SQL은 실행하지 마세요. 메모리 DB는 안전한 SQL 샌드박스가 아닙니다. 실제 수집에서는 WAL과 관련 파일·일관성 절차가 필요합니다.
- **파일 조각:** BF는 서명과 길이만 가진 가상 형식입니다. COMPLETE는 연속 길이가 충분하다는 뜻이며 실제 문서·원래 경로·파일명·행위의 증명이 아닙니다. 조각화·암호화·덮어쓰기 복구는 하지 않습니다.
- **로그 상관:** host와 session이 모두 같은 행만 UTC로 정렬합니다. W02의 session만 S10으로 바꾸면 계속 제외되고 host도 바꾸면 포함됩니다. 가까운 시각과 동일 키만으로 인과를 확정하지 않습니다.
- **대응:** READY-FOR-REVIEW는 승인·영향 검토·증거 보존의 모형 조건이 충족됐다는 뜻입니다. 자동 실행 승인이나 적합성 인증이 아닙니다. 복구의 정상/거부 동작, 원인 수정, 재발 관찰 기준을 따로 작성하세요.

## 주요 변경 과제의 기준 결과

1. 계획에 네 번째 유일한 증거를 추가하면 records=4입니다. 중복 ID/order 또는 문자열 형태의 volatile은 거부합니다.
2. C01의 PID를 999로 바꾸면 C01도 UNKNOWN입니다.
3. B03 transition을 auto→link로 바꾸면 total=3 displayed=3입니다.
4. fragments.hex 뒤에 5a3132를 더하면 둘째 후보는 declared=5 available=5 COMPLETE입니다.
5. crosslog의 W02를 workstation-7/S10으로 모두 바꾸면 linked=5 excluded=0입니다. 시간대 없는 값은 묵시적 UTC로 처리하지 않습니다.
6. 격리 authorized=false이면 HOLD입니다. 어떤 경우에도 이 도구는 실제 조치를 하지 않습니다.
