from pathlib import Path
from collections import Counter
import csv
with Path(__file__).with_name("flows.csv").open(newline="", encoding="utf-8") as f:
    counts = Counter(row["src"] for row in csv.DictReader(f) if row["action"] == "DENY")
for source, count in sorted(counts.items()):
    if count >= 3:
        print(f"REVIEW {source} denied={count}")
# Whole-file teaching counter. No time window, identity or intent inference.
