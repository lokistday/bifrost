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
           *[ROOT/'content'/n for n in ('fields.json','visuals.json','transfer-exercises.txt','projects.json','learning-paths.json','lesson-plans.json')],
           *sorted((ROOT/'templates').glob('*')),
           *sorted((ROOT/'assets/projects').glob('*.webp')),
           ROOT/'scripts/render_wordmark.cjs', ROOT/'scripts/render_backdrop.cjs', ROOT/'js/wordmark-motion.js', ROOT/'js/pointer-trail.js', ROOT/'css/pointer-trail.css', ROOT/'js/exam.js', ROOT/'js/exam-catalog.js', ROOT/'css/exams.css',
           *[ROOT/n for n in ('js/progress.js','scripts/render_learning_tools.cjs','js/learning-view.js','js/learning.js','js/path-progress.js','css/study.css','css/theme.css','js/theme.js','assets/logo.svg','assets/logo-mark.svg','css/splash.css','css/main.css','css/workspace.css','js/workspace.js','scripts/render_home.cjs','scripts/learning_design.py','scripts/site_security.cjs')]]
    digest=hashlib.sha256()
    for file in sorted(files, key=lambda p: p.relative_to(ROOT).as_posix()):
        digest.update(file.relative_to(ROOT).as_posix().encode('utf-8')+b'\0'+file.read_bytes().replace(b'\r\n', b'\n'))
    # Project motion and newly published exam/course bundles use scoped fingerprints.
    # Preserve the published cache ID at this migration baseline so unrelated
    # HTML does not change merely because the fingerprint scope gets narrower.
    cache_aliases = {'f9af35cc0b464c5adc48f4bb2d8786ca7330a66f9d911868ae661fea8025cd3e': 'learning-df5000eecc77', '739d91a7d8f8789025773fbcde51ab72e7a682a8bd082fbe4768cdda848b5b4e': 'learning-df5000eecc77'}
    key = digest.hexdigest()
    metrics['contentVersion']=cache_aliases.get(key, 'learning-'+key[:12])
    (ROOT/'content/site-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8',newline='\n')
    values={key.upper():str(value) for key,value in metrics.items()}
    values['COURSE_TABLE']='\n'.join(f'| {c["title"]} | {sum(len(m["lessons"]) for m in c["modules"])} |' for c in courses.values())
    # The repository introduction is authored directly in README.md.
    for source,dest in [('templates/og-image.svg','assets/og-image.svg')]:
        text=(ROOT/source).read_text(encoding='utf-8')
        for key,value in values.items(): text=text.replace('{{'+key+'}}',value)
        assert '{{' not in text, f'Unfilled metadata template: {source}'
        (ROOT/dest).write_text(text,encoding='utf-8',newline='\n')
    return metrics
