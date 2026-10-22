"""Generate the small static entry pages and keep the homepage's links semantic."""
from pathlib import Path
import json
import re
from build_visuals import build as build_visuals

ROOT = Path(__file__).resolve().parents[1]
build_visuals()
# Display numbers follow the desktop map clockwise from the top. Lesson IDs stay unchanged.
COURSES = [
    ('foundation', 'Foundation', '공통 기초', '터미널 · 코드 · 네트워크', 'CORE'),
    ('pwn', 'Pwn / System', '시스템 보안', '메모리 · 디버깅', 'SYSTEM'),
    ('forensic', 'Forensic', '디지털 포렌식', '흔적 · 증거 · 타임라인', 'FORENSIC'),
    ('misc', 'Misc', '문제 해결 · 자동화', '단서 · 데이터 · 도구', 'MISC'),
    ('cloud', 'Cloud Security', '클라우드 보안', '신원 · 구성 · 감사', 'CLOUD'),
    ('network', 'Network Security', '네트워크 보안 · 통합', '망 설계 · 정책 · 탐지', 'NETWORK'),
    ('crypto', 'Cryptography', '암호학', '수학 · 무결성 · 키 관리', 'CRYPTO'),
    ('rev', 'Reverse Engineering', '리버싱', '분석 · 실행 흐름', 'REVERSE'),
    ('web', 'Web Hacking', '웹 보안', '요청 · 인증 · 취약점', 'WEB'),
]

STAR = '<svg class="bifrost-star" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 3 24 15 36 20 24 24 20 36 16 24 4 20 16 15Z" fill="currentColor"/></svg>'
FIELD_GUIDES = json.loads((ROOT / 'content' / 'field-guides.json').read_text(encoding='utf-8'))
COURSE_NUMBERS = {course[0]: f'{i:02d}' for i, course in enumerate(COURSES)}

def course_introduction(key):
    # Show only the selected field card, without the shared roadmap or selection advice.
    card = FIELD_GUIDES['fields'][key]
    card = re.sub(r'(<span class="field-index">)\d+(</span>)', lambda match: match[1] + COURSE_NUMBERS[key] + match[2], card)
    card = re.sub(r'href="tracks/[^/]+/"', 'href="#courseModules"', card)
    return f'<section class="course-introduction" id="courseIntroduction" aria-label="분야 소개">{card}</section>'

for key, title, label, subtitle, number in COURSES:
    folder = ROOT / 'tracks' / key
    folder.mkdir(parents=True, exist_ok=True)
    for view, name in [('course', 'index.html'), ('lesson', 'lesson.html')]:
        introduction = course_introduction(key) if view == 'course' else ''
        introduction_link = '#courseIntroduction' if view == 'course' else './#courseIntroduction'
        content = f'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0b1220">
