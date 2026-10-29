"""Validate and attach the authored practice layer without changing permanent IDs."""
from pathlib import Path
import json
import ast
import re

ROOT = Path(__file__).resolve().parents[1]
READINESS = {
 'foundation': ('파일의 위치와 실행 결과를 따로 설명할 수 있나요?', '셸의 현재 폴더·파일 경로·프로그램 출력을 구별합니다. 환경 준비와 경로 차시에서 확인하세요.', 'python'),
 'web': ('인증과 대상 자원의 인가는 같은 검사인가요?', '인증은 주체 확인, 인가는 주체·대상·행동의 허용 판단입니다. 세션이 유효해도 타인의 자원은 거부해야 합니다.', 'web'),
 'pwn': ('버퍼 크기, 유효한 데이터 길이, 문자열 길이를 구분할 수 있나요?', '할당 용량과 채워진 바이트 수는 다르고 strlen은 첫 NUL까지만 셉니다. 읽기 전에 경계와 객체 수명을 확인합니다.', 'c'),
 'rev': ('문자열이 있다는 사실만으로 그 기능이 실행됐다고 말할 수 있나요?', '문자열은 단서입니다. 도달 가능한 분기·실제 입력·출력을 연결해 가설을 검증해야 합니다.', 'c'),
 'forensic': ('해시 일치와 파일 출처의 진위는 같은 것인가요?', '해시는 기준 바이트와의 일치를 확인합니다. 기준의 신뢰·보관 이력·수집 범위는 별도 근거가 필요합니다.', 'evidence'),
 'network': ('센서에 기록이 없다는 사실이 통신이 없었다는 뜻인가요?', '센서 위치·필터·손실·시간 범위를 확인해야 합니다. 관측되지 않은 경로가 남아 있을 수 있습니다.', 'network'),
 'crypto': ('암호학적 검증 성공이면 현재 요청을 처리해도 되나요?', '인증된 바이트와 현재 권한·문맥·재전송·만료는 다른 검증입니다. 목적과 상태를 함께 확인합니다.', 'bytes'),
 'misc': ('화면에 보이는 문자열과 파일의 원시 바이트는 같나요?', '인코딩·컨테이너·압축을 거치며 표현이 달라집니다. 변환 순서·크기 제한·중간 검증을 기록합니다.', 'bytes'),
 'cloud': ('사설 네트워크에 있으면 자원 접근 권한도 생기나요?', '경로 도달과 자원 인가는 별개입니다. 신원·정책·서비스 설정을 함께 확인해야 합니다.', 'network')}


def code_context(code, environment, partial=False):
    """Describe the block's actual syntax, retaining the authored execution notes."""
    debugger = re.search(r'(?m)^(?:\(gdb\)\s*|break |b main\b|run(?:\s|$)|next(?:\s|$)|finish(?:\s|$)|print [\w*$]|info registers)',code)
    if debugger and re.search(r'(?m)^(?:gcc|gdb)\b',code):
        return '혼합 절차 · 먼저 터미널에서 빌드·gdb 실행 → 주석 아래는 GDB 콘솔에 입력'
    if debugger:
        return 'GDB 콘솔 명령 · 대상 실행 파일을 연 같은 디버깅 세션'
    if re.search(r'(?m)^(?:python3\b|py -3\b|gcc\b|gdb\b|readelf\b|objdump\b|git\b|chmod\b|cp\b|mkdir\b|cd\b|pwd\b|ls\b|strings\b|nm\b|ldd\b|tshark\b|sha256sum\b|sudo\b|stat\b|cat\b|printf\b|wc\b|\./|\.venv/)',code):
        return '터미널 명령 · 이 분야의 작업 사본 폴더 · '+environment
    if re.search(r'#include|\bint main\s*\(|\b(?:char|int|size_t)\s+\*?[a-zA-Z_]\w*\s*(?:\[|=|;)',code):
        fragment = partial or 'int main' not in code
        return 'C 소스'+(' 조각 · 해당 함수·파일에 넣고 다시 컴파일' if fragment else ' · 파일에 저장한 뒤 컴파일')+' · '+environment
    if code.strip()=='dns' or re.match(r'^(?:tcp\.|http\.|ip\.|tls\.)',code):
        return 'Wireshark 표시 필터 · 터미널이나 Python에 입력하지 않음'
    if re.search(r'\b(?:const |document\.|textContent|innerHTML)',code):
        return 'JavaScript · 안내된 HTML의 script 부분 또는 같은 개발자 도구 콘솔'
    try:
        ast.parse(code)
    except SyntaxError:
        return '관찰 절차·자료 예시 · 그대로 셸에 붙여 넣지 말고 본문 안내를 따라 확인'
    return ('Python 부분 코드 · 앞 단계의 변수·객체를 유지한 같은 스크립트' if partial else 'Python 코드 · 안내된 .py 파일에 저장해 실행')+' · '+environment


