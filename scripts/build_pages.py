"""Generate the small static entry pages and keep the homepage's links semantic."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COURSES = [
    ('foundation', 'Foundation', '공통 기초', '터미널 · 코드 · 네트워크', 'CORE'),
    ('web', 'Web Hacking', '웹 보안', '요청 · 인증 · 취약점', 'WEB'),
    ('pwn', 'Pwn / System', '시스템 보안', '메모리 · 디버깅', 'SYSTEM'),
    ('rev', 'Reverse Engineering', '리버싱', '분석 · 실행 흐름', 'REVERSE'),
    ('forensic', 'Forensic', '디지털 포렌식', '흔적 · 증거 · 타임라인', 'FORENSIC'),
    ('network', 'Network Security', '네트워크 보안 · 통합', '망 설계 · 정책 · 탐지', 'NETWORK'),
    ('crypto', 'Cryptography', '암호학', '수학 · 무결성 · 키 관리', 'CRYPTO'),
    ('misc', 'Misc', '문제 해결 · 자동화', '단서 · 데이터 · 도구', 'MISC'),
    ('cloud', 'Cloud Security', '클라우드 보안', '신원 · 구성 · 감사', 'CLOUD'),
]

STAR = '<svg class="bifrost-star" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 3 24 15 36 20 24 24 20 36 16 24 4 20 16 15Z" fill="currentColor"/></svg>'
for key, title, label, subtitle, number in COURSES:
    folder = ROOT / 'tracks' / key
    folder.mkdir(parents=True, exist_ok=True)
    for view, name in [('course', 'index.html'), ('lesson', 'lesson.html')]:
        content = f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1220">
<meta name="description" content="Bifrost {title}: {label} 설명과 예제·실습·검증을 차시별로 학습합니다.">
<title>{title} — Bifrost</title>
<script src="../../js/theme.js"></script>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='11' fill='%23101a30'/%3E%3Cpath d='M20 3 24 15 36 20 24 24 20 36 16 24 4 20 16 15Z' fill='%235ce1e6'/%3E%3C/svg%3E">
<link rel="stylesheet" href="../../css/main.css"><link rel="stylesheet" href="../../css/theme.css"><link rel="stylesheet" href="../../css/learning.css">
<script src="../../js/curriculum.js" defer></script><script src="../../js/progress.js" defer></script><script src="../../js/learning.js" defer></script>
</head><body class="learning-page" data-course="{key}" data-view="{view}">
<a class="skip-link" href="#learningContent">학습 본문으로 건너뛰기</a>
<header class="topbar"><div class="wrap nav"><a class="brand" href="../../index.html"><span class="brand-mark">{STAR}</span><span>BIFROST</span></a><nav class="navlinks" aria-label="주 메뉴"><a href="../../index.html#study">모든 분야</a><a href="./">{label} 목차</a></nav><button class="theme-toggle" id="themeToggle" type="button" aria-label="다크 모드로 전환" aria-pressed="false">테마 전환</button><a class="nav-cta" href="../../index.html#mindmap">학습 지도 ↗</a></div></header>
<main class="learning-wrap" id="learningContent" tabindex="-1"><h1>{title}</h1><p>학습 목차를 준비하고 있습니다.</p><noscript><p>차시 본문과 진도 기능에는 JavaScript가 필요합니다. 실습 자료는 아래 링크로 받을 수 있습니다.</p></noscript><a href="../../labs/{key}.zip" download>실습 ZIP 내려받기</a><p><a href="../../index.html#study">전체 학습 지도</a></p></main>
<footer class="learning-footer"><div class="wrap">BIFROST · 이해하고, 실행하고, 근거를 남기기. <a href="../../index.html#study">다른 분야 탐색 ↗</a></div></footer>
</body></html>
'''
        (folder / name).write_text(content, encoding='utf-8', newline='\n')

# Updating generated blocks is idempotent; the splash, core and roadmap remain authored HTML.
home = (ROOT / 'index.html').read_text(encoding='utf-8')
nodes = '\n'.join(f'      <a class="map-node node-{key}" data-map-track="{key}" href="tracks/{key}/"><span class="node-number">{i:02d} / {number}</span><span class="node-arrow" aria-hidden="true">↗</span><strong>{title}</strong><small>{label}</small><i>{subtitle}</i></a>' for i, (key, title, label, subtitle, number) in enumerate(COURSES))
home = re.sub(r'      <(?:button|a) class="map-node node-foundation".*?(?=      <div class="map-core")', nodes + '\n', home, flags=re.S)
home = home.replace('SIX DIRECTIONS', 'EIGHT DIRECTIONS').replace('해당 학습 트랙으로 이동합니다.', '분야별 목차와 강의 페이지로 이동합니다.')
home = home.replace('href="#linux-guide" onclick="openLinuxGuide(); return false;"', 'href="guides/linux.html" onclick="openLinuxGuide(); return false;"')
home = home.replace('viewBox="0 0 1000 590"', 'viewBox="0 0 1000 760"')
start = home.index('        <path class="synapse ', home.index('<svg class="mindmap-lines"'))
end = home.index('      </svg>', start)
home = home[:start] + '''        <path class="synapse cyan" d="M500 295V126"/>
        <path class="synapse blue" d="M440 320C415 275 380 230 350 216"/>
        <path class="synapse violet" d="M560 320C585 275 620 230 650 216"/>
        <path class="synapse red" d="M415 370C370 370 335 343 296 343"/>
        <path class="synapse green" d="M585 370C630 370 665 343 704 343"/>
        <path class="synapse pink" d="M430 430C400 470 360 510 328 513"/>
        <path class="synapse orange" d="M570 430C600 470 640 510 672 513"/>
        <path class="synapse amber" d="M475 460C450 510 430 565 400 600"/>
        <path class="synapse sky" d="M525 460C550 510 570 565 600 600"/>
        <path class="synapse faint" d="M245 210C175 235 180 405 220 445"/>
        <path class="synapse faint" d="M755 210C825 235 820 405 780 445"/>
        <circle class="junction blue" cx="350" cy="216" r="3"/><circle class="junction violet" cx="650" cy="216" r="3"/>
        <circle class="junction red" cx="296" cy="343" r="3"/><circle class="junction green" cx="704" cy="343" r="3"/>
''' + home[end:]
if 'id="line-orange"' not in home:
    before = home.index('        </defs>', home.index('<svg class="mindmap-lines"'))
    home = home[:before] + '''          <linearGradient id="line-orange"><stop style="stop-color:var(--map-orange)" stop-opacity=".16"/><stop offset="1" style="stop-color:var(--map-orange)" stop-opacity=".9"/></linearGradient>
          <linearGradient id="line-sky"><stop style="stop-color:var(--map-sky)" stop-opacity=".16"/><stop offset="1" style="stop-color:var(--map-sky)" stop-opacity=".9"/></linearGradient>
''' + home[before:]

catalog = '\n'.join(f'<a class="track-button" href="tracks/{key}/"><span class="track-symbol">{i:02d}</span><span><strong>{title}</strong><small>{subtitle}</small></span><span class="track-arrow">→</span></a>' for i, (key, title, label, subtitle, number) in enumerate(COURSES))
study = f'''<section class="wrap section" id="study">
<div class="section-head"><div><div class="kicker mono">02 / STUDY TRACKS</div><h2>지도를 고르고, 강의 안으로</h2></div><p class="section-desc">공통 기초와 8개 전문 분야를 별도 과정으로 나눴습니다. 분야별 모듈에서 설명과 예제를 배우고, 파일 실습과 결과 검증으로 이어갑니다. 네트워크 보안은 여러 분야를 연결하는 통합 과정입니다.</p></div>
<div class="catalog-summary" id="catalogSummary"><div><strong>관심 분야에서 시작하세요</strong>공통 기초와 분야 입문을 함께 배울 수 있습니다.</div><a class="learning-button" href="tracks/foundation/">공통 기초 시작하기 →</a></div>
<div class="course-catalog" id="courseCatalog">{catalog}</div>
<div class="notice"><span>ⓘ</span><div><strong>진도 저장 안내</strong><span id="homeStorageNotice">차시별 완료 기록은 이 브라우저에 저장됩니다. 분야 페이지에서 JSON 백업을 받아 다른 브라우저로 옮길 수 있습니다. 계정·자동 동기화는 사용하지 않습니다.</span></div></div>
</section>

'''
home = re.sub(r'<section class="wrap section" id="study">.*?(?=<section class="wrap section" id="practice">)', study, home, flags=re.S)
# Remove the previous click-to-select handler; map nodes are now genuine links.
home = re.sub(r'<script>\s*document.addEventListener\(\'DOMContentLoaded\'.*?</script>\s*', '', home, flags=re.S)
if 'css/learning.css' not in home:
    home = home.replace('<link rel="stylesheet" href="css/mindmap.css">', '<link rel="stylesheet" href="css/mindmap.css">\n<link rel="stylesheet" href="css/learning.css">')
if 'js/curriculum.js' not in home:
    home = home.replace('<script src="js/app.js" defer></script>', '<script src="js/curriculum.js" defer></script>\n<script src="js/progress.js" defer></script>\n<script src="js/app.js" defer></script>')

# Update the exploration guide's field descriptions alongside the new taxonomy.
home = home.replace('<h4>Crypto / Misc</h4>', '<h4>Cryptography</h4>')
home = home.replace('인코딩·암호 문제, 데이터 표현, CTF의 다양한 논리·프로그래밍 과제', '기밀성·무결성·인증, 암호 프로토콜과 키 관리')
home = home.replace('정수·모듈러 연산, 고전 암호, 해시, 바이트 처리, Python', '정수·모듈러 연산, 대칭키·공개키, 해시·MAC, nonce와 키 수명')
home = home.replace('Python·수학 기초 → 문제 유형별 입문 → 재현 가능한 풀이 기록', '표현·수학 → 무결성·인증 → 현대 암호와 키 관리')
home = home.replace('IP, TCP/UDP, DNS, 포트와 Linux 명령어를 익히면 시작하기 좋다.', 'IP·HTTP·Linux 기초에서 시작해 웹 인가·클라우드 네트워크를 연결한다. 설계 모듈은 여러 분야를 함께 보는 중급 과정이다.')
home = home.replace('TCP/IP 기초 → Wireshark·프로토콜 분석 → 네트워크 위협과 방어', '패킷·TLS 관찰 → 망 분리·최소 허용 → 탐지·Zero Trust → 통합 설계')
home = home.replace('수학적 성질이나 작은 단서를 이용해 문제를 풀 수 있을까?', '데이터의 비밀과 진위를 어떤 보장으로 지킬 수 있을까?')
home = home.replace('수학·규칙·퍼즐은 Crypto/Misc를 먼저 살펴보세요.', '암호 원리·키 관리는 Cryptography, 단서·자동화는 Misc, 클라우드 신원·구성은 Cloud Security를 먼저 살펴보세요. Network Security는 이 지식을 연결해 통합 방어로 확장합니다.')
if '<h4>Cloud Security</h4>' not in home:
    extra = '''<div class="field-guide-card"><div class="field-guide-top"><span class="field-index">07</span><h4>Misc</h4></div><p class="field-question">낯선 데이터를 나누고 작은 도구로 검증할 수 있을까?</p><dl><dt>주로 다루는 문제</dt><dd>단서 추출, 바이트 변환, 자동화, 재현 가능한 풀이</dd><dt>도움 되는 기초</dt><dd>Python·파일 처리와 데이터 표현</dd><dt>첫 실습</dt><dd>제공된 텍스트에서 필드를 추출하고 두 단계 변환을 검증합니다.</dd></dl><div class="field-path"><a href="tracks/misc/">Misc 과정 열기 ↗</a></div></div>
<div class="field-guide-card"><div class="field-guide-top"><span class="field-index">08</span><h4>Cloud Security</h4></div><p class="field-question">누가 어떤 자원에 접근하고, 누가 설정을 책임질까?</p><dl><dt>주로 다루는 문제</dt><dd>공동 책임, IAM, 네트워크, 데이터 공개, 비밀 관리와 감사</dd><dt>도움 되는 기초</dt><dd>네트워크·웹 인가·JSON 읽기</dd><dt>첫 실습</dt><dd>계정과 결제 없이 로컬 구성 파일을 검토하고 수정안을 작성합니다.</dd></dl><div class="field-path"><a href="tracks/cloud/">Cloud Security 과정 열기 ↗</a></div></div>
'''
    pos = home.index('</div>\n<div class="field-choice">')
    home = home[:pos] + extra + home[pos:]
(ROOT / 'index.html').write_text(home, encoding='utf-8', newline='\n')
print('Generated 18 course/lesson entry pages and linked 9 homepage paths.')
