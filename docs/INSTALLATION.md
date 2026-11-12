# Installation, Configuration, User & Backup Guides
## Axiom OS — Comprehensive Operations Manual

---

## 1. Windows PowerShell Installation & Quick Start (Primary Host)

### Prerequisites Verified on This System
- **Python**: `3.11.9`
- **Node.js / npm**: `v24.19.0` / `11.17.0`
- **Ollama**: `0.40.16` (with `qwen3.5:4b` and `gemma3:4b` installed)

### One-Command Startup (PowerShell)
From `d:\Learn Anything`:
```powershell
.\start-axiom.ps1
```

### Manual Step-by-Step Startup (Windows PowerShell)
1. **Backend Setup**:
   ```powershell
   cd "d:\Learn Anything\backend"
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Frontend Setup** (in a second terminal):
   ```powershell
   cd "d:\Learn Anything\frontend"
   npm install
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
3. Open `http://localhost:5173` in your browser.

---

## 2. macOS / Linux Installation Instructions

```bash
chmod +x start-axiom.sh
./start-axiom.sh
```
Or manually:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
And in a second terminal:
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

---

## 3. Configuring Ollama & Selecting Models

1. Ensure Ollama is running (`ollama serve` or the Windows tray application, listening on `http://127.0.0.1:11434`).
2. Open **Settings -> AI Providers & Hardware** in Axiom OS.
3. Click **Run Hardware & Ollama Inspection**.
   - On your Lenovo ThinkPad P16 (32 GB RAM, NVIDIA RTX A4500 16 GB VRAM), Axiom OS automatically detects your installed models (`qwen3.5:4b`, `gemma3:4b`, `nomic-embed-text:latest`) and recommends optimal models for your 16 GB VRAM envelope.
4. Select your active model per task (or use `qwen3.5:4b` / `gemma3:4b` across all tasks for fast, 100% local inference).
5. **Optional Model Downloads**: Axiom OS never downloads models without your permission. If you want a larger model (such as `qwen3:8b` or `qwen3:14b`), review the displayed download size, VRAM requirement, and license in Settings, then run the displayed `ollama pull <model>` command.

---

## 4. Backup and Restore Guide

### Creating a Backup
- **Via UI**: Go to **Settings -> Backup & Data Sovereignty** and click **Create Full Snapshot** (exports both a timestamped SQLite snapshot and a human-readable Markdown + JSON archive under `backend/backups/YYYYMMDD_HHMMSS/`).
- **Via API**: `POST http://127.0.0.1:8000/api/v1/system/backups`
- **Automated via n8n**: Import `n8n_workflows/06_knowledge_backup.json` to run scheduled nightly backups. Existing backups are never overwritten.

### Restoring from a Backup
1. Stop the backend server (`Ctrl+C`).
2. Copy your chosen snapshot from `backend/backups/<timestamp>/axiom_snapshot.db` to `backend/axiom.db`, OR use **Settings -> Backup & Data Sovereignty -> Restore JSON Archive** to non-destructively merge a JSON backup into your active database.
