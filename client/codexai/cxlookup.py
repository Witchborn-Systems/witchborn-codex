import argparse
import json
import sys
from .resolver import CodexResolver


def main():
    parser = argparse.ArgumentParser(description="Witchborn Codex Lookup")
    parser.add_argument("uri", help="The URI (ai://acme)")
    parser.add_argument("--server", "-s", help="Override Root Server")
    parser.add_argument("--json", "-j", action="store_true")
    args = parser.parse_args()

    resolver = CodexResolver(root_url=args.server)

    if not args.json:
        print(f";; <<>> cxlookup 1.0.0 <<>> {args.uri}")
        print(f";; server: {resolver.root}")

    result = resolver.resolve(args.uri)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if result.get("error"):
        print(f";; STATUS: {result['error']}")
        print(f";; REASON: {result.get('message')}")
    elif result.get("mode") == "mcp":
        print(";; MODE: AGENT (MCP)")
        print(json.dumps(result.get("config"), indent=2))
    else:
        print(";; MODE: HUMAN (APP)")
        rec = result.get("selected_record")
        if rec:
            val = rec.get("value")
            # Handle Polymorphic App Object
            target = val if isinstance(val, str) else val.get("default", str(val))
            print(f";; TARGET: {target}")
            print(f";; TYPE:   {rec.get('type')}")
        else:
            print(";; TARGET: (No match)")


if __name__ == "__main__":
    main()