import base64
import hashlib
import hmac
import sys
mode = sys.argv[1] if len(sys.argv) > 1 else "representation"
data = b"Bifrost"
if mode == "representation":
    print(data.hex())
    print(base64.b64encode(data).decode())
    print(base64.b64decode("Qmlmcm9zdA==").decode())
elif mode == "modular":
    print(17 % 5, pow(3, -1, 26))
elif mode == "classical":
    text = "BIFROST"
    cipher = "".join(chr((ord(c) - 65 + 3) % 26 + 65) for c in text)
    print(cipher)
    print("".join(chr((ord(c) - 65 - 3) % 26 + 65) for c in cipher))
elif mode == "hash":
    a, b = hashlib.sha256(data).digest(), hashlib.sha256(data + b"!").digest()
    print("same=", a == b)
    print("hex_length=", len(a.hex()))
elif mode == "mac":
    key = b"DEMO-KEY-NOT-FOR-PRODUCTION"
    tag = hmac.digest(key, data, "sha256")
    print("original=", hmac.compare_digest(tag, hmac.digest(key, data, "sha256")))
    print("changed=", hmac.compare_digest(tag, hmac.digest(key, data + b"!", "sha256")))
elif mode == "nonce":
    # Toy XOR demonstration of stream reuse, NOT a cipher to deploy.
    a, b, stream = b"YES", b"NO!", bytes([31, 22, 9])
    xor = lambda x, y: bytes(i ^ j for i, j in zip(x, y))
    print(xor(xor(a, stream), xor(b, stream)) == xor(a, b))
elif mode == "password":
    # Fixed teaching salts; real systems need a fresh random salt per password.
    derive = lambda salt: hashlib.scrypt(b"demo-password", salt=salt, n=16384, r=8, p=1, dklen=32)
    print("same_salt=", derive(b"teaching-salt-A") == derive(b"teaching-salt-A"))
    print("other_salt=", derive(b"teaching-salt-A") == derive(b"teaching-salt-B"))
else:
    raise SystemExit("mode: representation modular classical hash mac nonce password")
