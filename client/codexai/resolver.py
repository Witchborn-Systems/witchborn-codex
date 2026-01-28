import requests
from typing import Dict, Any, Optional

class CodexResolver:
    def __init__(self, root: str = None):
        if not root:
            root = "https://witchbornsystems.ai"
        self.root = root.rstrip("/")

    def _fetch_identity(self, url: str) -> Dict[str, Any]:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()

    def get_full_context(self, identity: str) -> Dict[str, Any]:
        """Follows the Federation chain (Root -> Authority)."""
        clean_id = identity.replace("ai://", "")
        target_url = f"{self.root}/resolve?identity={clean_id}"
        data = self._fetch_identity(target_url)

        # Recursion for Federation
        if data.get("status") == "DELEGATED":
            auth_server = data.get("authoritative_server").rstrip("/")
            target_url = f"{auth_server}/resolve?identity={clean_id}"
            data = self._fetch_identity(target_url)

        return data

    def resolve(self, identity: str, prefer_mcp: bool = False) -> Dict[str, Any]:
        """
        Unified resolution logic.
        DEFAULT: Prioritizes APP (Human URL).
        OPTIONAL: Prioritizes MCP (Agent Config) only if prefer_mcp=True.
        """
        try:
            data = self.get_full_context(identity)
            records = data.get("records", [])

            # --- 1. IF AGENT REQUESTED (MCP) ---
            if prefer_mcp:
                mcp_records = sorted(
                    [r for r in records if r.get("type") == "MCP"],
                    key=lambda x: x.get("priority", 100)
                )
                if mcp_records:
                    return {
                        "mode": "mcp",
                        "config": mcp_records[0].get("value"),
                        "identity": identity
                    }
                return {"mode": "error", "message": "No MCP agent records found."}

            # --- 2. STANDARD LOOKUP (APP / HUMAN) ---
            app_records = [r for r in records if r.get("type") == "APP"]
            if app_records:
                return {
                    "mode": "app",
                    "url": app_records[0].get("value"),
                    "identity": identity
                }

            # --- 3. FALLBACK ---
            return {"mode": "unknown", "message": "No APP (Human Interface) record found."}

        except Exception as e:
            return {"error": "ResolutionFailed", "message": str(e)}