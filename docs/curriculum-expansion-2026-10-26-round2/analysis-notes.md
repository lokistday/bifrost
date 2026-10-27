# Reverse / Forensic / Misc · 2차 확장 검토

기존 108개 차시와 자료를 유지하고 이 작업에서는 15개 차시를 추가했습니다. 담당 분야의 최종 수는 Reverse 15, Forensic 16, Misc 14입니다. 새 차시마다 개념 4문단 이상, 따라하기 3단계, 변경 과제·구체적인 해설·오개념 2개·상황형 문제 2개·공식 참고 문서 2개 이상·고유 도식이 있습니다.

## 추가 ID

| 분야 | ID | 새 학습 범위 |
| --- | --- | --- |
| Reverse | rev.elf-layout | 섹션/세그먼트, 파일/메모리, NOBITS |
| Reverse | rev.relocation | 객체 재배치·자체 공유 라이브러리·NEEDED |
| Reverse | rev.integer-views | signed/unsigned·확장·비트 마스크 |
| Reverse | rev.switch-recovery | switch 의미와 컴파일러 구현 선택 |
| Reverse | rev.state-machine | 허용/거부 전이·최종 완료 조건 |
| Forensic | forensic.windows-events | 합성 Windows XML의 이름 기반 필드·UTC |
| Forensic | forensic.linux-auth | 인증과 sudo 요청·선행 연결/실행 결과 구분 |
| Forensic | forensic.filesystem-records | 이름/객체/링크·시간·부분 수집 |
| Forensic | forensic.memory-triage | 영역/권한/백킹 모형·검토 규칙의 한계 |
| Forensic | forensic.evidence-coverage | 시간대/시계 오차·불확실 구간·관측 설정 |
| Misc | misc.container-identification | 접두 후보/구조·바깥/안쪽 형식 |
| Misc | misc.pixel-data | P3 헤더·RGB 표본·채널·메타데이터 구분 |
| Misc | misc.byte-statistics | 빈도·경험적 엔트로피·순서와 분류의 한계 |
| Misc | misc.bounded-decompression | 입력/출력 예산·eof·여분/잘림 |
| Misc | misc.resumable-batch | 입력/버전 캐시 키·부분 재개·체크포인트 |

각 분야에 모듈 두 개를 추가했습니다. `analysis-visuals.json`에는 신규 ID만 있는 평면 도식 객체 15개가 있습니다. compare는 양쪽 행 수를 맞췄습니다. 루트가 픽셀 차시를 실제 RGB 스와치 도식으로 개선하기로 했으며 이 조각의 최초 표 도식은 그 통합 단계에서 교체합니다.

## 새 실습 원본

- Reverse: layout.c, linkmain.c, linkpart.c, switches.c, integer_views.py, state_machine.py.
- Forensic: artifacts_round2.py, events-synthetic.xml, linux-auth.jsonl, fs-records.json, memory-model.json, coverage.json.
- Misc: media_tools.py, sample-p3.ppm, batch-jobs.json.
- 분야별 **ROUND2-GUIDE.md**를 별도로 추가했습니다. 이전 LAB-GUIDE.md·원본·테스트는 수정하지 않았습니다.
- 실습은 표준 라이브러리 Python과 직접 작성한 C만 사용합니다. 실제 계정·네트워크 접속·클라우드 자원·외부 패키지가 없습니다.

## 검증 결과

- Windows: `python -m unittest discover -s tests -p analysis_round2_expansion_test.py` — 27개, 모두 통과. Linux ELF/공유 라이브러리 검사 1개는 환경 조건으로 건너뜁니다.
- WSL kali-linux: `python3 -m unittest discover -s /mnt/d/Bifrost/tests -p analysis_round2_expansion_test.py` — 27개 전부 통과.
- Linux 실제 검사는 GCC 경고 오류 처리 빌드, readelf의 BSS NOBITS/LOAD/adjust 재배치/NEEDED, 공유 라이브러리만 다시 빌드한 새 실행 12→14, -O0/-O2 switch 동작 일치를 확인합니다.
- 바이트 폭·부호 경계, 상태 순서·미완료, XML 중복/네임스페이스, 로그 세션/역순 입력, 링크 선언/관찰 불일치, 메모리 규칙/잘못된 범위, 겹치고 접하는 오차 구간, PPM 표본 수/값/크기, 엔트로피의 순서 반례, 정확한 해제 상한과 잘림/여분/연결 스트림, 배치 입력 변경·캐시 변조·중복/버전·체크포인트를 검사합니다.
- 새 본문의 Python `-c` 명령 6개를 실제 실행했습니다. 정상 출력뿐 아니라 의도한 EOFError와 ValueError의 종류·비정상 종료도 본문과 일치합니다.
- 15개 차시의 필수 항목·파일·도식과 compare 행 수를 확인했습니다. 글은 임시 초안 뒤 개념·과제·해설·피드백·도식 설명까지 자연스러운 띄어쓰기로 교정했습니다.

## 출처 확인

2026-10-26 다음 공식/원저자 문서를 웹으로 확인했습니다. 차시마다 해당 문서를 직접 연결합니다.

- GNU readelf/objdump, GCC 최적화와 코드 생성 옵션.
- Xinuos ELF gABI의 Sections, Program Loading, Dynamic Linking. 이전 refspecs 주소는 접근 차단이 있어 사용하지 않았습니다. 현재 문서의 DRAFT 상태를 최종 표준이라고 주장하지 않습니다.
- Microsoft Windows Event Schema, 4624 로그온 유형, Memory Protection Constants.
- systemd.journal-fields, Linux man-pages의 stat/link.
- Netpbm PPM 명세.
- Python struct·argparse·unittest·정수 비트 연산·ElementTree·datetime·json·gzip·zlib·Counter·math.log2·hashlib·pathlib.
- 기존부터 사용한 NIST SP800-86의 증거/관찰 한계를 새 차시와 연결했습니다.

## 명시한 실무 한계

EventRecordID 검사는 단일 컴퓨터/채널 내보내기, inode 조인은 단일 파일시스템/스냅샷 범위입니다. 선행 로그인 연결은 활성 세션이나 명령 완료의 증명이 아닙니다. XML은 실제 EVTX, FS JSON은 실제 파일시스템, 메모리 JSON은 실제 RAM/VAD 파서가 아닙니다. private-WX는 JIT 등 정상 사례도 있는 우선 검토 규칙입니다. 겹치거나 접하는 시간 구간은 순서 불확실로 남깁니다. 로그 활성화는 수집 완전성의 인증이 아닙니다.

P3는 작은 신뢰 표본을 읽는 제한된 파서이며 범용 적대적 이미지 디코더가 아닙니다. 결정적인 0~255 나열도 경험적 H8이므로 엔트로피는 암호화/난수 인증이 아닙니다. 단일 zlib 해제의 바이트 한도는 CPU·파일 읽기·중첩 전체 제한이 아닙니다. 체크포인트의 고정 .tmp 교체는 통제된 폴더·단일 작성자 전제이며 잠금·트랜잭션·fsync 내구성을 보장하지 않습니다. 작은 대문자 모형은 캐시 검증을 위해 결과를 다시 계산하므로 고비용 작업의 성능 벤치마크가 아닙니다.
