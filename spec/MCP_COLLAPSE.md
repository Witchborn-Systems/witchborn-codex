# MCP Collapse Semantics

Witchborn Codex Bind — Normative Specification

## Status

Public, normative.

## Scope

This document defines how the Codex Bind server resolves and collapses
MCP (Model Context Protocol) records for agent consumers.

This document does NOT define MCP execution, transport framing,
authentication, or session lifecycle.

---

## 1. Definitions

### Codex Bind

The authoritative public resolution service that answers identity queries
for the Witchborn Codex.

### MCP (Model Context Protocol)

An agent-to-service protocol used by AI systems to mount tools and
capabilities via network-accessible endpoints.

### Collapse

The deterministic process by which Codex Bind selects, filters, and
reduces a set of records into a single, client-ready response.

---

## 2. Canonical MCP Endpoint Representation

### Normative Rule

Codex Bind MUST publish MCP endpoints as canonical **HTTPS URLs**.

Example:

```json
{
  "type": "MCP",
  "value": "https://sentinel.example.com/mcp"
}
```

### Rationale

The MCP specification requires valid absolute URIs for server endpoints.
At present, MCP tooling expects standard HTTP(S) URLs.

### Non-Normative Aliases

Custom URI schemes such as `mcp://` MAY be used by clients as display or
shorthand aliases, but are NOT authoritative and MUST NOT be relied upon
for transport.

Codex Bind MUST NOT require clients to understand `mcp://`.

---

## 3. Record Model

An MCP record MUST have:

* `type`: `"MCP"`
* `value`: HTTPS URL pointing to an MCP-compliant server
* `priority`: Integer (higher wins)

Optional associated records:

* `CAPS`: Capability scopes
* `KEY`: Public verification key
* `CASCADE`: Upstream identity references

---

## 4. Collapse Modes

Codex Bind supports consumer-specific collapse modes.

### 4.1 Default (Human / Neutral)

* MCP records are included in raw record output
* No MCP descriptor is synthesized

### 4.2 MCP Mode

Activated by:

* Explicit client request (e.g. `mode=mcp`)
* MCP-aware client context

In MCP mode, Codex Bind MUST:

1. Identify all MCP records for the identity
2. Sort by descending `priority`
3. Apply CAPS filtering
4. Apply CASCADE inheritance (if present)
5. Select exactly ONE MCP endpoint
6. Emit a collapsed MCP descriptor

---

## 5. CAPS Filtering

If `CAPS` records are present:

* Only MCP endpoints whose declared capabilities intersect with the
  requested or allowed capability set MAY be selected.
* If no MCP endpoint satisfies CAPS constraints, resolution MUST fail
  with a clear error.

---

## 6. CASCADE Semantics

If a `CASCADE` record is present:

* Codex Bind MUST recursively resolve upstream identities
* MCP records from upstream identities MAY be inherited
* Local records override upstream records by priority

CASCADE resolution MUST be bounded to prevent infinite recursion.

---

## 7. Collapsed MCP Descriptor (Response Shape)

When collapsing for MCP mode, Codex Bind MUST return a response that
includes:

```json
{
  "identity": "ai://sentinel",
  "mode": "mcp",
  "endpoint": "https://sentinel.example.com/mcp",
  "capabilities": ["search", "summarize"],
  "key": "ed25519:BASE64...",
  "ttl": 3600,
  "source": "authoritative"
}
```

### Required Fields

* `identity`
* `mode`
* `endpoint`
* `ttl`

### Optional Fields

* `capabilities`
* `key`
* `source`

---

## 8. Execution Boundary (Critical)

Codex Bind MUST NOT:

* Proxy MCP traffic
* Establish MCP sessions
* Perform MCP authentication
* Inspect MCP payloads
* Maintain MCP state

After returning a collapsed MCP descriptor, Codex Bind exits the execution
path entirely.

All MCP execution occurs between the client and the MCP server.

---

## 9. Error Conditions

Codex Bind MUST return explicit errors for:

* No MCP records found
* CAPS constraints unsatisfied
* CASCADE resolution failure
* Invalid MCP endpoint URL

Silent fallback is NOT permitted.

---

## 10. Security Considerations

* MCP endpoints MUST be HTTPS
* Codex Bind does not guarantee MCP server safety
* Trust decisions beyond resolution are the responsibility of the client

---

## 11. Summary (Non-Normative)

Codex Bind describes MCP.
MCP servers execute MCP.

Codex collapses identity.
MCP executes capability.

These responsibilities MUST remain separate.
