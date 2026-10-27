import hashlib
from lab_input import read_json
from media_tools import bounded_decompress
def solve(root, variant):
    outcomes,hashes=[],[]
    for row in read_json(root/f'project-input-{variant}.json'):
        try: result=bounded_decompress(bytes.fromhex(row['hex']),output_limit=16,input_limit=1024)
        except ValueError: outcomes.append('REJECT'); continue
        outcomes.append('ACCEPT'); hashes.append(hashlib.sha256(result).hexdigest())
    return dict(outcomes=outcomes,hashes=hashes)
