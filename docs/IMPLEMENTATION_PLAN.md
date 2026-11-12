# Master Implementation Plan (Phases 0–10)
## Axiom OS — Sequential Execution Roadmap

---

## Phase 0 — Inspect & Plan (Completed)
- Inspected `d:\Learn Anything` workspace and host hardware (Windows 11, Intel i9-12900HX, 32 GB RAM, NVIDIA RTX A4500 16 GB VRAM, Python 3.11.9, Node v24.19.0, Ollama 0.40.16 with `qwen3.5:4b` & `gemma3:4b`).
- Authored `AGENTS.md`, `README.md`, and complete `docs/` specifications.

## Phase 1 & Phase 2 — Backend Storage + Frontend Foundation (Unified Full-Stack Core)
- Implement the 38+ SQLAlchemy 2.0 relational models + SQLite FTS5 search index + Alembic migration setup (`backend/app/models/`).
- Implement validated Pydantic v2 schemas (`backend/app/schemas/`).
- Seed rich, authentic initial data (`Transformers & TinyGPT`, `Operating Systems from First Principles`, `AI from Scratch in 30 Days`) so the application has immediate deep content out-of-the-box in addition to live generation.
- Build the complete React + TypeScript + Tailwind + Lucide + Monaco + Mermaid frontend (`frontend/src/`) covering all 11 navigation areas, Onboarding, Home Dashboard, Explore, Blueprint, Scholar, Builder, Research Library, Projects, Experiment Lab, My Knowledge, Think Deeper, and Settings.

## Phase 3 — Ollama & Pluggable AI Provider Architecture
- Implement `AIProvider` interface, `OllamaProvider` (`localhost:11434`), `GeminiProvider` (opt-in cloud), and `HardwareInspector` (detecting CPU, 32 GB RAM, RTX A4500 16 GB VRAM via `nvidia-smi`).
- Provide live health checks, model discovery, task-based model routing, streaming, and structured JSON validation.

## Phase 4 — AI Learning Intelligence (Scholar, Feynman, Recall, Think Deeper)
- Implement the 18 specialised AI orchestration services.
- Build the Multi-Stage Deep Explanation Engine (`Concise`, `Detailed`, `Research depth`) with `CORE`, `APPROXIMATE`, and `EXPLORATORY` epistemic badges.
- Build the 6-stage interactive Feynman Learning Engine with version diffing and evidence-based gap detection.
- Build Active Recall + transparent Spaced Repetition scheduling.
- Build the mandatory **Think Deeper** Socratic engine on every concept and milestone.

## Phase 5 — Builder Engine, Coding Workspace & Experiment Lab
- Implement editable Research & Build Blueprints and 13-part sequential Project Milestones (A. Mission through M. Think Deeper, including J. Break It).
- Implement 5-level progressive hints, Monaco code artifact management, controlled test verification, and the scientific Experiment Lab.

## Phase 6 — Resource Intelligence Engine
- Implement live adapters for arXiv, OpenAlex, GitHub, Hugging Face, YouTube, MIT OCW, Stanford SEE, and curated free courses with strict free-access classification and SQLite caching.

## Phase 7 — Obsidian Integration
- Implement Stage 1 (Markdown + YAML frontmatter + `[[wikilinks]]` + `obsidian://` URI launcher), Stage 2 (Local REST API connector), and Stage 3 (Safe folder-scoped sync preview without overwriting user notes).

## Phase 8 — Local n8n Automation
- Implement the optional n8n connector, 7 importable workflow JSON files (`n8n_workflows/`), `docker-compose.n8n.yml`, and local execution fallback when n8n is offline.

## Phase 9 — Adventure, Progression & Knowledge Graph
- Implement interactive SVG/Canvas Knowledge Constellation Graph, XP/Milestone unlock mechanics, non-punitive learning history, and seamless Scholar <-> Builder road switching.

## Phase 10 — Quality Verification & Acceptance Tests (Tests A–I + OS Definition of Success)
- Run backend Pytest suite covering all 9 critical acceptance tests (Tests A–I) and the Operating Systems Definition of Success workflow.
- Run frontend Vitest + production build verification and live end-to-end browser verification.
