import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Literal, Set, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# ============================================================
# APP SETUP
# ============================================================

APP_ROOT = Path(__file__).resolve().parents[1]
WWW_ROOT = APP_ROOT / "www"

app = FastAPI(
    title="Witchborn Codex API (Registrar)",
    version="1.1.1-genesis",
    description=(
        "Public, nonprofit reference implementation of the Witchborn Codex.\n\n"
        "This service provides authoritative identity resolution for "
        "autonomous AI systems."
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
ZONES_DIR = os.path.join(BASE_DIR, "zones")
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

    if ident.startswith("ai://"):
        ident = ident[len("ai://"):]
    elif ident.startswith("mcp://"):
        ident = ident[len("mcp://"):]

    if "@" in ident:
        # Registrar Logic: Resolve the local identity portion
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
        inherited.extend(resolve_cascade(upstream, seen, depth + 1, max_depth))

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
                "message": f"Reserved for {owner}."
            },
        )

    zone = load_zone(name)
    if zone:
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
    MCP Collapse and Flattening (MCP_COLLAPSE 5.2 / WCP 8.4.1).
    """
    name = normalize_identity(identity)
    target_path = "/" + subpath.strip("/")

    if name in GENESIS_PROTECTED:
        raise HTTPException(status_code=403, detail="Identity is protected.")

    all_records = resolve_cascade(name, seen=set())
    mcp_records = records_by_type(all_records, "MCP")

    if not mcp_records:
        raise HTTPException(status_code=404, detail="No machine-readable endpoints found.")

    # 1. Path Awareness
    selected_record = next((r for r in mcp_records if r.get("path") == target_path), None)
    if not selected_record:
        selected_record = next((r for r in mcp_records if r.get("path", "/") == "/"), None)

    if not selected_record:
        raise HTTPException(status_code=404, detail=f"No endpoint found for path {target_path}")

    # 2. Priority Sorting
    eligible_matches = [r for r in mcp_records if r.get("path", "/") == selected_record.get("path", "/")]
    eligible_matches.sort(key=lambda r: r.get("priority", 10))
    selected = eligible_matches[0]

    # 3. Aggregated Capabilities (CAPS)
    caps_records = records_by_type(all_records, "CAPS")
    allowed_caps: Set[str] = set()
    for c in caps_records:
        val = c.get("value")
        if isinstance(val, list):
            allowed_caps.update(str(v) for v in val)

    # 4. MCP SPEC COMPLIANCE: Extract raw HTTPS URL string
    # If value is an object (with version/features), extract just the 'endpoint' string.
    raw_val = selected["value"]
    endpoint_url = raw_val.get("endpoint") if isinstance(raw_val, dict) else raw_val

    response: Dict[str, Any] = {
        "identity": f"ai://{name}",
        "mode": "mcp",
        "endpoint": endpoint_url,  # Flattened to string per MCP Spec 2025-06-18
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)