"""Validate authored, named course records and emit browser bundles.

content/courses/*.json are the source. Generated JS must not be edited by hand.
"""
from pathlib import Path
import json
import re
from learning_design import attach, paths

ROOT = Path(__file__).resolve().parents[1]


def load_courses(strict=True):
    site = json.loads((ROOT / 'content/site.json').read_text(encoding='utf-8'))
    fields = json.loads((ROOT / 'content/fields.json').read_text(encoding='utf-8'))
    courses = {}
    for number, item in enumerate(site['courses']):
        key = item['id']
        assert re.fullmatch(r'[a-z][a-z0-9-]*', key), f'Invalid course path: {key}'
        course = json.loads((ROOT / f'content/courses/{key}.json').read_text(encoding='utf-8'))
        assert course['id'] == key and key not in courses, f'Duplicate/mismatched course: {key}'
        course['number'] = f'{number:02d}'
        course['accent'] = item['accent']
        course['introduction'] = fields[key]
        courses[key] = course
    lessons = {l['id']: l for c in courses.values() for m in c['modules'] for l in m['lessons']}
    count = sum(len(m['lessons']) for c in courses.values() for m in c['modules'])
    assert len(lessons) == count, 'Duplicate permanent lesson ID'
    registry = json.loads((ROOT / 'content/lesson-ids.json').read_text(encoding='utf-8'))
    assert set(registry) <= set(lessons), 'Permanent lesson IDs must not be removed'
    assert set(fields) == set(courses), 'Field introductions differ from course manifest'
    for course in courses.values():
        assert course['modules'] and course['sources'], f'Incomplete course: {course["id"]}'
        assert all(len(r)==2 and r[0] and r[1].startswith('https://') for r in course['sources']), f'Unsafe course reference: {course["id"]}'
        assert all(p in lessons for p in course['prereqs']), f'Unknown course prerequisite: {course["id"]}'
        assert len(course['introduction']['items']) == 5, f'Field introduction needs five entries: {course["id"]}'
        for module in course['modules']:
            assert module['title'] and module['intro'] and module['lessons']
            for lesson in module['lessons']:
                key = lesson['id']
                assert re.fullmatch(re.escape(course['id']) + r'\.[a-z0-9-]+', key), f'Invalid ID: {key}'
                for name in ['title', 'goal', 'code', 'expected', 'task', 'hint']:
                    assert isinstance(lesson.get(name), str) and lesson[name].strip(), f'{key}: missing {name}'
                for name in ['concepts', 'checks']:
                    assert len(lesson.get(name, [])) >= 2 and all(isinstance(x, str) and x.strip() for x in lesson[name]), f'{key}: {name}'
                for file in lesson['files']:
                    assert '/' not in file and '\\' not in file, f'Invalid lab path: {key}/{file}'
                    assert (ROOT / 'labs' / course['id'] / file).is_file(), f'Missing lab: {key}/{file}'
                if not strict:
                    continue
                assert len(lesson['concepts']) >= 4, f'{key}: incomplete concept explanation'
                environment = lesson.get('environment', {})
                assert environment.get('label') and environment.get('details'), f'{key}: environment'
                assert isinstance(environment['details'], list) and all(isinstance(d, str) and d.strip() for d in environment['details']), f'{key}: environment details'
                assert 'prerequisites' in lesson, f'{key}: prerequisite list'
                assert all(p in lessons and p != key for p in lesson['prerequisites']), f'{key}: unknown/self prerequisite'
                assert len(lesson.get('walkthrough', [])) >= 2, f'{key}: stepwise explanation'
                for step in lesson['walkthrough']:
                    assert step.get('title') and step.get('explanation'), f'{key}: incomplete step'
                solution = lesson.get('solution', {})
                assert len(solution.get('approach', [])) >= 2 and solution.get('expected'), f'{key}: solution'
                assert lesson.get('pitfalls'), f'{key}: missing misconceptions'
                assert all(p.get('mistake') and p.get('correction') for p in lesson['pitfalls']), f'{key}: incomplete misconception'
                assert len(lesson.get('questions', [])) >= 2, f'{key}: missing self checks'
                for question in lesson['questions']:
                    options = question.get('options', [])
                    answer = question.get('answer')
                    assert question.get('prompt') and question.get('explanation'), f'{key}: missing question rationale'
                    assert 3 <= len(options) <= 4 and len(set(options)) == len(options), f'{key}: options'
                    assert type(answer) is int and 0 <= answer < len(options), f'{key}: answer index'
                assert lesson.get('references'), f'{key}: missing lesson references'
                assert all(len(r) == 2 and r[0] and r[1].startswith('https://') for r in lesson['references']), f'{key}: references'
    if strict:
        visited = set()

        def check_prerequisites(key, stack):
            assert key not in stack, 'Cyclic prerequisites: ' + ' -> '.join([*stack, key])
            if key in visited:
                return
            for prerequisite in lessons[key]['prerequisites']:
                check_prerequisites(prerequisite, [*stack, key])
            visited.add(key)

        for key in lessons:
            check_prerequisites(key, [])
    attach(courses)
    return site, courses


def write_bundle(path, expression, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = '/* Generated by scripts/build_courses.py; edit content/courses/*.json. */\n'
    text += expression + ' = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
    path.write_text(text, encoding='utf-8', newline='\n')


def build(strict=True):
    site, courses = load_courses(strict)
    write_bundle(ROOT / 'js/curriculum.js', 'window.BifrostCourses', courses)
    catalog = {}
    for key, course in courses.items():
        catalog[key] = {k: course[k] for k in ['id', 'title', 'label']}
        catalog[key]['modules'] = [dict(title=m['title'], intro=m['intro'], lessons=[
            {k: l[k] for k in ['id', 'title', 'goal']} for l in m['lessons']]) for m in course['modules']]
        write_bundle(ROOT / f'js/courses/{key}.js', f'window.BifrostCourses.{key}', course)
    write_bundle(ROOT / 'js/catalog.js', 'window.BifrostCourses', catalog)
    (ROOT/'content/generated-paths.json').write_text(json.dumps(paths(courses),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return site, courses


if __name__ == '__main__':
    _, courses = build()
    print(f'Validated and bundled {len(courses)} courses.')
