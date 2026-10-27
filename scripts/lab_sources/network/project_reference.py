import ipaddress
from lab_input import read_json
def solve(root, variant):
    source=read_json(root/f'project-input-{variant}.json')
    decisions=[]
    for flow in source['flows']:
        result='DENY'
        for rule in source['rules']:
            if (ipaddress.ip_address(flow['src']) in ipaddress.ip_network(rule['src']) and
                ipaddress.ip_address(flow['dst']) in ipaddress.ip_network(rule['dst']) and flow['port']==rule['port']):
                result=rule['action']; break
        decisions.append(result)
    alerts=source['alerts']
    return dict(decisions=decisions,TP=sum(r['predicted'] and r['actual'] for r in alerts),
                FP=sum(r['predicted'] and not r['actual'] for r in alerts),FN=sum(not r['predicted'] and r['actual'] for r in alerts))
