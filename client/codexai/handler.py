import sys
import webbrowser
import json
from .resolver import CodexResolver


def main():
    if len(sys.argv) < 2: return
    uri = sys.argv[1]

    resolver = CodexResolver()

    # 1. Resolve
    result = resolver.resolve(uri)

    if result.get("error"):
        # If we can't find it, we just exit silently or print to stdout
        # In a future version, we might pop a tkinter alert box
        print(f"Error: {result['message']}")
        return

    # 2. Act
    if result.get("mode") == "app":
        rec = result.get("selected_record")
        if rec:
            val = rec.get("value")
            # Polymorphic Fallback: String > Default
            url = val if isinstance(val, str) else val.get("default")

            if url and (url.startswith("http") or url.startswith("https")):
                print(f"Opening: {url}")
                webbrowser.open(url)

    elif result.get("mode") == "mcp":
        # For now, just print config. Agents would consume this via API, not handler.
        print("MCP Configuration Resolved.")
        print(json.dumps(result.get("config"), indent=2))
        input("Press Enter to close...")


if __name__ == "__main__":
    main()