"""Offline cloud operations checklist models, not provider APIs or token validation."""
import argparse
import hashlib
import json
import math
from datetime import datetime
from pathlib import Path


def load(path=None):
    return json.loads(Path(path or Path(__file__).with_name('operations.json')).read_text(encoding='utf-8'))


def trust_matches(claims, expected):
    # Input fields are assumed already authenticated by a real OIDC verifier.
    return all(isinstance(claims.get(key), str) and claims[key] == value for key, value in expected.items())


def review_changes(changes):
    findings = []
    for change in changes:
        if change['operation'] == 'delete':
            findings.append((change['resource'], 'DATA_LOSS_REVIEW'))
        elif change['field'] == 'admin_source' and change['after'] == '0.0.0.0/0':
            findings.append((change['resource'], 'PUBLIC_ADMIN_REVIEW'))
        else:
            findings.append((change['resource'], 'CHANGE_REVIEW'))
    return findings


def review_image(image):
    import re
    pinned = re.fullmatch(r'[^\s@]+@sha256:[0-9a-f]{64}', image['reference']) is not None
    return {'pinned': pinned, 'provenance_present': bool(image.get('provenance')),
            'non_root': type(image.get('uid')) is int and image['uid'] > 0,
            'privileged_disabled': image.get('privileged') is False}


def audit_summary(rows, enabled):
    # One fictional provider; account+region+event identity avoids ID collisions.
    seen = {(row['account'], row['region'], row['event_id']) for row in rows}
    covered = {row['category'] for row in rows}
    return len(seen), len(rows) - len(seen), sorted(set(enabled) - covered)


def recovery(exercise):
    parse = lambda value: datetime.fromisoformat(value.replace('Z', '+00:00'))
    backup, incident = parse(exercise['latest_verified_backup']), parse(exercise['incident'])
    started, verified = parse(exercise['recovery_started']), parse(exercise['service_verified'])
    if any(stamp.utcoffset() is None for stamp in (backup, incident, started, verified)):
        raise ValueError('all timestamps require explicit timezone offsets')
    for field in ('rpo_minutes', 'rto_minutes'):
        value = exercise[field]
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError(f'{field} must be a finite nonnegative number')
    if not backup <= incident <= started <= verified:
        raise ValueError('timestamps must satisfy backup <= incident <= recovery_started <= service_verified')
    loss_seconds = (incident - backup).total_seconds()
    duration_seconds = (verified - incident).total_seconds()
    # RTO includes delay before recovery work begins, not only active repair time.
    return loss_seconds / 60, duration_seconds / 60, loss_seconds <= exercise['rpo_minutes'] * 60, duration_seconds <= exercise['rto_minutes'] * 60


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['trust', 'iac', 'image', 'audit', 'restore'])
    parser.add_argument('--input', help='working copy of operations.json')
    args = parser.parse_args()
    data = load(args.input)
    if args.mode == 'trust':
        for row in data['claims']:
            print(f"{row['id']} conditions={'MATCH' if trust_matches(row, data['trust']) else 'DENY'}")
        print('signature_validation=NOT_IMPLEMENTED')
    elif args.mode == 'iac':
        for resource, finding in review_changes(data['changes']):
            print(f'{resource} {finding}')
        print(f"changes={len(data['changes'])} automatic_apply=NO")
    elif args.mode == 'image':
        for row in data['images']:
            results = review_image(row)
            print(f"{row['id']} " + ' '.join(f'{key}={value}' for key, value in results.items()))
        print('signature_and_vulnerability_verification=NOT_IMPLEMENTED')
    elif args.mode == 'audit':
        unique, duplicate, missing = audit_summary(data['audit'], data['enabled_categories'])
        print(f'rows={len(data["audit"])} unique={unique} duplicates={duplicate}')
        print('unobserved_category=' + ','.join(missing))
        print('absence_of_events=NOT_PROOF_OF_NO_ACTIVITY')
    else:
        loss, duration, rpo, rto = recovery(data['recovery'])
        print(f'potential_loss_minutes={loss:g} recovery_minutes={duration:g}')
        backup = Path(__file__).with_name(data['recovery']['backup_file'])
        integrity = hashlib.sha256(backup.read_bytes()).hexdigest() == data['recovery']['backup_sha256']
        print(f'rpo_met={rpo} rto_met={rto} backup_hash_match={integrity}')


if __name__ == '__main__':
    main()
