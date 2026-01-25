# MCP Collapse Semantics

Witchborn Codex Bind — Normative Specification

**Status:** Public, normative (Frozen)
**Scope:** Public, authoritative

---

## Scope

This document defines how the Codex Bind server resolves and collapses MCP (Model Context Protocol) records for agent consumers.

This document does **NOT** define MCP execution, transport framing, authentication, or session lifecycle.

---

## 1. Definitions

### Codex Bind

The authoritative public resolution service that answers identity queries for the Witchborn Codex.

### MCP (Model Context Protocol)

An agent-to-service protocol used by AI systems to mount tools and capabilities via network-accessible endpoints.

### Collapse

The deterministic process by which Codex Bind selects, filters, and reduces a set of records into a single, client-ready response.

---

## 2. Identity Normalization

AI identity URIs MAY include an authority or registrar hint in the form:

ai://<identity>@<authority>

**All resolution and collapse operations MUST use only the base identity before the first `@`.**
Authority or registrar hints are ignored for collapse, inheritance, and record selection, and are used only for provenance, UI display, or client-side routing.

**Example:**

* Input: ai://sentinel@witchborn
* Canonical identity: sentinel
* Collapse operates on: zones/sentinel.json

---

## 3. Canonical MCP Endpoint Representation

### Normative Rule

Codex Bind MUST publish MCP endpoints as canonical **HTTPS URLs**.

Example:
{
"type": "MCP",
"value": "[https://sentinel.example.com/mcp](https://sentinel.example.com/mcp)"
}

### Rationale

The MCP specification requires valid absolute URIs for server endpoints. MCP tooling expects standard HTTP(S) URLs.

### Non-Normative Aliases

Custom URI schemes such as mcp:// MAY be used by clients as display or shorthand aliases, but are NOT authoritative and MUST NOT be relied upon for transport.

Codex Bind MUST NOT require clients to understand mcp://.

---

## 4. Record Model

An MCP record MUST have:

* type: "MCP"
* value: HTTPS URL pointing to an MCP-compliant server
* priority: Integer (lower value has higher precedence)

Optional associated records:

* CAPS: Capability scopes
* KEY: Public verification key
* CASCADE: Upstream identity references

---

## 5. Collapse Modes

Codex Bind supports consumer-specific collapse modes.

### 5.1 Default (Human / Neutral)

* MCP records are included in raw record output
* No MCP descriptor is synthesized

### 5.2 MCP Mode

Activated by:

* Request to a dedicated MCP resolution endpoint
  (e.g. /codex/resolve/mcp/{identity})

In MCP mode, Codex Bind MUST:

1. Identify all MCP records for the identity
2. Sort by ascending priority
3. Apply CAPS filtering
4. Apply CASCADE inheritance (if present)
5. Select exactly ONE MCP endpoint
6. Emit a collapsed MCP descriptor

---

## 6. CAPS Filtering

If CAPS records are present:

* Only MCP endpoints whose declared capabilities intersect with the client-requested capability set MAY be selected.
* If no CAPS records are present, all MCP endpoints are considered eligible.
* If no MCP endpoint satisfies CAPS constraints, resolution MUST fail with a clear error.

Requested capability sets are advisory; Codex Bind enforces only declared CAPS records.

---

## 7. CASCADE Semantics

If a CASCADE record is present:

* Codex Bind MUST recursively resolve upstream identities.
* MCP records from upstream identities MAY be inherited.
* Local identity records override inherited records by priority.
* If priorities are equal, local identity records take precedence.

CASCADE resolution MUST be bounded to prevent infinite recursion.

---

## 8. Collapsed MCP Descriptor (Response Shape)

When collapsing for MCP mode, Codex Bind MUST return a response that includes:

{
"identity": "ai://sentinel",
"mode": "mcp",
"endpoint": "[https://sentinel.example.com/mcp](https://sentinel.example.com/mcp)",
"capabilities": ["search", "summarize"],
"key": "ed25519:BASE64...",
"ttl": 3600,
"source": "authoritative"
}

### Required Fields

* identity
* mode
* endpoint
* ttl

### Optional Fields

* capabilities
* key
* source

TTL is advisory and reflects resolver cache guidance only.

---

## 9. Execution Boundary (Critical)

Codex Bind MUST NOT:

* Proxy MCP traffic
* Establish MCP sessions
* Perform MCP authentication
* Inspect MCP payloads
* Maintain MCP state

After returning a collapsed MCP descriptor, Codex Bind exits the execution path entirely.

All MCP execution occurs between the client and the MCP server.

---

## 10. Error Conditions

Codex Bind MUST return explicit errors for:

* No MCP records found
* CAPS constraints unsatisfied
* CASCADE resolution failure
* Invalid MCP endpoint URL

Silent fallback is NOT permitted.

---

## 11. Security Considerations

* MCP endpoints MUST be HTTPS
* Codex Bind does not guarantee MCP server safety
* Trust decisions beyond resolution are the responsibility of the client

---

## 12. Summary (Non-Normative)

Codex Bind describes MCP.
MCP servers execute MCP.

Codex collapses identity.
MCP executes capability.

These responsibilities MUST remain separate.
