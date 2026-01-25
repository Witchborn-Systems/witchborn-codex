import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi import Query
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

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
        "url": "https://github.com/WitchbornSystems/witchborn-codex/blob/main/LICENSE"
    },
)


# --- STORAGE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ZONES_DIR = os.path.join(BASE_DIR, "..", "zones")
os.makedirs(ZONES_DIR, exist_ok=True)

# --- GENESIS PROTECTIVE HOLDS ---
GENESIS_PROTECTED = {
    "openai": "OpenAI",
    "google": "Google",
    "anthropic": "Anthropic",
    "meta": "Meta",
    "root": "Witchborn Systems",
    "admin": "Witchborn Systems",
}

# --- MODELS ---
class Record(BaseModel):
    type: str = Field(..., description="APP, MCP, KEY, TXT, CAPS, CASCADE")
    value: Any
    priority: int = 10


class ClaimRequest(BaseModel):
    identity: str = Field(..., description="Canonical identity name (no ai://)")
    records: List[Record]


# --- HELPERS ---
def normalize_identity(raw: str) -> str:
    ident = raw.strip().lower()
    if ident.startswith("ai://"):
        ident = ident[len("ai://"):]
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


# --- ROUTES ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "witchborn-codex", "phase": "genesis"}


@app.get("/codex/resolve")
def resolve(identity: str = Query(..., description="ai:// identity to resolve")):
    name = normalize_identity(identity)

    # Protective hold
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

    # Live zone
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