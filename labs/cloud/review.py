from pathlib import Path
import json
import sys
path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("config.json")
c = json.loads(path.read_text(encoding="utf-8"))
checks = {
    "storage.public": not c["storage"]["public"],
    "storage.encrypted": c["storage"]["encrypted"],
    "identity.scope": c["identity"]["action"] != "*" and c["identity"]["resource"] != "*",
    "identity.temporary": not c["identity"]["long_lived_key"],
    "network.database": not c["network"]["database_public"],
    "network.admin": c["network"]["admin_source"] != "0.0.0.0/0",
    "audit.enabled": c["audit"]["enabled"],
    "audit.retention": c["audit"]["retention_days"] >= 30,
}
for name, passed in checks.items():
    print("PASS" if passed else "REVIEW", name)
print(f"passed={sum(checks.values())}/{len(checks)}")
# A fixture checker only; not an IAM evaluator or a cloud security scanner.
