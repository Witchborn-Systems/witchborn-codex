import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Literal, Set

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# ============================================================
# APP SETUP
# ============================================================

APP_ROOT = Path(__file__).resolve().parents[1]
WWW_ROOT = APP_ROOT / "www"

app = FastAPI(
    title="Witchborn Codex API",
    version="1.1.0-genesis",
    description=(
        "Public, nonprofit reference implementation of the Witchborn Codex.\n\n"
        "This API provides identity resolution and registry services for "
        "autonomous AI systems.\n\n"
        "This service does NOT host AI models, proxy traffic, or execute MCP calls."
    ),
    terms_of_service="https://witchbornsystems.ai/governance",
    contact={
        "name": "Witchborn Systems",
        "url": "https://witchbornsystems.ai",
    },
    license_info={
        "name": "ForgeBorn License v1.0.1",
        "url": "https://github.com/WitchbornSystems/witchborn-codex/blob/main/LICENSE",
    },
)

# ============================================================
# STORAGE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZONES_DIR = os.path.join(BASE_DIR, "..", "zones")
os.makedirs(ZONES_DIR, exist_ok=True)

# ============================================================
# GENESIS PROTECTIVE HOLDS
# ============================================================

GENESIS_PROTECTED = {
    "openai": "OpenAI",
    "google": "Google",
    "anthropic": "Anthropic",
    "meta": "Meta",
    "root": "Witchborn Systems",
    "admin": "Witchborn Systems",
}

# ============================================================
# MODELS
# ============================================================

RecordType = Literal["APP", "MCP", "KEY", "TXT", "CAPS", "CASCADE", "BIND"]


class Record(BaseModel):
    type: RecordType = Field(..., description="APP, MCP, KEY, TXT, CAPS, CASCADE, BIND")
    value: Any
    priority: int = 10
    path: str = Field("/", description="The sub-resource path for this record")


# ============================================================
# HELPERS
# ============================================================

def normalize_identity(raw: str) -> str:
    ident = raw.strip().lower()

    # 1. Strip Protocol Schemes
    if ident.startswith("ai://"):
        ident = ident[len("ai://"):]
    elif ident.startswith("mcp://"):
        ident = ident[len("mcp://"):]

    # 2. Hard-Stop on DNS Confusion
    if "." in ident:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Dots forbidden. Use @ for hierarchy.")

    # 3. Strip Authority Hint (THE FIX)
    if "@" in ident:
        ident = ident.split("@")[0]

    return ident.rstrip("/")


def zone_path(identity: str) -> str:
    safe = "".join(c for c in identity if c.isalnum() or c in "-_")
    return os.path.join(ZONES_DIR, f"{safe}.json")


def load_zone(identity: str) -> Dict[str, Any] | None:
    path = zone_path(identity)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def records_by_type(records: List[Dict[str, Any]], rtype: str) -> List[Dict[str, Any]]:
    return [r for r in records if r.get("type") == rtype]


def resolve_cascade(
    identity: str,
    seen: Set[str],
    depth: int = 0,
    max_depth: int = 8,
) -> List[Dict[str, Any]]:
    if identity in seen:
        raise HTTPException(status_code=400, detail="CASCADE cycle detected")

    if depth > max_depth:
        raise HTTPException(status_code=400, detail="CASCADE depth exceeded")

    seen.add(identity)

    zone = load_zone(identity)
    if not zone:
        return []

    records = zone.get("records", [])
    cascades = records_by_type(records, "CASCADE")

    inherited: List[Dict[str, Any]] = []

    for c in cascades:
        upstream = normalize_identity(str(c.get("value", "")))
        inherited.extend(
            resolve_cascade(upstream, seen, depth + 1, max_depth)
        )

    return inherited + records


# ============================================================
# ROUTES
# ============================================================

@app.get("/health")
def health():
    return {"status": "ok", "service": "witchborn-codex", "phase": "genesis"}


@app.get("/codex/resolve")
def resolve(identity: str = Query(..., description="ai:// identity to resolve")):
    name = normalize_identity(identity)

    if name in GENESIS_PROTECTED:
        owner = GENESIS_PROTECTED[name]
        return JSONResponse(
            status_code=403,
            content={
                "identity": f"ai://{name}",
                "status": "PROTECTED",
                "message": f"Reserved for {owner}.",
                "claim_url": f"https://www.witchbornsystems.org/claim?id={name}",
            },
        )

    zone = load_zone(name)
    if zone:
        # Federation/Delegation Check (WCP 8.4)
        bind_records = records_by_type(zone['records'], "BIND")
        for b in bind_records:
            bind_url = b.get("value", "")
            # If BIND points away from our server, signal delegation
            if "witchbornsystems.ai" not in bind_url:
                return {
                    "identity": f"ai://{name}",
                    "status": "DELEGATED",
                    "authoritative_server": bind_url,
                    "message": "This identity is managed by an external authority."
                }

        return {
            "identity": f"ai://{name}",
            "status": "LIVE",
            "ttl": 3600,
            "records": zone["records"],
            "created_at": zone["created_at"],
        }

    raise HTTPException(status_code=404, detail="Identity not forged.")


@app.get("/codex/resolve/mcp/{identity}")
@app.get("/codex/resolve/mcp/{identity}/{subpath:path}")
def resolve_mcp(identity: str, subpath: str = ""):
    """
    MCP Collapse with Path Awareness (MCP_COLLAPSE 5.2).
    """
    name = normalize_identity(identity)
    target_path = "/" + subpath.strip("/")

    if name in GENESIS_PROTECTED:
        raise HTTPException(status_code=403, detail="Identity is protected.")

    all_records = resolve_cascade(name, seen=set())

    # 1. Gather and Filter by Path
    mcp_records = records_by_type(all_records, "MCP")
    if not mcp_records:
        raise HTTPException(status_code=404, detail="No MCP records found.")

    # 2. Match exact path, fallback to "/"
    selected_record = next((r for r in mcp_records if r.get("path") == target_path), None)
    if not selected_record:
        selected_record = next((r for r in mcp_records if r.get("path", "/") == "/"), None)

    if not selected_record:
        raise HTTPException(status_code=404, detail=f"No endpoint found for path {target_path}")

    # 3. Sort by priority
    # Note: Using only path-filtered records for priority tie-breaking
    eligible_matches = [r for r in mcp_records if r.get("path", "/") == selected_record.get("path", "/")]
    eligible_matches.sort(key=lambda r: r.get("priority", 10))
    selected = eligible_matches[0]

    # 4. Handle CAPS Filtering
    caps_records = records_by_type(all_records, "CAPS")
    allowed_caps: Set[str] = set()
    if caps_records:
        for c in caps_records:
            val = c.get("value")
            if isinstance(val, list):
                allowed_caps.update(str(v) for v in val)

    response: Dict[str, Any] = {
        "identity": f"ai://{name}",
        "mode": "mcp",
        "endpoint": selected["value"],
        "ttl": 3600,
        "source": "authoritative",
    }

    if allowed_caps:
        response["capabilities"] = sorted(allowed_caps)

    key_records = records_by_type(all_records, "KEY")
    if key_records:
        response["key"] = key_records[0].get("value")

    return response


def _static_file(path: Path) -> FileResponse:
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not Found")
    return FileResponse(path)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return _static_file(WWW_ROOT / "index.html")


@app.get("/governance", include_in_schema=False)
def governance() -> FileResponse:
    return _static_file(WWW_ROOT / "governance.html")


def main() -> None:
    print("Witchborn Codex Server (Genesis)")


if __name__ == "__main__":
    main()