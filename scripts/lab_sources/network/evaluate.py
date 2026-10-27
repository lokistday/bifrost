from pathlib import Path
import csv
import ipaddress
import json
root = Path(__file__).parent
rules = json.loads((root / "policy.json").read_text())["rules"]
with (root / "flows.csv").open(newline="", encoding="utf-8") as f:
    for flow in csv.DictReader(f):
        action = "DENY"
        for rule in rules:
            if (ipaddress.ip_address(flow["src"]) in ipaddress.ip_network(rule["src"])
                and ipaddress.ip_address(flow["dst"]) in ipaddress.ip_network(rule["dst"])
                and int(flow["port"]) == rule["port"]):
                action = rule["action"]
                break
        print(flow["id"], action, "MATCH" if action == flow["action"] else "MISMATCH")
