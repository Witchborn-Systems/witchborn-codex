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
    version="1.0.0-genesis",
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

RecordType = Literal["APP", "MCP", "KEY", "TXT", "CAPS", "CASCADE"]


class Record(BaseModel):
    type: RecordType = Field(..., description="APP, MCP, KEY, TXT, CAPS, CASCADE")
    value: Any
    priority: int = 10


class ClaimRequest(BaseModel):
    identity: str = Field(..., description="Canonical identity name (no ai://)")
    records: List[Record]


# ============================================================
# HELPERS
# ============================================================

def normalize_identity(raw: str) -> str:
    ident = raw.strip().lower()
    if ident.startswith("ai://"):
        ident = ident[len("ai://") :]
    ident = ident.split("/")[0]
    ident = ident.split("@")[0]
    return ident


def zone_path(identity: str) -> str:
    safe = "".join(c for c in identity if c.isalnum() or c in "-_")
    return os.path.join(ZONES_DIR, f"{safe}.json")


def load_zone(identity: str) -> Dict[str, Any] | None:
    path = zone_path(identity)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_zone(identity: str, data: Dict[str, Any]) -> None:
    path = zone_path(identity)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


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

    # Upstream first, local later (local overrides by priority)
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
        return {
            "identity": f"ai://{name}",
            "status": "LIVE",
            "ttl": 3600,
            "records": zone["records"],
            "created_at": zone["created_at"],
        }

    raise HTTPException(status_code=404, detail="Identity not forged.")


@app.get("/codex/resolve/mcp/{identity}")
def resolve_mcp(identity: str):
    name = normalize_identity(identity)

    if name in GENESIS_PROTECTED:
        raise HTTPException(status_code=403, detail="Identity is protected.")

    zone = load_zone(name)
    if not zone:
        raise HTTPException(status_code=404, detail="Identity not forged.")

    all_records = resolve_cascade(name, seen=set())

    mcp_records = records_by_type(all_records, "MCP")
    if not mcp_records:
        raise HTTPException(status_code=404, detail="No MCP records found.")

    # Lower priority value wins
    mcp_records.sort(key=lambda r: r.get("priority", 10))

    caps_records = records_by_type(all_records, "CAPS")
    key_records = records_by_type(all_records, "KEY")

    allowed_caps: Set[str] = set()
    if caps_records:
        for c in caps_records:
            val = c.get("value")
            if isinstance(val, list):
                allowed_caps.update(str(v) for v in val)

        if allowed_caps:
            filtered = []
            for m in mcp_records:
                m_caps = m.get("capabilities")
                if not m_caps or set(m_caps) & allowed_caps:
                    filtered.append(m)

            if not filtered:
                raise HTTPException(
                    status_code=403,
                    detail="CAPS constraints unsatisfied.",
                )

            mcp_records = filtered

    selected = mcp_records[0]

    response: Dict[str, Any] = {
        "identity": f"ai://{name}",
        "mode": "mcp",
        "endpoint": selected["value"],
        "ttl": 3600,
        "source": "authoritative",
    }

    if allowed_caps:
        response["capabilities"] = sorted(allowed_caps)

    if key_records:
        response["key"] = key_records[0].get("value")

    return response


@app.post("/codex/claim")
def claim(req: ClaimRequest):
    name = normalize_identity(req.identity)

    if name in GENESIS_PROTECTED:
        raise HTTPException(status_code=403, detail="Identity is protected.")

    if load_zone(name):
        raise HTTPException(status_code=409, detail="Identity already claimed.")

    zone = {
        "identity": name,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "records": [r.model_dump() for r in req.records],
    }

    save_zone(name, zone)

    return {
        "status": "SUCCESS",
        "message": f"ai://{name} is now active.",
    }


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
