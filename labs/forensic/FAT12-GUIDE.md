# FAT12 볼륨: 구조 읽기 → 조각 연결 → 독립 대조

forensic.zip을 풀고 forensic 폴더에서 진행합니다. Python 3.10 이상 표준 라이브러리만 필요합니다.
Windows PowerShell에서는 python3를 py -3로 바꿉니다. 관리자 권한·마운트·실제 디스크 접근은 필요 없습니다.
자체 제작한 실제 FAT12 형식의 교육용 볼륨입니다. 실제 사용자의 디스크를 획득한 사건 증거는 아닙니다.
기존 fs-records.json의 inode/하드링크 모형과 다릅니다. FAT 디렉터리 엔트리·클러스터 번호를 Linux inode와 동일시하지 않습니다.

## 1. 새 작업 폴더와 해시

```sh
python3 fat12_lab.py setup disk-work
python3 fat12_lab.py inspect disk-work/volume.img
```

setup은 새 폴더에 1,474,560바이트 볼륨과 손상 사본 4개를 만듭니다. 기존 폴더는 거부합니다.
volume.img는 MBR 파티션 테이블이 없는 단일 FAT12 볼륨으로 파일 오프셋 0이 부트 섹터입니다.
부팅 가능한 OS나 실행용 부트 로더를 넣지 않았습니다. .img가 곧 전체 물리 디스크라는 뜻도 아닙니다.
sample-hashes.json은 생성 직후의 SHA-256입니다. 같은 스크립트가 만든 기준값과 비교만 하는 것으로 검증을 끝내지 말고 아래 독립 도구와 대조합니다.

## 2. BPB 바이트에서 위치 계산

Hex 편집기 또는 다음의 읽기 전용 명령으로 먼저 64바이트를 확인합니다.

```sh
python3 -c "from pathlib import Path; d=Path('disk-work/volume.img').read_bytes(); print(d[:64].hex(' ')); print(d[510:512].hex(' '))"
```

| 바이트 오프셋 | 길이 | 이 표본의 값 | 읽는 의미 |
|---|---|---|---|
| 11 | 2 | 00 02 → 512 | 섹터 바이트 수, little-endian |
| 13 | 1 | 01 → 1 | 클러스터당 섹터 |
| 14 | 2 | 01 00 → 1 | 예약 섹터 수 |
| 16 | 1 | 02 → 2 | FAT 사본 수 |
| 17 | 2 | e0 00 → 224 | 루트 엔트리 최대 수 |
| 19 | 2 | 40 0b → 2880 | 전체 섹터 수 |
| 22 | 2 | 09 00 → 9 | FAT 하나의 섹터 수 |
| 510 | 2 | 55 aa | 부트 섹터의 끝 식별자; 정상성 보증 아님 |

```text
sector 0       : boot / BPB
sector 1..9    : FAT #1
sector 10..18  : FAT #2
sector 19..32  : root directory (224 × 32 = 7168 bytes = 14 sectors)
sector 33..   : cluster data (cluster 2부터)
```

루트 시작=예약 1 + FAT 2×9 = 19. 데이터 시작=19+14=33입니다.
클러스터 c의 바이트 위치=(33+(c-2))×512입니다. 클러스터 2가 첫 데이터 클러스터이며 0이나 1부터 시작하지 않습니다.
데이터 클러스터 수는 (2880-33)/1=2847이므로 FAT12 범위입니다. FAT12라는 글자 라벨만으로 형식을 판정하지 않습니다.
위 숫자는 제공한 한 형식 프로필에 한정됩니다. 다른 장치의 섹터/클러스터 크기를 그대로 가정하지 않습니다.

## 3. 디렉터리 엔트리와 FAT 연결

루트 시작 바이트 9728부터 파일 엔트리는 32바이트씩입니다.
이 연습은 짧은 8.3 이름만 지원합니다. 긴 이름(LFN), 하위 디렉터리, FAT16/32, NTFS/ext4는 미지원입니다.
엔트리 안의 26..27은 첫 클러스터, 28..31은 파일 크기이며 모두 little-endian입니다.
이 위치는 엔트리 내부 상대 오프셋입니다. 볼륨 절대 위치와 구분해서 기록하세요.

| 엔트리 | 첫 클러스터 | 논리 크기 | 관찰 |
|---|---:|---:|---|
| README.TXT | 2 | 1100 | FAT 연결 2 → 5 → 3 → EOC |
| EVIDENCE.TXT | 4 | 43 | FAT 연결 4 → EOC |
| EMPTY.TXT | 0 | 0 | 데이터 클러스터 없음 |
| ?LDNOTE.TXT | 6 | 68 | 첫 바이트 E5, 삭제 엔트리 단서만 표시 |

FAT12 엔트리는 12비트씩 압축됩니다. c번 엔트리는 c+floor(c/2) 위치부터 두 바이트를 읽어 짝수 c면 하위 12비트, 홀수면 상위 12비트를 취합니다.
0은 비할당, 0xFF7은 bad cluster, 0xFF8..0xFFF는 EOC입니다. 이를 다음 클러스터 번호로 읽지 않습니다.
FAT 사본이 다르면 검사기는 하나를 임의로 채택하지 않고 UNVERIFIED로 멈춥니다.

