"""Local cryptographic record exercises. Not a service, protocol, or credential store.

All fixture keys and passwords are PUBLIC training data. Optional cryptography
is only needed by aad/envelope/context; migration and sampling use the stdlib.
"""
import argparse
from lab_input import read_json
from model_contracts import check
import hashlib
import hmac
import json
from pathlib import Path
import secrets


def load(path=None):
    return check(read_json(path or Path(__file__).with_name('round2-crypto.json')), 'crypto')


def optional_crypto():
    try:
        from cryptography.exceptions import InvalidTag, InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap, InvalidUnwrap
    except ImportError:
        raise SystemExit('Optional package missing. In a virtual environment run: python -m pip install -r requirements.txt')
    return InvalidTag, InvalidSignature, Ed25519PrivateKey, AESGCM, aes_key_wrap, aes_key_unwrap, InvalidUnwrap


def record_aad(tenant, document, version):
    if not all(isinstance(value, str) and value for value in (tenant, document, version)):
        raise ValueError('nonempty string identifiers required')
    return json.dumps(['bifrost-record-v1', tenant, document, version], ensure_ascii=True, separators=(',', ':')).encode('ascii')


def decrypt_record(fixture, tenant, document, version):
    _, _, _, AESGCM, _, _, _ = optional_crypto()
    return AESGCM(bytes.fromhex(fixture['dek_hex'])).decrypt(bytes.fromhex(fixture['nonce_hex']),
        bytes.fromhex(fixture['ciphertext_hex']), record_aad(tenant, document, version))


def verifier(password, salt, iterations=2000):
    # Tiny iteration costs are deliberately cheap teaching values, NOT guidance.
    if type(iterations) is not int or not 1 <= iterations <= 100000:
        raise ValueError('teaching iteration range is 1..100000')
    if not isinstance(salt, bytes) or len(salt) != 16:
        raise ValueError('fixture salt must be 16 bytes')
    return dict(format_version=1, algorithm='pbkdf2-sha256', iterations=iterations,
                salt_hex=salt.hex(), verifier_hex=hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32).hex())


def verify_and_plan(password, record, target_iterations=2000):
    if type(record['format_version']) is not int or record['format_version'] != 1 or record['algorithm'] != 'pbkdf2-sha256':
        raise ValueError('unsupported verifier format/algorithm')
    if type(target_iterations) is not int or not 1 <= target_iterations <= 100000:
        raise ValueError('target teaching iteration range is 1..100000')
    calculated = verifier(password, bytes.fromhex(record['salt_hex']), record['iterations'])
    saved = bytes.fromhex(record['verifier_hex'])
    if len(saved) != 32:
        raise ValueError('invalid verifier length')
    valid = hmac.compare_digest(bytes.fromhex(calculated['verifier_hex']), saved)
    # Never rehash an unverified candidate; never downgrade a stronger cost.
    return valid, valid and record['iterations'] < target_iterations


def rejection_sample(draw_byte, bound=10, max_draws=1024):
    if type(bound) is not int or not 1 <= bound <= 256:
        raise ValueError('byte demonstration bound must be 1..256')
    ceiling = 256 - 256 % bound
    for rejected in range(max_draws):
        value = draw_byte()
        if type(value) is not int or not 0 <= value < 256:
            raise ValueError('source must return a byte')
        if value < ceiling:
            return value % bound, rejected
    raise ValueError('demonstration source did not yield an acceptable byte')


def signed_claim(context, action, resource):
    return json.dumps(['bifrost-approval-v1', context, action, resource], separators=(',', ':')).encode('ascii')


def rewrap_envelope(envelope, old_kek, new_kek, new_key_id):
    """Return a new envelope while leaving the authenticated payload untouched.

    A real service must authorize key use and protect its trusted key-ID mapping.
    AES-KW authenticates the wrapped key, not this surrounding JSON metadata.
    """
    if not isinstance(new_key_id, str) or not new_key_id:
        raise ValueError('nonempty new key ID required')
    *_, wrap, unwrap, _ = optional_crypto()
    dek = unwrap(old_kek, bytes.fromhex(envelope['wrapped_dek_hex']))
    return {**envelope, 'wrapped_dek_hex': wrap(new_kek, dek).hex(), 'kek_id': new_key_id}


