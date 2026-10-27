"""Worked solution: read after an independent attempt."""
import csv
def solve(root, variant):
    with (root / f'project-input-{variant}.csv').open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['user', 'status']:
            raise ValueError('header must be user,status')
        rows = list(reader)
    valid, invalid = [], []
    for number, row in enumerate(rows, 2):
        if None in row or row['user'] is None or not row['user'].strip() or row['status'] not in ('ok','denied'):
            invalid.append(number)
        else:
            valid.append(row)
    return dict(total=len(rows), valid=len(valid), denied=sum(r['status']=='denied' for r in valid),
                denied_users=sorted({r['user'].strip() for r in valid if r['status']=='denied'}), invalid_rows=invalid)
