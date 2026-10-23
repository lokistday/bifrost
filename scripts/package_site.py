"""Copy only publishable assets into _site for the Pages artifact."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = (ROOT / '_site').resolve()
assert TARGET.parent == ROOT.resolve() and TARGET.name == '_site', 'Unexpected output directory'

if TARGET.exists():
    shutil.rmtree(TARGET)  # Resolved, fixed workspace output checked above.
TARGET.mkdir()
for name in ['index.html', 'og-image.png', 'sitemap.xml']:
    shutil.copy2(ROOT / name, TARGET / name)
for name in ['assets', 'css', 'js', 'guides', 'tracks', 'labs']:
    shutil.copytree(ROOT / name, TARGET / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules', '.venv'))
(TARGET / '.nojekyll').write_text('', encoding='utf-8')
print(f'Packaged {sum(p.is_file() for p in TARGET.rglob("*"))} static files in _site.')
