# 목록·사전: 예측 → 빈칸 → 직접 작성

foundation.zip을 풀고 foundation 폴더에서 진행합니다. Windows는 python3 대신 py -3입니다.
여기서는 user가 항상 문자열로 있고 status는 문자열이거나 생략된 자료만 다룹니다. 임의 JSON의 검증기는 아닙니다.

## 1. 실행 전에 기록

collections_predict.py를 읽고 print 세 줄의 결과를 종이에 적습니다. 아직 실행하지 않습니다.
rows는 행의 목록, rows[0]은 첫 사전, rows[0]["user"]는 그 사전의 user 값입니다.
0부터 세므로 rows[3]은 네 번째 행입니다. rows[4]는 IndexError입니다.
row["status"]는 키가 없으면 KeyError지만 row.get("status", "UNKNOWN")은 기본값을 돌려줍니다.
.get이 오타나 잘못된 자료를 자동 수정하는 것은 아닙니다. 이 과제에서만 status 생략을 미분류로 처리합니다.

| 반복 회차 | user | status 비교 | 반복 후 names |
|---|---|---|---|
| 1 | alice | ok == denied: 거짓 | [] |
| 2 | bob | 참 | [bob] |
| 3 | kim | 참 | [bob, kim] |
| 4 | lee | None == denied: 거짓 | [bob, kim] |

`python3 collections_predict.py` 예상: first=alice / missing=UNKNOWN / denied=bob,kim.
이제 rows[3]["status"]를 읽는 한 줄만 별도 실행해 KeyError와 UNKNOWN의 차이를 확인합니다.

## 2. 작은 빈칸

아래는 완성된 프로그램이 아닌 연습입니다. collections_practice.py의 함수에 적용합니다.

```python
for row in ____:
    if row.get("status") == ____:
        names.append(row[____])
return names
```

순서대로 rows, "denied", "user"입니다. return은 for 밖에 둡니다.
함수는 이름 목록을 반환합니다. print만 하고 끝내면 None을 반환하므로 같은 기능이 아닙니다.
names=[]를 반복 안에 쓰면 이전 결과가 사라집니다. 입력 목록을 수정할 필요는 없습니다.

## 3. 파일을 덮어쓰지 말고 직접 완성

collections_practice.py의 TODO와 raise를 자신의 코드로 교체한 뒤 `python3 collections_check.py`를 실행합니다.
처음 제공한 미완성 파일은 NOT YET와 종료 1이 정상입니다. 완성 후에는 3 cases passed와 종료 0입니다.
빈 목록, 정상+거부 혼합, status 누락+거부 두 명의 세 사례를 통과해야 합니다.
다른 이름과 순서의 행을 직접 만들어 예상 이름 목록을 먼저 적고 실행하세요.
마친 뒤에만 collections_reference.py와 비교합니다. 자신의 함수·예측표·차이를 보관하세요.
이 기본 조작을 익힌 뒤 CSV DictReader가 만든 행, JSON의 목록/사전으로 이어갑니다.
