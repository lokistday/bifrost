# Bifrost · cloud
이 묶음은 Bifrost가 직접 만든 교육용 자료입니다. 실제 개인정보·접속 키·운영 로그가 아닙니다.

ZIP을 먼저 풀고 파일을 확인하세요. Python 예제의 기본 환경은 Python 3.10 이상입니다.
기본 예제는 표준 라이브러리만 사용하며, crypto의 실제 AEAD·서명·봉투 암호 예제는 선택 패키지가 필요합니다.
선택 패키지 설치와 실행 범위는 crypto의 requirements.txt 및 차시별 가이드를 확인하세요.
Linux/WSL/macOS에서는 python3, Windows PowerShell에서는 py -3 명령으로 실행합니다.
C 예제는 Ubuntu/WSL의 gcc, gdb, binutils를 기준으로 합니다. 바이너리를 제공하지 않고 소스를 제공합니다.
명령은 각 차시를 따라 실행하세요. 스크립트가 외부 서비스에 접속하거나 클라우드 자원을 만들지는 않습니다.

각 폴더의 모든 파일을 함께 유지하세요. 수정할 때 원본은 보관하고 작업용 사본을 만드세요.
network의 traffic.pcap은 합성 DNS 2개와 TCP/HTTP 6개, 총 8프레임입니다.
별도 tls13.pcap은 메모리 안에서 실제 TLS 1.3 교환을 생성하고 합성 네트워크 헤더를 붙인 표본입니다.
network 정책·cloud 구성은 단순화한 교육 모델입니다. 실제 장비나 공급자에 그대로 적용할 형식이 아닙니다.
crypto의 고전 암호와 XOR 예제는 원리 관찰용이며 실제 보안에 사용하지 않습니다.
자세한 준비·예상 결과·한계·풀이가 제공된 묶음은 LAB-GUIDE.md를 먼저 읽으세요.
후속 응용 차시는 ROUND2-GUIDE.md를, network·cloud·crypto의 앞선 확장은 ADVANCED-GUIDE.md를 함께 확인하세요.
분야를 마치면 project-brief.md의 종합 프로젝트를 진행하세요. A/B 표본·결과 검사·보고서 루브릭이 있습니다.
