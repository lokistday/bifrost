import copy
from lab_input import read_json
from boundary_models import load, rbac_allowed, private_access, lease_decision
def solve(root, variant):
    change=read_json(root/f'project-input-{variant}.json')
    source=copy.deepcopy(load(root/'boundary-models.json'))
    source['role']['namespace']=change['role_namespace']
    source['binding']['subject']['namespace']=change['subject_namespace']
    source['lease']['revoked']=change['lease_revoked']
    return dict(rbac=[rbac_allowed(r,source['role'],source['binding']) for r in source['rbac_requests']],
                private=[private_access(r) for r in source['private_requests']],
                leases=[lease_decision(r,source['lease']) for r in source['lease_requests']])
