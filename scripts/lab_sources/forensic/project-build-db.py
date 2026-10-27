"""Generate a new SQLite file from the fixed public training records."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path
from lab_input import read_json
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--variant',choices=['a','b'],default='a')
args=parser.parse_args()
root=Path(__file__).resolve().parent
target=root / f'project-{args.variant}.sqlite'
# Exclusive creation protects any existing learner work.
try:
    with target.open('xb'): pass
except FileExistsError:
    parser.error('output already exists; use a new working copy, not an overwrite')
with closing(sqlite3.connect(target)) as db, db:
    db.execute('CREATE TABLE events (id TEXT PRIMARY KEY, at TEXT, host TEXT, session TEXT, event TEXT)')
    db.executemany('INSERT INTO events VALUES (?,?,?,?,?)',
        [(r['id'],r['at'],r['host'],r['session'],r['event']) for r in read_json(root/f'project-input-{args.variant}.json')])
print('Created',target.name)
