"""Build static HTML from authored templates; never mutate generated HTML input."""
from pathlib import Path
import subprocess
from build_courses import build as build_courses
from build_visuals import build as build_visuals
from build_metadata import build as build_metadata

ROOT = Path(__file__).resolve().parents[1]


def build():
    _, courses = build_courses()
    build_metadata(courses)
    build_visuals()
    subprocess.run(['node', str(ROOT / 'scripts/render_pages.cjs')], cwd=ROOT, check=True)


if __name__ == '__main__':
    build()
