# Witchborn Codex: Canonical Data & File Structure Specification

## 1. Zone File Format

### 1.1. Zone File Location

All authoritative identity zones are stored as individual JSON files under a directory such as:

```
zones/
```

Each identity’s canonical zone file is:

```
zones/<identity>.json
```

* `<identity>` = canonical name, authority hint always stripped, all lowercase

**Examples:**

```
zones/goodfellow.json
zones/sentinel.json
zones/root.json
```

### 1.2. Zone File Schema

Each zone file MUST be a valid JSON object with the following fields:

```json
{
  "identity": "<identity>",
  "created_at": "<ISO-8601 UTC timestamp>",
  "contact": "<required contact info (email, url, or handle)>",
  "info": "<free-form string, human/machine readable, optional>",
  "records": [ <record1>, <record2>, ... ]
}
```

* `identity`: the canonical, authority-free identity string.
* `created_at`: ISO-8601 UTC timestamp of registration.
* `contact`: **(REQUIRED)** A valid contact method for the zone operator. May be an email (`mailto:`), a URL, or a verified handle. This ensures accountability for the zone.
* `info`: (optional) a free-form string for description, provenance, or onboarding; for UI/UX, never protocol logic.
* `records`: an array of records (see below).

**Example:**

```json
{
  "identity": "goodfellow",
  "created_at": "2026-01-25T00:00:00Z",
  "contact": "mailto:admin@goodfellow.ai",
  "info": "This zone defines the official Goodfellow AI identity.",
  "records": [
    {
      "type": "MCP",
      "value": {
        "endpoint": "[https://goodfellow.ai/mcp](https://goodfellow.ai/mcp)",
        "version": "1.0.0",
        "features": ["resources", "tools"],
        "capabilities": ["search", "summarize"]
      },
      "priority": 0
    }
  ]
}
```

### 1.3. Zone File Naming & Canonicalization

* The file name MUST be the base identity, lowercased, with no authority/registrar hint.
* Zone files MUST NOT be named with `@authority`.
* Zone files MUST be UTF-8 encoded.

## 2. Record Types

Each entry in the `records` array MUST be a JSON object with at least:

* `type`: string (see allowed values below)
* `value`: type-specific data
* `priority`: integer (optional, default 10)

### 2.1. Allowed Record Types

| Type      | Required Fields | Description                                                                     |
| --------- | --------------- | ------------------------------------------------------------------------------- |
| `BIND`    | value           | Machine-discoverable canonical cxbind endpoint(s); HTTPS URL (multiple allowed) |
| `APP`     | value           | Application or human metadata, URLs, legal/provenance                           |
| `MCP`     | value, priority | MCP endpoint (MUST be object, see MCP spec)                                     |
| `KEY`     | value           | Public verification key (string)                                                |
| `TXT`     | value           | Arbitrary text, description, labels                                             |
| `CAPS`    | value           | List of capabilities, e.g. `["search", "summarize"]`                            |
| `CASCADE` | value           | Delegates/inherits from identity (string, canonical form)                       |

### 2.2. Field Rules

* `type`: MUST be one of the types above, case-sensitive
* `value`: type-dependent:

  * `APP`, `TXT`, `CASCADE`, `KEY`, `BIND`: string
  * `CAPS`: list/array of strings
  * `MCP`: object with at least endpoint (and optional features/capabilities/version)
* `priority`: integer; lower value = higher precedence (default 10); only meaningful for MCP and any type with multiple entries

### 2.2.1 BIND Record URI Formatting

The value for a BIND record MUST be a full absolute HTTPS URI.

Explicit Porting: If the registrar's cxbind server is hosted on a non-standard port, that port MUST be explicitly defined within the URI string (e.g., https://cxbind.registrar-node.net:8443).

Registrar Responsibility: Registrars are responsible for ensuring their infrastructure is reachable on the port specified in their registered BIND record.

### 2.2.2 Path-Based Resolution (New)
Records MAY include a `path` field to support sub-apps or specific service endpoints within a single identity.

* **`path`**: A string representing the sub-resource (e.g., `/chatgpt`).
* **Default**: If omitted, the path MUST be treated as `/` (the root of the identity).
* **Selection**: When resolving `ai://identity/subpath`, the resolver MUST match the requested subpath against this field.

## 3. Zone File Authority

* Canonical zone for an identity is the file at `zones/<identity>.json`, with identity normalized per the spec (authority/registrar hints always stripped).
* Only one canonical zone per identity.
* All updates are via authenticated registrar actions (not in scope for Genesis).
* No recursive or merged zones; all CASCADE/inheritance is via record logic, not file inclusion.

## 4. Immutability & Mutations

* `identity` and `created_at` MUST NEVER change after initial registration.
* Record array (`records`) may be mutated, added to, or pruned only by authorized actions.
* History retention is implementation-defined (e.g., snapshot, signed log, or append-only ledger).

## 5. Root Zone File

The root authority is always published as:

```
zones/root.json
```

**Example:**

```json
{
  "identity": "root",
  "created_at": "2026-01-25T00:00:00Z",
  "contact": "mailto:governance@witchbornsystems.ai",
  "info": "Root authority and governance for Witchborn Codex. Registry public key, legal provenance, and canonical cxbind endpoint(s).",
  "records": [
    {
      "type": "BIND",
      "value": "[https://cxbind.witchbornsystems.ai](https://cxbind.witchbornsystems.ai)"
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
      "value": "[https://witchbornsystems.ai/governance](https://witchbornsystems.ai/governance)"
    }
  ]
}
```

* The root zone is protected (cannot be claimed).
* All genesis and registrar keys MUST be listed here.

## 6. Genesis Protections

* Certain reserved identities (e.g. `root`, `admin`, `openai`, `google`, etc.) are protected from claim or mutation during Genesis.
* Genesis protections are code/policy only, not enforced in the file format.

## 7. Extending/Customizing the Zone Schema

* New record types MAY be introduced in future protocol versions, and MUST NOT conflict with existing ones.
* Custom records for organization/consortium-specific metadata MUST use a distinct, prefixed type (e.g., `X_CUSTOM`).

## 8. Encoding, Formatting, and Security

* Files MUST be valid UTF-8 JSON, newline-normalized (LF).
* No comments or extraneous fields allowed.
* No secrets or private keys ever stored in zone files.
* For distributed/federated use, file signatures and hash-chains are recommended (future spec).

## 9. Zone File Example Directory Structure

```
zones/
  goodfellow.json
  sentinel.json
  root.json
```

## 10. Meta/Administrative Data (optional)

Registrars MAY store auxiliary meta or log files in a distinct, non-zone directory:

```
meta/
  goodfellow.log
  changelog.txt
```

These MUST never be loaded by cxbind as canonical identity data.

## 11. Canonicalization & Authority Recap

* All lookups, zone file names, and resolver logic use only the identity up to (but not including) any `@authority` suffix.
* All client/provenance logic MAY display the registrar/authority for human benefit.
* Authority hints are never used as part of zone file names or lookups.

# End of Canonical Zone File Spec