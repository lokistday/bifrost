# 실제 파일 시그니처와 구조 검증

forensic 폴더에서 `python3 signature_lab.py setup signature-work`를 실행합니다.
Windows에서는 `py -3`를 사용합니다. 표준 라이브러리만 필요합니다.
원본은 signature-fixtures.json이며 새 작업 폴더만 생성합니다. 기존 폴더·추출 파일은 덮어쓰지 않습니다.

## 덤프를 읽는 순서

`python3 signature_lab.py inspect signature-work/image.png`

왼쪽 00000010은 십진수 16번째 오프셋입니다. 가운데 두 자리 Hex가 한 바이트이고 오른쪽은 ASCII 보기입니다.
PNG 첫 8바이트는 `89 50 4e 47 0d 0a 1a 0a`입니다.
오프셋 8의 `00 00 00 0d`는 데이터 길이 13이며, 오프셋 12의 `49 48 44 52`는 IHDR입니다.
청크의 총 길이는 데이터 길이 + 12입니다. CRC는 종류+데이터에 대한 오류 검출값이며 디지털 서명이 아닙니다.

## 직접 채울 표

| 표본 | 확인할 점 | 예상 판정 |
| --- | --- | --- |
| image.png | IHDR·IDAT·IEND, CRC, 압축 픽셀 길이 | PNG_CONTRACT_VALID |
| renamed.txt | 확장자와 바이트 비교 | image.png와 같은 해시·구조 |
| photo.jpg | ff d8 ff | JPEG_CANDIDATE |
| notes.zip | 50 4b 03 04 | ZIP_CANDIDATE |
| truncated.png | 끝 청크 잘림 | PNG_UNVERIFIED |
| bad-crc.png | IHDR CRC 오류 | PNG_UNVERIFIED |
| prefix-only.png | 헤더만 존재 | PNG_UNVERIFIED |

JPEG/ZIP 표시는 접두 식별뿐입니다. ZIP 파일은 아카이브 도구로 목록을 확인하고 JPEG는 이미지 뷰어로 열어 추가 관찰을 남기세요.
열린다는 사실이 출처·진실성·악성 여부를 증명하지는 않습니다.

## 연속 표본 추출

`python3 signature_lab.py carve signature-work/mixed.bin signature-work/recovered.png`

예상 offset=17. recovered.png와 image.png의 바이트와 SHA-256을 별도로 대조하고 이미지 뷰어로 여세요.
다시 같은 출력 이름을 사용하면 거부됩니다. bad-crc.png를 추출 대상으로 주면 구조 검사에서 거부됩니다.
carve는 첫 PNG 후보만 검사하며 첫 후보가 손상되면 멈춥니다. 여러 후보를 모두 복구하는 도구가 아닙니다.

## 판정의 범위

PNG 검사는 작은 RGB8·비인터레이스 PNG에 한정됩니다. 다른 정상 형식도 미지원일 수 있습니다.
1 MiB 입력 한도와 픽셀 크기 한도가 있으며, 압축 픽셀 해제에도 출력 한도를 적용합니다.
CRC·IHDR·IDAT·IEND 검사로 PNG 명세 전체나 임의 파일의 안전성을 보장하지 않습니다.
inspect 종료 0은 보고 완료입니다. 판정 문자열을 읽으세요. 파일 접근·carve 오류는 종료 2입니다.
조각화·삭제 메타데이터·원래 이름·작성자 복원은 범위 밖입니다.

보고서: 원본 해시 → 입력 경로 → Hex 근거와 오프셋 → 판정 범위 → 추출 범위 → 독립 대조 → 미확인 사항.
