from lab_input import read_json
def solve(root, variant):
    accepted, nul, total = [], [], 0
    for row in read_json(root / f'project-input-{variant}.json'):
        raw = bytes.fromhex(row['hex'])
        if len(raw) < 2: continue
        length = int.from_bytes(raw[:2], 'big')
        if length > 8 or len(raw)-2 != length: continue
        accepted.append(row['id']); total += sum(raw[2:])
        if 0 in raw[2:]: nul.append(row['id'])
    return dict(accepted_ids=accepted, payload_sum=total, nul_ids=nul)