<meta name="description" content="Bifrost {title}: {label} 설명과 예제·실습·검증을 차시별로 학습합니다.">
<title>{title} — Bifrost</title>
<script src="../../js/theme.js"></script>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='11' fill='%23101a30'/%3E%3Cpath d='M20 3 24 15 36 20 24 24 20 36 16 24 4 20 16 15Z' fill='%235ce1e6'/%3E%3C/svg%3E">
<link rel="stylesheet" href="../../css/main.css"><link rel="stylesheet" href="../../css/theme.css"><link rel="stylesheet" href="../../css/learning.css"><link rel="stylesheet" href="../../css/visuals.css">
<script src="../../js/curriculum.js" defer></script><script src="../../js/progress.js" defer></script><script src="../../js/visual-data.js" defer></script><script src="../../js/visuals.js" defer></script><script src="../../js/learning.js" defer></script>
</head><body class="learning-page" data-course="{key}" data-course-number="{COURSE_NUMBERS[key]}" data-view="{view}">
<a class="skip-link" href="#learningContent">학습 본문으로 건너뛰기</a>
<header class="topbar"><div class="wrap nav"><a class="brand" href="../../index.html"><span class="brand-mark">{STAR}</span><span>BIFROST</span></a><nav class="navlinks" aria-label="주 메뉴"><a href="../../index.html#mindmap">모든 분야</a><a href="{introduction_link}">분야 소개</a><a href="./#courseModules">{label} 목차</a></nav><button class="theme-toggle" id="themeToggle" type="button" aria-label="다크 모드로 전환" aria-pressed="false">테마 전환</button><a class="nav-cta" href="../../index.html#mindmap">학습 지도 ↗</a></div></header>
<main class="learning-wrap" id="learningContent" tabindex="-1"><h1>{title}</h1><p>학습 목차를 준비하고 있습니다.</p>{introduction}<noscript><p>차시 본문과 진도 기능에는 JavaScript가 필요합니다. 실습 자료는 아래 링크로 받을 수 있습니다.</p></noscript><a href="../../labs/{key}.zip" download>실습 ZIP 내려받기</a><p><a href="../../index.html#mindmap">전체 학습 지도</a></p></main>
<footer class="learning-footer"><div class="wrap">BIFROST · 이해하고, 실행하고, 근거를 남기기. <a href="../../index.html#mindmap">다른 분야 탐색 ↗</a></div></footer>
</body></html>
'''
        (folder / name).write_text(content, encoding='utf-8', newline='\n')

# Updating generated blocks is idempotent; splash and core stay authored HTML.
home = (ROOT / 'index.html').read_text(encoding='utf-8')
nodes = '\n'.join(f'      <a class="map-node node-{key}" data-map-track="{key}" href="tracks/{key}/"><span class="node-number">{i:02d} / {number}</span><span class="node-arrow" aria-hidden="true">↗</span><strong>{title}</strong><small>{label}</small><i>{subtitle}</i></a>' for i, (key, title, label, subtitle, number) in enumerate(COURSES))
home = re.sub(r'      <(?:button|a) class="map-node node-foundation".*?(?=      <div class="map-core")', nodes + '\n', home, flags=re.S)
home = home.replace('SIX DIRECTIONS', 'EIGHT DIRECTIONS').replace('해당 학습 트랙으로 이동합니다.', '분야별 목차와 강의 페이지로 이동합니다.')
home = home.replace('href="#linux-guide" onclick="openLinuxGuide(); return false;"', 'href="guides/linux.html" onclick="openLinuxGuide(); return false;"')
home = re.sub(r'viewBox="0 0 1000 (?:590|760|900)"', 'viewBox="0 0 1000 760"', home)
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

# The radial map is the homepage's single field selector. Field introductions live in content/field-guides.json.
home = re.sub(r'<section class="wrap section" id="roadmap">.*?(?=<section class="wrap section" id="study">)', '', home, flags=re.S)
home = re.sub(r'<section class="wrap section" id="study">.*?(?=<section class="wrap section" id="practice">)', '', home, flags=re.S)
home = home.replace('<a href="#roadmap">ROADMAP</a><a href="#study">STUDY</a>', '<a href="#mindmap">LEARNING MAP</a>')
home = home.replace('href="#study"', 'href="#mindmap"')
home = home.replace('03 / PRACTICE LOOP', '01 / PRACTICE LOOP').replace('04 / CAREER & RESOURCES', '02 / CAREER & RESOURCES')
# Remove the previous click-to-select handler; map nodes are now genuine links.
home = re.sub(r'<script>\s*document.addEventListener\(\'DOMContentLoaded\'.*?</script>\s*', '', home, flags=re.S)
if 'css/learning.css' not in home:
    home = home.replace('<link rel="stylesheet" href="css/mindmap.css">', '<link rel="stylesheet" href="css/mindmap.css">\n<link rel="stylesheet" href="css/learning.css">')
home = re.sub(r'<script src="js/(?:curriculum|progress|app)\.js" defer></script>\s*', '', home)
(ROOT / 'index.html').write_text(home, encoding='utf-8', newline='\n')
print('Generated 18 course/lesson entry pages and linked 9 homepage paths.')
