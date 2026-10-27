from pathlib import Path
import base64
import sys
path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("puzzle.txt")
fields = dict(line.split("=", 1) for line in path.read_text(encoding="utf-8").splitlines() if "=" in line)
value = fields["payload"].encode("ascii")
for step in range(2):
    value = base64.b64decode(value, validate=True)
    print(f"step={step + 1}: {value.decode('ascii')}")
