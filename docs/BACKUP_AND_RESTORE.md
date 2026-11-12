# Configuration & Backup/Restore Reference
## Axiom OS

See `docs/INSTALLATION.md` and `docs/USER_GUIDE.md` for full setup details.

## Backup & Restore Operations

### Automated & Manual Backups
1. **Database & Markdown Snapshots**:
   - Endpoint: `POST /api/v1/system/backups`
   - Creates a timestamped folder under `backend/backups/YYYYMMDD_HHMMSS/` containing:
     - `axiom_snapshot.db`: Binary consistent SQLite backup (`sqlite3.Connection.backup`).
     - `knowledge_export.json`: Complete structured JSON export of all journeys, concepts, lessons, Feynman histories, Think Deeper responses, projects, milestones, experiments, notes, and memories.
     - `markdown_vault/`: Clean Obsidian-ready Markdown hierarchy (`01 - Learning Journeys` through `09 - Daily Logs`).
2. **Non-Destructive Guarantee**:
   - Backups use unique timestamped directories and never overwrite previous backups.
3. **Restore Procedure**:
   - Endpoint: `POST /api/v1/system/backups/{backup_id}/restore` or via **Settings -> Backup & Data Sovereignty**.
