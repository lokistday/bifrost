# Reverse / Forensic / Misc 확장 검토 · 2026-10-26

기존 ID와 14개 기존 차시를 유지하고 16개 차시를 추가했습니다. 계정·진도 저장 기능과 디자인은 변경하지 않았습니다. 각 신규 차시는 4개 이상의 개념 문단, 3개 이상의 따라하기, 변경 과제·해설·오개념 2개 이상·자기 점검 2개·공식 참고 문서 2개 이상·고유 도식을 제공합니다.

## 추가 차시

| 분야 | ID | 내용 |
| --- | --- | --- |
| Reverse | rev.byte-order | endian·오프셋·전체 길이 검증 |
| Reverse | rev.calling-convention | System V ABI 인자·반환값 |
| Reverse | rev.control-flow | 루프·continue·break·누적 상태 |
| Reverse | rev.data-flow | 바이트 변환·인덱스 의존·역변환 반례 |
| Reverse | rev.differential | 참조/후보 차등 검증·최소 반례 |
| Forensic | forensic.collection-plan | 휘발성·수집 목적·증거 인계 |
| Forensic | forensic.host-triage | 부모/자식·PID·연결·UNKNOWN |
| Forensic | forensic.browser-sqlite | 합성 SQLite 질의·필터와 행위 해석 |
| Forensic | forensic.file-signatures | 모형 carving·선언/가용 길이·복구 한계 |
| Forensic | forensic.log-correlation | UTC·호스트/세션 AND·상관과 인과 |
| Forensic | forensic.incident-response | 확인 범위·승인/영향/증거·복구 기준 |
| Misc | misc.structured-parsing | fullmatch·중복 ID·오류 행 보존 |
| Misc | misc.archive-inspection | 목록·경로 후보·자원 한도와 추출 한계 |
| Misc | misc.graph-search | BFS·순환·동일 비용 최단·도달 불가 |
| Misc | misc.constraint-solving | 완전 탐색·조건 부족·모순·유일해 |
| Misc | misc.reproducible-results | 정규화 계약·순서/값 차이·재현 메타데이터 |

새 모듈은 분야마다 2개이며 최종 분야별 차시는 Reverse 10, Forensic 11, Misc 9입니다. `analysis-visuals.json`은 신규 ID 16개를 키로 하는 평면 객체입니다. 루트 통합 단계에서 공용 도식 원본·영구 ID 레지스트리를 갱신하고 생성기를 실행합니다.

## 실습 원본

- rev: binary_lab.py, calling.c, flow.c, dataflow.py, differential.py, LAB-GUIDE.md.
- forensic: casework.py, case.json, snapshot.json, history.sql, fragments.hex, crosslog.csv, response.json, LAB-GUIDE.md.
- misc: toolbox.py, events.txt, graph.json, clues.json, repro.json, LAB-GUIDE.md.
- 각 `scripts/lab_sources/<분야>/`의 새 파일은 기존 `build_labs.py`가 생성 자료에 복사합니다. 새 Python 외부 패키지는 없습니다.

## 검증

- Windows: `python -m unittest discover -s tests -p analysis_expansion_test.py` — 36개, 통과; GCC가 없는 Windows에서 C 케이스 1개 건너뜀.
- WSL kali-linux: `python3 -m unittest discover -s /mnt/d/Bifrost/tests -p analysis_expansion_test.py` — 36개 모두 통과. Linux GCC -g -O0 -Wall -Wextra -Werror로 두 C 프로그램의 정상/분기/오류 입력 검증.
- GDB 실제 smoke: *combine 진입 edi=3,esi=5,edx=7, finish 후 eax=20 확인. 임시 폴더에서 빌드·실행 후 임시 자료 정리.
- 신규 본문 Python `-c` 명령 4개를 실제 실행해 본문의 예상 출력과 일치 확인.
- 16개 차시의 필수 항목·실습 파일·고유 도식·참고 문서 개수 확인.
- 회귀 검사는 입력 변형·경계·오류를 다룹니다. 단순 출력만 확인하는 검사 외에 잘림/여분/길이 상한, 연산 경계, 승인 타입, 중복·오류 행, 두 조인 키, 시간대 누락, 그래프 순환, 모순·다해, 정규화 의미 변화를 확인합니다.

## 참고 문서 확인

2026-10-26 공식 문서를 웹으로 확인했습니다. NIST SP800-86, 최신 최종판 SP800-61r3(2025-04), Python struct/re/zipfile/sqlite3/collections/itertools/datetime/csv/json/hashlib/unittest/stdtypes/pathlib/functions, SQLite WAL, GNU objdump/GDB, x86-64 psABI 공식 GitLab, Microsoft Win32_Process 문서를 차시별로 연결했습니다.

주요 출처:

- https://csrc.nist.gov/pubs/sp/800/86/final
- https://csrc.nist.gov/pubs/sp/800/61/r3/final
- https://sqlite.org/wal.html
- https://gitlab.com/x86-psABIs/x86-64-ABI
- https://sourceware.org/gdb/current/onlinedocs/gdb.html/Registers.html
- https://sourceware.org/binutils/docs/binutils/objdump.html
- https://docs.python.org/3/library/struct.html
- https://docs.python.org/3/library/re.html
- https://docs.python.org/3/library/zipfile.html

ABI의 과거 linuxbase PDF URL은 접근 차단이 확인되어 인용하지 않고 공식 psABI 프로젝트를 사용합니다. 소스 인자 표시가 프롤로그 전 부정확할 수 있으므로 실제 *combine 경계에서는 레지스터를 읽도록 설명했습니다.

## 해석 한계

실메모리 획득·악성코드 실행·실제 브라우저 개인정보·실제 파일시스템 복구·실제 격리/삭제는 수행하지 않습니다. BF는 자체 제작한 장난감 형식입니다. 프로세스 조인은 단일 합성 스냅샷 안에서만 해석하며 PID 재사용·수집 시각을 명시합니다. SQLite SQL은 제공한 신뢰 원본만 실행하고 메모리 DB를 임의 SQL 샌드박스로 주장하지 않습니다. ZIP CANDIDATE는 문자열 검사일 뿐 안전한 추출이 아닙니다. 응답 READY-FOR-REVIEW는 실행 승인이나 적합성 인증이 아닙니다. JSON 정규화는 명시한 작은 계약에만 적용하며 범용 표준이 아닙니다.
