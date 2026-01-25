
Below is a **full, canonical draft of the WCP (Witchborn Codex Protocol)** suitable to live at:

```
spec/WCP.md
```

It is written to be **normative, boring, and enforceable**.
No metaphors. No marketing. No implementation leaks.

---

# Witchborn Codex Protocol (WCP)

**Version:** 1.0
**Status:** Normative
**Scope:** Public, authoritative
**Audience:** Registry operators, registrars, client implementers, auditors

---

## 1. Purpose

The Witchborn Codex Protocol (WCP) defines the **authoritative rules, data model, and resolution semantics** for registered AI identities within the Witchborn Codex ecosystem.

WCP specifies **what may be described, resolved, and published** about an AI entity.

WCP explicitly does **not** define:

* Model execution
* Inference behavior
* MCP execution
* Hosting, routing, or proxying
* Enforcement mechanisms beyond description

---

## 2. Core Principle

> **Codex describes. Execution occurs elsewhere.**

The Codex is a **civil registry**, not a runtime.

---

## 3. Terminology (Normative)

| Term                    | Definition                                                   |
| ----------------------- | ------------------------------------------------------------ |
| **Codex**               | The authoritative registry of AI identities and records      |
| **Codex Bind (cxbind)** | A public resolver that answers questions about Codex records |
| **Registrar (cxreg)**   | A writable system authorized to submit changes               |
| **Identity**            | A canonical, human-readable AI entity name                   |
| **Zone**                | The complete record set bound to an identity                 |
| **Record**              | A typed declaration attached to an identity                  |
| **MCP**                 | Machine Control Protocol descriptor (descriptive only)       |
| **Collapse**            | Deterministic transformation of records into a resolved view |

---

## 4. Identity Model

### 4.1 Canonical Identity Format

Identities are expressed canonically as:

```
ai://<identity>
```

Where `<identity>`:

* Is lowercase
* Is ASCII
* May include `a–z`, `0–9`, `-`, `_`
* Is case-insensitive
* Has no path, query, or fragment components

Examples:

```
ai://forgekeeper
ai://legalbot_us
ai://weather-agent
```

---

### 4.2 Identity Scope

An identity represents a **logical AI entity**, not:

* A model
* A deployment
* A server
* A version

Identity **persists across**:

* Model swaps
* Infrastructure changes
* Hosting providers

---

## 5. Zone Structure

A **Zone** is the authoritative data object associated with an identity.

### 5.1 Zone Fields

```json
{
  "identity": "forgekeeper",
  "created_at": "2026-01-25T00:00:00Z",
  "records": [ "..." ]
}
```

### 5.2 Immutability

* `identity` and `created_at` are immutable
* All changes occur through record mutation, addition, or removal
* History retention is implementation-defined

---

## 6. Record Model

### 6.1 Record Structure

```json
{
  "type": "APP | MCP | KEY | TXT | CAPS | CASCADE",
  "value": "<type-specific>",
  "priority": 10
}
```

### 6.2 Priority Rules

* Lower numbers have higher precedence
* Default priority is `10`
* Priority is only meaningful **within the same record type**

---

## 7. Record Types (Normative)

### 7.1 `APP`

Application or descriptive metadata.

Used for:

* Human-readable descriptions
* URLs
* Contact references

Codex does **not** interpret APP semantics.

---

### 7.2 `MCP`

A Machine Control Protocol descriptor.

* Value MUST reference an **HTTPS endpoint**
* Codex MUST NOT execute MCP
* MCP execution is always client ↔ MCP server

Details of MCP handling are defined in `MCP_COLLAPSE.md`.

---

### 7.3 `KEY`

Public cryptographic material.

* Used for identity binding, signatures, or verification
* Codex does not enforce crypto semantics
* Codex publishes only

---

### 7.4 `TXT`

Freeform textual declarations.

* Human or machine readable
* No enforced schema
* No semantic guarantees

---

### 7.5 `CAPS`

Capability declarations.

Examples:

* Network access permissions
* Actuation constraints
* Jurisdictional limits

CAPS records are **descriptive only**.
Enforcement occurs elsewhere.

---

### 7.6 `CASCADE`

Inheritance or delegation reference.

* Points to another identity
* Used during collapse resolution
* Cycles MUST be detected and rejected

---

## 8. Resolution Semantics

### 8.1 Resolver Responsibility

A Codex resolver:

* Loads the authoritative zone
* Validates record structure
* Returns records **without execution**
* May return collapsed views

Resolvers MUST NOT:

* Execute MCP
* Rewrite records
* Inject inferred meaning

---

### 8.2 Resolution States

| Status         | Meaning                           |
| -------------- | --------------------------------- |
| `LIVE`         | Identity exists and is resolvable |
| `PROTECTED`    | Identity reserved by policy       |
| `UNREGISTERED` | No zone exists                    |

---

## 9. Write Authority

* Codex Bind is **read-mostly**
* Writes originate from registrars
* Genesis write paths are temporary
* Long-term writes MUST be authenticated and signed

Registrar protocol is out of scope for WCP v1.

---

## 10. Genesis Period

During Genesis:

* Certain identities may be protected
* Claim operations may exist inline
* Behavior is transitional

Genesis mechanisms MUST be removable without breaking WCP semantics.

---

## 11. Security Model

The Codex assumes:

* Public readability
* Zero trust in clients
* No secret material

Security guarantees are **descriptive**, not preventative.

---

## 12. Non-Goals (Explicit)

WCP does NOT attempt to:

* Prevent misuse
* Enforce ethics
* Guarantee safety
* Judge behavior
* Act as a policy engine

Those concerns belong to **execution environments and law**.

---

## 13. Extensibility

Future versions may introduce:

* New record types
* Additional collapse rules
* Signed zone bundles

Backward compatibility is REQUIRED.

---

## 14. Canonical Statement

> **The Witchborn Codex is a registry of responsibility, not a system of control.**

---
