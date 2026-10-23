"""Validate a fictional teaching configuration, then review eight local rules.

PASS only means this fixture meets a named local rule. It is not an IAM policy
evaluation, a test of deployed resources, or proof of cloud security.
"""
from pathlib import Path
import ipaddress
import json
import re
import sys


RULES = (
    ("storage.public", "storage", "public", bool, "외부 공개를 해제합니다."),
    ("storage.encrypted", "storage", "encrypted", bool, "저장 암호화를 켭니다."),
    ("identity.scope", "identity", "action", str, "동작과 자원을 구체적으로 지정합니다."),
    ("identity.temporary", "identity", "long_lived_key", bool, "이 모형에서는 임시 신원을 사용합니다."),
    ("network.database", "network", "database_public", bool, "DB의 인터넷 직접 공개를 해제합니다."),
    ("network.admin", "network", "admin_source", str, "관리 출발지를 유효한 제한 CIDR로 지정합니다."),
    ("audit.enabled", "audit", "enabled", bool, "감사 기록을 켭니다."),
    ("audit.retention", "audit", "retention_days", int, "이 모형의 보관 기준은 30일 이상입니다."),
)
SCHEMA = {
    "storage": {"name", "public", "encrypted"},
    "identity": {"action", "resource", "long_lived_key"},
    "network": {"database_public", "admin_source"},
    "audit": {"enabled", "retention_days"},
}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-standard JSON constant: " + value)


def review(config):
    """Return (rows, document_errors); invalid input never contributes a PASS."""
    if not isinstance(config, dict):
        return [], ["document: JSON 객체가 필요합니다."]
    document_errors = []
    extra = set(config) - {"workload", "provider", *SCHEMA}
    if extra:
        document_errors.append("document: 알 수 없는 항목 " + ", ".join(sorted(extra)))
    for field in ("workload", "provider"):
        value = config.get(field)
        if not isinstance(value, str) or not value.strip():
            document_errors.append(f"{field}: 비어 있지 않은 문자열이 필요합니다.")
    for section_name, allowed in SCHEMA.items():
        section = config.get(section_name)
        if isinstance(section, dict):
            extra = set(section) - allowed
            if extra:
                document_errors.append(f"{section_name}: 알 수 없는 항목 " + ", ".join(sorted(extra)))
    storage = config.get("storage")
    if isinstance(storage, dict) and (not isinstance(storage.get("name"), str) or not storage["name"].strip()):
        document_errors.append("storage.name: 비어 있지 않은 문자열이 필요합니다.")
    rows = []
    for name, section_name, field, kind, guidance in RULES:
        section = config.get(section_name)
        error = ""
        value = None
        if not isinstance(section, dict):
            error = f"{section_name}: JSON 객체가 필요합니다."
        elif field not in section:
            error = f"{section_name}.{field}: 필수 항목이 없습니다."
        else:
            value = section[field]
            # bool is an int subclass in Python, so use exact scalar types.
            if type(value) is not kind:
                error = f"{section_name}.{field}: {kind.__name__} 자료형이 필요합니다."
        if not error and kind is str and (not value.strip() or value != value.strip()):
            error = f"{section_name}.{field}: 빈 값이나 앞뒤 공백을 허용하지 않습니다."
        if not error and name == "identity.scope":
            resource = section.get("resource")
            if not isinstance(resource, str) or not resource.strip() or resource != resource.strip():
                error = "identity.resource: 비어 있지 않은 문자열이 필요합니다."
            elif not re.fullmatch(r"[A-Za-z0-9*?][A-Za-z0-9._:/?*-]{0,199}", resource):
                error = "identity.resource: 이 모형의 자원 식별자 형식이 아닙니다."
            elif not re.fullmatch(r"[A-Za-z*?][A-Za-z0-9:*?]{0,99}", value):
                error = "identity.action: 이 모형의 동작 식별자 형식이 아닙니다."
        if not error and name == "network.admin":
            try:
                if "/" not in value:
                    raise ValueError("CIDR prefix required")
                network = ipaddress.ip_network(value, strict=True)
            except ValueError:
                error = "network.admin_source: 네트워크 주소/접두사 형식의 CIDR이 필요합니다."
        if not error and name == "audit.retention" and not 0 <= value <= 36500:
            error = "audit.retention_days: 0~36500 사이의 정수가 필요합니다."
        if error:
            rows.append(("INVALID", name, error))
            continue
        if name in ("storage.public", "identity.temporary", "network.database"):
            passed = value is False
        elif name in ("storage.encrypted", "audit.enabled"):
            passed = value is True
        elif name == "identity.scope":
            passed = not any(char in value + section["resource"] for char in "*?")
        elif name == "network.admin":
            passed = network.prefixlen > 0
        else:
            passed = value >= 30
        rows.append(("PASS" if passed else "REVIEW", name, guidance))
    return rows, document_errors


def main(argv=None):
    # Stable UTF-8 output in Windows terminals and redirected lesson tests.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:] if argv is None else argv
    if len(args) > 1:
        print("usage: python3 review.py [config.json]")
        return 2
    path = Path(args[0]) if args else Path(__file__).with_name("config.json")
    try:
        config = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object,
                            parse_constant=reject_constant)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"INVALID document: JSON 파일을 읽을 수 없습니다. ({type(error).__name__})")
        print("passed=0/8 review=0 invalid=1")
        return 2
    rows, errors = review(config)
    for error in errors:
        print(f"INVALID {error}")
    for status, name, reason in rows:
        print(status, name + ":", reason)
    invalid = len(errors) + sum(status == "INVALID" for status, _, _ in rows)
    passed = sum(status == "PASS" for status, _, _ in rows)
    # A malformed document cannot be shown as 8/8 even if its rule fields match.
    if errors:
        passed = 0
    print(f"passed={passed}/8 review={sum(status == 'REVIEW' for status, _, _ in rows)} invalid={invalid}")
    print("범위: 형식과 8개 모형 규칙만 검사합니다. 실제 권한·신뢰 경로·운영 보안은 별도로 검증하세요.")
    return 2 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
