"""Read after completing your own implementation."""
def denied_users(rows):
    names = []
    for row in rows:
        if row.get("status") == "denied":
            names.append(row["user"])
    return names
