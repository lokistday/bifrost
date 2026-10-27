from pathlib import Path
import csv

path = Path(__file__).with_name("events.csv")
with path.open(encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))
denied = [row for row in rows if row["status"] == "denied"]
print(f"events={len(rows)} denied={len(denied)}")
for row in denied:
    print(row["user"])
