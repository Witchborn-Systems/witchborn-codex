# Witchborn Codex Protocol (WCP)

**Version:** 1.0
**Status:** Normative (Frozen)
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
| **Codex** | The authoritative registry of AI identities and records      |
| **Codex Bind (cxbind)** | A public resolver that answers questions about Codex records |
| **Registrar (cxreg)** | A writable system authorized to submit changes               |
| **Identity** | A canonical, human-readable AI entity name                   |
| **Zone** | The complete record set bound to an identity                 |
| **Record** | A typed declaration attached to an identity                  |
| **MCP** | Machine Control Protocol descriptor (descriptive only)       |
| **Collapse** | Deterministic transformation of records into a resolved view |

---

## 4. Identity Model

### 4.1 Canonical Identity Format

Identities are expressed canonically as:

```
ai://<identity>
```

Where `<identity>`:
* Is lowercase, ASCII, and case-insensitive.
* May include `a–z`, `0–9`, `-`, `_`.
* Has no path, query, or fragment components.

### 4.2 Authority Hints (`@authority`)

AI identity URIs MAY include an authority or registrar hint in the form: `ai://<identity>@<authority>`.

**Resolution and collapse always use only the base identity before `@`.** Authority hints are utilized by Discovery Proxies to route requests to the correct authoritative node; however, once the authoritative node is reached, the hint is stripped to resolve the local identity file.

---

## 5. Zone Structure

A **Zone** is the authoritative data object associated with an identity.

### 5.1 Zone Fields
Zones include `identity`, `created_at`, and an array of `records`. 

### 5.2 Immutability
`identity` and `created_at` are immutable. All changes occur through record mutation, addition, or removal.

---

## 6. Record Model

### 6.1 Record Structure
Records contain a `type`, a `value`, and a `priority` (Default: 10).

### 6.2 Priority Rules
Lower numbers have higher precedence. Priority is only meaningful **within the same record type**.

---

## 7. Record Types (Normative)

* **7.1 APP**: Application or descriptive metadata (URLs, Contact references).
* **7.2 MCP**: Machine Control Protocol descriptor. MUST reference an HTTPS endpoint.
* **7.3 KEY**: Public cryptographic material for verification.
* **7.4 TXT**: Freeform textual declarations.
* **7.5 CAPS**: Descriptive capability declarations (constraints, permissions).
* **7.6 CASCADE**: Inheritance reference to another identity.

---

## 8. Resolution Semantics

### 8.1 Resolver Responsibility
A Codex resolver loads zones, validates structure, and returns records without execution.

### 8.2 Resolution States
* `LIVE`: Identity exists and is resolvable.
* `PROTECTED`: Identity reserved by policy.
* `UNREGISTERED`: No zone exists.
* `DELEGATED`: Authority resides elsewhere.

### 8.3 Port Discovery and Persistence
Resolution is protocol-agnostic regarding port assignments. If a BIND record includes a port (e.g., `:9000`), the client MUST use that specific port for subsequent requests to that authority.

### 8.4 Federated Delegation (BIND)
An identity zone MAY delegate authoritative resolution to an external server using a `BIND` record.

#### 8.4.1 Discovery Proxying
To reduce client complexity, a Root Authority MAY act as a Discovery Proxy. When a Root receives a resolution request for a delegated identity (e.g., `user@registrar`), it SHOULD recursively fetch the record from the BIND target and return the authoritative result to the client.

---

## 9. Write Authority
Writes originate from registrars. Genesis write paths are temporary; long-term writes MUST be authenticated and signed.

---

## 10. Security Model
The Codex assumes public readability and no secret material. Security guarantees are **descriptive**, not preventative.

---

## 11. Non-Goals (Explicit)
WCP does NOT attempt to act as a policy engine, judge behavior, or enforce ethics. Those concerns belong to **execution environments and law**.

---

## 12. Canonical Statement

> **The Witchborn Codex is a registry of responsibility, not a system of control.**