## 4. 파일 추출과 슬랙 분리

```sh
python3 fat12_lab.py extract disk-work/volume.img README.TXT disk-work/recovered.txt
python3 -c "from pathlib import Path; import hashlib; b=Path('disk-work/recovered.txt').read_bytes(); print(len(b), hashlib.sha256(b).hexdigest()); print(b[:80])"
```

결과 size=1100, chain=[2,5,3]입니다. 기존 출력 파일은 덮어쓰지 않습니다.
클러스터의 물리 섹터 순서는 33 → 36 → 34입니다. 섹터 33부터 연속 1100바이트를 복사하면 다른 내용이 섞입니다.
마지막 클러스터는 76바이트만 파일 내용입니다. 남은 436바이트는 이 파일의 논리 내용에 포함하지 않습니다.
마지막 클러스터 뒤에 있는 OUTSIDE_FILE_SIZE 표식이 추출 결과에 들어가면 잘못된 크기 처리입니다.
슬랙이나 비할당 영역에 바이트가 있다는 사실만으로 특정 사람의 삭제·작성 시각이나 완전 복구를 증명하지 않습니다.

## 5. 손상 사본의 반례

```sh
python3 fat12_lab.py inspect disk-work/loop.img
python3 fat12_lab.py inspect disk-work/early-end.img
python3 fat12_lab.py inspect disk-work/fat-mismatch.img
python3 fat12_lab.py inspect disk-work/truncated.img
```

각각 순환 연결, 크기보다 짧은 연결, FAT 불일치, BPB와 이미지 길이 불일치를 거부합니다. 모두 종료 2이며 정상 파일 추출 결과로 쓰지 않습니다.
원본 SHA-256은 실습 전후 같아야 합니다. 검사 완료는 모든 섹터·엔트리·파일시스템 불변식의 완전 검증을 뜻하지 않습니다.

## 6. 선택: 독립 도구로 대조

Ubuntu/WSL에서 Sleuth Kit가 준비돼 있으면 아래를 수행합니다. 없으면 `sudo apt install sleuthkit`으로 설치할 수 있습니다.
기본 Python 실습에는 필요 없습니다. 이미지 마운트는 하지 않습니다.

```sh
fsstat -f fat12 disk-work/volume.img
fls -f fat12 disk-work/volume.img
```

fsstat의 FAT12·sector 0..2879·클러스터 512바이트와 배치를 비교합니다.
fls에서 README.TXT의 메타데이터 번호를 읽습니다. 이 표본의 TSK 버전에서는 3이지만 자신의 출력 번호를 사용하세요.
번호는 TSK가 FAT 엔트리를 참조하는 식별자로, Linux inode나 FAT 클러스터 번호와 같지 않습니다.

```sh
# Bash/Ubuntu에서 실행; README.TXT의 실제 fls 번호가 3인 경우
icat -f fat12 disk-work/volume.img 3 > disk-work/tsk-readme.txt
sha256sum disk-work/recovered.txt disk-work/tsk-readme.txt
cmp disk-work/recovered.txt disk-work/tsk-readme.txt
```

리디렉션은 기존 파일을 덮어쓸 수 있으므로 새 출력 이름을 사용합니다. 위 명령은 Bash에서 수행하며 Windows 구형 PowerShell의 텍스트 리디렉션으로 바꾸지 않습니다.
cmp 종료 0과 두 해시 일치로 독립 추출을 대조합니다. 삭제 엔트리는 TSK에서 _LDNOTE.TXT처럼 다른 표시 이름으로 보일 수 있습니다.
삭제 엔트리의 원래 첫 글자·클러스터 재사용·조각 연결은 별도 근거가 필요합니다. 이 도구는 삭제 파일을 자동 복구하지 않습니다.

## 직접 수행할 보고서

1. BPB 원시 바이트 → little-endian 값 → 루트/데이터 오프셋 계산표를 직접 채웁니다.
2. README의 엔트리 위치, 첫 클러스터, 세 FAT 연결, 각 데이터 바이트 위치를 적습니다.
3. 연속 복사와 FAT 연결 추출의 차이를 비교하고 슬랙이 제외됐는지 확인합니다.
4. 정상·손상 4개 사본의 판정과 파일 보존 해시, 독립 도구 실행 여부를 보고합니다.
5. label 필드만 FAT16으로 바꾼 새 사본을 만들면 실제 FAT 유형이 바뀌는지 예상하고 비교하세요. 구조·클러스터 수와 글자 라벨을 구분합니다.

미완료 확장: 실제 EVTX·레지스트리·Prefetch/Amcache, 실제 RAM 이미지. 이 FAT12 실습으로 완료했다고 표시하지 않습니다.

기준 문서: Microsoft FAT Specification (https://www.scs.stanford.edu/~zyedidia/docs/_other/fat.pdf)
도구 기준: https://github.com/sleuthkit/sleuthkit/wiki/The_Sleuth_Kit_commands
