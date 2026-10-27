"""Offline cryptographic design exercises, NOT a production protocol or PKI.

All keys are public teaching constants. HKDF follows RFC 5869 for observation;
real applications should use reviewed protocol/library implementations.
"""
import argparse
import hashlib
import hmac
import json
from pathlib import Path

TEACHING_KEY = bytes(range(32))


def hkdf(ikm, salt, info, length):
    if not 1 <= length <= 255 * hashlib.sha256().digest_size:
        raise ValueError('length outside HKDF-SHA256 range')
    prk = hmac.digest(salt, ikm, 'sha256')
    previous, result = b'', b''
    for counter in range(1, (length + 31) // 32 + 1):
        previous = hmac.digest(prk, previous + info + bytes([counter]), 'sha256')
        result += previous
    return result[:length]


def encode_fields(fields):
    result = b''
    for field in fields:
        if not isinstance(field, bytes):
            raise TypeError('fields must be bytes')
        result += len(field).to_bytes(4, 'big') + field
    return result


def sign_request(sequence, method, path, body):
    message = encode_fields([b'bifrost-request-v1', str(sequence).encode('ascii'), method, path, body])
    return hmac.digest(TEACHING_KEY, message, 'sha256')


def accept(sequence, method, path, body, tag, last_seen):
    expected = sign_request(sequence, method, path, body)
    if not hmac.compare_digest(tag, expected):
        return 'BAD_TAG', last_seen
    if sequence <= last_seen:
        return 'REPLAY', last_seen
    return 'ACCEPT', sequence


def certificate_metadata(cert, host, date):
    # Not X.509 signature/path/revocation validation. Exact DNS names only.
    return {'name_match': host in cert['dns_names'],
            'time_match': cert['not_before'] <= date <= cert['not_after'],
            'root_in_training_store': cert['root'] in ['Training Root']}


def key_allowed(state, operation):
    return operation in {'active': {'encrypt', 'decrypt'}, 'retired': {'decrypt'}, 'compromised': set(), 'destroyed': set()}.get(state, set())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['lifecycle', 'hkdf', 'certificate', 'replay', 'encoding'])
    parser.add_argument('--input', help='working copy of design-records.json')
    args = parser.parse_args()
    data = json.loads(Path(args.input or Path(__file__).with_name('design-records.json')).read_text(encoding='utf-8'))
    if args.mode == 'lifecycle':
        for key in data['keys']:
            print(f"{key['id']} encrypt={key_allowed(key['state'], 'encrypt')} decrypt={key_allowed(key['state'], 'decrypt')}")
        print('compromise_action=investigate_and_recover')
    elif args.mode == 'hkdf':
        ikm = bytes.fromhex('0b' * 22)
        salt = bytes.fromhex('000102030405060708090a0b0c')
        info = bytes.fromhex('f0f1f2f3f4f5f6f7f8f9')
        result = hkdf(ikm, salt, info, 42)
        expected = bytes.fromhex('3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865')
        print(f'rfc5869_case1={hmac.compare_digest(result, expected)} length={len(result)}')
        print('different_context=' + str(hkdf(ikm, salt, b'client-v1', 32) != hkdf(ikm, salt, b'server-v1', 32)))
    elif args.mode == 'certificate':
        for row in data['certificate_cases']:
            result = certificate_metadata(data['certificate'], row['host'], row['date'])
            print(row['id'] + ' ' + ' '.join(f'{key}={value}' for key, value in result.items()))
        print('x509_validation=NOT_IMPLEMENTED')
    elif args.mode == 'replay':
        tag = sign_request(1, b'POST', b'/notes', b'hello')
        last = 0
        for label, seq, body in [('first', 1, b'hello'), ('repeated', 1, b'hello'), ('changed', 1, b'bye')]:
            decision, last = accept(seq, b'POST', b'/notes', body, tag, last)
            print(f'{label}={decision} last_seen={last}')
        decision, last = accept(2, b'POST', b'/notes', b'hello', sign_request(2, b'POST', b'/notes', b'hello'), last)
        print(f'next={decision} last_seen={last}')
    else:
        left, right = [b'ab', b'c'], [b'a', b'bc']
        print('naive_same=' + str(b''.join(left) == b''.join(right)))
        print('framed_same=' + str(encode_fields(left) == encode_fields(right)))
        mac = lambda fields: hmac.digest(TEACHING_KEY, encode_fields(fields), 'sha256')
        print('framed_tag_same=' + str(hmac.compare_digest(mac(left), mac(right))))


if __name__ == '__main__':
    main()
