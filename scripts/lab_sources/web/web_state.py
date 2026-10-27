"""Offline state/contract exercises. No account service, HTTP listener or email sender."""
import argparse
from dataclasses import dataclass
import hashlib
import hmac
import json
import re
import sqlite3


def update_profile(current, payload, actor):
    if actor != current.get("owner"):
        raise PermissionError("not owner")
    if not isinstance(payload, dict) or not payload or set(payload) - {"display_name", "theme"}:
        raise ValueError("unexpected or empty fields")
    if "display_name" in payload and (not isinstance(payload["display_name"], str)
                                     or not payload["display_name"].strip()
                                     or not 1 <= len(payload["display_name"]) <= 40):
        raise ValueError("invalid display name")
    if "theme" in payload and payload["theme"] not in ("dark", "light"):
        raise ValueError("invalid theme")
    result = dict(current)
    result.update(payload)
    return result


class SessionModel:
    """Single-process transitions only; IDs are public fixtures, never credentials."""
    def __init__(self):
        self.sessions = {"S-OLD": {"user": None, "expires": 100}}

    def rotate_after_verified_login(self, old_id, new_id, user, now):
        old = self.sessions.get(old_id)
        if not old or now >= old["expires"] or new_id in self.sessions:
            raise ValueError("old session invalid or new ID reused")
        if not isinstance(new_id, str) or not new_id or not isinstance(user, str) or not user:
            raise ValueError("new ID and verified user required")
        del self.sessions[old_id]
        self.sessions[new_id] = {"user": user, "expires": now + 50}

    def user_for(self, session_id, now):
        session = self.sessions.get(session_id)
        if not session or now >= session["expires"]:
            return None
        return session["user"]

    def logout(self, session_id):
        self.sessions.pop(session_id, None)


@dataclass
class ResetTicket:
    digest: bytes
    user: str
    purpose: str
    expires: int
    used: bool = False


def fixture_ticket(expires=100):
    return ResetTicket(hashlib.sha256(b"PUBLIC-RESET-TOKEN").digest(), "alice", "reset-password", expires)


def consume_ticket(ticket, token, user, purpose, now):
    if ticket.used or now >= ticket.expires or user != ticket.user or purpose != ticket.purpose:
        return False
    if not isinstance(token, str) or not token.isascii() or not 1 <= len(token) <= 128:
        return False
    supplied = hashlib.sha256(token.encode("ascii")).digest()
    if not hmac.compare_digest(ticket.digest, supplied):
        return False
    ticket.used = True
    return True


def cache_rule(cache_control):
    """Classify a fixed exercise subset; not an RFC-complete cache implementation."""
    directives = {part.strip().lower() for part in cache_control.split(",")}
    if "no-store" in directives:
        return "NO_STORE"
    if "private" in directives:
        return "PRIVATE_ONLY"
    if "no-cache" in directives:
        return "STORE_REVALIDATE"
    if "public" in directives and "max-age=60" in directives:
        return "SHARED_FRESH"
    return "REVIEW"


def cached_profile(cache, user, policy):
    # Deliberately simplified path-only cache illustrates a bad public policy.
    path = "/profile"
    mode = cache_rule(policy)
    if mode == "SHARED_FRESH" and path in cache:
        return cache[path]
    body = "profile:" + user
    if mode == "SHARED_FRESH":
        cache[path] = body
    return body


