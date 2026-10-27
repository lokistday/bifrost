from lab_input import read_json
import json
from record_crypto import optional_crypto
def solve(root, variant):
    InvalidTag,_,_,AESGCM,*_=optional_crypto()
    record=read_json(root/'round2-crypto.json')['record']
    last=0; outcomes=[]
    for row in read_json(root/f'project-input-{variant}.json'):
        aad=json.dumps(['project-v1',row['tenant'],row['document'],row['version'],row['seq']],separators=(',',':')).encode('utf-8')
        try: AESGCM(bytes.fromhex(record['dek_hex'])).decrypt(bytes.fromhex(row['nonce_hex']),bytes.fromhex(row['ciphertext_hex']),aad)
        except InvalidTag: outcomes.append('AUTH_FAIL'); continue
        if row['seq']<=last: outcomes.append('REPLAY')
        else: outcomes.append('ACCEPT'); last=row['seq']
    return dict(outcomes=outcomes,last=last)
