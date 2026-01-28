# Witchborn Codex Server

This directory contains the authoritative resolution engine for the Witchborn Codex. Depending on its configuration, this server acts as either the **Global Root Authority** or a **Sovereign Registrar Node** (like @webai).

---


## 🚀 Installation & Service Setup

While the server code lives in this directory, it relies on a shared environment at the project root.

1. **Setup Environment (From Project Root):**
   ```bash
   cd ..
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Install Service (From Server Directory):**
   ```bash
   cd server
   sudo ./install_service.sh
   ```

This ensures the `systemd` unit file correctly maps to your `.venv` for `uvicorn` execution.

---

## 🏗️ Federated Architecture

The Codex is designed to be federated. You can run multiple instances of this server on one machine using different configurations.

### Root Authority (`root_server.py`)
The Root Authority manages the top-level directory of registrars.
- **Port:** 8000
- **Zone Directory:** `zones/`
- **Responsibility:** Resolving TLDs (e.g., `ai://webai`, `ai://google`) and delegating traffic via `BIND` records.

### Registrar Node (e.g., `@webai`)
A Node manages individual user identities for a specific registrar.
- **Port:** 9000 (Example)
- **Zone Directory:** `zones_webai/` (Example)
- **Responsibility:** Resolving specific user records (e.g., `ai://brandon@webai`).

---

## 📁 Zone File Management

### Metadata Requirements
Per `spec/ZONE_SPEC.md`, every zone file MUST contain:
- `identity`: Canonical name (no @ hint).
- `created_at`: ISO-8601 timestamp.
- `contact`: Mandatory email or URL for operator accountability.

### Validation
Before pushing changes to any zone, run the local validator:
```bash
python validate_zone.py zones/example.json
```

---

## 🔧 Configuration (Environment Variables)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `CODEX_PORT` | The internal port for the API. | `8000` |
| `CODEX_ZONES_DIR` | The path to the folder containing .json zones. | `zones` |
| `PYTHONUNBUFFERED` | Ensures logs appear in real-time in `journalctl`. | `1` |

---

## 🛡️ Security & Nginx
This server should always run behind a reverse proxy (Nginx) to handle SSL termination and load balancing. 

**Recommended Nginx Flow:**
1. **SSL:** Managed by Certbot.
2. **Pathing:** Root Authority at `cxbind.witchbornsystems.ai`.
3. **Delegation:** Registrar Node at `webai.witchbornsystems.ai/codex`.

---

## ⚖️ License
Licensed under the **ForgeBorn License v1.0.1**.
Attribution is required for public distribution or SaaS hosting.