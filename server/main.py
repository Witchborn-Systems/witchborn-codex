"""
Witchborn Codex Server
Genesis Entry Point

This file will initialize the Codex Root and Public Registry
in accordance with the Witchborn Codex Protocol (WCP).

No operational logic is defined here yet.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

APP_ROOT = Path(__file__).resolve().parents[1]
WWW_ROOT = APP_ROOT / "www"

app = FastAPI()


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