def semantic_authorization(verified, claim, request, allowed_actions):
    return (verified is True and all(isinstance(claim.get(key), str) and bool(claim[key])
            and claim.get(key) == request.get(key) for key in ('context', 'action', 'resource'))
            and request['action'] in allowed_actions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['aad', 'migration', 'envelope', 'context', 'sampling'])
    parser.add_argument('--input')
    args = parser.parse_args()
    data = load(args.input)
    if args.mode == 'aad':
        InvalidTag, *_ = optional_crypto()
        row = data['record']
        for label, tenant, document, version in [('original', 'blue', '17', '1'), ('other_record', 'blue', '18', '1'), ('other_tenant', 'red', '17', '1')]:
            try:
                plaintext = decrypt_record(row, tenant, document, version)
            except InvalidTag:
                print(f'{label}=REJECT plaintext_released=False')
            else:
                print(f'{label}=ACCEPT plaintext={plaintext.decode("utf-8")}')
    elif args.mode == 'migration':
        row = data['password_record']
        for label, candidate in [('wrong', 'not-the-password'), ('correct', 'training-pass')]:
            valid, needs = verify_and_plan(candidate, row)
            print(f'{label} valid={valid} needs_rehash={needs}')
        valid, needs = verify_and_plan('training-pass', row)
        if valid and needs:
            updated = verifier('training-pass', secrets.token_bytes(16))
            print(f'updated_valid={verify_and_plan("training-pass", updated)[0]} iterations={updated["iterations"]} needs_rehash={verify_and_plan("training-pass", updated)[1]}')
    elif args.mode == 'envelope':
        _, _, _, AESGCM, wrap, unwrap, InvalidUnwrap = optional_crypto()
        row, keys = data['record'], data['wrapping']
        old_kek, new_kek = bytes.fromhex(keys['old_kek_hex']), bytes.fromhex(keys['new_kek_hex'])
        original_wrap = bytes.fromhex(keys['wrapped_dek_hex'])
        dek = unwrap(old_kek, original_wrap)
        envelope = dict(ciphertext_hex=row['ciphertext_hex'], nonce_hex=row['nonce_hex'],
                        wrapped_dek_hex=keys['wrapped_dek_hex'], kek_id='kek-v1')
        rotated = rewrap_envelope(envelope, old_kek, new_kek, 'kek-v2')
        new_wrap = bytes.fromhex(rotated['wrapped_dek_hex'])
        print(f'unwrap_matches={hmac.compare_digest(dek, bytes.fromhex(row["dek_hex"]))}')
        ciphertext_before = bytes.fromhex(row['ciphertext_hex'])
        print(f'rewrapped_different={new_wrap != original_wrap} ciphertext_unchanged={bytes.fromhex(rotated["ciphertext_hex"]) == ciphertext_before}')
        recovered = AESGCM(unwrap(new_kek, new_wrap)).decrypt(bytes.fromhex(rotated['nonce_hex']), bytes.fromhex(rotated['ciphertext_hex']), record_aad('blue', '17', '1'))
        print('rotated_decrypt=' + recovered.decode('utf-8'))
        try:
            unwrap(old_kek, new_wrap)
        except InvalidUnwrap:
            print('old_kek_for_new_wrap=REJECT')
        else:
            raise AssertionError('old KEK unexpectedly unwrapped the new envelope')
    elif args.mode == 'context':
        _, InvalidSignature, Private, *_ = optional_crypto()
        key = Private.from_private_bytes(bytes.fromhex(data['signing_seed_hex']))
        message = signed_claim('review', 'approve', 'note-17')
        signature = key.sign(message)
        key.public_key().verify(signature, message)
        print('signature=VALID claimed_action=approve')
        claim = dict(context='review', action='approve', resource='note-17')
        request = dict(context='review', action='publish', resource='note-17')
        allowed = semantic_authorization(True, claim, request, data['reviewer_actions'])
        print(f'requested_action=publish authorized={allowed}')
        print('approved_request_authorized=' + str(semantic_authorization(True, claim, claim, data['reviewer_actions'])))
        try:
            key.public_key().verify(signature, signed_claim('deploy', 'approve', 'note-17'))
        except InvalidSignature:
            print('changed_context=INVALID')
        else:
            raise AssertionError('context alteration unexpectedly verified')
    else:
        counts = [sum(value % 10 == residue for value in range(256)) for residue in range(10)]
        stream = iter(data['sample_bytes'])
        selected, rejected = rejection_sample(lambda: next(stream))
        print('modulo_counts=' + ','.join(map(str, counts)))
        print(f'rejected={rejected} selected={selected}')
        sample = secrets.randbelow(10)
        print(f'fresh_sample_in_range={0 <= sample < 10}')


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print("INVALID input: " + str(error), file=__import__("sys").stderr)
        raise SystemExit(2)
