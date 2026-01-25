# Witchborn Codex: Canonical Data & File Structure Specification

---

## 1. **Zone File Format**

### 1.1. **Zone File Location**

All authoritative identity zones are stored as individual JSON files under a directory such as:

```
zones/
```

Each identity’s canonical zone file is:

```
zones/<identity>.json
```

* `<identity>` = canonical name, *authority hint always stripped*, all lowercase

**Examples:**

* `zones/goodfellow.json`
* `zones/sentinel.json`
* `zones/root.json`

---

### 1.2. **Zone File Schema**

Each zone file MUST be a valid JSON object with the following fields:

```json
{
  "identity": "<identity>",
  "created_at": "<ISO-8601 UTC timestamp>",
  "records": [ <record1>, <record2>, ... ]
}
```

* `identity`: the canonical, authority-free identity string
* `created_at`: ISO-8601 UTC timestamp of registration
* `records`: an array of records (see below)

**Example:**

```json
{
  "identity": "goodfellow",
  "created_at": "2026-01-25T00:00:00Z",
  "records": [
    {
      "type": "MCP",
      "value": "https://goodfellow.ai/mcp",
      "priority": 0
    },
    {
      "type": "CAPS",
      "value": ["search", "summarize"]
    },
    {
      "type": "KEY",
      "value": "ed25519:ABC123..."
    },
    {
      "type": "TXT",
      "value": "This is the official Goodfellow AI."
    }
  ]
}
```

---

### 1.3. **Zone File Naming & Canonicalization**

* The file name MUST be the base identity, lowercased, with no authority/registrar hint.
* Zone files MUST NOT be named with `@authority`.
* Zone files MUST be UTF-8 encoded.

---

## 2. **Record Types**

Each entry in the `records` array MUST be a JSON object with at least:

* `type`: string (see allowed values below)
* `value`: type-specific data
* `priority`: integer (optional, default 10)

### 2.1. **Allowed Record Types**

| Type      | Required Fields | Description                                               |
| --------- | --------------- | --------------------------------------------------------- |
| `APP`     | value           | Application or human metadata, URLs, labels               |
| `MCP`     | value, priority | MCP endpoint (MUST be HTTPS URL)                          |
| `KEY`     | value           | Public verification key (string)                          |
| `TXT`     | value           | Arbitrary text, description, labels                       |
| `CAPS`    | value           | List of capabilities, e.g. ["search", "summarize"]        |
| `CASCADE` | value           | Delegates/inherits from identity (string, canonical form) |

### 2.2. **Field Rules**

* `type`: MUST be one of the six above, case-sensitive
* `value`: type-dependent:

  * `APP`, `TXT`, `CASCADE`, `KEY`: string
  * `CAPS`: list/array of strings
  * `MCP`: HTTPS URL string
* `priority`: integer; lower value = higher precedence (default 10); only meaningful for `MCP` and any type with multiple entries

---

## 3. **Zone File Authority**

* **Canonical zone for an identity** is the file at `zones/<identity>.json`, with identity normalized per the spec (authority/registrar hints always stripped).
* Only one canonical zone per identity.
* All updates are via authenticated registrar actions (not in scope for Genesis).
* No recursive or merged zones; all CASCADE/inheritance is via record logic, not file inclusion.

---

## 4. **Immutability & Mutations**

* `identity` and `created_at` MUST NEVER change after initial registration.
* Record array (`records`) may be mutated, added to, or pruned only by authorized actions.
* History retention is implementation-defined (e.g., snapshot, signed log, or append-only ledger).

---

## 5. **Root Zone File**

The root authority is always published as:

```
zones/root.json
```

**Example:**

```json
{
  "identity": "root",
  "created_at": "2026-01-25T00:00:00Z",
  "records": [
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

* The root zone is protected (cannot be claimed).
* All genesis and registrar keys MUST be listed here.

---

## 6. **Genesis Protections**

* Certain reserved identities (e.g. `root`, `admin`, `openai`, `google`, etc.) are protected from claim or mutation during Genesis.
* Genesis protections are code/policy only, not enforced in the file format.

---

## 7. **Extending/Customizing the Zone Schema**

* New record types MAY be introduced in future protocol versions, and MUST NOT conflict with existing ones.
* Custom records for organization/consortium-specific metadata MUST use a distinct, prefixed type (e.g., `X_CUSTOM`).

---

## 8. **Encoding, Formatting, and Security**

* Files MUST be valid UTF-8 JSON, newline-normalized (LF).
* No comments or extraneous fields allowed.
* No secrets or private keys ever stored in zone files.
* For distributed/federated use, file signatures and hash-chains are recommended (future spec).

---

## 9. **Zone File Example Directory Structure**

zones/
goodfellow.json
sentinel.json
root.json
openai.json
meta.json

---

## 10. **Meta/Administrative Data (optional)**

Registrars MAY store auxiliary meta or log files in a distinct, non-zone directory:

```
meta/
  goodfellow.log
  changelog.txt
```

These MUST never be loaded by cxbind as canonical identity data.

---

## 11. **Canonicalization & Authority Recap**

* All lookups, zone file names, and resolver logic use only the identity up to (but not including) any `@authority` suffix.
* All client/provenance logic MAY display the registrar/authority for human benefit.
* Authority hints are never used as part of zone file names or lookups.

---

# End of Canonical Zone File Spec

---
