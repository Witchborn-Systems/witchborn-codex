# Witchborn Codex Server

This directory contains the reference implementation of the Witchborn Codex
**Root Resolver** and **Public Registry**.

The Codex server is responsible for:
- Resolving `ai://` identities to signed record sets
- Enforcing protective holds and safe-harbor behavior
- Operating as a neutral, read-only authority for identity resolution

This server **does not**:
- Proxy traffic
- Host AI models
- Execute MCP calls
- Perform analytics or tracking

---

## Status

Genesis scaffold.

Implementation will proceed in public, in alignment with the
Witchborn Codex Protocol (WCP) located in `/spec/WCP.md`.

---

## Design Principles

- Identity before execution
- Resolution before hosting
- Law before optimization
- Exit before lock-in