class Checkout:
    """One fixed product, one SQLite connection; no payments or distributed lock."""
    def __init__(self, stock=3):
        self.db = sqlite3.connect(":memory:", isolation_level=None)
        self.db.executescript("""
            CREATE TABLE inventory (id TEXT PRIMARY KEY, stock INTEGER NOT NULL CHECK(stock >= 0));
            CREATE TABLE orders (user TEXT NOT NULL, request_key TEXT NOT NULL,
                                 quantity INTEGER NOT NULL CHECK(quantity > 0),
                                 PRIMARY KEY(user, request_key));
        """)
        self.db.execute("INSERT INTO inventory VALUES ('kit', ?)", (stock,))

    def reserve(self, user, request_key, quantity, fail_after_update=False):
        if (not isinstance(user, str) or not re.fullmatch(r"[a-z]{1,20}", user)
                or not isinstance(request_key, str) or not re.fullmatch(r"[A-Z0-9-]{1,40}", request_key)
                or type(quantity) is not int or not 1 <= quantity <= 10):
            raise ValueError("invalid reservation contract")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute("SELECT quantity FROM orders WHERE user=? AND request_key=?",
                                       (user, request_key)).fetchone()
            if previous:
                self.db.execute("COMMIT")
                return "REPLAY" if previous[0] == quantity else "CONFLICT"
            changed = self.db.execute("UPDATE inventory SET stock=stock-? WHERE id='kit' AND stock>=?",
                                      (quantity, quantity)).rowcount
            if changed != 1:
                self.db.execute("ROLLBACK")
                return "OUT_OF_STOCK"
            if fail_after_update:
                raise RuntimeError("simulated failure between update and order")
            self.db.execute("INSERT INTO orders VALUES (?, ?, ?)", (user, request_key, quantity))
            self.db.execute("COMMIT")
            return "RESERVED"
        except Exception:
            if self.db.in_transaction:
                self.db.execute("ROLLBACK")
            raise

    def stock(self):
        return self.db.execute("SELECT stock FROM inventory WHERE id='kit'").fetchone()[0]

    def close(self):
        self.db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("contract", "sessions", "reset", "cache", "checkout"))
    args = parser.parse_args(argv)
    if args.mode == "contract":
        profile = {"owner": "alice", "display_name": "Loki", "role": "learner", "theme": "dark"}
        changed = update_profile(profile, {"display_name": "Freya"}, "alice")
        print("normal_name=" + changed["display_name"])
        try:
            update_profile(profile, {"role": "admin"}, "alice")
        except ValueError:
            print("role_assignment=REJECT")
        print("original_role=" + profile["role"])
        print("original_name=" + profile["display_name"])
    elif args.mode == "sessions":
        model = SessionModel()
        model.rotate_after_verified_login("S-OLD", "S-NEW", "alice", now=90)
        print("old_after_rotate=" + str(model.user_for("S-OLD", 91)))
        print("new_after_rotate=" + str(model.user_for("S-NEW", 91)))
        expiry_model = SessionModel()
        expiry_model.rotate_after_verified_login("S-OLD", "S-NEW", "alice", now=90)
        print("at_expiry=" + str(expiry_model.user_for("S-NEW", 140)))
        model.logout("S-NEW")
        print("after_logout=" + str(model.user_for("S-NEW", 92)))
    elif args.mode == "reset":
        ticket = fixture_ticket()
        allowed = consume_ticket(ticket, "PUBLIC-RESET-TOKEN", "alice", "reset-password", 90)
        replay = consume_ticket(ticket, "PUBLIC-RESET-TOKEN", "alice", "reset-password", 91)
        wrong_user = consume_ticket(fixture_ticket(), "PUBLIC-RESET-TOKEN", "bob", "reset-password", 90)
        expired = consume_ticket(fixture_ticket(), "PUBLIC-RESET-TOKEN", "alice", "reset-password", 100)
        wrong_purpose = consume_ticket(fixture_ticket(), "PUBLIC-RESET-TOKEN", "alice", "email-change", 90)
        for label, result in (("valid", allowed), ("replay", replay), ("wrong_user", wrong_user),
                              ("expired", expired), ("wrong_purpose", wrong_purpose)):
            print(label + "=" + ("ACCEPT" if result else "REJECT"))
    elif args.mode == "cache":
        shared = {}
        print("public_alice=" + cached_profile(shared, "alice", "public, max-age=60"))
        print("public_bob=" + cached_profile(shared, "bob", "public, max-age=60"))
        private = {}
        cached_profile(private, "alice", "no-store")
        print("no_store_bob=" + cached_profile(private, "bob", "no-store"))
        print("no_cache=" + cache_rule("no-cache"))
        print("private=" + cache_rule("private, max-age=60"))
    else:
        shop = Checkout()
        try:
            for label, user, key, qty in (("first", "alice", "REQ-1", 2), ("repeat", "alice", "REQ-1", 2),
                                          ("changed", "alice", "REQ-1", 1), ("other", "bob", "REQ-2", 2)):
                print(f"{label}={shop.reserve(user,key,qty)} stock={shop.stock()}")
            try:
                shop.reserve("bob", "REQ-3", 1, fail_after_update=True)
            except RuntimeError:
                print("rollback_stock=" + str(shop.stock()))
        finally:
            shop.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
