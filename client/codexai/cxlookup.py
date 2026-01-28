import argparse
import json
import sys
from codexai.resolver import CodexResolver


def main():
    parser = argparse.ArgumentParser(description="Witchborn Codex Lookup Tool")
    parser.add_argument("uri", help="The ai:// identity to resolve")
    parser.add_argument("--server", help="Override Root Authority URL", default=None)
    parser.add_argument("--mcp", action="store_true", help="Request AGENT (MCP) configuration")
    parser.add_argument("--raw", action="store_true", help="Show full authoritative zone file")

    args = parser.parse_args()

    try:
        resolver = CodexResolver(root=args.server)

        # 1. RAW MODE (Admin View)
        if args.raw:
            print(f";; <<>> cxlookup 1.0.0 <<>> {args.uri} (RAW)")
            data = resolver.get_full_context(args.uri)
            print(json.dumps(data, indent=2))
            return

        # 2. RESOLVE (Standard vs MCP)
        # We pass the flag directly to the resolver
        result = resolver.resolve(args.uri, prefer_mcp=args.mcp)

        # 3. DISPLAY
        if "error" in result:
            print(f";; STATUS: ResolutionFailed")
            print(f";; REASON: {result['message']}")
            sys.exit(1)

        mode = result.get("mode", "UNKNOWN").upper()

        if mode == "APP":
            print(f";; <<>> cxlookup 1.0.0 <<>> {args.uri}")
            print(f";; TYPE: HUMAN (APP)")
            print(f";; ANSWER: {result['url']}")

        elif mode == "MCP":
            # If they asked for MCP, dump the JSON so it can be piped
            print(json.dumps(result["config"], indent=2))

        else:
            print(f";; STATUS: {mode}")
            print(f";; MSG: {result.get('message')}")

    except Exception as e:
        print(f"\n[!] ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()