# Witchborn Codex

The Witchborn Codex is a public, nonprofit reference implementation of a neutral
identity and resolution layer for autonomous AI systems.

This repository contains the **Codex Root** and **Public Registry** software.
It does not host AI models, proxy traffic, sell access, or operate a marketplace.

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

## Getting Started

### Directory Layout

```
spec/           # All protocol and data format specs (WCP, MCP_COLLAPSE, ZONE_SPEC)
server/         # Reference FastAPI resolver and all zone files
  zones/        # All canonical zone files (root, identities, etc)
meta/           # (Optional) Changelogs and registry audit files
```

### How to Add or Update a Zone File

1. **Copy or create a canonical zone file** in `server/zones/`, named `<identity>.json`.
2. **Follow the schema** in `spec/ZONE_SPEC.md` (see example below).
3. **Add or update only by pull request or authorized change.**
4. **Do not** use authority/registrar hints in file names—identity only, all lowercase.
5. **Run validation** (`validate_zone.py`, coming soon) before submitting.

---

## Zone File Example

```json
{
  "identity": "acme",
  "created_at": "2026-01-25T00:00:00Z",
  "info": "Official ACME AI identity zone. Defines DNS-style global identity, multi-endpoint service discovery, OAuth-like delegated authentication concepts, and real-time capability negotiation for agent and human clients. Registry-driven, provenance-aware, and execution-neutral.",
  "records": [
    {
      "type": "MCP",
      "value": {
        "endpoint": "https://acme.example.com/mcp",
        "version": "1.0.0",
        "features": ["resources", "tools", "oauth"],
        "capabilities": ["search", "summarize", "login", "userinfo"]
      },
      "priority": 0
    },
    {
      "type": "MCP",
      "value": {
        "endpoint": "https://acme-b2b.example.com/mcp",
        "version": "1.1.0",
        "features": ["tools", "prompts"],
        "capabilities": ["transcribe", "analyze"]
      },
      "priority": 5
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
      "value": "https://cxbind.witchbornsystems.ai"
    },
    {
      "type": "APP",
      "value": "https://acme.example.com"
    },
    {
      "type": "TXT",
      "value": "ACME: Autonomous Compute & Model Entity"
    }
  ]
}
```

---

### Genesis Root Zone File

```json
{
  "identity": "root",
  "created_at": "2026-01-25T00:00:00Z",
  "info": "Witchborn Codex root authority and governance. Registry public key, legal provenance, and canonical cxbind endpoint(s).",
  "records": [
    {
      "type": "BIND",
      "value": "https://cxbind.witchbornsystems.ai"
    },
    {
      "type": "TXT",
      "value": "Witchborn Codex Root Authority"
    },
    {
      "type": "KEY",
      "value": "ed25519:BASE64_ROOT_PUBLIC_KEY"
    },
    {
      "type": "APP",
      "value": "https://witchbornsystems.ai/governance"
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
* Validate all records with future `validate_zone.py` (planned).
* Only modify `identity` or `created_at` with a full re-registration event.

---

## Status

**Genesis Release**
This repository is under active development.
APIs, schemas, and tooling will stabilize through public use and review.

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

