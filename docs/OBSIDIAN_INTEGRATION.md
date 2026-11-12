# Obsidian Integration Specification
## Axiom OS — 3-Stage Local Vault & Knowledge Synchronisation

---

## 1. Core Guardrails

- **Respect Existing Installation**: Obsidian is already installed on the host computer. Axiom OS never attempts to reinstall Obsidian or modify global Obsidian settings.
- **Explicit Vault Permission**: Axiom OS **never** accesses or scans the user's personal Obsidian vault without explicit configuration and folder-level authorization in **Settings -> Obsidian Integration**.
- **Non-Destructive Guarantee**: Existing user-authored notes are never silently overwritten. Every write or sync operation checks for existing content, offers a diff preview, and creates timestamped conflict backups if needed.

---

## 2. Three-Stage Architecture

### Stage 1: Clean Markdown Export & `obsidian://` URI Scheme (Zero-Config)
Works immediately without plugins or file-system permissions:
- Generates clean, valid Markdown with YAML frontmatter (`title`, `created`, `journey`, `road`, `epistemic_status`, `tags`), `[[Wikilinks]]`, and backlink sections for:
  - Scholar Lesson Notes
  - Feynman Explanations & Evolution History
  - Source-Grounded Research Summaries & Citation Lists
  - Builder Project Journals & Architecture Specs
  - Experiment Lab Records
  - Think Deeper Socratic Dialogues
- Generates RFC-compliant `obsidian://new?vault=...&file=...&content=...` and `obsidian://open?vault=...&file=...` URIs so the user can open or create notes in their existing Obsidian app with one click, or download a `.md` bundle.

### Stage 2: Optional Obsidian Local REST API Connector
Supports the **Obsidian Local REST API** community plugin (`https://127.0.0.1:27124` or `http://127.0.0.1:27123`):
- Configurable in Settings:
  - Endpoint URL (bound to `127.0.0.1` / `localhost` by default)
  - Bearer API Token (stored server-side only; never exposed to frontend bundles)
  - Vault Name
  - Approved Folder Whitelist (e.g. `Learning OS/`)
  - Explicit Read Permission toggle & Write Permission toggle
- All requests route through the FastAPI backend (`backend/app/services/obsidian_connector.py`) to avoid browser CORS leaks and protect the API token.

### Stage 3: Safe Folder-Scoped Two-Way Synchronisation
When an approved local vault folder or Local REST API is configured:
- Scans only explicitly whitelisted subdirectories.
- Computes content hashes (`SHA-256`) and modification timestamps (`last_synced_at`).
- Generates a **Sync Preview** showing:
  - `NEW_EXPORT` (Note exists in Axiom OS, ready to create in Obsidian)
  - `NEW_IMPORT` (Note created in approved Obsidian folder, ready to import into Axiom OS)
  - `MODIFIED_SAFE` (Only one side changed since last sync)
  - `CONFLICT_DETECTED` (Both sides edited; presents side-by-side diff and saves `.conflict-YYYYMMDD-HHMMSS.md` rather than overwriting).

---

## 3. Suggested Export Folder Template

Offered as an optional structure inside an approved subfolder:

```text
Learning OS/
  00 - Dashboard/
  01 - Learning Journeys/
  02 - Concepts/
  03 - Research Papers/
  04 - Resources/
  05 - Projects/
  06 - Experiments/
  07 - Reflections/
  08 - Think Deeper/
  09 - Daily Logs/
```
