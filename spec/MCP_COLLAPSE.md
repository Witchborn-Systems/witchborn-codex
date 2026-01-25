# MCP Collapse Semantics

Witchborn Codex Bind — Normative Specification

**Status:** Public, normative (Genesis)

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

### Collapse ("The Squish")

The deterministic process by which Codex Bind selects, filters, and reduces a set of records into a single, client-ready response.

---

## 2. Identity Normalization

AI identity URIs MAY include an authority or registrar hint in the form: `ai://<identity>@<authority>`.

**All resolution and collapse operations MUST use only the base identity before the first `@`.** Authority or registrar hints are ignored for collapse, inheritance, and record selection.

---

## 3. Canonical MCP Endpoint Representation

### 3.1 Normative Rule

Codex Bind MUST publish MCP endpoints as canonical **HTTPS URLs**.

### 3.2 Port Flexibility

While the transport protocol is locked to HTTPS, the port is arbitrary and defined by the agent host.

### 3.3 The Squish Rule

The `endpoint` returned in a collapsed MCP descriptor MUST include the port if it differs from the standard 443 (e.g., `https://agent.forge.io:3000/mcp`). Clients MUST connect to the exact port provided in the collapsed `endpoint` field during the execution phase.

---

## 4. Record Model

An MCP record MUST have:

* **type**: "MCP"
* **value**: HTTPS URL (including optional port) pointing to an MCP-compliant server
* **priority**: Integer (lower value has higher precedence)

Optional associated records:

* **CAPS**: Capability scopes
* **KEY**: Public verification key
* **CASCADE**: Upstream identity references

---

## 5. Collapse Modes

### 5.1 Default (Human / Neutral)

* MCP records are included in raw record output.
* No MCP descriptor is synthesized.

### 5.2 MCP Mode

Activated by a request to a dedicated MCP resolution endpoint (e.g., `/codex/resolve/mcp/{identity}/{subpath}`). In this mode, Codex Bind MUST:

1.  **Identify all MCP records** for the identity, including those gathered via `CASCADE` inheritance.
2.  **Apply Path Filtering**:
    * The resolver MUST search for an MCP record where the `path` attribute exactly matches the requested `{subpath}`.
    * If no exact match is found, the resolver MUST fall back to the record where `path` is defined as `"/"` (the Authority Root).
    * If no records exist for either the specific path or the root path, resolution MUST fail with a `404 Not Found` error.
3.  **Sort by ascending priority**: Lower priority values have higher precedence; the default priority is `10` if not specified.
4.  **Apply CAPS filtering**: If `CAPS` records are present, only endpoints intersecting with the requested capability set remain eligible.
5.  **Select exactly ONE MCP endpoint** based on the highest remaining priority after filtering.
6.  **Emit a collapsed MCP descriptor**: Return the final synthesized JSON object to the client.
---

## 6. CAPS Filtering

If CAPS records are present, only MCP endpoints whose declared capabilities intersect with the client-requested capability set MAY be selected. If no MCP endpoint satisfies CAPS constraints, resolution MUST fail with a clear error.

---

## 7. CASCADE Semantics

If a CASCADE record is present:

* Codex Bind MUST recursively resolve upstream identities.
* Local identity records override inherited records by priority.
* CASCADE resolution MUST be bounded to prevent infinite recursion.

---

## 8. Collapsed MCP Descriptor (Response Shape)

When collapsing for MCP mode, Codex Bind MUST return a response that includes:

```json
{
  "identity": "ai://sentinel",
  "mode": "mcp",
  "endpoint": "https://sentinel.example.com:8443/mcp",
  "capabilities": ["search", "summarize"],
  "key": "ed25519:BASE64...",
  "ttl": 3600,
  "source": "authoritative"
}

```

**Required Fields:** identity, mode, endpoint, ttl.

---

## 9. Execution Boundary (Critical)

Codex Bind MUST NOT proxy MCP traffic, establish sessions, or maintain MCP state. After returning a collapsed MCP descriptor, Codex Bind exits the execution path entirely.

---

## 10. Summary (Non-Normative)

Codex Bind describes MCP; MCP servers execute MCP. Codex collapses identity; MCP executes capability. These responsibilities MUST remain separate.