# n8n Local Automation Specification
## Axiom OS — Optional Local Workflow Layer

---

## 1. Architectural Role & Licensing Compliance

- **FastAPI Owns Core State**: FastAPI owns all business logic, SQLite/FTS5 persistence, AI provider routing, and security permissions. **Axiom OS functions 100% normally when n8n is offline or not installed.**
- **n8n as Optional Local Automation Layer**: n8n runs locally (`http://127.0.0.1:5678`) for scheduled digests, reminders, link verification, and backups.
- **Licensing Compliance**: Uses n8n Sustainable Use License compliant personal/local deployment. The n8n editor and webhooks are bound strictly to `127.0.0.1` and never exposed as a multi-tenant hosted commercial service.

---

## 2. Starting Local n8n (Docker & Non-Docker Options)

Because the host inspection revealed **Node.js v24.19.0 is installed** while Docker Desktop is not currently installed, we support both launch paths:

### Option A: Native Node.js (Recommended on this machine — Zero Docker required)
```powershell
npx n8n start
```
n8n starts at `http://localhost:5678`.

### Option B: Docker Compose (When Docker is installed)
```powershell
docker compose -f docker-compose.n8n.yml up -d
```

---

## 3. The 7 Documented Workflows (`n8n_workflows/`)

All 7 workflows are provided as importable n8n JSON files in `n8n_workflows/` AND have corresponding backend webhook/execution endpoints in `/api/v1/automation/workflows/{workflow_id}/trigger` so they can be triggered either by n8n on a schedule or directly from the Axiom OS Automation Center:

1. **`01_daily_learning_digest.json` — Daily Learning Digest**: Retrieves active journey, incomplete tasks, and due flashcards; generates a concise daily brief and saves it to `Notes` (`daily_log`).
2. **`02_spaced_repetition_reminder.json` — Spaced Repetition Reminder**: Queries `/api/v1/recall/due`, posts a dashboard notification/reminder, and logs review readiness.
3. **`03_resource_reverification.json` — Resource Reverification**: Checks saved resource URLs via HTTP HEAD/GET, detects broken links or changed access status, and updates `last_verified_at`.
4. **`04_weekly_project_review.json` — Weekly Project Review**: Retrieves project milestones and Experiment Lab logs, summarises engineering velocity and unresolved bugs, and recommends the next milestone task.
5. **`05_obsidian_export.json` — Obsidian Export Pipeline**: Processes user-approved export payloads, writes formatted Markdown via the authorised Obsidian connector, and records completion.
6. **`06_knowledge_backup.json` — Knowledge Backup**: Triggers `/api/v1/system/backups/create`, writing timestamped Markdown + JSON snapshots to `backups/YYYY-MM-DD_HHMMSS/` without ever overwriting prior backups.
7. **`07_research_inbox.json` — Research Inbox Processor**: Fetches user-approved RSS feeds (e.g., arXiv CS.AI, MIT News) or queued URLs, extracts metadata, links related concepts, and adds items to the review queue.
