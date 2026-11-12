# Configuration Guide
## Axiom OS — Local AI, Providers, Obsidian & Automation

---

## 1. Local AI (Ollama) Configuration

Axiom OS uses local **Ollama** (`http://127.0.0.1:11434`) as its primary zero-cost AI provider.
- **Detected Host Hardware**: Intel Core i9-12900HX (16C/24T), 32 GB RAM, NVIDIA RTX A4500 Laptop GPU (16 GB VRAM).
- **Detected Installed Models**: `qwen3.5:4b` (3.4 GB), `gemma3:4b` (3.3 GB), `nomic-embed-text:latest` (274 MB).
- **Model Routing**: In **Settings -> AI Providers**, you can assign specific models to:
  1. General Explanation Model
  2. Deep Research Explanation Model
  3. Coding & Architecture Model
  4. Lightweight Classification Model
  5. Socratic Question Generation Model

---

## 2. Optional Cloud AI (Google Gemini Developer API)

- Disabled by default (`ALLOW_CLOUD_AI=false`).
- To enable:
  1. Open **Settings -> AI Providers -> Optional Gemini Cloud**.
  2. Review the Free-Tier vs. Paid-Tier privacy disclosure.
  3. Enter your Gemini API Key and toggle **Enable Gemini Provider**.
  4. Choose your data egress boundaries (Notes/Obsidian egress and Source Code egress default to **Blocked**).

---

## 3. Obsidian Configuration

1. **Stage 1 (No setup required)**: Click **Export to Obsidian** or **Open in Obsidian (`obsidian://`)** on any Lesson, Feynman cycle, Think Deeper dialogue, Project, or Note.
2. **Stage 2 (Local REST API)**: Install the *Local REST API* community plugin in Obsidian, copy the API key, and enter it in **Settings -> Obsidian Integration**.
3. **Stage 3 (Folder Synchronisation)**: Specify an approved subfolder (e.g. `Learning OS`) and click **Generate Sync Preview** before applying any two-way sync.

---

## 4. Optional Local n8n Automation

1. Start n8n locally via `npx n8n start` (uses installed Node.js v24) or `docker compose -f docker-compose.n8n.yml up -d`.
2. Import any of the 7 workflows from `n8n_workflows/*.json`.
3. Configure the webhook target as `http://127.0.0.1:8000/api/v1/automation/workflows/{workflow_key}/execute`.
