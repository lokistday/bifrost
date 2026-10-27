"""Copy only publishable assets into _site for the Pages artifact."""
from pathlib import Path
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
TARGET = (ROOT / '_site').resolve()
assert TARGET.parent == ROOT.resolve() and TARGET.name == '_site', 'Unexpected output directory'

if TARGET.exists():
    shutil.rmtree(TARGET)  # Resolved, fixed workspace output checked above.
TARGET.mkdir()
for name in ['index.html', 'og-image.png', 'sitemap.xml']:
    shutil.copy2(ROOT / name, TARGET / name)
for name in ['assets', 'css', 'js', 'guides', 'tracks', 'learn', 'projects']:
    shutil.copytree(ROOT / name, TARGET / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules', '.venv'))
lab_names = json.loads((ROOT / 'labs/manifest.json').read_text(encoding='utf-8'))
for name in [*lab_names, 'manifest.json']:
    source = ROOT / 'labs' / name
    assert not source.is_symlink() and source.resolve().is_relative_to((ROOT / 'labs').resolve())
    assert name == Path(name).as_posix() and '..' not in Path(name).parts
    destination = TARGET / 'labs' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
(TARGET / '.nojekyll').write_text('', encoding='utf-8')
print(f'Packaged {sum(p.is_file() for p in TARGET.rglob("*"))} static files in _site.')
