"""Small, intentionally limited parser for the supplied Ethernet/IPv4/TCP TLS fixture.

No connection, key log or decryption. It reassembles the two ordered streams in
this original fixture; it is not a general packet analyzer or retransmit engine.
"""
from pathlib import Path
import struct
import sys


def pcap_frames(data):
    if len(data) < 24 or struct.unpack("<IHHIIII", data[:24]) != (0xa1b2c3d4, 2, 4, 0, 0, 65535, 1):
        raise ValueError("expected this fixture's little-endian Ethernet PCAP")
    offset = 24
    while offset < len(data):
        if offset + 16 > len(data):
            raise ValueError("truncated PCAP packet header")
        _, _, size, original = struct.unpack("<IIII", data[offset:offset + 16])
        offset += 16
        if size != original or offset + size > len(data):
            raise ValueError("truncated PCAP packet")
        yield data[offset:offset + size]
        offset += size


def tls_records(data):
    offset = 0
    while offset < len(data):
        if offset + 5 > len(data):
            raise ValueError("truncated TLS record header")
        kind, version, length = struct.unpack("!BHH", data[offset:offset + 5])
        if offset + 5 + length > len(data):
            raise ValueError("truncated TLS record body")
        yield kind, version, data[offset + 5:offset + 5 + length]
        offset += 5 + length


def hello_extensions(body, server=False):
    # legacy_version(2), random(32), session_id length(1) and session_id
    offset = 35 + body[34]
    if server:
        offset += 3  # selected cipher suite(2), legacy compression(1)
    else:
        size = int.from_bytes(body[offset:offset + 2], "big")
        offset += 2 + size
        offset += 1 + body[offset]  # legacy compression methods
    end = offset + 2 + int.from_bytes(body[offset:offset + 2], "big")
    offset += 2
    if end != len(body):
        raise ValueError("inconsistent hello extensions")
    extensions = {}
    while offset < end:
        kind, size = struct.unpack("!HH", body[offset:offset + 4])
        offset += 4
        if offset + size > end:
            raise ValueError("truncated hello extension")
        extensions[kind] = body[offset:offset + size]
        offset += size
    return extensions


def summarize(path):
    frames = list(pcap_frames(path.read_bytes()))
    streams = {"client": bytearray(), "server": bytearray()}
    for frame in frames:
        if len(frame) < 54 or frame[12:14] != b"\x08\x00" or frame[23] != 6:
            raise ValueError("expected Ethernet/IPv4/TCP fixture packets")
        ip_size = (frame[14] & 15) * 4
        tcp_start = 14 + ip_size
        tcp_size = (frame[tcp_start + 12] >> 4) * 4
        source_port, destination_port = struct.unpack("!HH", frame[tcp_start:tcp_start + 4])
        if 443 not in (source_port, destination_port):
            raise ValueError("expected HTTPS port 443")
        direction = "server" if source_port == 443 else "client"
        streams[direction].extend(frame[tcp_start + tcp_size:])
    hellos = {}
    encrypted = 0
    for direction, stream in streams.items():
        for kind, _, payload in tls_records(stream):
            if kind == 23:
                encrypted += 1
            elif kind == 22:
                offset = 0
                while offset < len(payload):
                    message_type = payload[offset]
                    length = int.from_bytes(payload[offset + 1:offset + 4], "big")
                    body = payload[offset + 4:offset + 4 + length]
                    if len(body) != length:
                        raise ValueError("truncated handshake")
                    if message_type in (1, 2):
                        hellos[message_type] = hello_extensions(body, server=message_type == 2)
                    offset += 4 + length
    if set(hellos) != {1, 2}:
        raise ValueError("ClientHello and ServerHello are required")
    client, server = hellos[1], hellos[2]
    sni = client[0]
    if sni[2] != 0 or len(sni) != 5 + int.from_bytes(sni[3:5], "big"):
        raise ValueError("expected one host_name SNI")
    hostname = sni[5:].decode("ascii")
    if server[43] != b"\x03\x04":
        raise ValueError("ServerHello did not select TLS 1.3")
    if b"\x03\x04" not in client[43][1:]:
        raise ValueError("ClientHello did not offer TLS 1.3")
    visible = any(b"GET /lesson" in stream or b"HTTP/1.1 200" in stream for stream in streams.values())
    return [f"frames={len(frames)}", "client_hello=1 server_hello=1", f"sni={hostname}",
            "negotiated=TLS1.3", f"encrypted_records={encrypted}", f"plaintext_http_visible={visible}"]


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("tls13.pcap")
    try:
        for line in summarize(path):
            print(line)
    except (OSError, ValueError, IndexError, KeyError, struct.error, UnicodeError) as error:
        print("INVALID fixture:", error)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
