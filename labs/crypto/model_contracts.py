"""Authored input contracts for the three advanced offline models."""
from lab_input import InputError, validate

S, I, B, N = str, int, bool, (int, float)
CLOUD = {
    '?description': S, 'identity_allow': [S], 'boundary_allow': [S],
    'permission_requests': [{'id': S, 'action': S, '?explicit_deny': B, '?resource_policy_grant': B}],
    'role': {'name': S, 'namespace': S, 'rules': [{'api_group': S, 'resource': S, 'verbs': [S]}]},
    'binding': {'namespace': S, 'role': S, 'subject': {'namespace': S, 'name': S}},
    'rbac_requests': [{'id': S, 'namespace': S, 'subject_namespace': S, 'subject_name': S,
                       'api_group': S, 'resource': S, 'verb': S}],
    'metadata_options': {'endpoint_enabled': B, 'tokens_required': B},
    'instance_role_actions': [S], 'metadata_requests': [{'id': S, 'network_reachable': B, '?token_valid': B}],
    'private_requests': [{'id': S, 'dns_target': S, 'network_path': B, 'endpoint_policy': B, 'identity_permission': B}],
    'lease': {'actor': S, 'resource': S, 'actions': [S], 'approved_by': S, 'start': S, 'expires': S, 'revoked': B},
    'lease_requests': [{'id': S, 'actor': S, 'resource': S, 'action': S, 'at': S}]}
SEGMENT = {'offset': I, 'hex': S}
NETWORK = {
    '?description': S, 'family_rules': [{'network': S, 'port': I}],
    'family_requests': [{'id': S, 'destination': S, 'port': I, '?interface': S}],
    'stream': {'length': I, 'complete': [SEGMENT], 'gap': [SEGMENT], 'conflict': [SEGMENT]},
    'dns_records': [{'name': S, 'qtype': S, 'status': S, 'received': N, '?ttl': N,
                     '?answer': S, '?soa_ttl': N, '?soa_minimum': N}],
    'queries': [{'id': S, 'name': S, 'qtype': S, 'now': N}],
    'mtu': {'version': I, 'packet_bytes': I, 'path_mtu': I},
    'lateness': N, 'timeout': N, 'events': [{'id': S, 'event_time': N}]}
CRYPTO = {
    '?description': S, 'record': {'dek_hex': S, 'nonce_hex': S, 'ciphertext_hex': S},
    'wrapping': {'old_kek_hex': S, 'new_kek_hex': S, 'wrapped_dek_hex': S},
    'password_record': {'format_version': I, 'algorithm': S, 'iterations': I, 'salt_hex': S, 'verifier_hex': S},
    'signing_seed_hex': S, 'reviewer_actions': [S], 'sample_bytes': [I]}


def check(data, kind):
    validate(data, {'cloud': CLOUD, 'network': NETWORK, 'crypto': CRYPTO}[kind])
    if kind == 'network':
        for i, row in enumerate(data['dns_records']):
            if row['status'] not in ('POSITIVE', 'NXDOMAIN', 'NODATA'):
                raise InputError(f'$.dns_records[{i}].status: expected POSITIVE/NXDOMAIN/NODATA')
            required = ('ttl', 'answer') if row['status'] == 'POSITIVE' else ('soa_ttl', 'soa_minimum')
            for key in required:
                if key not in row:
                    raise InputError(f'$.dns_records[{i}].{key}: required for {row["status"]}')
                if key != 'answer' and row[key] < 0:
                    raise InputError(f'$.dns_records[{i}].{key}: must be nonnegative')
    if kind == 'crypto' and (not data['sample_bytes'] or any(not 0 <= n <= 255 for n in data['sample_bytes'])
                            or not any(n < 250 for n in data['sample_bytes'])):
        raise InputError('$.sample_bytes: need byte values and a value below 250 for this exercise')
    return data
