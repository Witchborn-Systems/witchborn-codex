# Witchborn Codex

The Witchborn Codex is a public, nonprofit reference implementation of a neutral
identity and resolution layer for autonomous AI systems.

This repository contains the **Codex Root** and **Public Registry** software.
It does not host AI models, proxy traffic, sell access, or operate a marketplace.

- to install manually see https://github.com/Witchborn-Systems/witchborn-codex/wiki
---

## What This Is

* A public utility for **AI identity, discovery, and resolution**
* A reference implementation of the **Witchborn Codex Protocol (WCP)**
* Open infrastructure to prevent proprietary capture of the agentic web
* Free to use, free to mirror, and free to self-host

---

## What This Is Not

* Not a token, coin, or NFT project
* Not a hosting provider
* Not a plugin store
* Not a commercial gatekeeper
* Not affiliated with OpenAI, Google, Anthropic, or any other trademark holder

---

## Governance Posture

The Codex is operated by **Witchborn Systems**, a Texas-based 501(c)(3) nonprofit.
Witchborn Systems acts as a steward, not an owner.

Identity resolution is cryptographically verifiable.
Authority is based on signature, not server location.

---

## 🔍 Discovery & Resolution Authority

Witchborn Systems operates a **Discovery Proxy** architecture. This allows agents and developers to interact with a single, trusted entry point to resolve identities across the entire federated network without managing complex delegation logic.

### 🚀 The "Single Entry" Pattern
You do not need to know the specific IP or URL of a Registrar Node to get an identity's configuration. The Root Authority handles the recursive lookup for you.

| Target Type | Endpoint | Description |
| :--- | :--- | :--- |
| **Identity Trace** | `/resolve?identity={id}` | Returns the full, raw record set and authority status. |
| **The Squish** | `/resolve/mcp/{id}` | Returns a flattened, machine-ready MCP descriptor. |

### 🛠 Example: Resolving a Federated Identity
To fetch the flattened MCP file for an identity like `acme` hosted on the `@webai` registrar:

```bash
# Requesting via the Root Discovery Proxy
curl -L [https://witchbornsystems.ai/resolve/mcp/acme@webai](https://witchbornsystems.ai/resolve/mcp/acme@webai)
```

**What happens behind the scenes:**
1. **Detection**: The Root identifies `@webai` as a delegated registrar via its internal `BIND` records.
2. **Proxying**: The Root silently forwards the request to the registrar's authoritative node (using the node's internal `/codex/` path).
3. **Delivery**: The Root returns the authoritative "Squished" JSON directly to the caller.

### 🌐 Web Fallback (Deep Linking)
The Discovery Authority supports "Smart Push" deep linking for human browsers:
* **UI Trace**: `https://witchbornsystems.ai/?query=acme@webai`
* **Direct Connect**: Clicking an `ai://` link will attempt to open your local Codex handler; if unavailable, the Root will render the terminal-style trace or redirect you to the identity's `APP` interface.

---
*Note: The `/resolve` path on the Root is the public discovery layer. Authoritative nodes maintain the `/codex/` namespace for internal federation.*

---


### Directory Layout

```
spec/           # All protocol and data format specs (WCP, MCP_COLLAPSE, ZONE_SPEC)
server/         # Reference FastAPI resolver and all zone files
  zones/        # All canonical zone files (root, identities, etc)
meta/           # (Optional) Changelogs and registry audit files
registry/       # The Storefront/Cart application (Self-Hosted Registrar)
```

### How to Add or Update a Zone File

1. **Copy or create a canonical zone file** in `server/zones/`, named `<identity>.json`.
2. **Follow the schema** in `spec/ZONE_SPEC.md`.
3. **Add or update only by pull request or authorized change.**
4. **Do not** use authority/registrar hints in file names—identity only, all lowercase.
5. **Run validation** (`python validate_zone.py zones/myname.json`) before submitting.

---

## Zone File Example

