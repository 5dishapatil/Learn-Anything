# Configuration, User Guide & Backup Reference
## Axiom OS — Detailed Guides

---

## 1. Environment Configuration (`.env`)

Copy `.env.example` to `backend/.env` (optional — sensible local defaults work out of the box with zero configuration):

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./axiom.db` | Local SQLite database path (PostgreSQL compatible URI supported) |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Local Ollama server endpoint |
| `DEFAULT_OLLAMA_MODEL` | `qwen3.5:4b` | Primary local model (auto-falls back to first available local model) |
| `ALLOW_CLOUD_AI` | `false` | Must be explicitly enabled by user before Gemini can be called |
| `GEMINI_API_KEY` | *(empty)* | Optional user-configured Google Gemini Developer API key |
| `GITHUB_TOKEN` | *(empty)* | Optional GitHub PAT to increase rate limit from 60 to 5,000 req/hr |
| `YOUTUBE_API_KEY` | *(empty)* | Optional YouTube Data API v3 key |
| `OBSIDIAN_REST_URL` | `http://127.0.0.1:27123` | Optional Obsidian Local REST API endpoint |
| `OBSIDIAN_API_TOKEN` | *(empty)* | Optional Obsidian Local REST API token |
| `N8N_WEBHOOK_BASE_URL` | `http://127.0.0.1:5678` | Optional local n8n instance URL |

---

## 2. User Guide: Navigating Axiom OS

### Keyboard Shortcuts & Command Palette
- **`Ctrl+K` / `Cmd+K`**: Open the global **Command Palette** from anywhere to jump to any screen, search concepts/notes/resources via SQLite FTS5, switch between **Scholar Road** and **Builder Road**, or trigger an Obsidian export.

### The Core Workflow
1. **Onboarding / Explore**: Enter any curiosity or engineering goal (e.g., *"I want to understand how operating systems work and eventually build my own tiny operating system"* or *"I want to build a tiny GPT from scratch"*).
2. **Research & Build Blueprint**: Inspect the generated prerequisite graph (`Essential`, `Recommended`, `Optional`), review the linked Scholar and Builder milestones, edit any milestone or deliverable, and approve the blueprint.
3. **Scholar Workspace**:
   - Read multi-stage explanations at `Concise`, `Detailed`, or `Research depth` with `CORE`, `APPROXIMATE`, and `EXPLORATORY` epistemic badges.
   - Complete the **6-Stage Feynman Engine**: write your intuition, review evidence-based gap analysis, answer Socratic guiding questions, and compare your revised explanation with your original draft.
   - Practice **Active Recall** (Flashcards, Free Recall, Derivations) scheduled via transparent spaced repetition.
   - Engage with **Think Deeper**: answer higher-order counterfactual and trade-off questions to unlock Socratic follow-ups and research discussions.
4. **Builder Workspace**:
   - Work through sequential milestones (**A. Mission** through **M. Think Deeper**).
   - Use **5-Tier Progressive Hints** only when needed.
   - Write and inspect code in the integrated **Monaco Editor**, run controlled verification tests, and complete the **Break It** controlled-failure challenges.
5. **Experiment Lab**: Log formal hypotheses, variables changed, procedures, expected vs. actual outcomes, and quantitative metrics across runs.
6. **My Knowledge & Obsidian**: Browse connected notes, backlinks, citations, and learning history, and export or synchronise directly with your Obsidian vault.
