"""Offline examples in real policy formats; not an AWS/Kubernetes authorizer."""
import argparse
import fnmatch
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def load(path):
    with Path(path).open('rb') as f: data=f.read(65537)
    if len(data)>65536: raise ValueError('policy exceeds 64 KiB')
    return json.loads(data)

def strings(value):
    values=[value] if isinstance(value,str) else value
    if not isinstance(values,list) or not values or not all(isinstance(v,str) and v for v in values):
        raise ValueError('nonempty string/list required')
    return values

def iam(policy,action,resource):
    if not isinstance(policy,dict) or set(policy)-{'Version','Statement','Id'}:
        raise ValueError('unsupported document fields')
    if policy.get('Version')!='2012-10-17':raise ValueError('unsupported policy version')
    rows=policy.get('Statement')
    if isinstance(rows,dict):rows=[rows]
    if not isinstance(rows,list) or not rows:raise ValueError('Statement required')
    matched=[]
    # Validate ALL statements before making any allow decision.
    for row in rows:
        if not isinstance(row,dict) or set(row)-{'Sid','Effect','Action','Resource'}:
            raise ValueError('unsupported statement: Condition/Principal/NotAction etc. require real policy evaluation')
        if row.get('Effect') not in ('Allow','Deny'):raise ValueError('Effect must be Allow/Deny')
        actions,resources=strings(row.get('Action')),strings(row.get('Resource'))
        # Only AWS-style * and ? wildcards are supported; shell character classes are not.
        if any('[' in s or ']' in s or '${' in s for s in actions+resources):raise ValueError('unsupported pattern')
        if any(fnmatch.fnmatchcase(action.lower(),a.lower()) for a in actions) and any(fnmatch.fnmatchcase(resource,r) for r in resources):
            matched.append(row['Effect'])
    return 'EXPLICIT_DENY_MODEL' if 'Deny'in matched else 'ALLOW_MODEL' if 'Allow'in matched else 'IMPLICIT_DENY_MODEL'

def rbac(doc,namespace,subject_namespace,user,verb,resource,group=''):
    if not isinstance(doc,dict) or doc.get('kind')!='List':raise ValueError('Kubernetes List required')
    items=doc.get('items')
    if not isinstance(items,list):raise ValueError('items required')
    roles={};bindings=[]
    for obj in items:
        kind=obj.get('kind');meta=obj.get('metadata',{})
        if kind in ('Namespace','ServiceAccount'):continue
        if kind=='Role':
            if obj.get('apiVersion')!='rbac.authorization.k8s.io/v1':raise ValueError('unsupported API')
            key=(meta.get('namespace'),meta.get('name'))
            if key in roles:raise ValueError('duplicate role')
            rules=obj.get('rules')
            if not isinstance(rules,list):raise ValueError('rules required')
            for rule in rules:
                if set(rule)-{'apiGroups','resources','verbs'}:raise ValueError('unsupported RBAC rule')
                for field in ['apiGroups','resources','verbs']:
                    if not isinstance(rule.get(field),list) or not rule[field] or not all(isinstance(v,str)for v in rule[field]):raise ValueError('invalid RBAC rule')
            roles[key]=rules
        elif kind=='RoleBinding':
            if obj.get('apiVersion')!='rbac.authorization.k8s.io/v1':raise ValueError('unsupported API')
            if obj.get('roleRef',{}).get('kind')!='Role' or obj['roleRef'].get('apiGroup')!='rbac.authorization.k8s.io':raise ValueError('only namespaced Role references supported')
            if not isinstance(obj.get('subjects'),list):raise ValueError('subjects required')
            if any(s.get('kind')!='ServiceAccount' for s in obj['subjects']):raise ValueError('only ServiceAccount subjects supported')
            bindings.append(obj)
        else:raise ValueError('unsupported resource kind')
    allowed=False
    for binding in bindings:
        ns=binding.get('metadata',{}).get('namespace')
        key=(ns,binding['roleRef'].get('name'))
        if key not in roles:raise ValueError('Role reference is unresolved')
        if ns!=namespace:continue
        if not any(s.get('namespace')==subject_namespace and s.get('name')==user for s in binding['subjects']):continue
        for rule in roles[key]:
            if all(wanted in rule[field] or '*'in rule[field] for wanted,field in [(group,'apiGroups'),(resource,'resources'),(verb,'verbs')]):allowed=True
    return 'ALLOW_MODEL' if allowed else 'NO_ALLOW_IN_THIS_DOCUMENT'

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('iam');a.add_argument('--policy',default=str(HERE/'iam-reader.json'));a.add_argument('--action',default='s3:GetObject');a.add_argument('--resource',default='arn:aws:s3:::bifrost-training-notes/readme.txt')
    b=sub.add_parser('rbac');b.add_argument('--policy',default=str(HERE/'rbac-resources.json'));b.add_argument('--namespace',default='bifrost-learn');b.add_argument('--subject-namespace',default='bifrost-learn');b.add_argument('--user',default='reader');b.add_argument('--verb',default='get');b.add_argument('--resource',default='pods')
    args=p.parse_args()
    try:
        doc=load(args.policy)
        print(iam(doc,args.action,args.resource) if args.command=='iam'else rbac(doc,args.namespace,args.subject_namespace,args.user,args.verb,args.resource))
        print('scope=offline subset; production permission NOT verified')
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError) as e:p.exit(2,'UNSUPPORTED_OR_INVALID: '+str(e)+'\n')

if __name__=='__main__':main()
