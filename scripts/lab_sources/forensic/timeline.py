from pathlib import Path
from datetime import datetime, timezone
import csv
with Path(__file__).with_name("auth.csv").open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
for row in sorted(rows, key=lambda r: datetime.fromisoformat(r["time"])):
    time = datetime.fromisoformat(row["time"]).astimezone(timezone.utc)
    print(time.isoformat(), row["id"], row["event"])
