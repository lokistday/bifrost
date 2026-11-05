# 시스템 보안 모의고사 검토 · 2026-11-05

## 범위

기존 `content/courses/pwn.json`의 6개 모듈·16개 차시만을 출제 범위로 사용했다.
각 모듈 25문항, 총 150문항이며 강의·다운로드 파일·따라 하는 실습 내용은 변경하지 않았다.
차시 안의 확인 문제는 기존 공통 기초와 동일하게 별도 모듈 모의고사 링크로 대체했다.

| 시험 | 범위 | 차시별 문항 수 |
|---|---|---|
| pwn-01 | 실행과 메모리 모델 | build 8 / lifetime 8 / bounds 9 |
| pwn-02 | 관찰·진단·완화 | debugger 8 / errors 8 / mitigations 9 |
| pwn-03 | 정수와 출력의 경계 | integer-input 8 / allocation-size 8 / format-strings 9 |
| pwn-04 | 소유권과 작은 파서 | ownership 12 / binary-parser 13 |
| pwn-05 | 메모리 표현과 데이터 계약 | struct-layout 12 / binary-strings 13 |
| pwn-06 | 열린 객체와 스트림 경계 | file-descriptors 8 / partial-io 8 / atomic-open 9 |

## 문항별 근거 및 편집 검토

`pwn-exam-evidence-2026-11-05.json`에 150문항 각각의 차시 ID·절·원문 문단을 기록했다.
테스트는 해당 문단이 실제 해당 모듈의 강의 원문에 존재하는지 검사한다.
이는 출제 범위 검증이며 의미적 정답 검토를 자동으로 대신하지 않는다.

150문항의 질문·정답·세 오답·해설을 읽고 다음 조건을 확인했다.

- 한 문항에서 요구하는 조건을 충족하는 정답은 하나다. 다른 보기는 강의 계약과 배치되거나 질문에 답하지 않는다.
- 입력 범위, 크기 단위, 문자열 종료, 바이트 순서, 수명 종료 시점을 구분한다.
- `0003`은 값만 묻는 대신 **해석 방식과 결과**를 묻도록 수정했다. 잘못된 진법을 적용한 3과 수치가 우연히 같은 혼동을 피했다.
- 크기 상한 식은 count·header·element가 `size_t`이고 element>0이라는 전제를 문제에 명시했다.
- snprintf 반환값은 NUL 제외 필요 길이이며 capacity와 같아도 잘림이다. ASCII 표본임을 명시했다.
- 빈 payload를 허용하는 실습 계약을 일반 업무 규칙과 구분했다. 여분 바이트는 엄격한 파서에서 거부한다.
- NUL 포함 버퍼 크기와 strlen 결과, 명시적 5바이트 텍스트 검사 범위를 구분했다.
- dup 오프셋 공유와 FD 정수 대입을 구분했다. 정수 대입 결함 문제는 중간에 새 FD 생성이 없다는 조건을 명시했다.
- partial I/O의 EOF 확인 호출 수를 포함했다. 모형 writer의 0 진행과 실제 EAGAIN을 동일시하지 않았다.
- GNU_STACK의 RW, ASLR/NX/Canary, O_NOFOLLOW와 fstat의 보장을 과장하지 않았다.
- UB 출력·메모리 주소·ABI별 구조체 크기·실제 네트워크 스케줄링처럼 환경에 따라 달라지는 값을 고정 정답으로 쓰지 않았다.
- 정답 위치는 시험마다 6/6/6/7개로 분산했다. 중복 질문·중복 보기·모듈 밖 차시 연결이 없다.

## 실행 검토

`tests/pwn_exam_answers_test.py`는 학습자가 받는 실제 C 파일을 GCC로 빌드한다.
정상 예제와 강의 과제의 안전한 사본을 실행하여 다음을 정답 보기와 함께 대조한다.

- memory 초기값 변경 및 경계를 고친 배열의 10/20/30 출력
- 0003·0·1024 허용, 1025·부호·공백·접미·빈 값·변환 범위 초과 거부
- 할당 크기 28, huge 거부, empty 헤더 크기, element=0 거부
- %s%n의 데이터 출력, needed=8/capacity=8 잘림, Bifrost의 NUL 포함 용량 10
- 실제 parser 함수에 big-endian 258·여분 본문·빈 본문·정상 길이 3 입력
- 7바이트 전송 Hex, roundtrip, 짧은 입력 거부
- 중간 NUL과 끝 NUL의 strlen·전체 Hex
- dup의 AB/CD/EF와 12/34/56, 정수 대입 결함 실패
- chunk=1 완전 입력 reads=7, 잘린 입력 reads=6, writer calls=7 및 0 진행 거부
- 원자적 생성 중복 거부·symlink 거부·열린 객체 수명, O_NOFOLLOW 제거 결함 실패

기존 `tests/exam_answers_test.py`에서 새 검사 클래스를 함께 실행하므로 Linux CI에서도 GCC 검사가 필수 실행된다.
Windows 단독 실행은 GCC 부분을 건너뛰지만 WSL에서 별도로 전체 실행한다.
`tests/exams.test.cjs`는 기존 5개와 신규 6개 시험 전체의 실제 생성 HTML/JS를 대상으로
100점·혼합 점수·오답 필터·재응시·별도 초안 저장·해설·모든 차시 연결·실습 보존을 검사한다.

## 참고 문서 대조

출제 근거는 사이트의 강의이며, 해석 혼동이 쉬운 부분은 다음 원문 문서로 교차 확인했다.

- [Linux man-pages printf](https://man7.org/linux/man-pages/man3/printf.3.html): 서식 인자, snprintf 필요 길이와 잘림
- [Linux man-pages dup](https://man7.org/linux/man-pages/man2/dup.2.html): 열린 파일 설명과 공유 오프셋, FD 플래그 구분
- [Linux man-pages open](https://man7.org/linux/man-pages/man2/open.2.html): O_EXCL, 마지막 구성 요소의 O_NOFOLLOW, 열린 객체 참조

## 배포 범위

시험 데이터와 시험 페이지·전용 JS, 시험 목록·사이트맵, 시스템 보안 차시와 해당 학습 경로의 연결,
생성기·검사·비공개 개발 노트만 변경한다. 기존 공통 기초 시험과 다른 분야 페이지는 유지한다.
신규 분야 시험과 해당 course bundle에 별도 캐시 지문을 적용해 문제 추가 때문에 무관한 페이지의 공유 버전이 바뀌지 않게 했다.
