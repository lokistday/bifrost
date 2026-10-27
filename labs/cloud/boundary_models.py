"""Offline authorization and access-path models; not AWS/Kubernetes implementations."""
import argparse
from lab_input import read_json
from model_contracts import check
from datetime import datetime
from pathlib import Path


def load(path=None):
    return check(read_json(path or Path(__file__).with_name('boundary-models.json')), 'cloud')


def effective_permission(request, identity, boundary):
    if request.get('explicit_deny') is True:
        return 'DENY_EXPLICIT'
    if request.get('resource_policy_grant') is True:
        return 'UNMODELED_RESOURCE_POLICY'
    if request['action'] not in identity:
        return 'DENY_NO_IDENTITY_ALLOW'
    if request['action'] not in boundary:
        return 'DENY_BOUNDARY'
    return 'ALLOW_MODEL'


def rbac_allowed(request, role, binding):
    subject = binding['subject']
    return (binding['namespace'] == role['namespace'] == request['namespace']
            and binding['role'] == role['name']
            and request['subject_namespace'] == subject['namespace']
            and request['subject_name'] == subject['name']
            and any(request['api_group'] == rule['api_group']
                    and request['resource'] == rule['resource']
                    and request['verb'] in rule['verbs'] for rule in role['rules']))


def metadata_access(request, config):
    if config['endpoint_enabled'] is not True:
        return 'DISABLED'
    if request['network_reachable'] is not True:
        return 'BLOCKED_NETWORK'
    if config['tokens_required'] is True and request.get('token_valid') is not True:
        return 'DENY_TOKEN'
    return 'REACHABLE_MODEL'


def private_access(row):
    if row['dns_target'] != 'private-endpoint':
        return 'PUBLIC_PATH'
    if row['network_path'] is not True:
        return 'NO_NETWORK_PATH'
    if row['endpoint_policy'] is not True:
        return 'DENY_ENDPOINT_POLICY'
    if row['identity_permission'] is not True:
        return 'DENY_IDENTITY'
    return 'ALLOW_MODEL'


def lease_decision(request, lease):
    parse = lambda value: datetime.fromisoformat(value.replace('Z', '+00:00'))
    now, start, end = parse(request['at']), parse(lease['start']), parse(lease['expires'])
    if any(stamp.utcoffset() is None for stamp in (now, start, end)) or start >= end:
        raise ValueError('explicit timezones and start < expires required')
    if lease['revoked'] is True:
        return 'DENY_REVOKED'
    if not start <= now < end:
        return 'DENY_TIME'
    if not isinstance(lease['approved_by'], str) or not lease['approved_by'].strip() or request['actor'] != lease['actor']:
        return 'DENY_IDENTITY_OR_APPROVAL'
    if request['action'] not in lease['actions'] or request['resource'] != lease['resource']:
        return 'DENY_SCOPE'
    return 'ALLOW_MODEL'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['effective', 'rbac', 'metadata', 'private', 'breakglass'])
    parser.add_argument('--input')
    args = parser.parse_args()
    data = load(args.input)
    if args.mode == 'effective':
        for row in data['permission_requests']:
            print(row['id'] + ' ' + effective_permission(row, data['identity_allow'], data['boundary_allow']))
    elif args.mode == 'rbac':
        for row in data['rbac_requests']:
            print(f"{row['id']} {'ALLOW_MODEL' if rbac_allowed(row, data['role'], data['binding']) else 'DENY'}")
    elif args.mode == 'metadata':
        for row in data['metadata_requests']:
            result = metadata_access(row, data['metadata_options'])
            print(f"{row['id']} metadata={result}")
        print(f"role_ReadNotes={'ReadNotes' in data['instance_role_actions']} role_DeleteNotes={'DeleteNotes' in data['instance_role_actions']}")
    elif args.mode == 'private':
        for row in data['private_requests']:
            print(row['id'] + ' ' + private_access(row))
    else:
        for row in data['lease_requests']:
            print(row['id'] + ' ' + lease_decision(row, data['lease']))
        print('evidence_required=approval,activation,actions,revocation,review')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print("INVALID input: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(2)
