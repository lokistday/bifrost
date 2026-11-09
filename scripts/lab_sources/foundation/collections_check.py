"""Small independent cases; missing status means not denied in this exercise."""
import sys
from collections_practice import denied_users
cases = [([], []),
         ([{"user": "maya", "status": "ok"}, {"user": "zoe", "status": "denied"}], ["zoe"]),
         ([{"user": "lee"}, {"user": "bob", "status": "denied"}, {"user": "kim", "status": "denied"}], ["bob", "kim"])]
try:
    for rows, expected in cases:
        actual = denied_users(rows)
        if actual != expected:
            raise ValueError(f"expected {expected!r}, got {actual!r}")
except (NotImplementedError, ValueError) as exc:
    print(f"NOT YET: {exc}")
    sys.exit(1)
print("3 cases passed")
