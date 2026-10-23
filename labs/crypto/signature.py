"""Ed25519 signs and verifies bytes; it does not encrypt the message."""
from pathlib import Path
import base64
import json
import sys

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
except ImportError:
    raise SystemExit("Optional package missing. In a virtual environment run: python -m pip install -r requirements.txt")


def verify(public_key, signature, message):
    try:
        public_key.verify(signature, message)
    except InvalidSignature:
        return False
    return True


def main():
    fixture = json.loads(Path(__file__).with_name("signature.json").read_text(encoding="utf-8"))
    key = Ed25519PublicKey.from_public_bytes(base64.b64decode(fixture["public_key_base64"], validate=True))
    signature = base64.b64decode(fixture["signature_base64"], validate=True)
    message = fixture["message_utf8"].encode()
    altered = bytes([signature[0] ^ 1]) + signature[1:]
    cases = {
        "original": (key, signature, message),
        "tampered_message": (key, signature, message + b"!"),
        "tampered_signature": (key, altered, message),
        "wrong_key": (Ed25519PrivateKey.generate().public_key(), signature, message),
    }
    for label, args in cases.items():
        print(label + ("=VALID" if verify(*args) else "=INVALID"))
    fresh_private = Ed25519PrivateKey.generate()
    fresh_signature = fresh_private.sign(message)
    print("fresh_round_trip=" + str(verify(fresh_private.public_key(), fresh_signature, message)))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print("fixture=INVALID reason=" + type(error).__name__)
        raise SystemExit(2)
