rows = [
    {"user": "alice", "status": "ok"},
    {"user": "bob", "status": "denied"},
    {"user": "kim", "status": "denied"},
    {"user": "lee"},
]
print("first=" + rows[0]["user"])
print("missing=" + rows[3].get("status", "UNKNOWN"))
names = []
for row in rows:
    if row.get("status") == "denied":
        names.append(row["user"])
print("denied=" + ",".join(names))
