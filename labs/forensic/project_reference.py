from datetime import datetime
from lab_input import read_json
def solve(root, variant):
    rows=read_json(root/f'project-input-{variant}.json')
    scoped=[r for r in rows if r['host']=='lab-1' and r['session']=='S7']
    ordered=sorted(scoped,key=lambda r:(datetime.fromisoformat(r['at'].replace('Z','+00:00')),r['id']))
    return dict(timeline=[r['id'] for r in ordered],reads=[r['id'] for r in ordered if r['event']=='read'],suspect_actor='UNKNOWN')
