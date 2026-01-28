import sys
import webbrowser
import ctypes
from codexai.resolver import CodexResolver


def main():
    # 1. Get the URI passed by Windows (e.g. "ai://acme@webai")
    if len(sys.argv) > 1:
        identity = sys.argv[1]
    else:
        # If user just double-clicks the EXE without a link
        ctypes.windll.user32.MessageBoxW(0, "Please open an ai:// link instead.", "Witchborn Codex", 0)
        return

    # 2. Resolve (Standard Human Lookup)
    try:
        resolver = CodexResolver()
        # We do NOT prefer MCP here. Handlers are for Humans (Browsers).
        result = resolver.resolve(identity, prefer_mcp=False)

        if result.get("mode") == "app":
            # SUCCESS: Open the URL in Chrome/Edge/Default
            target_url = result.get("url")
            webbrowser.open(target_url)

        elif result.get("mode") == "mcp":
            # Edge case: If it's ONLY an agent, we can't "open" it.
            ctypes.windll.user32.MessageBoxW(0, "This identity is for AI Agents only.", "Witchborn Codex", 0)

        else:
            # Error or Unknown
            msg = result.get("message", "Unknown Error")
            ctypes.windll.user32.MessageBoxW(0, f"Could not resolve identity:\n{msg}", "Resolution Failed", 0x10)

    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"Critical Error:\n{str(e)}", "Handler Crash", 0x10)


if __name__ == "__main__":
    main()