import requests
from typing import Dict, Any, Optional

class CodexResolver:
    def __init__(self, root: str = "https://witchbornsystems.ai"):
        self.root = root.rstrip("/")

    def get_mcp(self, identity: str) -> Dict[str, Any]:
        """Returns the spec-perfect MCP descriptor for AI tool mounting."""
        clean_id = identity.replace("ai://", "")
        # Hits the Root Proxy forwarder
        resp = requests.get(f"{self.root}/resolve/mcp/{clean_id}", timeout=5)
        resp.raise_for_status()
        return resp.json()

    def get_full_context(self, identity: str) -> Dict[str, Any]:
        """Returns everything: MCP, custom TXT records, and APP metadata."""
        clean_id = identity.replace("ai://", "")
        # Hits the full resolve path
        resp = requests.get(f"{self.root}/resolve?identity={clean_id}", timeout=5)
        resp.raise_for_status()
        return resp.json()