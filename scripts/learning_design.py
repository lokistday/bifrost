"""Validate and attach the authored practice layer without changing permanent IDs."""
from pathlib import Path
import json
import ast
import re

ROOT = Path(__file__).resolve().parents[1]


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
    plans = json.loads((ROOT/'content/lesson-plans.json').read_text(encoding='utf-8'))
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
    assert set(plans) == set(lessons), 'Every lesson needs an individually authored plan'
    assert set(projects) == set(courses), 'Every course needs a final project'
    for key, course in courses.items():
        project = projects[key]
        assert all(i in lessons for i in project['prerequisites']), f'{key}: project prerequisites'
        assert len(project['rubric']) == 4 and len(project['tasks']) >= 4
        course['project'] = project
        for mi, module in enumerate(course['modules']):
            for lesson in module['lessons']:
                plan = plans[lesson['id']]
                level, minutes = plan['level'], plan['minutes']
                assert level in ('기초','응용','심화 연결')
                assert len(minutes)==2 and all(type(n) is int and n>0 for n in minutes) and minutes[0]<=minutes[1]
                assert plan['troubleshooting'] and plan['diagnostic']['options']
                lesson['learning'] = dict(**exercises[lesson['id']], level=level, minutes=minutes,
                    setup=plan['setup'], readiness=plan['readiness'], readinessAnswer=plan['readinessAnswer'], bridge=plan['bridge'],
                    diagnostic=plan['diagnostic'], support=plan['support'], troubleshooting=plan['troubleshooting'], estimateBasis=plan['estimateBasis'],
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
        route['milestones'] = []
        for start in range(0,len(sequence),5):
            ids = sequence[start:start+5]
            last = lessons[ids[-1]]
            route['milestones'].append(dict(number=len(route['milestones'])+1, lessons=ids,
                title=last['title']+'까지', outcome=last['goal'],
                artifact='해설을 닫고 다음 기준을 보여 주는 명령·입력·출력 또는 분석 기록을 남기세요: '+last['checks'][0],
                minutes=[sum(lessons[k]['learning']['minutes'][i] for k in ids) for i in (0,1)]))
    return result
