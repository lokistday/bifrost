"""Derive display counts and cache identity from authored inputs."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def build(courses):
    lesson_count=sum(len(m['lessons']) for c in courses.values() for m in c['modules'])
    metrics=dict(courses=len(courses),modules=sum(len(c['modules']) for c in courses.values()),
                 lessons=lesson_count,projects=len(courses),visuals=len(courses)+lesson_count)
    files=[*sorted((ROOT/'content/courses').glob('*.json')),
           *[ROOT/'content'/n for n in ('fields.json','visuals.json','transfer-exercises.txt','projects.json','learning-paths.json')],
           *sorted((ROOT/'templates').glob('*')),
           *[ROOT/n for n in ('js/learning-view.js','js/learning.js','js/path-progress.js','js/study-search.js','css/study.css','css/theme.css','js/theme.js','css/main.css','scripts/render_pages.cjs','scripts/render_study.cjs','scripts/learning_design.py','scripts/site_security.cjs')]]
    digest=hashlib.sha256()
    for file in sorted(files, key=lambda p: p.relative_to(ROOT).as_posix()):
        digest.update(file.relative_to(ROOT).as_posix().encode('utf-8')+b'\0'+file.read_bytes())
    metrics['contentVersion']='learning-'+digest.hexdigest()[:12]
    (ROOT/'content/site-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8',newline='\n')
    values={key.upper():str(value) for key,value in metrics.items()}
    values['COURSE_TABLE']='\n'.join(f'| {c["title"]} | {sum(len(m["lessons"]) for m in c["modules"])} |' for c in courses.values())
    for source,dest in [('templates/README.md','README.md'),('templates/og-image.svg','assets/og-image.svg')]:
        text=(ROOT/source).read_text(encoding='utf-8')
        for key,value in values.items(): text=text.replace('{{'+key+'}}',value)
        assert '{{' not in text, f'Unfilled metadata template: {source}'
        (ROOT/dest).write_text(text,encoding='utf-8',newline='\n')
    return metrics