def attach(courses):
    exercises = {}
    for line in (ROOT/'content/transfer-exercises.txt').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        key, challenge, answer = line.split('|')
        assert key not in exercises and challenge.strip() and answer.strip(), f'Bad transfer exercise: {key}'
        exercises[key] = dict(challenge=challenge, answer=answer)
    projects = json.loads((ROOT/'content/projects.json').read_text(encoding='utf-8'))
    lessons = {l['id']:l for c in courses.values() for m in c['modules'] for l in m['lessons']}
    assert set(exercises) == set(lessons), 'Every lesson needs its own transfer exercise'
    assert set(projects) == set(courses), 'Every course needs a final project'
    for key, course in courses.items():
        project = projects[key]
        assert all(i in lessons for i in project['prerequisites']), f'{key}: project prerequisites'
        assert len(project['rubric']) == 4 and len(project['tasks']) >= 4
        course['project'] = project
        for mi, module in enumerate(course['modules']):
            for lesson in module['lessons']:
                level = '기초' if mi < 2 else ('응용' if mi < 4 else '심화 연결')
                minutes = [25,45] if level == '기초' else ([40,65] if level == '응용' else [50,80])
                if key in ('pwn','rev'): minutes=[45,80] if mi<2 else [60,100]
                question, answer, bridge = READINESS[key]
                lesson['learning'] = dict(**exercises[lesson['id']], level=level, minutes=minutes,
                    setup=[30,90] if lesson['id']=='foundation.environment' else [0,30],
                    readiness=question, readinessAnswer=answer, bridge=bridge,
                    tags=[course['label'],level,*lesson['title'].replace('·',' ').replace('·',' ').split()],
                    codeContext=code_context(lesson['code'],lesson['environment']['label']))
                for step in lesson['walkthrough']:
                    if step.get('code'):
                        step['context']=code_context(step['code'],lesson['environment']['label'],partial=True)
    return courses


def paths(courses):
    result=json.loads((ROOT/'content/learning-paths.json').read_text(encoding='utf-8'))
    lessons={l['id']:l for c in courses.values() for m in c['modules'] for l in m['lessons']}
    seen_ids=set()
    for route in result:
        assert re.fullmatch(r'[a-z][a-z0-9-]*', route['id']), 'Invalid learning path ID'
        route['label'] = {'start':'보안 입문','web-defense':'웹 보안','dfir':'DFIR','red-foundations':'레드팀 기초','cloud-operations':'클라우드 보안'}.get(route['id'],route['title'])
        assert route['id'] not in seen_ids and route['project'] in courses
        seen_ids.add(route['id'])
        sequence=[]
        def visit(key,stack):
            assert key in lessons and key not in stack, f'Invalid route/prerequisite: {key}'
            if key in sequence: return
            for predecessor in lessons[key]['prerequisites']:
                visit(predecessor,[*stack,key])
            sequence.append(key)
        for key in route['lessons']: visit(key,[])
        for key in courses[route['project']]['project']['prerequisites']: visit(key,[])
        route['sequence']=sequence
    return result
