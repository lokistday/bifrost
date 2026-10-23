"""Offline models, not a server or a production authentication system."""
import html
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (id INTEGER, name TEXT)")
db.executemany("INSERT INTO users VALUES (?, ?)", [(1, "alice"), (2, "bob")])
payload = "' OR 1=1 --"
unsafe = db.execute("SELECT name FROM users WHERE name = '" + payload + "'").fetchall()
safe = db.execute("SELECT name FROM users WHERE name = ?", (payload,)).fetchall()
print(f"unsafe_rows={len(unsafe)} safe_rows={len(safe)}")
print("alice_rows=" + str(len(db.execute("SELECT name FROM users WHERE name = ?", ("alice",)).fetchall())))
print(html.escape('<b>hello</b>'))
def can_read(user, owner):
    return (isinstance(user, str) and bool(user.strip())
            and isinstance(owner, str) and bool(owner.strip())
            and user == owner)
print(f"own={can_read('alice', 'alice')} other={can_read('alice', 'bob')}")
assert len(unsafe) == 2 and len(safe) == 0
assert can_read("alice", "alice") and not can_read("alice", "bob")
print("regression=PASS")
