import os
import requests
from typing import Dict, Any, Optional


class CodexResolver:
    """
    The Witchborn Codex Resolver.
    Connects to the Root Authority to resolve ai:// and mcp:// URIs.
    """

    def __init__(self, root_url: str = None, timeout: int = 5):
        # Default to public root, override via env for local dev
        # Use "http://localhost:8000" if testing locally!
        default = os.getenv("CODEX_ROOT", "https://witchbornsystems.ai")
        self.root = (root_url or default).rstrip("/")
        self.timeout = timeout

    def resolve(self, uri: str) -> Dict[str, Any]:
        """
        Smart Resolve. Automatically detects intent (Agent vs Human).
        """
        clean_uri = uri.strip()
        if clean_uri.startswith("mcp://"):
            return self.resolve_mcp(clean_uri)
        return self.resolve_app(clean_uri)

    def resolve_app(self, uri: str) -> Dict[str, Any]:
        """
        Standard Lookup (A-Record). Finds the APP target for humans.
        """
        identity, path = self._parse_uri(uri)
        try:
            resp = requests.get(f"{self.root}/codex/resolve", params={"identity": identity}, timeout=self.timeout)

            if resp.status_code == 404:
                return {"error": "NXDOMAIN", "message": f"Identity '{identity}' not found."}
            if resp.status_code != 200:
                return {"error": "SERVFAIL", "message": f"Server error {resp.status_code}"}

            zone = resp.json()

            # Client-Side Path Matching
            target_path = "/" + path.strip("/")
            best_match = None

            # Find best APP record
            for rec in [r for r in zone.get("records", []) if r.get("type") == "APP"]:
                rec_path = rec.get("path", "/")
                if rec_path == target_path:
                    best_match = rec
                    break
                if rec_path == "/" and not best_match:
                    best_match = rec

            return {
                "status": "NOERROR",
                "mode": "app",
                "identity": zone.get("identity"),
                "selected_record": best_match,
                "requested_path": target_path
            }
        except Exception as e:
            return {"error": "CONNECTION_ERROR", "message": str(e)}

    def resolve_mcp(self, uri: str) -> Dict[str, Any]:
        """
        Agent Lookup. Fetches Flattened Config.
        """
        identity, path = self._parse_uri(uri)
        endpoint = f"{self.root}/codex/resolve/mcp/{identity}"
        if path: endpoint += f"/{path}"

        try:
            resp = requests.get(endpoint, timeout=self.timeout)
            if resp.status_code == 200:
                return {"status": "NOERROR", "mode": "mcp", "config": resp.json()}
            return {"error": "NXDOMAIN" if resp.status_code == 404 else "SERVFAIL"}
        except Exception as e:
            return {"error": "CONNECTION_ERROR", "message": str(e)}

    def _parse_uri(self, uri: str) -> tuple[str, str]:
        clean = uri
        for proto in ["ai://", "mcp://"]:
            if clean.startswith(proto): clean = clean[len(proto):]

        # Handle @authority (strip it for basic resolution)
        if "@" in clean: clean = clean.split("@")[0]

        if "/" in clean:
            parts = clean.split("/", 1)
            return parts[0], parts[1]
        return clean, ""