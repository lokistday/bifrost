"""Pure offline policy models, not a web server or a production security library."""
import argparse
import hmac
from pathlib import Path
import re
from urllib.parse import urlsplit

SITE = "https://learn.example.invalid"
TOKEN = "public-teaching-token"  # Public fixture only; never a production token.


def allow_change(method, session, token, origin):
    return (method == "POST" and session == "alice" and origin == SITE
            and isinstance(token, str) and token.isascii()
            and hmac.compare_digest(token, TOKEN))


def cors_headers(origin):
    # An exact serialized-Origin allowlist for this one exercise.
    if origin == SITE:
        return {"Access-Control-Allow-Origin": SITE,
                "Access-Control-Allow-Credentials": "true", "Vary": "Origin"}
    return {}


def review_csp(header_name, policy):
    # Tiny checklist for a fixed exercise, NOT a CSP parser or enforcement engine.
    parts = [part.strip() for part in policy.split(";") if part.strip()]
    required = {"default-src 'self'", "script-src 'self'", "object-src 'none'",
                "base-uri 'none'", "frame-ancestors 'none'"}
    if header_name != "Content-Security-Policy":
        return "REPORT_ONLY"
    return "CHECKLIST_PASS" if required <= set(parts) and "'unsafe-inline'" not in policy else "REVIEW"


def choose_file(root, name):
    # Reject path syntax up front; no URL decoding or file opening takes place.
    # The directory must be controlled by the application, not a concurrent writer.
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.txt", name):
        raise ValueError("only a single .txt filename is allowed")
    root = Path(root).resolve()
    target = (root / name).resolve()
    if not target.is_relative_to(root):
        raise ValueError("outside root")
    return target


def allowed_fetch(url):
    # URL syntax allowlist only. Never resolves DNS or sends an HTTP request.
    if not isinstance(url, str) or any(ord(c) <= 32 or ord(c) == 127 for c in url):
        return False
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https" and parsed.hostname == "assets.example.invalid"
                and parsed.port in (None, 443) and parsed.username is None
                and parsed.password is None and parsed.path in ("/guide.txt", "/diagram.png")
                and not parsed.query and not parsed.fragment)
    except ValueError:
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("csrf", "cors", "csp", "files", "ssrf"))
    args = parser.parse_args(argv)
    if args.mode == "csrf":
        cases = [("valid", "POST", "alice", TOKEN, SITE),
                 ("no-token", "POST", "alice", "", SITE),
                 ("foreign", "POST", "alice", TOKEN, "https://other.example.invalid"),
                 ("get-change", "GET", "alice", TOKEN, SITE)]
        for label, *values in cases:
            print(f"{label}={'ALLOW' if allow_change(*values) else 'DENY'}")
    elif args.mode == "cors":
        for label, origin in (("allowed", SITE), ("foreign", "https://other.example.invalid"),
                              ("suffix", SITE + ".attacker.invalid"), ("null", "null")):
            print(f"{label}={'EXPOSE' if cors_headers(origin) else 'NO_CORS_HEADERS'}")
        print("authorization=SEPARATE_CHECK")
    elif args.mode == "csp":
        base = "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        print("enforced=" + review_csp("Content-Security-Policy", base))
        print("report-only=" + review_csp("Content-Security-Policy-Report-Only", base))
        print("inline=" + review_csp("Content-Security-Policy", base.replace("script-src 'self'", "script-src 'self' 'unsafe-inline'")))
        print("browser_enforcement=NOT_TESTED")
    elif args.mode == "files":
        for name in ("note.txt", "../private.txt", "nested/note.txt", "note.txt.exe", "%2e%2e.txt"):
            try:
                choose_file(Path(__file__).parent, name)
                result = "ALLOW_NAME"
            except ValueError:
                result = "DENY"
            print(f"{name}={result}")
    else:
        for label, url in (("allowed", "https://assets.example.invalid/guide.txt"),
                           ("loopback", "http://127.0.0.1/"),
                           ("userinfo", "https://assets.example.invalid@other.invalid/guide.txt"),
                           ("redirect-param", "https://assets.example.invalid/guide.txt?next=http://127.0.0.1")):
            print(f"{label}={'ALLOW_SYNTAX' if allowed_fetch(url) else 'DENY'}")
        print("network_requests=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
