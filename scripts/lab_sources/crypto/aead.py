"""Real AES-GCM authentication observations; published fixture keys are teaching data."""
from pathlib import Path
import base64
import json
import os
import sys

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    raise SystemExit("Optional package missing. In a virtual environment run: python -m pip install -r requirements.txt")


def flip(data):
    return bytes([data[0] ^ 1]) + data[1:]


def read_fixture():
    root = Path(__file__).parent
    envelope = json.loads((root / "envelope.json").read_text(encoding="utf-8"))
    teaching = json.loads((root / "teaching-key.json").read_text(encoding="utf-8"))
    decode = lambda name: base64.b64decode(envelope[name], validate=True)
    return (bytes.fromhex(teaching["key_hex"]), decode("nonce_base64"),
            decode("ciphertext_base64") + decode("tag_base64"), envelope["aad_utf8"].encode())


def main():
    key, nonce, ciphertext_and_tag, aad = read_fixture()
    plaintext = AESGCM(key).decrypt(nonce, ciphertext_and_tag, aad)
    print("original=ACCEPT message=" + plaintext.decode())
    cases = {
        "tampered_ciphertext": (key, nonce, flip(ciphertext_and_tag), aad),
        "tampered_tag": (key, nonce, ciphertext_and_tag[:-1] + bytes([ciphertext_and_tag[-1] ^ 1]), aad),
        "changed_aad": (key, nonce, ciphertext_and_tag, aad + b"!"),
        "changed_nonce": (key, flip(nonce), ciphertext_and_tag, aad),
        "wrong_key": (flip(key), nonce, ciphertext_and_tag, aad),
    }
    for label, (candidate_key, candidate_nonce, candidate_data, candidate_aad) in cases.items():
        try:
            AESGCM(candidate_key).decrypt(candidate_nonce, candidate_data, candidate_aad)
        except InvalidTag:
            print(label + "=REJECT")
        else:
            raise AssertionError(label + " unexpectedly accepted")
    # Fresh random values for each new encryption; do not encrypt a changed
    # message with the published fixed fixture key/nonce pair.
    fresh_key = AESGCM.generate_key(bit_length=256)
    fresh_nonce = os.urandom(12)
    encrypted = AESGCM(fresh_key).encrypt(fresh_nonce, plaintext, aad)
    print("fresh_round_trip=" + str(AESGCM(fresh_key).decrypt(fresh_nonce, encrypted, aad) == plaintext))


if __name__ == "__main__":
    try:
        main()
    except InvalidTag:
        print("fixture=REJECT reason=authentication_failed")
        raise SystemExit(2)
    except (OSError, ValueError, KeyError) as error:
        print("fixture=INVALID reason=" + type(error).__name__)
        raise SystemExit(2)
