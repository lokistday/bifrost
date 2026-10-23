"""Author original crypto fixtures and a real, entirely in-memory TLS 1.3 exchange.

Run explicitly when authoring a new fixture, not as part of the deterministic
site build. The TLS implementation chooses fresh handshake randomness, so a
refresh intentionally changes the frozen transcript. No sockets are opened.
Requires the optional package in scripts/lab_sources/crypto/requirements.txt.
"""
from pathlib import Path
from datetime import datetime, timezone
import base64
import json
import ssl
import tempfile

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/lab_sources/crypto"
FROZEN = ROOT / "content/lab-fixtures"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def crypto_fixtures():
    # Public, fixed teaching data used for exactly one frozen encryption.
    key, nonce = bytes(range(32)), bytes(range(12))
    message, aad = b"Bifrost lesson 17", b"record-id=17"
    encrypted = AESGCM(key).encrypt(nonce, message, aad)
    encode = lambda data: base64.b64encode(data).decode("ascii")
    write_json(SOURCE / "envelope.json", {
        "provenance": "Bifrost original, real AES-256-GCM output; fixed public training key/nonce, one message only.",
        "algorithm": "AES-256-GCM", "key_id": "PUBLIC-TEACHING-KEY-DO-NOT-USE",
        "nonce_base64": encode(nonce), "ciphertext_base64": encode(encrypted[:-16]),
        "tag_base64": encode(encrypted[-16:]), "aad_utf8": aad.decode(),
    })
    write_json(SOURCE / "teaching-key.json", {
        "warning": "Public synthetic teaching key, NOT a secret. Never use for real data or re-encrypt another message with its fixed nonce.",
        "key_hex": key.hex(),
    })
    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    write_json(SOURCE / "signature.json", {
        "provenance": "Bifrost original Ed25519 signature; public deterministic teaching seed bytes(range(32)), not a real identity.",
        "algorithm": "Ed25519", "message_utf8": message.decode(),
        "public_key_base64": encode(private_key.public_key().public_bytes_raw()),
        "signature_base64": encode(private_key.sign(message)),
    })


def tls_fixture():
    key = ec.generate_private_key(ec.SECP256R1())
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "bifrost.test")])
    cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
            .public_key(key.public_key()).serial_number(1701)
            .not_valid_before(datetime(2026, 1, 1, tzinfo=timezone.utc))
            .not_valid_after(datetime(2036, 1, 1, tzinfo=timezone.utc))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("bifrost.test")]), critical=False)
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                key_encipherment=False, data_encipherment=False, key_agreement=False,
                key_cert_sign=True, crl_sign=True, encipher_only=None, decipher_only=None), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .sign(key, hashes.SHA256()))
    certificate = cert.public_bytes(serialization.Encoding.PEM).decode("ascii")
    request = b"GET /lesson HTTP/1.1\r\nHost: bifrost.test\r\n\r\n"
    response = b"HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\nBifrost\n"
    chunks = []
    with tempfile.TemporaryDirectory(prefix="bifrost-memory-tls-") as name:
        folder = Path(name)
        cert_path, key_path, log_path = folder / "cert.pem", folder / "key.pem", folder / "fixture.keys"
        cert_path.write_text(certificate, encoding="ascii")
        key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(cert_path, key_path)
        server_context.minimum_version = server_context.maximum_version = ssl.TLSVersion.TLSv1_3
        server_context.num_tickets = 0
        client_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        client_context.minimum_version = client_context.maximum_version = ssl.TLSVersion.TLSv1_3
        client_context.load_verify_locations(cadata=certificate)
        client_context.keylog_filename = str(log_path)
        ci, co, si, so = [ssl.MemoryBIO() for _ in range(4)]
        client = client_context.wrap_bio(ci, co, server_side=False, server_hostname="bifrost.test")
        server = server_context.wrap_bio(si, so, server_side=True)

        def transfer(source, destination, direction, stage):
            data = source.read()
            if data:
                chunks.append({"direction": direction, "stage": stage, "hex": data.hex()})
                destination.write(data)

        completed = {"client": False, "server": False}
        for _ in range(10):
            for label, peer, outgoing, incoming, direction in (
                ("client", client, co, si, "client_to_server"),
                ("server", server, so, ci, "server_to_client")):
                if not completed[label]:
                    try:
                        peer.do_handshake()
                        completed[label] = True
                    except ssl.SSLWantReadError:
                        pass
                transfer(outgoing, incoming, direction, "handshake")
            if all(completed.values()):
                break
        if not all(completed.values()):
            raise RuntimeError("memory handshake did not finish")
        assert client.version() == server.version() == "TLSv1.3"
        cipher_name = client.cipher()[0]
        client.write(request)
        transfer(co, si, "client_to_server", "http_request")
        assert server.read() == request
        server.write(response)
        transfer(so, ci, "server_to_client", "http_response")
        assert client.read() == response
        try:
            client.unwrap()
        except ssl.SSLWantReadError:
            pass
        transfer(co, si, "client_to_server", "close_notify")
        server.unwrap()
        transfer(so, ci, "server_to_client", "close_notify")
        client.unwrap()
        write_json(FROZEN / "tls13.json", {
            "provenance": "Original Bifrost fixture: Python ssl.MemoryBIO / OpenSSL, TLS 1.3 handshake and encrypted HTTP, no sockets or personal network capture. Ethernet/IP/TCP headers and timestamps are synthetic.",
            "generated_by": "scripts/refresh_lab_fixtures.py", "openssl": ssl.OPENSSL_VERSION,
            "cipher": cipher_name,
            "hostname": "bifrost.test", "request_ascii": request.decode("ascii"),
            "response_ascii": response.decode("ascii"), "certificate_pem": certificate,
            "keylog": log_path.read_text(encoding="ascii"), "chunks": chunks,
        })
        # SSLContext holds the key-log handle open on Windows.
        client_context.keylog_filename = None


if __name__ == "__main__":
    crypto_fixtures()
    tls_fixture()
    print("Refreshed frozen original teaching fixtures. Run build_labs.py and lab tests next.")