```json
{
  "identity": "acme",
  "created_at": "2026-01-25T00:00:00Z",
  "contact": "mailto:admin@acme.example.com",
  "info": "Official ACME AI identity zone.",
  "records": [
    {
      "type": "MCP",
      "value": {
        "endpoint": "[https://acme.example.com/mcp](https://acme.example.com/mcp)",
        "version": "1.0.0",
        "features": ["resources", "tools", "oauth"],
        "capabilities": ["search", "summarize", "login", "userinfo"]
      },
      "priority": 0
    },
    {
      "type": "CAPS",
      "value": ["search", "summarize", "login", "userinfo", "transcribe", "analyze"]
    },
    {
      "type": "KEY",
      "value": "ed25519:ACME_PUBLIC_KEY_BASE64"
    },
    {
      "type": "BIND",
      "value": "[https://cxbind.witchbornsystems.ai](https://cxbind.witchbornsystems.ai)"
    },
    {
      "type": "APP",
      "value": "[https://acme.example.com](https://acme.example.com)"
    },
    {
      "type": "TXT",
      "value": "ACME: Autonomous Compute & Model Entity"
    }
  ]
}
```

---

## Protocol Specifications

* **Zone file schema and record types:** see `spec/ZONE_SPEC.md`
* **Canonical protocol and identity law:** see `spec/WCP.md`
* **Collapse, capability negotiation, inheritance:** see `spec/MCP_COLLAPSE.md`

---

## Validation & Best Practices

* Always use canonical identity only (no `@authority` in filenames).
* Do not store secrets or private keys in zone files.
* **MANDATORY:** You must include a `contact` field (email/url) for accountability.
* Only modify `identity` or `created_at` with a full re-registration event.

---

## Status

**Genesis Release**
This repository is under active development. APIs, schemas, and tooling will stabilize through public use and review.

---

## Roadmap

* Digital signature support and hash chain for zone file audit
* Validator CLI and web tools
* Federation/mirroring protocol
* Meta/admin log ingestion and query

---

## License

ForgeBorn License v1.0.1
Attribution required. No white-label resale.

---
## Real time federated MCP.json dcollapsed link
https://witchbornsystems.ai/resolve/mcp/acme@webai

---

## Bonus command line output 
```commandline
D:\Dev\witchborn-codex\client\dist>cxlookup.exe acme@webai
;; <<>> ailookup 1.0.0 <<>> acme@webai
;; TYPE: HUMAN (APP)
;; ANSWER: https://acme.example.com



D:\Dev\witchborn-codex\client\dist>cxlookup.exe acme@webai
;; <<>> ailookup 1.0.0 <<>> acme@webai
;; TYPE: HUMAN (APP)
;; ANSWER: https://acme.example.com

D:\Dev\witchborn-codex\client\dist>cxlookup.exe acme@webai --mcp
{
  "endpoint": "https://acme.example.com/mcp",
  "version": "1.0.0",
  "features": [
    "resources",
    "tools",
    "oauth"
  ],
  "capabilities": [
    "search",
    "summarize",
    "login",
    "userinfo"
  ]
}

D:\Dev\witchborn-codex\client\dist>cxlookup.exe acme@webai --raw
;; <<>> ailookup 1.0.0 <<>> acme@webai (RAW)
{
  "identity": "ai://acme",
  "status": "LIVE",
  "ttl": 3600,
  "records": [
    {
      "type": "MCP",
      "value": {
        "endpoint": "https://acme.example.com/mcp",
        "version": "1.0.0",
        "features": [
          "resources",
          "tools",
          "oauth"
        ],
        "capabilities": [
          "search",
          "summarize",
          "login",
          "userinfo"
        ]
      },
      "priority": 0
    },
    {
      "type": "MCP",
      "value": {
        "endpoint": "https://acme-b2b.example.com/mcp",
        "version": "1.1.0",
        "features": [
          "tools",
          "prompts"
        ],
        "capabilities": [
          "transcribe",
          "analyze"
        ]
      },
      "priority": 5
    },
    {
      "type": "CAPS",
      "value": [
        "search",
        "summarize",
        "login",
        "userinfo",
        "transcribe",
        "analyze"
      ]
    },
    {
      "type": "KEY",
      "value": "ed25519:ACME_PUBLIC_KEY_BASE64"
    },
    {
      "type": "APP",
      "value": "https://acme.example.com"
    },
    {
      "type": "TXT",
      "value": "ACME: Autonomous Compute & Model Entity"
    }
  ],
  "created_at": "2026-01-25T00:00:00Z",
  "contact": "mailto:admin@acme.example.com",
  "info": "Official ACME AI identity zone. Defines DNS-style global identity and multi-endpoint service discovery."
}
```