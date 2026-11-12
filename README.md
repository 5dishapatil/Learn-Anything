# Axiom OS — Personal AI Research, Learning & Creation OS

> **An intelligent personal environment where curiosity becomes first-principles understanding, understanding becomes implementation, implementation leads to experimentation, and experimentation creates new knowledge.**

---

## Overview

**Axiom OS** is a local-first, zero-mandatory-cost AI Research, Learning, and Creation Operating System built for learners who want to think from first principles, conduct rigorous research, and build working engineering systems independently.

### Key Capabilities
- **Two Interconnected Learning Roads**:
  - **Road A — Scholar**: Concept & prerequisite discovery (`Essential` / `Recommended` / `Optional`), 18-point Multi-Stage Deep Explanation Engine (`Concise`, `Detailed`, `Research depth`) with `CORE`, `APPROXIMATE`, and `EXPLORATORY` epistemic labels, **6-Stage Feynman Learning Engine**, **Active Recall & Spaced Repetition**, and **Think Deeper** Socratic reasoning.
  - **Road B — Builder**: Editable Research & Build Blueprints, 13-part sequential engineering milestones (**Mission**, **Why It Matters**, **Prerequisites**, **Research**, **Architecture**, **Step-by-Step Implementation**, **Code Understanding**, **Testing**, **Experimentation**, **Break It**, **Deliverable**, **Reflection**, **Think Deeper**), **5-Level Progressive Hints**, **Monaco Coding Workspace**, and a scientific **Experiment Lab**.
- **Shared Hybrid Knowledge Graph**: Every concept links seamlessly between its Scholar theory and Builder implementation, backed by persistent 5-tier AI memory (`Learner`, `Knowledge`, `Research`, `Project`, `Session`) and instant session resume.
- **Authentic Resource Intelligence Engine**: Live discovery across **arXiv**, **OpenAlex**, **GitHub**, **Hugging Face**, **YouTube**, **MIT OpenCourseWare**, and **Stanford Engineering Everywhere** with honest free-access classification (`Completely free`, `Free audit`, `Free learning, paid certificate`, `Free preview only`, `Paid`, `Unverified`).
- **Hardware-Aware Pluggable AI Architecture**:
  - **Primary Default**: Local **Ollama** (`http://127.0.0.1:11434`) with automatic hardware inspection (verified on host: Intel Core i9-12900HX, 32 GB RAM, NVIDIA RTX A4500 Laptop GPU with 16 GB VRAM, `qwen3.5:4b` & `gemma3:4b`).
  - **Optional Cloud**: User-configured **Google Gemini Developer API** (disabled by default; explicit opt-in with privacy controls).
- **Obsidian Integration**: Clean Markdown export with YAML frontmatter and `[[wikilinks]]`, `obsidian://` URI launcher, optional Local REST API connector, and safe previewed folder synchronisation that never overwrites user notes.
- **Optional Local n8n Automation**: 7 ready-to-import workflows (`n8n_workflows/`) for Daily Learning Digests, Spaced Repetition Reminders, Resource Reverification, Weekly Project Reviews, Obsidian Exports, Knowledge Backups, and Research Inbox processing.

---

## Quick Start (Windows PowerShell)

```powershell
# Launch both Backend (FastAPI on :8000) and Frontend (Vite React on :5173)
.\start-axiom.ps1
```

Or start each service manually:

```powershell
# 1. Start Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Start Frontend (in a second terminal)
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open **http://localhost:5173** in your browser.

---

## Documentation Index

- [Non-Negotiable Principles (`AGENTS.md`)](file:///d:/Learn%20Anything/AGENTS.md)
- [Product Requirements Document (`docs/PRD.md`)](file:///d:/Learn%20Anything/docs/PRD.md)
- [System Architecture & Hardware Profile (`docs/ARCHITECTURE.md`)](file:///d:/Learn%20Anything/docs/ARCHITECTURE.md)
- [Database Schema & Data Model (`docs/DATA_MODEL.md`)](file:///d:/Learn%20Anything/docs/DATA_MODEL.md)
- [AI Architecture & Multi-Stage Engine (`docs/AI_ARCHITECTURE.md`)](file:///d:/Learn%20Anything/docs/AI_ARCHITECTURE.md)
- [Resource Discovery Engine (`docs/RESOURCE_DISCOVERY.md`)](file:///d:/Learn%20Anything/docs/RESOURCE_DISCOVERY.md)
- [Obsidian Integration (`docs/OBSIDIAN_INTEGRATION.md`)](file:///d:/Learn%20Anything/docs/OBSIDIAN_INTEGRATION.md)
- [n8n Local Automation (`docs/N8N_INTEGRATION.md`)](file:///d:/Learn%20Anything/docs/N8N_INTEGRATION.md)
- [Security & Privacy (`docs/SECURITY.md`)](file:///d:/Learn%20Anything/docs/SECURITY.md)
- [Implementation Plan (`docs/IMPLEMENTATION_PLAN.md`)](file:///d:/Learn%20Anything/docs/IMPLEMENTATION_PLAN.md)
- [Testing Plan (`docs/TESTING_PLAN.md`)](file:///d:/Learn%20Anything/docs/TESTING_PLAN.md)
- [Installation & Backup Guide (`docs/INSTALLATION.md`)](file:///d:/Learn%20Anything/docs/INSTALLATION.md)
- [User & Configuration Guide (`docs/USER_GUIDE.md`)](file:///d:/Learn%20Anything/docs/USER_GUIDE.md)
