import sys
import os
import json
import re

REQUIRED_FIELDS = ["identity", "created_at", "records"]
ALLOWED_RECORD_TYPES = {"BIND", "APP", "MCP", "KEY", "TXT", "CAPS", "CASCADE"}
IDENTITY_REGEX = re.compile(r"^[a-z0-9\-_]+$")

def error(msg):
    print(f"[ERROR] {msg}")

def warn(msg):
    print(f"[WARN] {msg}")

def ok(msg):
    print(f"[OK] {msg}")

def validate_zone_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            zone = json.load(f)
    except Exception as e:
        error(f"{path}: invalid JSON ({e})")
        return False

    # Check top-level required fields
    for field in REQUIRED_FIELDS:
        if field not in zone:
            error(f"{path}: missing required field '{field}'")
            return False

    # identity checks
    identity = zone["identity"]
    if not isinstance(identity, str) or not IDENTITY_REGEX.match(identity):
        error(f"{path}: 'identity' must be lowercase, ascii, no spaces, no authority, no @ (got '{identity}')")
        return False
    filename = os.path.splitext(os.path.basename(path))[0]
    if identity != filename:
        error(f"{path}: 'identity' does not match filename ('{identity}' vs '{filename}')")
        return False

    # created_at
    if not isinstance(zone["created_at"], str) or not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", zone["created_at"]):
        error(f"{path}: 'created_at' must be ISO-8601 UTC string")
        return False

    # info field
    if "info" in zone and not isinstance(zone["info"], str):
        error(f"{path}: 'info' must be a string if present")
        return False

    # records array
    records = zone["records"]
    if not isinstance(records, list) or not records:
        error(f"{path}: 'records' must be a non-empty array")
        return False

    # Per-record validation
    for i, rec in enumerate(records):
        rec_loc = f"{path}:records[{i}]"
        if "type" not in rec or "value" not in rec:
            error(f"{rec_loc}: missing required 'type' or 'value'")
            return False
        rtype = rec["type"]
        if rtype not in ALLOWED_RECORD_TYPES:
            error(f"{rec_loc}: invalid type '{rtype}'")
            return False
        # Priority
        if rtype == "MCP" and "priority" in rec and not isinstance(rec["priority"], int):
            error(f"{rec_loc}: MCP priority must be integer")
            return False
        # Type-specific checks
        val = rec["value"]
        if rtype == "MCP":
            if not isinstance(val, dict) or "endpoint" not in val or not isinstance(val["endpoint"], str) or not val["endpoint"].startswith("https://"):
                error(f"{rec_loc}: MCP value must be object with 'endpoint' HTTPS URL")
                return False
        elif rtype == "CAPS":
            if not isinstance(val, list) or not all(isinstance(c, str) for c in val):
                error(f"{rec_loc}: CAPS value must be list of strings")
                return False
        elif rtype in ("BIND", "APP", "TXT", "KEY", "CASCADE"):
            if not isinstance(val, str):
                error(f"{rec_loc}: {rtype} value must be string")
                return False

    ok(f"{path}: valid")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_zone.py <zonefile1.json> [zonefile2.json ...]")
        sys.exit(1)
    all_ok = True
    for path in sys.argv[1:]:
        if not validate_zone_file(path):
            all_ok = False
    if not all_ok:
        sys.exit(2)

if __name__ == "__main__":
    main()
